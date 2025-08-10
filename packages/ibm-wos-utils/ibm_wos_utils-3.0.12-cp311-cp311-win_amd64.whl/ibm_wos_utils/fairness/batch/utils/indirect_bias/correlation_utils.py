# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2022
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

try:
    from pyspark.ml.classification import LogisticRegression
    from pyspark.ml.feature import OneHotEncoder, StringIndexer, IndexToString, VectorAssembler, StandardScaler, QuantileDiscretizer
    from pyspark.ml.regression import LinearRegression
    from pyspark.ml import Pipeline
    import pyspark.sql.functions as F
except ImportError as ie:
    pass

import logging
import numpy as np
import statistics
from operator import itemgetter

from ibm_wos_utils.fairness.batch.utils import constants
from ibm_wos_utils.fairness.batch.utils.date_util import DateUtil
from ibm_wos_utils.fairness.batch.utils.python_util import get
from ibm_wos_utils.fairness.batch.utils.sql_utils import SQLUtils

logger = logging.getLogger(__name__)

MODEL_ACCURACY_THRESHOLD = 0.75
CORRELATION_COEFFICIENT_THRESHOLD = 0.15
CUMULATIVE_CORRELATION_COEFFICIENT_THRESHOLD = 0.6
BINS_COUNT = 10

