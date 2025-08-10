# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import uuid
from abc import abstractmethod
from collections import OrderedDict

import pandas as pd
from service.core.constraints.constants import ConstraintKind, ConstraintName


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

    def __init__(self, name: ConstraintName = None, kind: ConstraintKind = None):
        """
        Arguments:
            name {ConstraintName} -- One of the names from ConstraintName enum with value as human readable name without any whitespaces
            kind {ConstraintKind} -- ConstraintKind indicating single/two column constraint
        """
        self.name = name
        # system generated instance id for the constraint
        self.id = str(uuid.uuid4())
        self.kind = kind
        self.columns = []
        self.content = dict()  # all of the specific information of a constraint

        # This flag controls whether a constraint will be added to the set or not. 
        # Child classed need to change this to True after successfully learning a constraint.
        self.constraint_learned = False

    @abstractmethod
    def learn_constraints(self):
        """
            Method to add logic for learning constraints
        """
        raise NotImplementedError

    @abstractmethod
    def to_json(self):
        # serialize using json dumps - TODO define protocol
        raise NotImplementedError

    def __preprocess(self, payload: pd.DataFrame):
        return payload.dropna(subset=self.columns)

    @abstractmethod
    def _check_violations(self, payload: pd.DataFrame, result_df: pd.DataFrame):
        raise NotImplementedError

    def check_violations(self, payload: pd.DataFrame, result_df: pd.DataFrame):
        """
            Method for checking violations in the payload data
        """
        payload_df = self.__preprocess(payload)
        if len(payload_df):
            return self._check_violations(payload_df, result_df)

        return {}

    @abstractmethod
    def from_json(self, json_obj):
        self.id = json_obj.get("id")
        self.kind = ConstraintKind(json_obj.get("kind"))
        self.columns = json_obj.get("columns")
        self.content = json_obj.get("content")
        self.constraint_learned = True


    def get_violation_info(self, code: str, parameters: list):
        """
            Method to construct the violation information
        """

        messages = {
            "AIQDD9001E": "The values of the {0} and {1} features rarely occur together.",
            "AIQDD9002E": "The {0} feature value falls outside of the training data distribution.",
            "AIQDD9003E": "The {0} feature values are typically between the range of {1}.",
            "AIQDD9004E": "For the {0} feature the value of {1} feature falls outside of the training data distribution.",
            "AIQDD9005E": "For the {0} feature the value of the {1} feature is outside of its typical value ranges.",
            "AIQDD9006E": "The {0} feature value is unexpected.",
            "AIQDD9007E": "The {0} and {1} feature values are causing a drop in accuracy. The {0} feature has a large impact on drift. "
                        "The {1} feature has some impact on drift. The feature values are similar to those in the training data, "
                        "but the model is known to provide incorrect predictions for similar transactions in the training data.",
            "AIQDD9008E": "Review the {0} and {1} feature values to determine why the model may be providing incorrect predictions. "
                        "Supplement the training data with similar records with corrected predictions and retrain the model.",
            "AIQDD9009E": "The {0} and {1} feature values are unexpected compared to the training data. The feature values exhibit the "
                        "following inconsistencies.",
            "AIQDD9010E": "These transactions are not causing drift so no action may be needed. Review the {0} and {1} features to determine "
                        "why their values are not consistent with the training data. If a value is unexpected, a data entry or data processing "
                        "problem may exist or the type of data the model is processing may be slowly changing."
        }

        violation_info = {
            self.id: {
                "name": self.name.value,
                "code": code,
                "parameters": parameters,
                "columns": self.columns,
                "message": messages.get(code).format(*parameters)
            }
        }

        return violation_info
