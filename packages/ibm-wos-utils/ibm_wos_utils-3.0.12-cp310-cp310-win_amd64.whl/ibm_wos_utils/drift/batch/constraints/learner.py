# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import datetime
import json
import logging
import time
from itertools import product
from typing import Union

import numpy as np
import pandas as pd

from ibm_wos_utils.drift.batch.constraints.catcat_distribution_constraint import \
    CatCatDistributionConstraint
from ibm_wos_utils.drift.batch.constraints.categorical_distribution_constraint import \
    CategoricalDistributionConstraint
from ibm_wos_utils.drift.batch.constraints.catnum_range_constraint import \
    CategoricalNumericRangeConstraint
from ibm_wos_utils.drift.batch.constraints.column import DataColumn
from ibm_wos_utils.drift.batch.constraints.entity import DataConstraintSet
from ibm_wos_utils.drift.batch.constraints.numeric_range_constraint import \
    NumericRangeConstraint
from ibm_wos_utils.drift.batch.constraints.unified_constraint_learner import \
    UnifiedConstraintLearner
from ibm_wos_utils.drift.batch.util.constants import ColumnType, ConstraintKind
from ibm_wos_utils.drift.batch.util.constraint_utils import (
    check_user_override, get_max_bins_for_column, get_tail_thresholds)

logger = logging.getLogger(__name__)


