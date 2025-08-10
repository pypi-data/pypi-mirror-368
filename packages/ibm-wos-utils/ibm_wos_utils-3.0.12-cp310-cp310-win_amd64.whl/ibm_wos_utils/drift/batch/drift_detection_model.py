
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
import logging
import uuid
from functools import reduce

import numpy as np
import pyspark.sql.functions as F
from ibm_wos_utils.drift.batch.util.constants import (DDM_LABEL_COLUMN,
                                                      PROBABILITY_DIFFERENCE)
from pyspark.ml import Pipeline
from pyspark.ml.classification import GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.sql.utils import IllegalArgumentException

logger = logging.getLogger(__name__)


class DriftDetectionModel():
    RANDOM_SEED = 272

    def __init__(self, spark_df, ddm_inputs: dict):
        self.feature_columns = None
        self.categorical_columns = None
        self.label_column = None
        self.prediction = None
        self.probability = None
        self.spark_df = spark_df
        self.class_labels = None
        self.missing_labels = None
        self.ddm_model = None
        self.base_model_accuracy = None
        self.base_predicted_accuracy = None
        self.enable_ddm_tuning = ddm_inputs.get("enable_tuning") or False
        self.max_bins = ddm_inputs.get("max_bins")
        self.ddm_features = None
        self.build_id = str(uuid.uuid4()).replace("-", "")
        self.ddm_cat_index_col = lambda col: "{}_index_{}".format(
            col, self.build_id)
        self.ddm_label_col = "{}_{}".format(DDM_LABEL_COLUMN, self.build_id)
        self.ddm_features_col = "features_{}".format(self.build_id)
        self.ddm_prediction_col = "prediction_{}".format(self.build_id)
        self.ddm_probability_diff_col = "{}_{}".format(
            PROBABILITY_DIFFERENCE, self.build_id)

        self.__validate_inputs(ddm_inputs)
        self.__filter_missing_values()

    def __validate_inputs(self, ddm_inputs):
        self.model_type = ddm_inputs.get("model_type")
        self.feature_columns = ddm_inputs.get("feature_columns")
        self.categorical_columns = ddm_inputs.get("categorical_columns")
        self.label_column = ddm_inputs.get("label_column")
        self.prediction = ddm_inputs.get("prediction")
        self.probability = ddm_inputs.get("probability")

        spark_df_columns = self.spark_df.columns
        spark_df_dtypes = {col[0]: col[1] for col in self.spark_df.dtypes}

        missing_details = {}
        missing_feature_columns = list(
            set(self.feature_columns) - set(spark_df_columns))
        if len(missing_feature_columns) > 0:
            missing_details["missing_feature_columns"] = missing_feature_columns

        unknown_categorical_columns = list(
            set(self.categorical_columns) - set(self.feature_columns))
        if len(missing_feature_columns) > 0:
            missing_details["unknown_categorical_columns"] = unknown_categorical_columns

        if self.label_column not in spark_df_columns:
            missing_details["missing_label_column"] = self.label_column

        if self.prediction not in spark_df_columns:
            missing_details["missing_prediction_column"] = self.prediction

        if self.probability not in spark_df_columns:
            missing_details["missing_probability_column"] = self.probability

        if spark_df_dtypes.get(
                self.label_column) != spark_df_dtypes.get(
                self.prediction):
            missing_details["label_prediction_dtype_mismatch"] = "true"

        if len(missing_details) > 0:
            raise Exception(
                "Validation failure  Reason:{}".format(
                    json.dumps(missing_details)))

        # Verify and set output column entries
        self.__verify_output_columns()
        logger.info("Validation and setting of the ddm arguments is completed")

    def __verify_output_columns(self):
        # Get unique value count using probability
        first_row = self.spark_df.limit(1).collect()[
            0].asDict()
        logger.info(
            "Fetched a single row from training data to determine length of probability array. Row: {}".format(first_row))
        unique_label_count = len(first_row.get(self.probability, []))

        if self.model_type == "binary" and unique_label_count != 2:
            raise Exception(
                "Probability column should be a vector of size 2 for binary model type")

        self.__verify_predictions(unique_label_count)
        logger.info("Validation and setting of output columns is completed")

    def __get_unique_values(self, col_name):
        unique_rows = self.spark_df.select(col_name).distinct().collect()
        unique_labels = [row[col_name] for row in unique_rows]
        return unique_labels

    def __verify_predictions(self, unique_label_count: int):
        self.class_labels = self.__get_unique_values(self.label_column)

        if len(self.class_labels) != unique_label_count:
            raise Exception(
                "The unique label count:{} does not match probability vector shape:{}".format(
                    self.class_labels, unique_label_count))

        self.predicted_labels = self.__get_unique_values(self.prediction)

        self.missing_labels = list(set(self.predicted_labels) -
                                   set(self.class_labels))

        if len(self.missing_labels) > 0:
            raise Exception(
                "The model predictions '{}' are not present in class labels '{}' in the training data.".format(
                    self.missing_labels, self.class_labels))
        logger.info("Validation and setting of prediction is completed")

    def __add_probability_columns(self):
        for idx, _ in enumerate(self.class_labels):
            prob_col_name = "{}_{}_{}".format(
                self.probability, self.build_id, idx)
            self.spark_df = self.spark_df.withColumn(
                prob_col_name, F.col(self.probability).getItem(idx))

        max_probability = F.reverse(F.array_sort(
            F.col(self.probability))).getItem(0)
        second_probability = F.reverse(
            F.array_sort(F.col(self.probability))).getItem(1)
        self.spark_df = self.spark_df.withColumn(
            self.ddm_probability_diff_col,
            max_probability - second_probability)

    def __balance_data(self, ddm_train):
        ddm_labels_count = ddm_train.groupBy(
            self.ddm_label_col).count().collect()
        ddm_label_counts = [val.asDict() for val in ddm_labels_count]
        logger.info("The DDM Label counts: {}".format(ddm_label_counts))
        label_dict = {0: 0, 1: 0}
        for label in ddm_label_counts:
            label_dict[int(label[self.ddm_label_col])] = label["count"]
        if label_dict[0] == 0:
            raise Exception(
                "There are no incorrect predictions in the training data."
                " Please retry this configuration after adding more rows where {} is not same as {}.".format(
                    self.prediction, self.label_column))

        if label_dict[1] == 0:
            raise Exception(
                "There are no correct predictions in the training data."
                " Please retry this configuration after adding more rows where {} is same as {}.".format(
                    self.prediction, self.label_column))
        num_sample = abs(label_dict[0] - label_dict[1])
        value = 0 if label_dict[0] >= label_dict[1] else 1
        new_rows = ddm_train.filter(
            ddm_train[self.ddm_label_col] == value)
        fraction = num_sample / new_rows.count()
        fraction = 1.0 if fraction > 1 else fraction
        supp_set = new_rows.sample(
            False, fraction, seed=DriftDetectionModel.RANDOM_SEED).limit(num_sample)
        ddm_train = ddm_train.union(supp_set)
        logger.info("Balanced data size: {}".format(ddm_train.count()))
        logger.info(ddm_train.printSchema())
        return ddm_train

    def __filter_missing_values(self):
        """
        Filter out the null/nan values
        from the spark data frame

        Raises:
            Exception: if the dataframe is empty after
            removing null/nan values
        """
        if not self.feature_columns:
            return

        condition = [~(F.col(c).isNull() | F.isnan(F.col(c)))
                     for c in self.feature_columns]
        self.spark_df = self.spark_df.filter(
            reduce(lambda x, y: x & y, condition))

        if self.spark_df.isEmpty():
            raise Exception(
                "There are no rows left in the training data after dropping missing values. Please fix the missing values in the training data.")
        return

    def generate_drift_detection_model(self):
        extra_columns = [
            self.label_column,
            self.prediction,
            self.probability]
        self.spark_df = self.spark_df.select(
            self.feature_columns + extra_columns)
        # Add ddm label columns to spark_df
        self.spark_df = self.spark_df.withColumn(self.ddm_label_col, F.when(
            (F.col(self.label_column) == F.col(self.prediction)), 1).otherwise(0))

        # Add probability columns
        self.__add_probability_columns()

        # Drop unwanted columns from spark dataframe
        logger.info(
            "Dropping {} columns from spark_df".format(extra_columns))
        self.spark_df = self.spark_df.drop(*extra_columns)

        self.__filter_missing_values()
        logger.info(self.spark_df.printSchema())

        # Split data into train and test
        ddm_train, ddm_test = self.spark_df.randomSplit(
            [0.8, 0.2], seed=DriftDetectionModel.RANDOM_SEED)

        # Balance gbt data
        new_ddm_train = self.__balance_data(ddm_train)

        # Encode categorical columns
        self.ddm_features = new_ddm_train.columns
        self.ddm_features.remove(self.ddm_label_col)

        # Get Stages , GBT
        stages, gbt = self.__get_ddm_stages(self.ddm_features)

        # Train DDM
        try:
            if self.enable_ddm_tuning:
                logger.info("Drift Model tuning is enabled.")
                self.__train_ddm_with_tuning(
                    stages, gbt, new_ddm_train, ddm_test)
            else:
                logger.info("Drift Model tuning is disabled.")
                self.__train_ddm_without_tuning(
                    stages, new_ddm_train, ddm_test)
        except IllegalArgumentException as ex:
            if "already exists" in str(ex):
                raise Exception(str(ex))
            logger.exception(ex)
            raise ex

        return

    def __get_ddm_stages(self, ddm_features):

        stages = []
        for cat_col in self.categorical_columns:
            stage_encoder = StringIndexer(
                inputCol=cat_col,
                outputCol=self.ddm_cat_index_col(cat_col),
                handleInvalid="keep")
            stages.append(stage_encoder)

        ddm_input_cols = [self.ddm_cat_index_col(
            col) if col in self.categorical_columns else col for col in ddm_features]
        ddm_assembler = VectorAssembler(
            inputCols=ddm_input_cols, outputCol=self.ddm_features_col, handleInvalid="keep")

        if not self.categorical_columns:
            logger.info(
                "There are no categorical columns specified. Setting maxBins to default 32.")
            self.max_bins = 32
        elif self.max_bins <= 0:
            logger.info(
                "max_bins not supplied as an argument. Finding approximate distinct counts.")
            maxBins = self.spark_df.agg(*(F.approx_count_distinct(F.col(c)).alias(c)
                                          for c in self.categorical_columns)).toPandas()
            from tabulate import tabulate
            logger.info(
                "Approximate distinct counts for categorical variables: \n{}".format(
                    tabulate(
                        maxBins.T)))
            self.max_bins = np.max(maxBins.values) * 2
        logger.info(
            "Using {} as maxBins argument for GBTClassifier.".format(
                self.max_bins))

        # Set gbt
        gbt = GBTClassifier(
            labelCol=self.ddm_label_col,
            maxBins=self.max_bins,
            maxIter=10,
            featuresCol=self.ddm_features_col,
            predictionCol=self.ddm_prediction_col,
            seed=DriftDetectionModel.RANDOM_SEED)

        stages.append(ddm_assembler)
        stages.append(gbt)
        return stages, gbt

    def __train_ddm_with_tuning(self, stages, gbt, ddm_train, ddm_test):
        ddm_pipeline = Pipeline(stages=stages)
        # We need a better approach for tuning. Right now, there are only 36
        # options.
        paramGrid = (ParamGridBuilder()
                     .addGrid(gbt.maxDepth, [2, 4, 6])
                     .addGrid(gbt.stepSize, [0.1, 0.15, 0.2])
                     .addGrid(gbt.featureSubsetStrategy, ["log2", "sqrt"])
                     .addGrid(gbt.subsamplingRate, [0.7, 0.9])
                     .build())
        evaluator = BinaryClassificationEvaluator(labelCol=self.ddm_label_col)
        cv = CrossValidator(
            estimator=ddm_pipeline,
            estimatorParamMaps=paramGrid,
            evaluator=evaluator,
            numFolds=3)

        cvModel = cv.fit(ddm_train)
        # Get the best model
        ddm_model = cvModel.bestModel
        predictions = cvModel.transform(ddm_test)

        ddm_accuracy = evaluator.evaluate(predictions)
        logger.info("Tuned Model Accuracy = %3.2f%%" % (ddm_accuracy * 100))
        test_rows = predictions.count()
        predicted_accuracy = predictions.filter(
            predictions[self.ddm_prediction_col] == 1).count() / test_rows

        original_accuracy = predictions.filter(
            predictions[self.ddm_label_col] == 1).count() / test_rows

        logger.info("original_accuracy:{} predicted_accuracy:{}".format(
            original_accuracy, predicted_accuracy))

        self.ddm_model = ddm_model
        self.base_model_accuracy = original_accuracy
        self.base_predicted_accuracy = predicted_accuracy

    def __train_ddm_without_tuning(self, stages, ddm_train, ddm_test):
        ddm_pipeline = Pipeline(stages=stages)
        ddm_model = ddm_pipeline.fit(ddm_train)
        ddm_test_predictions = ddm_model.transform(ddm_test)
        evaluator = BinaryClassificationEvaluator(labelCol=self.ddm_label_col)
        ddm_accuracy = evaluator.evaluate(ddm_test_predictions)
        logger.info("Model Accuracy = %3.2f%%" % (ddm_accuracy * 100))

        predicted_accuracy = ddm_test_predictions.filter(
            ddm_test_predictions[self.ddm_prediction_col] == 1).count() / ddm_test.count()

        original_accuracy = ddm_test_predictions.filter(
            ddm_test_predictions[self.ddm_label_col] == 1).count() / ddm_test.count()

        logger.info("original_accuracy:{} predicted_accuracy:{}".format(
            original_accuracy, predicted_accuracy))
        self.ddm_model = ddm_model
        self.base_model_accuracy = original_accuracy
        self.base_predicted_accuracy = predicted_accuracy