class CorrelationUtils():
    """
    Class for correlation identification utilities
    """

    @classmethod
    def find_correlated_attributes(cls, training_data, model_details: dict, protected_attribute: str):
        """
        Finds correlated attributes for given protected attribute
        Arguments:
            training_data: The spark dataframe containing training data 
            model_details: The model details like features, categorical columns, label column
            protected_attribute: The protected attribute
        """
        logger.info("Identifying correlated attributes for {}".format(protected_attribute))
        start_time = DateUtil.current_milli_time()
        correlated_attributes = []
        features = model_details.get("feature_columns")
        categorical_features = model_details.get("categorical_columns")
        selected_cols = features + [protected_attribute]
        data = training_data.select(selected_cols)

        # Build correlation identification model
        corr_model_details = cls.build_correlation_identification_model(data, features, categorical_features, protected_attribute)

        model_type = corr_model_details.get("model_type")
        # Return empty correlations if generated model is of poor quality
        if (constants.CLASSIFICATION_MODEL_TYPE == model_type and corr_model_details.get("accuracy") < MODEL_ACCURACY_THRESHOLD) or \
            (constants.REGRESSION_MODEL_TYPE == model_type and corr_model_details.get("normalized_rmse") > 1):
            logger.info("The quality of the generated correlation identification model is below threshold. Hence returning empty correlations for the protected attribute {}".format(protected_attribute))
            return correlated_attributes

        coefficients = corr_model_details.get("feature_coefficients")
        coefficients = [abs(coef) for coef in coefficients]            
        # Normalizing the coefficients
        coefficients = [round(float(i)/sum(coefficients), 4) for i in coefficients]

        # Calculate the mean, standard deviation and tau
        coef_mean = statistics.mean(coefficients)
        coef_stddev = statistics.stdev(coefficients)
        tau = coef_mean - coef_stddev if coef_mean > coef_stddev else coef_mean + coef_stddev

        # Get coefficients greater than tau
        training_features = corr_model_details.get("training_features")
        correlation_coefficients = dict()
        for idx, col in enumerate(training_features):
            if coefficients[idx] > tau:
                correlation_coefficients[col] = coefficients[idx]

        # Sort the attributes in decreasing order of coefficient and take upto top 5 entries having coefficient >= threshold
        correlation_coefficients = dict(
            sorted(correlation_coefficients.items(), key=lambda x: x[1], reverse=True))
        top_correlation_coefficients = {k: round(float(v), 4) for k, v in list(
            correlation_coefficients.items())[0:5]}
        # If some features exist with correlation coefficient > threshold, they are picked as correlated features
        # Otherwise if cumulative correlation coefficient of attributes(max 5) is >= 0.75, then they are picked as correlated features
        correlated_attr_coefficients = {k: v for k, v in top_correlation_coefficients.items() if v >= CORRELATION_COEFFICIENT_THRESHOLD}

        # If there are no features having correlation coefficient > threshold, check top 5 features if their cumulative coefficient >= CUMULATIVE_CORRELATION_COEFFICIENT_THRESHOLD.
        if len(correlated_attr_coefficients) == 0:
            if sum(top_correlation_coefficients.values()) >= CUMULATIVE_CORRELATION_COEFFICIENT_THRESHOLD:
                total_coef = 0
                for k,v in top_correlation_coefficients.items():
                    total_coef += v
                    correlated_attr_coefficients[k] = v
                    if total_coef >= CUMULATIVE_CORRELATION_COEFFICIENT_THRESHOLD:
                        break

        # Return correlation information in required format
        if len(correlated_attr_coefficients) > 0:
            for attr, value in correlated_attr_coefficients.items():
                correlated_attribute_info = {
                    "feature": attr,
                    "correlation_value": value
                }
                correlated_attributes.append(correlated_attribute_info)
        else:
            logger.info("There are no correlated attributes for protected attribute '{}'".format(protected_attribute))
        time_taken = DateUtil.current_milli_time() - start_time
        logger.info("Time taken to find correlated attributes for the protected attribute {} is {} seconds.".format(protected_attribute, time_taken/1000))

        return correlated_attributes

    @classmethod
    def build_correlation_identification_model(cls, data, features: list, categorical_features: list, label_column: str):
        """
        Finds correlation coefficients of features for given protected attribute
        - Internally builds a model with non-protected attributes as features and the protected attribute as label
        Arguments:
            data: The spark dataframe containing features and the protected_attribute
            features: The list of all feature columns
            categorical_features: The list of all categorical features
            label_column: The label column
            model_type: The type of correlation identification model
        Returns:
            model_details: Details of the generated correlation identification model like coefficients, accuracy or rmse
        """
        start_time = DateUtil.current_milli_time()
        logger.info("Started building correlation identification model for the protected attribute {}".format(label_column))
        model_details = dict()
        # Prepare stages for pipeline
        stages = []
        prediction_column = label_column

        # Convert categorical columns to numerical using StringIndexer
        for cat_feature in categorical_features:
            string_indexer = StringIndexer(inputCol = cat_feature, outputCol = cat_feature + 'Index')
            stages.append(string_indexer)

        # Checking if label column is categorical to decide the model type
        dtypes_dict = dict(data.dtypes)
        is_categorical_label = dtypes_dict.get(label_column) in ["string", "boolean"]
        if is_categorical_label:
            model_type = constants.CLASSIFICATION_MODEL_TYPE
            # If label is categorical, convert it to numerical
            prediction_column = "encoded_label"
            label_indexer = StringIndexer(inputCol = label_column, outputCol = prediction_column)
            stages.append(label_indexer)
        else:
            model_type = constants.REGRESSION_MODEL_TYPE       

        model_details["model_type"] = model_type

        # Generate VectorAssembler
        numerical_features = list(set(features) - set(categorical_features))
        assembler_inputs = [c + "Index" for c in categorical_features] + numerical_features
        assembler = VectorAssembler(inputCols=assembler_inputs, outputCol="vectorized_features")
        stages.append(assembler)

        # Add feature scaler
        scaler = StandardScaler(inputCol="vectorized_features", outputCol="features")
        stages.append(scaler)

        # Create pipeline
        pipeline = Pipeline(stages = stages)
        pipeline_model = pipeline.fit(data)
        df = pipeline_model.transform(data)

        # Build and evaluate model based on the model type
        if constants.CLASSIFICATION_MODEL_TYPE == model_type:
            logger.info("Building logistic regression model to identify correlated attributes for {}".format(label_column))
            lr = LogisticRegression(featuresCol = 'features', labelCol = prediction_column, regParam=0.01)
            selected_cols = ['features', prediction_column] + data.columns
            df = df.select(selected_cols)
            # Split data set into training and test data sets
            train_data, test_data = df.randomSplit([0.8, 0.2])
            # Fit the logistic regression model
            lr_model = lr.fit(train_data)

            # Find accuracy of the model on test data
            accuracy = lr_model.evaluate(test_data).accuracy
            model_details["accuracy"] = accuracy
            coefficient_matrix = lr_model.coefficientMatrix.toArray()
            coefficients = cls.get_aggregate_coefficients(coefficient_matrix)
        else:
            logger.info("Building linear regression model to identify correlated attributes for {}".format(label_column))
            lr = LinearRegression(featuresCol = 'features', labelCol=prediction_column, regParam=0.3, elasticNetParam=0.8)
            selected_cols = ['features', prediction_column]
            df = df.select(selected_cols)
            # Split data set into training and test data sets
            train_data, test_data = df.randomSplit([0.8, 0.2])
            # Fit the linear regression model
            lr_model = lr.fit(train_data)

            # Find RMSE(Root Mean Squared Error) of the model on test data
            rmse = lr_model.evaluate(test_data).rootMeanSquaredError
            # Get normalized RMSE
            std_dev = test_data.select(F.stddev(prediction_column)).first()[0]
            normalized_rmse = rmse/std_dev if std_dev != 0 else 0
            model_details["normalized_rmse"] = normalized_rmse
            coefficients = lr_model.coefficients
        
        # Get training features in the same sequence as they are used in VectorAssembler to match the coefficients
        model_details["training_features"] = categorical_features + numerical_features
        model_details["feature_coefficients"] = coefficients

        time_taken = DateUtil.current_milli_time() - start_time
        logger.info("Time taken to build correlation identification model for the protected attribute {} is {} seconds.".format(label_column, time_taken/1000))
        return model_details
    
    @classmethod
    def get_aggregate_coefficients(cls, coefficient_matrix: np.ndarray):
        """
        Finds aggregate coefficient of each feature from the n-dimentional coefficient_matrix
        """
        # Initialize the aggregate coefficient to 0 for each feature
        agg_coefficients = [0 for i in range(len(coefficient_matrix[0]))]
        for coef in coefficient_matrix:
            # Get absolute value of coefficients
            abs_coef = [abs(x) for x in coef]
            for i in range(len(abs_coef)):
                agg_coefficients[i] += abs_coef[i]
        return agg_coefficients