class DataConstraintLearner(object):

    def __init__(
            self,
            training_data,
            feature_columns: list,
            categorical_columns: list,
            callback):
        self.training_data = training_data
        self.feature_columns = sorted(feature_columns)
        self.categorical_columns = sorted(categorical_columns)
        self.callback = callback

        self.numerical_columns = sorted(
            [column for column in self.feature_columns if column not in self.categorical_columns])
        logger.info("******** Numerical Columns [{}]: {} ********".format(
            len(self.numerical_columns), self.numerical_columns))

    def __compute_summary_df(self, tail_discard_threshold: float = 0.01):
        """Computes summary for numerical columns

        Spark Operations:
            1. Summary Statistics [count, mean, stddev, min, approximate quartiles
            (percentiles at 25%, 50%, and 75%), and max.] for each numerical column.

        Returns:
            pd.DataFrame -- Summary Dataframe
        """
        if len(self.numerical_columns) == 0:
            return pd.DataFrame()

        summary_args = ["count", "mean", "stddev", "min", "25%", "50%", "75%", "max"]

        # For default value of tail_discard_threshold, we are appending
        # the following rows to the summary_args list: 1.0% and 99.0%
        summary_args.extend(get_tail_thresholds(tail_discard_threshold))
        
        summary_df = self.training_data.select(self.numerical_columns).summary(summary_args).toPandas().set_index("summary").astype(float)
        summary_df.loc["width"] = summary_df.loc["max"] - \
            summary_df.loc["min"]
        summary_df.loc["iqr"] = summary_df.loc["75%"] - \
            summary_df.loc["25%"]
        # Original rule: https://en.wikipedia.org/wiki/Freedman–Diaconis_rule
        # Modified rule: Reducing the above bin width to one third,
        # for tripling the number of bins for more precise ranges
        summary_df.loc["bin_width"] = (
            2 * summary_df.loc["iqr"] / np.power(summary_df.loc["count"], 1 / 3)) / 3
        summary_df.loc["bins"] = (
            summary_df.loc["width"] /
            summary_df.loc["bin_width"])
        summary_df.loc["expected"] = np.round(
            summary_df.loc["count"] / (10 * summary_df.loc["bins"]))
        logger.info(json.dumps(summary_df.to_dict("split")))
        return summary_df

    def learn_constraints(
            self,
            enable_two_col_learner: bool,
            categorical_unique_threshold: float,
            max_distinct_categories: int,
            max_ranges_modifier: Union[float, dict],
            tail_discard_threshold: float,
            user_overrides=[]):

        self.summary_df = self.__compute_summary_df(tail_discard_threshold)
        self.callback(status="Data Drift: Summary Stats Calculated")

        self.constraint_set = DataConstraintSet()
        self.constraint_set.summary_stats = self.summary_df

        logger.info("[SPARK-OP] Counting rows in training data.")
        total_rows = self.training_data.count()
        logger.info(
            "[SPARK-OP] {} rows in training data.".format(total_rows))

        # learn the information of columns
        ColStatsComputer(
            self.constraint_set,
            self.training_data,
            self.summary_df,
            self.feature_columns,
            self.categorical_columns,
            self.callback).compute_stats(
            total_rows,
            categorical_unique_threshold,
            max_distinct_categories,
            max_ranges_modifier,
            tail_discard_threshold)

        logger.info("Adding bucketed columns to training data")
        for name, column in self.constraint_set.columns.items():
            if column.dtype in (
                    ColumnType.CATEGORICAL,
                    ColumnType.NUMERIC_DISCRETE):
                continue
            if column.sparse or column.skip_learning:
                continue

            from pyspark.ml.feature import Bucketizer
            bucketizer = Bucketizer(
                splits=column.splits,
                inputCol=name,
                outputCol="{}_buckets".format(name),
                handleInvalid="keep")
            self.training_data = bucketizer.transform(
                self.training_data)
            logger.info(
                " - Added column {} buckets transformation.".format(column.name))

        # learn single column constraints
        SingleColCtrLearner(
            self.constraint_set,
            self.training_data,
            self.feature_columns,
            self.categorical_columns,
            self.callback).learn_constraints(
                user_overrides=user_overrides)

        # learn two column constraints
        if enable_two_col_learner:
            TwoColCtrLearner(
                self.constraint_set,
                self.training_data,
                self.feature_columns,
                self.categorical_columns,
                self.callback).learn_constraints(
                total_rows=total_rows,
                max_distinct_categories=max_distinct_categories,
                user_overrides=user_overrides)

        self.constraint_set.user_inputs = {
            "enable_two_col_learner": enable_two_col_learner,
            "categorical_unique_threshold": categorical_unique_threshold,
            "max_distinct_categories": max_distinct_categories,
            "max_ranges_modifier": max_ranges_modifier,
            "tail_discard_threshold": tail_discard_threshold,
            "user_overrides": user_overrides
        }

        return self.constraint_set

    def learn_constraints_v2(
            self,
            enable_two_col_learner: bool,
            categorical_unique_threshold: float,
            max_distinct_categories: int,
            max_ranges_modifier: Union[float, dict],
            tail_discard_threshold: float,
            user_overrides=[]):

        self.summary_df = self.__compute_summary_df(tail_discard_threshold)
        self.callback(status="Data Drift: Summary Stats Calculated")

        self.constraint_set = DataConstraintSet()
        self.constraint_set.summary_stats = self.summary_df

        logger.info("[SPARK-OP] Counting rows in training data.")
        total_rows = self.training_data.count()
        logger.info(
            "[SPARK-OP] {} rows in training data.".format(total_rows))

        logger.info("Computing column statistics: Start, {}.".format(datetime.datetime.now().isoformat()))
        # learn the information of columns
        ColStatsComputer(
            self.constraint_set,
            self.training_data,
            self.summary_df,
            self.feature_columns,
            self.categorical_columns,
            self.callback).compute_stats(
            total_rows,
            categorical_unique_threshold,
            max_distinct_categories,
            max_ranges_modifier,
            tail_discard_threshold)
        logger.info("Computing column statistics: Complete, {}.".format(datetime.datetime.now().isoformat()))

        logger.info("Adding bucketed columns to training data")
        bucket_columns = []
        buckets = {}
        for name, column in self.constraint_set.columns.items():
            if column.dtype in (
                    ColumnType.CATEGORICAL,
                    ColumnType.NUMERIC_DISCRETE):
                continue
            if column.sparse or column.skip_learning:
                continue

            from pyspark.ml.feature import Bucketizer
            bucketizer = Bucketizer(
                splits=column.splits,
                inputCol=name,
                outputCol="{}_buckets".format(name),
                handleInvalid="keep")
            self.training_data = bucketizer.transform(
                self.training_data)

            bucket_columns.append("{}_buckets".format(column.name))
            buckets[column.name] = list(zip(column.splits, column.splits[1:]))
            logger.info(
                " - Added column {} buckets transformation.".format(column.name))
        logger.info("Bucket Columns: {}".format(bucket_columns))

        logger.info("Learning constraints: Start, {}.".format(datetime.datetime.now().isoformat()))
        # learn constraints
        ConstraintLearner(
            self.constraint_set,
            self.training_data,
            self.feature_columns,
            self.categorical_columns,
            self.callback).learn_constraints(
                bucket_columns=bucket_columns,
                buckets=buckets,
                enable_two_col_learner=enable_two_col_learner,
                max_distinct_categories=max_distinct_categories,
                user_overrides=user_overrides)

        self.constraint_set.user_inputs = {
            "enable_two_col_learner": enable_two_col_learner,
            "categorical_unique_threshold": categorical_unique_threshold,
            "max_distinct_categories": max_distinct_categories,
            "max_ranges_modifier": max_ranges_modifier,
            "tail_discard_threshold": tail_discard_threshold,
            "user_overrides": user_overrides
        }
        logger.info("Learning constraints: Complete, {}.".format(datetime.datetime.now().isoformat()))

        return self.constraint_set


