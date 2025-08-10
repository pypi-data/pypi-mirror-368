# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import sys
import time
from functools import reduce
from itertools import product
from typing import List, Optional

import numpy as np
import pandas as pd
from service.core.constraints.catcat_distribution_constraint import \
    CatCatDistributionConstraint
from service.core.constraints.categorical_distribution_constraint import \
    CategoricalDistributionConstraint
from service.core.constraints.catnum_distribution_constraint import \
    CategoricalNumericDistributionConstraint
from service.core.constraints.catnum_range_constraint import \
    CategoricalNumericRangeConstraint
from service.core.constraints.column import DataColumn
from service.core.constraints.constants import ColumnType, ConstraintKind
from service.core.constraints.entity import DataConstraintSet
from service.core.constraints.numeric_distribution_constraint import \
    NumericDistributionConstraint
from service.core.constraints.numeric_range_constraint import \
    NumericRangeConstraint
from service.core.constraints.util import check_user_override
from tqdm import tqdm


class DataConstraintLearner(object):

    def __init__(
            self,
            training_data: pd.DataFrame,
            feature_columns: list,
            categorical_columns: list,
            progress_bar: bool,
            callback=None):

        self.training_data = training_data
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.progress_bar = progress_bar
        self.callback = callback

        self.constraint_set = DataConstraintSet()

    def learn_constraints(
            self,
            enable_two_col_learner,
            categorical_unique_threshold: float = 0.8,
            debug: bool = False,
            user_overrides: Optional[List] = []):

        # learn the information of columns
        ColStatsComputer(
            self.constraint_set,
            self.training_data,
            self.feature_columns,
            self.categorical_columns,
            self.progress_bar).compute_stats(
                categorical_unique_threshold)

        # learn single column constraints
        SingleColCtrLearner(
            self.constraint_set,
            self.training_data, self.feature_columns,
            self.categorical_columns,
            self.progress_bar,
            self.callback,
            debug=debug).learn_constraints(
                user_overrides=user_overrides)

        # learn two column constraints
        if enable_two_col_learner:
            TwoColCtrLearner(
                self.constraint_set,
                self.training_data,
                self.feature_columns,
                self.categorical_columns,
                self.progress_bar,
                self.callback,
                debug=debug).learn_constraints(
                    user_overrides=user_overrides)

        return self.constraint_set


class ColStatsComputer(DataConstraintLearner):
    """
        Class to compute column information from training data
    """

    def __init__(self, ctrset, training_data, feature_columns: list, categorical_columns: list, progress_bar: bool):
        self.constraint_set = ctrset
        self.training_data = training_data
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.progress_bar = progress_bar

    def compute_stats(self, categorical_unique_threshold: float = 0.8):
        """
            Method to compute column related stats /info in training data
        """
        if (categorical_unique_threshold <= 0) or (categorical_unique_threshold > 1):
            raise Exception(
                "Value of 'categorical_unique_threshold' should be be between 0 and 1.")

        tqdm_bar = tqdm(self.feature_columns, desc="Computing feature stats...", file=sys.stdout,
                        unit="features", dynamic_ncols=True, disable=not (self.progress_bar))
        for column in tqdm_bar:
            skip_learning = False
            column_data = self.training_data[column]
            num_unique = len(column_data.unique())
            if column in self.categorical_columns:
                if num_unique > categorical_unique_threshold * len(column_data):
                    print("Skiping column '{}' from constraint learning process as it has large number of unique values. Please tweak 'categorical_unique_threshold' for more control on this.".format(column))
                    skip_learning = True
                column_type = ColumnType.CATEGORICAL
            else:
                is_discrete = num_unique <= 5 * \
                    round(np.log2(len(column_data)))
                column_type = ColumnType.NUMERIC_DISCRETE if is_discrete else ColumnType.NUMERIC_CONTINUOUS

            column = DataColumn(column, column_type)
            column.skip_learning = skip_learning
            column.compute_stats(self.training_data)
            self.constraint_set.add_cl(column)


