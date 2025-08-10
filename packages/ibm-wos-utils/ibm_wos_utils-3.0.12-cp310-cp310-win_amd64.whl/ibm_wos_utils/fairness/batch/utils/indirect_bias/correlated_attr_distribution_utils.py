# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2022
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

try:
    from pyspark.ml.feature import Bucketizer
    import pyspark.sql.functions as F
except ImportError as ie:
    pass

import logging
from ibm_wos_utils.fairness.batch.utils.date_util import DateUtil
from ibm_wos_utils.fairness.batch.utils.python_util import get

logger = logging.getLogger(__name__)

class CorrelatedAttrDistributionUtils():
    """
    Class for correlation attributes distribution utilities
    """
    @classmethod
    def get_correlated_attr_group_counts(cls, group_val, group_correlations: list, group_df, group_fav_df, group_count: int, group_fav_count: int):
        """
        Returns counts for distinct values of correlated attributes of a protected attribute. This is required to compute correlated attribute distribution.
        Arguments:
            :group_val: The majority/minority group of protected attibute for which correlated attribute counts are to be calculated.
            :group_correlations: The correlation details for the majority/minority group of the protected attribute.
            :group_df: The dataframe containing rows of specific majority/minority group of the protected attribute.
            :group_fav_df: The dataframe containing favourable outcome rows of specific majority/minority group of the protected attribute.
            :group_count: The number of rows in group_df.
            :group_fav_count: The number of rows in group_fav_df.
        Returns:
            :The counts for distinct values of correlated attributes calculated using correlation details.
        Ex. For protected attribute group 'Female' of attribute 'sex' with correlated attriubtes ['relationship', 'Marital'], the correlated attribute counts look like this:
        {
            'Female': {
                'fav_count': 19,
                'total_count': 74,
                'correlated_attr_group_counts': {
                    'relationship': [{
                        'feature_value': 'Not-in-family',
                        'fav_count': 8,
                        'total_count': 30,
                        'row_percent': 40.54
                    }, {
                        'feature_value': 'Unmarried',
                        'fav_count': 4,
                        'total_count': 13,
                        'row_percent': 17.57
                    }, {
                        'feature_value': 'Own-child',
                        'fav_count': 5,
                        'total_count': 18,
                        'row_percent': 24.32
                    }, {
                        'feature_value': 'Wife',
                        'fav_count': 2,
                        'total_count': 12,
                        'row_percent': 16.22
                    }, {
                        'feature_value': 'Other-relative',
                        'fav_count': 0,
                        'total_count': 1,
                        'row_percent': 1.35
                    }],
                    'Marital': [{
                        'feature_value': 'Never-married',
                        'fav_count': 12,
                        'total_count': 42,
                        'row_percent': 56.76
                    }, {
                        'feature_value': 'Divorced',
                        'fav_count': 4,
                        'total_count': 14,
                        'row_percent': 18.92
                    }, {
                        'feature_value': 'Married-civ-spouse',
                        'fav_count': 1,
                        'total_count': 12,
                        'row_percent': 16.22
                    }, {
                        'feature_value': 'Widowed',
                        'fav_count': 1,
                        'total_count': 5,
                        'row_percent': 6.76
                    }, {
                        'feature_value': 'Separated',
                        'fav_count': 1,
                        'total_count': 1,
                        'row_percent': 1.35
                    }]
                }
            }
        }
        """
        logger.info("Calculating correlated attributes group counts for the protected attribute group {}".format(group_val))
        start_time = DateUtil.current_milli_time()
        correlated_attr_group_counts = {}
        dtypes_dict = dict(group_df.dtypes)
        # For each correlated attribute, get distinct value counts
        for correlated_attr_details in group_correlations:
            group_counts = []
            correlated_attr = correlated_attr_details.get("feature")
            data_type = dtypes_dict.get(correlated_attr)
            is_categorical = data_type in ["string", "boolean"]
            if is_categorical:
                # Get distinct value counts using groupBy
                group_counts = cls._get_group_counts_for_cat_correlated_attr(correlated_attr_details, group_df, group_fav_df, group_count, group_fav_count)
            else:
                # Get distinct range counts using Bucketizer which gives counts of rows belonging to each range using input splits
                group_counts = cls._get_group_counts_for_num_correlated_attr(correlated_attr_details, group_df, group_fav_df, group_count, group_fav_count)
            
            correlated_attr_group_counts[correlated_attr] = group_counts

        time_taken = DateUtil.current_milli_time() - start_time
        logger.info("Time taken to calculate correlated attributes group counts for the protected attribute group {} is {} seconds.".format(group_val, time_taken/1000))
        return correlated_attr_group_counts
    
    @classmethod
    def _get_group_counts_for_cat_correlated_attr(cls, correlated_attr_details: dict, group_df, group_fav_df, group_count: int, group_fav_count: int):
        """
        Returns counts for distinct values of categorical correlated attribute of a protected attribute.
        Arguments:
            :correlated_attr_details: The details of a correlated attribute like distinct values, relative weights
            :group_df: The dataframe containing rows of specific majority/minority group of the protected attribute
            :group_fav_df: The dataframe containing favourable outcome rows of specific majority/minority group of the protected attribute
            :group_count: The number of rows in group_df
            :group_fav_count: The number of rows in group_fav_df
        Returns:
            :The counts for distinct values of categorical correlated attribute calculated using correlation details.

        """
        group_counts = []
        correlated_attr = correlated_attr_details.get("feature")
        correlated_attr_values = [val["feature_value"] for val in correlated_attr_details.get("values")]
        counts_df = group_df.groupBy(correlated_attr).count()
        attr_values = list(counts_df.select(correlated_attr).toPandas()[correlated_attr])
        attr_counts = list(counts_df.select("count").toPandas()["count"])
        attr_counts_dict = dict(zip(attr_values, attr_counts))
        
        # Get the distinct value counts with favourable outcomes
        attr_fav_counts_dict = {}
        if group_fav_count > 0:
            fav_counts_df = group_fav_df.groupBy(correlated_attr).count()
            attr_values = list(fav_counts_df.select(correlated_attr).toPandas()[correlated_attr])
            attr_counts = list(fav_counts_df.select("count").toPandas()["count"])
            attr_fav_counts_dict = dict(zip(attr_values, attr_counts))

        # Add entry in group_counts for each value
        for corr_attr_value in correlated_attr_values:
            row_count = attr_counts_dict.get(corr_attr_value, 0) # Default row_count 0 if not found in attr_counts_dict
            if row_count > 0:
                row_percent = round(100 * float(row_count/group_count), 2) if group_count > 0 else 0
                counts_dict = {
                    "feature_value": corr_attr_value,
                    "fav_count": attr_fav_counts_dict.get(corr_attr_value, 0),
                    "total_count": row_count,
                    "row_percent": row_percent
                }
                group_counts.append(counts_dict)

        return group_counts

    @classmethod
    def _get_group_counts_for_num_correlated_attr(cls, correlated_attr_details: dict, group_df, group_fav_df, group_count: int, group_fav_count: int):
        """
        Returns counts for distinct values of numerical correlated attribute of a protected attribute.
        Arguments:
            :correlated_attr_details: The details of a correlated attribute like distinct values, relative weights
            :group_df: The dataframe containing rows of specific majority/minority group of the protected attribute
            :group_fav_df: The dataframe containing favourable outcome rows of specific majority/minority group of the protected attribute
            :group_count: The number of rows in group_df
            :group_fav_count: The number of rows in group_fav_df
        Returns:
            :The counts for distinct values of numerical correlated attribute calculated using correlation details.
        """
        group_counts = []
        correlated_attr = correlated_attr_details.get("feature")
        correlated_attr_values = [val["feature_value"] for val in correlated_attr_details.get("values")]
        # Generate splits using the bins from correlation details
        # Bucketizer needs n+1 splits where n is number of bins in which we need to group the data
        splits = sorted([bin_range[0] for bin_range in correlated_attr_values])

        # Adding range_end of the last bin as n+1 split
        range_end_for_last_bin = max([bin_range[1] for bin_range in correlated_attr_values])
        # The splits needs to be strictly increasing. It might be possible that range_end for last bin is same as range_start. Incrementing the split value by 0.1 to avoid duplicate splits. WI #27699
        if range_end_for_last_bin <= splits[-1]:
            range_end_for_last_bin = splits[-1] + 0.1
        splits.append(range_end_for_last_bin)

        # Bucketizer needs -infinity and +infinity to be added to the splits to handle values which do not belong to any split
        bucketizer_splits = [-float("inf")] + splits + [float("inf")]

        # Creating a dict to map splits to the bin ranges
        splits_dict = {i:bucketizer_splits[i] for i in range(len(bucketizer_splits))}

        output_col = "{}_buckets".format(correlated_attr)

        bucketizer = Bucketizer(splits=bucketizer_splits, inputCol=correlated_attr, outputCol=output_col, handleInvalid='skip')
        # Get counts for group df
        attr_group_counts = bucketizer.transform(group_df).groupBy(output_col).agg(F.count(correlated_attr).alias("count")).replace(to_replace=splits_dict, subset=[output_col]).collect()
        attr_group_counts_dict = {val[output_col]: val["count"] for val in attr_group_counts}
    
        # Get counts for favourable rows
        attr_group_fav_counts_dict = {}
        if group_fav_count > 0:
            attr_group_fav_counts = bucketizer.transform(group_fav_df).groupBy(output_col).agg(F.count(correlated_attr).alias("count")).replace(to_replace=splits_dict, subset=[output_col]).collect()
            attr_group_fav_counts_dict = {val[output_col]: val["count"] for val in attr_group_fav_counts}

        # Add entry in group_counts for each value
        for bin_range in correlated_attr_values:
            # For a bin, the count is be fetched from dict by using start_value of bin as key as the start_value is used as a split
            row_count = attr_group_counts_dict.get(bin_range[0], 0)
            if row_count > 0:
                row_percent = round(100 * float(row_count/group_count), 2) if group_count > 0 else 0
                fav_row_count = attr_group_fav_counts_dict.get(bin_range[0], 0)
                counts_dict = {
                    "feature_value": bin_range,
                    "fav_count": fav_row_count,
                    "total_count": row_count,
                    "row_percent": row_percent
                }
                group_counts.append(counts_dict)
        
        return group_counts
    
    @classmethod
    def get_correlated_attr_dist_values(cls, protected_attr: str, protected_attr_group, correlated_attr_counts: dict, protected_attr_group_type: str):
        """
        Generates distribution values for correlated attributes  c
        Arguments:
            :protected_attr: The protected attribute.
            :protected_attr_group: The majority/minority group of the protected attribute.
            :correlated_attr_counts: The dictionary containing correlated attribute counts for the protected_attr_group.
            :protected_attr_group_type: The type of protected_attr_group i.e reference or monitored.
        Returns:
            :The distribution values for correlated attributes distribution values for correlated attributes.
        """
        dist_values = []
        for attr in correlated_attr_counts:
            attr_value_counts = correlated_attr_counts.get(attr, [])
            # Generate a distribution row for each distinct value of the correlated attribute
            for count_dict in attr_value_counts:
                total_count = count_dict.get("total_count")
                fav_count = count_dict.get("fav_count")
                unfav_count = total_count - fav_count
                dist_values.append([protected_attr,
                    protected_attr_group,
                    attr,
                    count_dict.get("feature_value"),
                    fav_count,
                    unfav_count,
                    count_dict.get("row_percent"),
                    protected_attr_group_type
                ])

        return dist_values