class ColStatsComputer(DataConstraintLearner):
    """
        Class to compute column information from training data
    """

    def __init__(
            self,
            ctrset,
            training_data,
            summary_df,
            feature_columns: list,
            categorical_columns: list,
            callback):
        self.constraint_set = ctrset
        self.training_data = training_data
        self.summary_df = summary_df
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.callback = callback

    def compute_stats(
            self,
            total_rows: int,
            categorical_unique_threshold: float,
            max_distinct_categories: int,
            max_ranges_modifier: Union[float, dict],
            tail_discard_threshold: float):
        """
            Method to compute column related stats /info in training data

            Spark Operations:
            1. Approximate Distinct Counts for each feature column
        """

        # Generate a dictionary of column names and an approx count of
        # distinct values in that column.
        from pyspark.sql.functions import approx_count_distinct

        logger.info(
            "[SPARK-OP] Calculating approx distinct count in feature columns.")
        approx_count = self.training_data.select([approx_count_distinct(column).alias(
            column) for column in self.feature_columns]).toPandas().transpose()
        if len(self.feature_columns) == 1:
            approx_count = approx_count.to_dict()[0]
        else:
            approx_count = approx_count.squeeze().to_dict()
        logger.info(
            "[SPARK-OP] Calculated approx distinct count in feature columns. {}".format(approx_count))

        for column in self.feature_columns:
            if column in self.categorical_columns:
                column_type = ColumnType.CATEGORICAL
                column_summary = None
            else:
                is_discrete = approx_count[column] <= 5 * \
                    round(np.log2(total_rows))
                column_type = ColumnType.NUMERIC_DISCRETE if is_discrete else ColumnType.NUMERIC_CONTINUOUS
                column_summary = self.summary_df[column]
            column = DataColumn(column, column_type)
            column.summary = column_summary

            # Sometimes when there is only a single value in the column, Spark may give
            # an approx_count_distinct of 0. Putting a minimum of 1 for such columns.
            column.approx_count_distinct = max(approx_count[column.name], 1)
            if column_type in (
                    ColumnType.CATEGORICAL,
                    ColumnType.NUMERIC_DISCRETE):
                self.__validate_params(categorical_unique_threshold, max_distinct_categories)

                if (column.approx_count_distinct/total_rows) > categorical_unique_threshold:
                    column.skip_learning = True
                    column.skip_learning_reason = "The number of unique values[{}] is too high for total count [{}].".format(column.approx_count_distinct, total_rows)
                    column.skip_learning_reason += " Try to reduce the number of unique values in the column or "
                    column.skip_learning_reason += "increase the categorical_unique_threshold [].".format(categorical_unique_threshold)
                    logger.info(column.name + ": " + column.skip_learning_reason)

                elif column.approx_count_distinct > max_distinct_categories:
                    column.skip_learning = True
                    column.skip_learning_reason = "The number of unique values[{}] is too high.".format(column.approx_count_distinct)
                    column.skip_learning_reason += " Try to reduce the number of unique values in the column or "
                    column.skip_learning_reason += "increase the max_distinct_categories [].".format(max_distinct_categories)
                    logger.info(column.name + ": " + column.skip_learning_reason)

            self.callback("Computing stats for column: {}".format(column.name))
            max_bins = get_max_bins_for_column(column.name, approx_count, max_ranges_modifier)
            
            column.compute_stats(self.training_data, total_rows, max_bins, tail_discard_threshold)
            self.constraint_set.add_cl(column)
        self.callback(status="Data Drift: Column Stats calculated.")

    def __validate_params(self, categorical_unique_threshold, max_distinct_categories):
        if categorical_unique_threshold <= 0 or categorical_unique_threshold >= 1:
            raise ValueError("categorical_unique_threshold must be between 0 and 1")
        
        if max_distinct_categories <= 0:
            raise ValueError("max_distinct_categories must be greater than 0")