class SingleColCtrLearner(DataConstraintLearner):
    """
        Class to learn single column constraints from training data
    """

    def __init__(self, ctrset, training_data, feature_columns: list, categorical_columns: list, progress_bar: bool, callback=None, debug: bool = False):
        self.constraint_set = ctrset
        self.training_data = training_data
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.progress_bar = progress_bar
        self.callback = callback
        self.debug = debug

    def _learn_constraints_helper(self, column, constraint, tqdm_bar, is_learn_constraint):
        start_time = time.time() * 1000

        if is_learn_constraint:
            constraint.learn_constraints(column, self.training_data)
            self.constraint_set.add_ctr(constraint)
        else:
            constraint.constraint_learned = True

        if self.callback and constraint.constraint_learned:
            self.callback(constraint.name, start_time)
        if self.debug:
            print("{},{},{}".format(column.name, constraint.name.value,
                  time.time()*1000 - start_time))
        tqdm_bar.update(n=1)

    def learn_constraints(self, user_overrides: Optional[List] = []):
        """
            Learns/mines single column constraints from a dataset
        """
        def countFn(col):
            if col.skip_learning:
                return 0

            if col.dtype in (ColumnType.CATEGORICAL, ColumnType.NUMERIC_DISCRETE):
                return 1

            if (col.dtype is ColumnType.NUMERIC_CONTINUOUS) and col.sparse:
                return 0
            return 2

        total = reduce(lambda total, col: total + countFn(col),
                       self.constraint_set.columns.values(), 0)
        tqdm_bar = tqdm(total=total, desc="Learning single feature constraints...", file=sys.stdout,
                        unit="constraints", dynamic_ncols=True, disable=(not (self.progress_bar) or self.debug))

        if self.debug:
            print("Column,Constraint,Time(ms)")
        for column in self.constraint_set.columns.values():
            if column.dtype in (ColumnType.CATEGORICAL, ColumnType.NUMERIC_DISCRETE):
                # Categorical Distribution Constraint
                if column.skip_learning:
                    continue

                # check if this column is asked to be skipped by user for single column learning,
                # skip learning if true
                learn_distribution_constraint, _ = check_user_override(
                    column_names=[column.name],
                    constraint_kind=ConstraintKind.SINGLE_COLUMN.value,
                    user_overrides=user_overrides)

                self._learn_constraints_helper(
                    column=column,
                    constraint=CategoricalDistributionConstraint(),
                    tqdm_bar=tqdm_bar,
                    is_learn_constraint=learn_distribution_constraint)

            else:
                # Now, the column type is ColumnType.NUMERIC_CONTINUOUS
                if column.sparse or column.skip_learning:
                    continue

                # check if this column is asked to be skipped by user for single column learning,
                # skip learning if true
                learn_distribution_constraint, learn_range_constraint = check_user_override(
                    column_names=[column.name],
                    constraint_kind=ConstraintKind.SINGLE_COLUMN.value,
                    user_overrides=user_overrides)

                # Numeric Distribution Constraint
                self._learn_constraints_helper(
                    column=column,
                    constraint=NumericDistributionConstraint(),
                    tqdm_bar=tqdm_bar,
                    is_learn_constraint=learn_distribution_constraint)

                # Numeric Range Constraint
                self._learn_constraints_helper(
                    column=column,
                    constraint=NumericRangeConstraint(),
                    tqdm_bar=tqdm_bar,
                    is_learn_constraint=learn_range_constraint)

        if self.callback:
            self.callback()
        tqdm_bar.close()