class MappingUtils():
    """
    Class for utility methods related to computing indirect majority/minority of correlated attributes
    from majority/minority of protected attribute
    """
    @classmethod
    def find_correlated_maj_min(cls, training_data, protected_attribute_details: dict, correlated_attributes: list):
        """
        Finds correlated majority/minority of correlated attributes based on majority/minority of the protected attribute
        """
        start_time = DateUtil.current_milli_time()
        protected_attribute = protected_attribute_details.get("feature")
        majority = protected_attribute_details.get("majority")
        minority = protected_attribute_details.get("minority")
        logging.info("Started finding correlated majority/minority for the protected attribute {}".format(protected_attribute))

        selected_cols = [protected_attribute] + correlated_attributes
        data = training_data.select(selected_cols)
        dtypes_dict = dict(data.dtypes)
        categorical_columns = [col for col, col_dtype in dtypes_dict.items() if col_dtype in ["string", "boolean"]]

        correlated_majority = cls.find_maj_min_mapping(data, protected_attribute, majority, correlated_attributes, categorical_columns)
        correlated_minority = cls.find_maj_min_mapping(data, protected_attribute, minority, correlated_attributes, categorical_columns)

        time_taken = DateUtil.current_milli_time() - start_time
        logger.info("Time taken to find correlated majority/minority for the protected attribute {} is {} seconds.".format(protected_attribute, time_taken/1000))
        return correlated_majority, correlated_minority

    @classmethod
    def find_maj_min_mapping(cls, data, protected_attribute: str, maj_min: list, correlated_attributes: list, categorical_columns: list):
        """
        Finds mapping of protected attribute's majority/minority to each of the correlated attributes
        - Finds subset of the data for each majority/minority group by filtering rows belonging to each group
        - Generates correlation information for each group
        Arguments:
            data: The spark dataframe containg protected attribute and the correlated attributes
            protected_attribute: The protected attribute
            maj_min: The majority or minority of the protected attribute
            correlated_attributes: The list of correlated attributes
            categorical_columns: The categorical columns in the data
        Returns:
            maj_min_mapping: The mapping of protected attribute's majority/minority to each of the correlated attributes
        
        Ex. The mapping for protected attribute 'race' looks like this:
            [{
                'feature_value': 'White',
                'correlations': [{
                    'feature': 'fnlwgt',
                    'values': [{
                        'feature_value': [318082, 1484705],
                        'relative_weight': 0.1087
                    }, {
                        'feature_value': [104280, 128777],
                        'relative_weight': 0.1042
                    }, {
                        'feature_value': [128796, 158506],
                        'relative_weight': 0.1027
                    }, {
                        'feature_value': [58447, 104272],
                        'relative_weight': 0.1016
                    }, {
                        'feature_value': [251073, 318046],
                        'relative_weight': 0.1005
                    }, {
                        'feature_value': [177526, 194205],
                        'relative_weight': 0.0981
                    }, {
                        'feature_value': [158508, 177522],
                        'relative_weight': 0.0977
                    }, {
                        'feature_value': [194231, 214731],
                        'relative_weight': 0.0975
                    }, {
                        'feature_value': [214738, 250976],
                        'relative_weight': 0.0957
                    }, {
                        'feature_value': [18827, 58441],
                        'relative_weight': 0.0931
                    }]
                }, {
                    'feature': 'citizen_status',
                    'values': [{
                        'feature_value': 'United-States',
                        'relative_weight': 0.9211
                    }, {
                        'feature_value': 'Mexico',
                        'relative_weight': 0.0212
                    }, {
                        'feature_value': '?',
                        'relative_weight': 0.0139
                    }, {
                        'feature_value': 'Germany',
                        'relative_weight': 0.0045
                    }, {
                        'feature_value': 'Canada',
                        'relative_weight': 0.0043
                    }, {
                        'feature_value': 'El-Salvador',
                        'relative_weight': 0.0036
                    }, {
                        'feature_value': 'Cuba',
                        'relative_weight': 0.0032
                    }, {
                        'feature_value': 'Puerto-Rico',
                        'relative_weight': 0.0029
                    }, {
                        'feature_value': 'England',
                        'relative_weight': 0.0029
                    }, {
                        'feature_value': 'Italy',
                        'relative_weight': 0.0026
                    }]
                }]
            }, {
                'feature_value': 'Asian-Pac-Islander',
                'correlations': [{
                    'feature': 'fnlwgt',
                    'values': [{
                        'feature_value': [297335, 506329],
                        'relative_weight': 0.1088
                    }, {
                        'feature_value': [122575, 142897],
                        'relative_weight': 0.1068
                    }, {
                        'feature_value': [14878, 72887],
                        'relative_weight': 0.102
                    }, {
                        'feature_value': [160724, 178469],
                        'relative_weight': 0.102
                    }, {
                        'feature_value': [86143, 102343],
                        'relative_weight': 0.1011
                    }, {
                        'feature_value': [223206, 296085],
                        'relative_weight': 0.0991
                    }, {
                        'feature_value': [73025, 85995],
                        'relative_weight': 0.0991
                    }, {
                        'feature_value': [180211, 222294],
                        'relative_weight': 0.0982
                    }, {
                        'feature_value': [143003, 160261],
                        'relative_weight': 0.0943
                    }, {
                        'feature_value': [102420, 122283],
                        'relative_weight': 0.0885
                    }]
                }, {
                    'feature': 'citizen_status',
                    'values': [{
                        'feature_value': 'United-States',
                        'relative_weight': 0.281
                    }, {
                        'feature_value': 'Philippines',
                        'relative_weight': 0.1809
                    }, {
                        'feature_value': 'India',
                        'relative_weight': 0.0818
                    }, {
                        'feature_value': '?',
                        'relative_weight': 0.0799
                    }, {
                        'feature_value': 'South',
                        'relative_weight': 0.0741
                    }, {
                        'feature_value': 'China',
                        'relative_weight': 0.0703
                    }, {
                        'feature_value': 'Vietnam',
                        'relative_weight': 0.0626
                    }, {
                        'feature_value': 'Taiwan',
                        'relative_weight': 0.0462
                    }, {
                        'feature_value': 'Japan',
                        'relative_weight': 0.0366
                    }, {
                        'feature_value': 'Cambodia',
                        'relative_weight': 0.0173
                    }]
                }]
            }]
        """
        maj_min_mapping = []
        for maj_min_group in maj_min:
            maj_min_group_mapping = []
            # Get subset of the data set where value of protected attribute belongs to the maj_min_group
            if protected_attribute in categorical_columns:
                group_query = SQLUtils.get_cat_filter_query(protected_attribute, "==", [maj_min_group])
            else:
                group_query = SQLUtils.get_num_filter_query(protected_attribute, [maj_min_group])

            group_df = data.filter(group_query)

            # Find mapping for each correlated attribute
            for corr_attribute in correlated_attributes:
                attr_correlations = {}
                correlation_values = []
                if corr_attribute in categorical_columns:
                    correlation_values = cls.get_mapping_for_categorical_corr_attr(group_df, corr_attribute)
                else:
                    correlation_values = cls.get_mapping_for_numerical_corr_attr(group_df, corr_attribute)
                attr_correlations["feature"] = corr_attribute
                attr_correlations["values"] = correlation_values
                maj_min_group_mapping.append(attr_correlations)
            # Add the group mapping to overall majority/minority mapping
            maj_min_group_correlations = {
                "feature_value": maj_min_group,
                "correlations": maj_min_group_mapping
            }
            maj_min_mapping.append(maj_min_group_correlations)

        return maj_min_mapping

    @classmethod
    def get_mapping_for_categorical_corr_attr(cls, spark_df, correlated_attribute: str):
        """
        Generates majority/minority mapping for categorical correlated attribute
        - The input is a spark dataframe filtered using majority/minority group of protected attribute
        - The distribution counts of each distinct value of the correlated attribute are calculated
        - The relative weights are calculated by dividing distribution count by total records count
        - Returns correlation_values which get stored in fairness configuration
        Arguments:
            spark_df: The spark dataframe
            correlated_attribute: The correlated attribute for which mapping is to be calculated
        Returns:
            correlation_values: The correlation details like feature values, relative weights
        """
        correlation_values = []
        # Get the distribution counts for distinct values of the correlated attribute
        dist_counts = spark_df.groupBy(correlated_attribute).count()
        attr_values = list(dist_counts.select(correlated_attribute).toPandas()[correlated_attribute])
        attr_counts = list(dist_counts.select("count").toPandas()["count"])
        total_rows = sum(attr_counts)
        # If there are no records in the dataframe, return empty correlations
        if total_rows == 0:
            return correlation_values
        
        attr_counts = [round(i/total_rows, 4) for i in attr_counts]
        # Create dict of attribute value to distribution counts mapping
        attr_value_dist = dict(zip(attr_values, attr_counts))

        # Sort the mapped values based on the relative weights
        attr_value_dist = dict(
            sorted(attr_value_dist.items(), key=lambda x: x[1], reverse=True))
        # Pick top 10 values having the higher relative weights
        attr_value_dist = {k: v for k, v in list(
            attr_value_dist.items())[0:10] if v > 0}
        correlation_values = cls.get_formatted_correlation_values(
            attr_value_dist)

        return correlation_values

    @classmethod
    def get_mapping_for_numerical_corr_attr(cls, spark_df, correlated_attribute: str):
        """
        Generates majority/minority mapping for numerical correlated attribute
        - The input is a spark dataframe filtered using majority/minority group of protected attribute
        - Different numerical bins/intervals are identified for the correlated attribute from the data
        - Distribution counts i.e number of rows belonging to each bin are calculated
        - The relative weights are calculated by dividing distribution count by total records count
        - Returns correlation_values which get stored in fairness configuration
        Arguments:
            spark_df: The spark dataframe
            correlated_attribute: The correlated attribute for which mapping is to be calculated
        Returns:
            correlation_values: The correlation details like feature values, relative weights
        """
        correlation_values = []

        # Find numerical bins for the correlated attribute data using QuantileDiscretizer
        output_col = "{}_buckets".format(correlated_attribute) 
        discretizer = QuantileDiscretizer(numBuckets=BINS_COUNT, inputCol=correlated_attribute, outputCol=output_col, relativeError=0.01, handleInvalid="skip")
        discretized_data = discretizer.fit(spark_df).transform(spark_df)
        dist_counts = discretized_data.groupBy(output_col).agg(F.count(correlated_attribute).alias("count"), F.min(correlated_attribute).alias("min"), F.max(correlated_attribute).alias("max")).collect()
        dist_values = [val.asDict() for val in dist_counts]
        # Sort the distribution counts based on the row count for each bin
        dist_values = sorted(dist_values, key=itemgetter('count'), reverse=True)

        bins = []
        row_count_per_bin = []
        total_count = 0
        for val in dist_values:
            bins.append([val.get('min'), val.get('max')])
            row_count = val.get('count')
            row_count_per_bin.append(row_count)
            total_count += row_count

        # If there are no records in the dataframe, return empty correlations
        if total_count == 0:
            return correlation_values
        
        # Calculate relative weight for each bin
        for idx, bin_range in enumerate(bins):
            corr_value = row_count_per_bin[idx]/total_count
            if corr_value > 0:
                corr_value = round(float(corr_value), 4)
                value_dict = {
                    "feature_value": bin_range,
                    "relative_weight": corr_value
                }
                correlation_values.append(value_dict)

        return correlation_values

    @classmethod
    def get_formatted_correlation_values(cls, correlation_info: dict):
        """
        Formats correlation information
        Arguments:
            correlation_info: The correlation information
        Returns:
            correlation_values: Formatted correlation information
        """
        correlation_values = []
        for feature_value, correlation in correlation_info.items():
            corr_value_dict = {}
            corr_value_dict["feature_value"] = feature_value
            corr_value_dict["relative_weight"] = correlation
            correlation_values.append(corr_value_dict)

        return correlation_values