class SingleColCtrLearner(DataConstraintLearner):
    """
        Class to learn single column constraints from training data
    """

    def __init__(
            self,
            ctrset,
            training_data,
            feature_columns: list,
            categorical_columns: list,
            callback):
        self.constraint_set = ctrset
        self.training_data = training_data
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.callback = callback

    def _learn_constraints_helper(self, column, constraint, is_learn_constraint):
        if is_learn_constraint:
            constraint.learn_constraints(column, self.training_data)
            self.constraint_set.add_ctr(constraint)

        return constraint

    def learn_constraints(self, user_overrides=[]):
        """
            Learns/mines single column constraints from a dataset
        """

        cat_columns = []
        num_range_columns = []

        for column in self.constraint_set.columns.values():
            if column.sparse or column.skip_learning:
                continue
            if column.dtype in (
                    ColumnType.CATEGORICAL,
                    ColumnType.NUMERIC_DISCRETE):
                cat_columns.append(column)
            else:
                num_range_columns.append(column)

        # Categorical Distribution Constraint
        total = len(cat_columns)
        logger.info("(#/total) : Column,Constraint,Time(ms)")
        for idx, column in enumerate(cat_columns):
            start_time = time.time() * 1000

            # check if this column is asked to be skipped by user for single column learning,
            # skip learning if true
            learn_distribution_constraint, _ = check_user_override(
                column_names=[column.name], 
                constraint_kind=ConstraintKind.SINGLE_COLUMN.value, 
                user_overrides=user_overrides)

            constraint = self._learn_constraints_helper(
                column=column, 
                constraint=CategoricalDistributionConstraint(),
                is_learn_constraint=learn_distribution_constraint)

            logger.info("({}/{}) : {},{},{}".format(idx + 1,
                                                    total,
                                                    column.name,
                                                    constraint.name.value,
                                                    time.time() * 1000 - start_time))
            if (idx + 1) % 5 == 0:
                self.callback(
                    status="Data Drift: ({}/{}) CategoricalDistributionConstraint columns processed".format(idx + 1, total))
        self.callback(
            status="Data Drift: ({}/{}) CategoricalDistributionConstraint columns processed".format(total, total))

        # Numeric Range Constraint
        total = len(num_range_columns)
        logger.info("(#/total) : Column,Constraint,Time(ms)")
        for idx, column in enumerate(num_range_columns):
            start_time = time.time() * 1000

            # check if this column is asked to be skipped by user for single column learning,
            # skip learning if true
            _, learn_range_constraint = check_user_override(
                column_names=[column.name], 
                constraint_kind=ConstraintKind.SINGLE_COLUMN.value, 
                user_overrides=user_overrides)

            constraint = self._learn_constraints_helper(
                column=column, 
                constraint=NumericRangeConstraint(),
                is_learn_constraint=learn_range_constraint)

            logger.info("({}/{}) : {},{},{}".format(idx + 1,
                                                    total,
                                                    column.name,
                                                    constraint.name.value,
                                                    time.time() * 1000 - start_time))
            if (idx + 1) % 5 == 0:
                self.callback(
                    status="Data Drift: ({}/{}) NumericRangeConstraint columns processed".format(idx + 1, total))
        self.callback(
            status="Data Drift: ({}/{}) NumericRangeConstraint columns processed".format(total, total))


