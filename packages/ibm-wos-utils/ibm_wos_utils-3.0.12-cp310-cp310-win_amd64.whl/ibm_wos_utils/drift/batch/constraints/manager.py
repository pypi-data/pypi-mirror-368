# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


import logging
from typing import Union
import numpy as np
import pandas as pd

from ibm_wos_utils.drift.batch.constraints.entity import DataConstraintSet
from ibm_wos_utils.drift.batch.constraints.learner import DataConstraintLearner
from ibm_wos_utils.drift.batch.constraints.schema import \
    DriftedTransactionsSchema
from ibm_wos_utils.drift.batch.util.constants import (
    CATEGORICAL_UNIQUE_THRESHOLD, MAX_DISTINCT_CATEGORIES, ConstraintName)

logger = logging.getLogger(__name__)

class DataConstraintMgr(object):
    """
    This is the entry-point class for all that needs to be done with constraints
    """

    @staticmethod
    def learn_constraints(
            training_data,
            feature_columns,
            categorical_columns,
            callback,
            enable_two_col_learner: bool = True,
            categorical_unique_threshold: float = CATEGORICAL_UNIQUE_THRESHOLD,
            max_distinct_categories: int = MAX_DISTINCT_CATEGORIES,
            max_ranges_modifier: Union[float, dict] = 0.01,
            tail_discard_threshold: float = 0.01,
            user_overrides=[]):
        """Learns/mines constraints from a dataset

        Arguments:
            training_data {pyspark.sql.dataframe.DataFrame} -- Training Data, spark dataframe
            feature_columns {list} -- List of feature columns in the training data
            categorical_columns {list} -- List of categorical columns in the training data
            callback {function} -- Function to get status of the operations

        Keyword Arguments:
            enable_two_col_learner {bool} -- Flag to enable Two Column Constraint learner (default: {True})
            categorical_unique_threshold {float} -- Used to discard categorical columns with a large number of unique
                                                    values relative to total rows in the column. Should be between 0 and 1.
                                                    Default value indicates that the constraint will not be learned if a
                                                    categorical column has distinct values more than 80% of the total count.
                                                    Should be between 0 and 1. (default: {0.8})
            max_distinct_categories {int} -- Used to discard categorical columns with a large absolute number of unique
                                            categories. Also, used for not learning categorical-categorical constraint, if
                                            potential combinations of two columns are more than this number. Default value 
                                            indicates that the constraint will not be learned if a categorical column 
                                            has more than 100,000 distinct values. Should be greater than 0. (default: {100000})
            max_ranges_modifier {float or dict of str -> float} -- Affects the number of ranges we find for a numerical column.
                                                                For a numerical column, we learn multiple ranges instead of one
                                                                min-max depending on how sparse data is. This modifier combined
                                                                with approximate distinct values in the column defines the upper
                                                                limit on how many bins to divide data into during multiple ranges
                                                                computation. This can either be a float or a dictionary of column
                                                                names and float values. Its value should be greater than 0.
                                                                (default: {0.01})
                                                                1. float: This value is applied for all numerical columns. Default
                                                                value of 0.01 indicates total number of bins used during computation
                                                                of ranges are not more than 1% of distinct values in the column.
                                                                2. dict of str -> float: A column name -> value, dict can be used to
                                                                over-ride individual modifier for each column. If not provided for a
                                                                column, default value of 0.01 will be used.
            tail_discard_threshold {float} --  Used to discard off values from either end of data distribution in a column if
                                                    the data is found to have large ranges which results in data being divided into a
                                                    large number of bins for multiple ranges computation. This threshold will be used
                                                    if the these bins are found be greater than `max_ranges_modifier * approx_distinct_count`
                                                    for a column. Default value indicates that 1 percentile data from either ends will
                                                    be discarded. Its value can be between 0 and 0.1, with a default of 0.01. (default: {0.01})
            user_overrides {list} -- Used to override drift constraint learning to selectively learn constraints on feature
                                    columns. Its a list of configuration, each specifying whether to learn distribution and/or
                                    range constraint on given set of columns. First configuration of a given column would take
                                    preference. (default: {[]})

        Returns:
            DataConstraintSet -- A collection of constraints and associated information
        """        

        learning_params = {
            "enable_two_col_learner": enable_two_col_learner,
            "categorical_unique_threshold": categorical_unique_threshold,
            "max_distinct_categories": max_distinct_categories,
            "user_overrides": user_overrides,
            "max_ranges_modifier": max_ranges_modifier,
            "tail_discard_threshold": tail_discard_threshold
        }
        ctrset = DataConstraintLearner(
            training_data,
            feature_columns,
            categorical_columns,
            callback).learn_constraints(
            **learning_params)
        return ctrset

    @staticmethod
    def learn_constraints_v2(
        training_data,
        feature_columns,
        categorical_columns,
        callback,
        enable_two_col_learner: bool = True,
        categorical_unique_threshold: float = CATEGORICAL_UNIQUE_THRESHOLD,
        max_distinct_categories: int = MAX_DISTINCT_CATEGORIES,
        max_ranges_modifier: Union[float, dict] = 0.01,
        tail_discard_threshold: float = 0.01,
        user_overrides=[]):

        learning_params = {
            "enable_two_col_learner": enable_two_col_learner,
            "categorical_unique_threshold": categorical_unique_threshold,
            "max_distinct_categories": max_distinct_categories,
            "user_overrides": user_overrides,
            "max_ranges_modifier": max_ranges_modifier,
            "tail_discard_threshold": tail_discard_threshold
        }

        return DataConstraintLearner(
            training_data,
            feature_columns,
            categorical_columns,
            callback).learn_constraints_v2(
            **learning_params)

    @staticmethod
    def generate_schema(
            record_id_column: str,
            record_timestamp_column: str = None,
            model_drift_enabled: bool = True,
            data_drift_enabled: bool = True,
            max_constraints_per_column: int = 1000000,
            constraint_set: DataConstraintSet = None):
        """Generate Drifted Transactions Table Schema

        Keyword Arguments:
            model_drift_enabled {bool} -- Flag to indicate if model drift is enabled (default: {True})
            data_drift_enabled {bool} -- Flag to indicate if data drift is enabled (default: {True})
            max_constraints_per_column {int} -- Maximum number of constraints in a bitmap in drift table (default: {1000000})
            constraint_set {DataConstraintSet} -- Data Constraint Set (default: {None})

        Raises:
            Exception: if both model_drift_enabled and data_drift_enabled are False
            Exception: if data_drift_enabled is True but constraint_set is not given

        Returns:
            DriftedTransactionsSchema -- Schema JSON for Drifted Transactions Table
        """
        if not model_drift_enabled and not data_drift_enabled:
            raise Exception(
                "Need either model drift or data drift enabled to generate schema.")
        if data_drift_enabled and constraint_set is None:
            raise Exception(
                "Data Constraint Set needs to be provided if Data Drift is enabled.")
        schema = DriftedTransactionsSchema(max_constraints_per_column=max_constraints_per_column)
        schema.generate(record_id_column, record_timestamp_column, constraint_set)
        return schema

    @staticmethod
    def check_violations(
            index,
            constraints_set: DataConstraintSet,
            payload_df: pd.DataFrame,
            violations_counter,
            record_id_column: str,
            record_timestamp_column: str = None,
            feature_columns: list = []):
        """Checks violations against constraints and returns:
        A pandas dataframe containing all transactions from payload. If there are `m` constraints and
        `n` transactions, the DataFrame will be:

        # TODO Replace 0 with False, 1 with True
        |   record_id  | constraint_id_1 | constraint_id_2 | ... | constraint_id_m |
        |:-------------:|:---------------:|:---------------:|:---:|:---------------:|
        | transaction_1 |        0        |        0        |     |        1        |
        | transaction_2 |        1        |        1        |     |        0        |
        |      ...      |                 |                 |     |                 |
        | transaction_n |        0        |        1        |     |        0        |

        1 under a column signifies that a particular transaction violates that constraint. 0 otherwise.

        Arguments:
            constraints_set {DataConstraintSet} -- Constraints Set containing all information
            payload {pd.DataFrame} -- Payload DataFrame

        Returns:
            pd.DataFrame -- transactions data frame with binary values.
        """

        results_df = pd.DataFrame(
            np.zeros(
                shape=(
                    len(payload_df), len(
                        constraints_set.constraints))), dtype=int)
        constraint_keys = list(constraints_set.constraints.keys())
        results_df.columns = constraint_keys
        results_df[record_id_column] = payload_df[record_id_column].copy()
        if record_timestamp_column:
            results_df[record_timestamp_column] = payload_df[record_timestamp_column].copy()

        # Compute violations for single column constraints
        for constraint in constraints_set.single_column_constraints().values():
            constraint.check_violations(payload_df, results_df)

        # Compute violations for two column constraints
        for constraint in constraints_set.two_column_constraints().values():
            constraint.check_violations(payload_df, results_df)

        total_drifted_txns = sum(results_df[constraint_keys].sum(axis="columns") > 0)

        drifted_txns_per_constraint_name = {}
        for constraint_name in ConstraintName:
            column_keys = list(constraints_set.get_constraints_for_name(constraint_name).keys())
            drifted_txns_per_constraint_name[constraint_name.value] = sum(results_df[column_keys].sum(axis="columns") > 0)

        drifted_txns_per_column = {}
        for column in feature_columns:
            column_keys = list(constraints_set.get_constraints_for_column(column).keys())
            drifted_txns_per_column[column] = sum(results_df[column_keys].sum(axis="columns") > 0)


        counter_str = {
            "data_drift": {
                "count": total_drifted_txns,
                "constraints": drifted_txns_per_constraint_name,
                "features": drifted_txns_per_column
            }
        }
        logger.warn("\npart_{} {}".format(str(index).zfill(5), counter_str))
        violations_counter.add(counter_str)
        return results_df
