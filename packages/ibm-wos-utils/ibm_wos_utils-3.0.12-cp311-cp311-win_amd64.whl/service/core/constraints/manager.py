# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd

from service.core.constraints.constants import ColumnType, ConstraintName
from service.core.constraints.entity import DataConstraintSet
from service.core.constraints.learner import DataConstraintLearner


class DataConstraintMgr(object):
    """
    This is the entry-point class for all that needs to be done with constraints
    """

    @staticmethod
    def learn_constraints(training_data, feature_columns, categorical_columns, progress_bar=False, callback=None, enable_two_col_learner=True, categorical_unique_threshold=0.8, debug=False, user_overrides=[]):
        """Learns/mines constraints from a dataset

        Arguments:
            ds {pandas.DataFrame} -- a pandas dataframe of the dataset
            cols {list} -- the list of columns on which the constraints have to be learnt
            coltypes {list} -- the type of each column in the 'cols' list

        Returns:
            DataConstraintSet -- A collection of constraints and associated information
        """

        ctrset = DataConstraintLearner(
            training_data, feature_columns, categorical_columns, progress_bar, callback).learn_constraints(
                enable_two_col_learner=enable_two_col_learner, categorical_unique_threshold=categorical_unique_threshold, 
                debug=debug, user_overrides=user_overrides)
        return ctrset

    @staticmethod
    def check_violations(constraints_set: DataConstraintSet, payload: dict):
        """Checks violations against constraints and returns two things:
        1. A dictionary of violated constraints with constraint ids as keys like so..
        {
            "constraint_id_1": {
                "name": "constraint_name"
                "code": "meesage_cde",
                "parameter":[<array of pameters supplued in message>]
                "message": "a message telling exactly how that constraint was violated"
            }
            ...
        }
        2. A pandas dataframe containing all drifted transactions. If there are `m` constraints and
        `n` drifted transactions, the DataFrame will be:

        |   scoring_id  | constraint_id_1 | constraint_id_2 | ... | constraint_id_m |
        |:-------------:|:---------------:|:---------------:|:---:|:---------------:|
        | transaction_1 |        0        |        0        |     |        1        |
        | transaction_2 |        1        |        1        |     |        0        |
        |      ...      |                 |                 |     |                 |
        | transaction_n |        0        |        1        |     |        0        |

        1 under a column signifies that a particular transaction violates that constraint. 0 otherwise.

        Arguments:
            constraints_set {DataConstraintSet} -- Constraints Set containing all information
            payload {dict} -- Payload Data

        Returns:
            tuple -- constraint violations, drifted transactions
        """
        violations = {}

        payload_df = pd.DataFrame(payload["values"], columns=payload["fields"])
        results_df = pd.DataFrame(
            np.zeros(shape=(len(payload_df), len(constraints_set.constraints))), dtype=int)
        results_df.columns = list(constraints_set.constraints.keys())
        results_df["scoring_id"] = payload_df["scoring_id"].copy()

        # Compute violations for single column constraints
        for constraint in constraints_set.single_column_constraints():
            column_type = constraints_set.columns[constraint.columns[0]].dtype
            # Do not compute violations for Numeric Range Constraints for discrete columns.
            if (constraint.name is ConstraintName.NUMERIC_RANGE_CONSTRAINT) and (column_type is ColumnType.NUMERIC_DISCRETE):
                continue

            # Do not compute violations for Numeric Distribution constraints, if the column is sparse.
            if (constraint.name is ConstraintName.NUMERIC_DISTRIBUTION_CONSTRAINT) and  (constraints_set.columns[constraint.columns[0]].sparse):
                continue
            violations.update(
                constraint.check_violations(payload_df, results_df))

        # Compute violations for two column constraints
        for constraint in constraints_set.two_column_constraints():
            # Do not compute violations for CATNUM Distribution constraints, if target column is sparse.
            if (constraint.name is ConstraintName.CAT_NUM_DISTRIBUTION_CONSTRAINT) and (constraints_set.columns[constraint.target_column].sparse):
                continue

            # Ignore the already learnt CATNUM Range Constraint if the Num/target column is discrete
            if (constraint.name is ConstraintName.CAT_NUM_RANGE_CONSTRAINT) and (constraints_set.columns[constraint.target_column].dtype is ColumnType.NUMERIC_DISCRETE):
                continue
            violations.update(
                constraint.check_violations(payload_df, results_df))

        return violations, results_df[results_df.sum(axis=1, numeric_only=True) > 0]