class TwoColCtrLearner(DataConstraintLearner):
    """
        Class to learn two column constraints from training data
    """

    def __init__(
            self,
            ctrset,
            training_data,
            feature_columns: list,
            categorical_columns: list,
            callback):
        self.constraint_set = ctrset
        self.training_data = training_data
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.callback = callback

    def _learn_constraints_helper(
            self,
            src_col,
            tgt_col,
            constraint,
            total_rows=None,
            is_learn_constraint: bool=False):

        if is_learn_constraint:
            source_column = self.constraint_set.columns[src_col]
            target_column = self.constraint_set.columns[tgt_col]

            constraint.learn_constraints(
                source_column=source_column,
                target_column=target_column,
                training_data=self.training_data,
                total_rows=total_rows)
            self.constraint_set.add_ctr(constraint)
        return constraint

    def learn_constraints(
            self,
            total_rows: int,
            max_distinct_categories: int,
            user_overrides=[]):
        """
          Method that learns/mines two column constraints from training data

        """

        categorical_columns = []
        numerical_columns = []
        for column in self.constraint_set.columns.values():
            if column.skip_learning or column.sparse:
                continue
            if column.dtype in (
                    ColumnType.CATEGORICAL,
                    ColumnType.NUMERIC_DISCRETE):
                categorical_columns.append(column.name)
            else:
                numerical_columns.append(column.name)
        categorical_columns = sorted(categorical_columns)
        numerical_columns = sorted(numerical_columns)

        catnum_range_columns = [
            (src_col,
             tgt_col) for (
                src_col,
                tgt_col) in product(
                categorical_columns,
                numerical_columns) if src_col != tgt_col]
        logger.info(
            "******** CatNum Range Columns [{}]: {} ********".format(
                len(catnum_range_columns),
                catnum_range_columns))

        # Learn CATNUM Range constraint for categorical and numeric
        # columns
        total = len(catnum_range_columns)
        logger.info(
            "(#/total) : SourceColumn,TargetColumn,Constraint,Time(ms)")
        for idx, (src_col, tgt_col) in enumerate(
                catnum_range_columns):
            start_time = time.time() * 1000

            _, learn_range_constraint = check_user_override(
                column_names=[src_col, tgt_col], 
                constraint_kind=ConstraintKind.TWO_COLUMN.value, 
                user_overrides=user_overrides)

            constraint = self._learn_constraints_helper(
                src_col=src_col, 
                tgt_col=tgt_col, 
                constraint=CategoricalNumericRangeConstraint(),
                is_learn_constraint=learn_range_constraint)

            logger.info("({}/{}) : {},{},{},{}".format(idx + 1,
                                                       total,
                                                       src_col,
                                                       tgt_col,
                                                       constraint.name.value,
                                                       time.time() * 1000 - start_time))
            if (idx + 1) % 5 == 0:
                self.callback(
                    status="Data Drift: ({}/{}) CategoricalNumericRangeConstraint columns processed".format(idx + 1, total))
        self.callback(
            status="Data Drift: ({}/{}) CategoricalNumericRangeConstraint columns processed".format(total, total))

        potential_catcat_distribution_columns = []
        for src_col, tgt_col in product(
                categorical_columns, categorical_columns):
            if (src_col == tgt_col) or ((tgt_col, src_col)
                                        in potential_catcat_distribution_columns):
                continue
            potential_catcat_distribution_columns.append(
                (src_col, tgt_col))
        logger.info(
            "******** CatCat Distribution Columns [{}]: {} ********".format(
                len(potential_catcat_distribution_columns),
                potential_catcat_distribution_columns))

        catcat_distribution_columns = []
        for src_col, tgt_col in potential_catcat_distribution_columns:
            src_col_approx_count = self.constraint_set.columns[src_col].approx_count_distinct
            tgt_col_approx_count = self.constraint_set.columns[tgt_col].approx_count_distinct
            if (src_col_approx_count *
                    tgt_col_approx_count) > max_distinct_categories:
                logger.info(
                    "Skipping combination '{}' from constraint learning process as it has {} unique values.".format(
                        (src_col, tgt_col), src_col_approx_count * tgt_col_approx_count))
                continue
            catcat_distribution_columns.append((src_col, tgt_col))
        logger.info(
            "******** CatCat Distribution Columns [{}]: {} ********".format(
                len(catcat_distribution_columns),
                catcat_distribution_columns))

        # Learn CATCAT constraints for categorical columns (select by
        # user + detected as numeric_discrete)
        total = len(catcat_distribution_columns)
        logger.info(
            "(#/total) : SourceColumn,TargetColumn,Constraint,Time(ms)")
        for idx, (src_col, tgt_col) in enumerate(
                catcat_distribution_columns):
            start_time = time.time() * 1000

            learn_distribution_constraint, _ = check_user_override(
                column_names=[src_col, tgt_col], 
                constraint_kind=ConstraintKind.TWO_COLUMN.value, 
                user_overrides=user_overrides)

            constraint = self._learn_constraints_helper(
                src_col=src_col, 
                tgt_col=tgt_col, 
                constraint=CatCatDistributionConstraint(), 
                total_rows=total_rows,
                is_learn_constraint=learn_distribution_constraint)

            logger.info("({}/{}) : {},{},{},{}".format(idx + 1,
                                                       total,
                                                       src_col,
                                                       tgt_col,
                                                       constraint.name.value,
                                                       time.time() * 1000 - start_time))
            if (idx + 1) % 5 == 0:
                self.callback(
                    status="Data Drift: ({}/{}) CatCatDistributionConstraint columns processed".format(idx + 1, total))
        self.callback(
            status="Data Drift: ({}/{}) CatCatDistributionConstraint columns processed".format(total, total))