class TwoColCtrLearner(DataConstraintLearner):
    """
        Class to learn two column constraints from training data
    """

    def __init__(self, ctrset, training_data, feature_columns: list, categorical_columns: list, progress_bar: bool, callback=None, debug: bool = False):
        self.constraint_set = ctrset
        self.training_data = training_data
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.progress_bar = progress_bar
        self.callback = callback
        self.debug = debug

    def _learn_constraints_helper(self, src_col, tgt_col, constraint, tqdm_bar, is_learn_constraint):
        source_column = self.constraint_set.columns[src_col]
        target_column = self.constraint_set.columns[tgt_col]
        start_time = time.time() * 1000

        if is_learn_constraint:
            constraint.learn_constraints(
                source_column=source_column,
                target_column=target_column,
                training_data=self.training_data)
            self.constraint_set.add_ctr(constraint)
        else:
            constraint.constraint_learned = True

        if self.callback and constraint.constraint_learned:
            self.callback(constraint.name, start_time)
        if self.debug:
            print("{},{},{},{}".format(src_col, tgt_col,
                  constraint.name.value, time.time() * 1000 - start_time))
        tqdm_bar.update(n=1)

    def learn_constraints(self, user_overrides: Optional[List] = []):
        """
          Method that learns/mines two column constraints from training data

        """

        categorical_columns = [
            column for column in self.categorical_columns if not self.constraint_set.columns[column].skip_learning]
        discrete_columns = [
            column for column in self.feature_columns if self.constraint_set.columns[column].dtype is ColumnType.NUMERIC_DISCRETE]
        continuous_columns = [
            column for column in self.feature_columns if self.constraint_set.columns[column].dtype is ColumnType.NUMERIC_CONTINUOUS and not self.constraint_set.columns[column].sparse]

        catnum_range_columns = list(
            product(categorical_columns + discrete_columns, continuous_columns))
        catnum_range_columns = [(src_col, tgt_col) for (
            src_col, tgt_col) in catnum_range_columns if src_col != tgt_col]

        catnum_distribution_columns = list(
            product(categorical_columns + discrete_columns, continuous_columns))

        columns = categorical_columns + discrete_columns
        catcat_distribution_columns = []
        for src_col, tgt_col in product(columns, columns):
            if (src_col == tgt_col) or ((tgt_col, src_col) in catcat_distribution_columns):
                continue
            catcat_distribution_columns.append((src_col, tgt_col))

        total = len(catnum_range_columns) + \
            len(catnum_distribution_columns) + len(catcat_distribution_columns)
        tqdm_bar = tqdm(total=total, desc="Learning two feature constraints...", file=sys.stdout,
                        unit="constraints", dynamic_ncols=True, disable=(not (self.progress_bar) or self.debug))
        if self.debug:
            print("SourceColumn,TargetColumn,Constraint,Time(ms)")
        # Learn constraint for categorical and numeric columns
        for src_col, tgt_col in catnum_range_columns:
            _, learn_range_constraint = check_user_override(
                column_names=[src_col, tgt_col],
                constraint_kind=ConstraintKind.TWO_COLUMN.value,
                user_overrides=user_overrides)

            self._learn_constraints_helper(
                src_col=src_col,
                tgt_col=tgt_col,
                constraint=CategoricalNumericRangeConstraint(),
                tqdm_bar=tqdm_bar,
                is_learn_constraint=learn_range_constraint)

        if self.callback:
            self.callback()

        for src_col, tgt_col in catnum_distribution_columns:
            learn_distribution_constraint, _ = check_user_override(
                column_names=[src_col, tgt_col],
                constraint_kind=ConstraintKind.TWO_COLUMN.value,
                user_overrides=user_overrides)

            self._learn_constraints_helper(
                src_col=src_col,
                tgt_col=tgt_col,
                constraint=CategoricalNumericDistributionConstraint(),
                tqdm_bar=tqdm_bar,
                is_learn_constraint=learn_distribution_constraint)

        if self.callback:
            self.callback()

        # Learn constraints for categorical columns (select by user + detected as numeric_discrete)
        for src_col, tgt_col in catcat_distribution_columns:
            learn_distribution_constraint, _ = check_user_override(
                column_names=[src_col, tgt_col],
                constraint_kind=ConstraintKind.TWO_COLUMN.value,
                user_overrides=user_overrides)

            self._learn_constraints_helper(
                src_col=src_col,
                tgt_col=tgt_col,
                constraint=CatCatDistributionConstraint(),
                tqdm_bar=tqdm_bar,
                is_learn_constraint=learn_distribution_constraint)

        if self.callback:
            self.callback()

        tqdm_bar.close()
