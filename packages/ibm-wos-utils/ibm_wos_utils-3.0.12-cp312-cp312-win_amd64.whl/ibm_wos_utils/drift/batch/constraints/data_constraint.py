# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


from abc import abstractmethod
from ibm_wos_utils.drift.batch.util.constraint_utils import get_constraint_id

import pandas as pd
from ibm_wos_utils.drift.batch.util.constants import (ConstraintKind,
                                                      ConstraintName)


class DataConstraint(object):
    """
    All statistical data constraints of a column or a combination of columns
    are described by an instance of a DataConstraint. A constraint has a
    unique readable name and also a unique instance identifier generated
    by the system. There can be many constraints learnt with the same name,
    but with unique instance ids.

    Constraints inferred by constraint learner are accessible by users
    via the DataConstraintSet, which is a container for DataConstraint objects
    """

    def __init__(
            self,
            name: ConstraintName = None,
            kind: ConstraintKind = None):
        """
        Arguments:
            name {ConstraintName} -- One of the names from ConstraintName enum with value as human readable name without any whitespaces
            kind {ConstraintKind} -- ConstraintKind indicating single/two column constraint
        """
        self.name = name
        # The id is the hash of constraint name + column name(s) in lower case
        # sorted alphabetically.
        self.id = None
        self.kind = kind
        self.columns = []
        self.content = dict()  # all of the specific information of a constraint

        # This flag controls whether a constraint will be added to the set or not.
        # Child classes need to change this to True after successfully
        # learning a constraint.
        self.constraint_learned = False

    def generate_id(self):
        self.id = get_constraint_id(
            constraint_name=self.name,
            columns=self.columns)

    @abstractmethod
    def learn_constraints(self):
        """
            Method to add logic for learning constraints
        """
        raise NotImplementedError

    def __preprocess(self, payload: pd.DataFrame):
        return payload.dropna(subset=self.columns)

    @abstractmethod
    def _check_violations(
            self,
            payload: pd.DataFrame,
            result_df: pd.DataFrame):
        raise NotImplementedError

    def check_violations(
            self,
            payload: pd.DataFrame,
            result_df: pd.DataFrame):
        """
            Method for checking violations in the payload data
        """
        payload_df = self.__preprocess(payload)
        if len(payload_df):
            self._check_violations(
                payload_df, result_df)
        result_df[self.id] = result_df[self.id].astype(int)

    @abstractmethod
    def to_json(self):
        raise NotImplementedError

    @abstractmethod
    def from_json(self, json_obj):
        self.id = json_obj.get("id")
        self.kind = ConstraintKind(json_obj.get("kind"))
        self.columns = json_obj.get("columns")
        self.content = json_obj.get("content")
        self.constraint_learned = True