class ConstraintLearner(DataConstraintLearner):
    """
        Class to learn column constraints from training data
    """

    def __init__(
            self,
            ctrset,
            training_data,
            feature_columns: list,
            categorical_columns: list,
            callback):
        self.constraint_set = ctrset
        self.training_data = training_data
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.callback = callback

    def learn_constraints(
        self,
        bucket_columns,
        buckets,
        enable_two_col_learner: bool,
        max_distinct_categories: int,
        user_overrides=[]):

        cat_distribution_columns = []
        categorical_columns = []

        num_range_columns = []
        num_columns = []

        # identify columns for categorical distribution or numerical range constraints learning
        logger.info("Identifying columns for learning single column constraints")
        for column in self.constraint_set.columns.values():
            if column.sparse or column.skip_learning:
                continue
            if column.dtype in (
                    ColumnType.CATEGORICAL,
                    ColumnType.NUMERIC_DISCRETE):
                cat_distribution_columns.append(column)
                categorical_columns.append(column.name)
            else:
                num_range_columns.append(column)
                num_columns.append(column.name)
        logger.info("Identification complete.")
        logger.info("Categorical Columns identified: {}".format(categorical_columns))
        logger.info("Numerical Columns identified: {}".format(num_columns))

        # identify columns for categorical-numerical range constraint learning
        logger.info("Identifying columns for learning categorical-numerical range constraint")
        categorical_categories = {}
        if enable_two_col_learner:
            for column in categorical_columns:
                value_counts = self.training_data.groupBy(column)\
                    .count().dropna().sort(column)\
                    .withColumnRenamed("count", "frequency")\
                    .toPandas().set_index(column)["frequency"]
                count = int(value_counts.sum())

                categories = value_counts[value_counts >= 0.02 * count].index.tolist()

                categorical_categories[column] = categories

        logger.info("Identification complete.")
        logger.info("Combinations identified: {}".format(categorical_categories))

        # identify columns for categorical-categorical distribution constraint learning
        logger.info("Identifying columns for learning categorical-categorical distribution constraint")
        catcat_distribution_columns = []
        if enable_two_col_learner:
            potential_catcat_distribution_columns = []
            for src_col, tgt_col in product(
                    categorical_columns, categorical_columns):
                if (src_col == tgt_col) or ((tgt_col, src_col)
                                            in potential_catcat_distribution_columns):
                    continue
                potential_catcat_distribution_columns.append(
                    (src_col, tgt_col))
            logger.info(
                "******** CatCat Distribution Columns [{}]: {} ********".format(
                    len(potential_catcat_distribution_columns),
                    potential_catcat_distribution_columns))

            catcat_distribution_columns = []
            for src_col, tgt_col in potential_catcat_distribution_columns:
                src_col_approx_count = self.constraint_set.columns[src_col].approx_count_distinct
                tgt_col_approx_count = self.constraint_set.columns[tgt_col].approx_count_distinct
                if (src_col_approx_count *
                        tgt_col_approx_count) > max_distinct_categories:
                    logger.info(
                        "Skipping combination '{}' from constraint learning process as it has {} unique values.".format(
                            (src_col, tgt_col), src_col_approx_count * tgt_col_approx_count))
                    continue
                catcat_distribution_columns.append((src_col, tgt_col))
        logger.info("Identification complete.")
        logger.info("Combinations identified: {}".format(catcat_distribution_columns))

        columns = self.feature_columns.copy()
        columns.extend(bucket_columns)

        unified_constraint_learner = UnifiedConstraintLearner(
            columns=columns,
            bucket_columns=bucket_columns,
            buckets=buckets,
            categorical_columns=categorical_columns.copy(),
            categorical_categories=categorical_categories,
            numerical_range_columns=num_range_columns,
            catcat_distribution_columns=catcat_distribution_columns)

        logger.info(
            "Calling partition function and collecting results: Start, {}.".format(
                datetime.datetime.now().isoformat()))
        result = self.training_data.select(columns).rdd.mapPartitions(
            unified_constraint_learner).collect()
        logger.debug("Collected result: {}".format(result))
        logger.info(
            "Calling partition function and collecting results: Complete, {}.".format(
                datetime.datetime.now().isoformat()))

        self.__add_constraints_to_set(
            constraints=unified_constraint_learner.get_categorical_distribution_constraint(
                categorical_columns=cat_distribution_columns))

        self.__add_constraints_to_set(
            constraints=unified_constraint_learner.get_numeric_range_constraints(
                result=result,
                buckets=buckets))

        if enable_two_col_learner:
            self.__add_constraints_to_set(
                constraints=unified_constraint_learner.get_catnum_range_constraints(
                    result=result))
            self.__add_constraints_to_set(
                constraints=unified_constraint_learner.get_catcat_distribution_constraints(
                    result=result))

        logger.info("Complete!!!")

    def __add_constraints_to_set(self, constraints):
        for constraint in constraints:
            self.constraint_set.add_ctr(constraint)