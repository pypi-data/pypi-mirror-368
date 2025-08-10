# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from collections import OrderedDict

import pandas as pd

from service.core.constraints.column import DataColumn
from service.core.constraints.constants import ConstraintKind, ConstraintName
from service.core.constraints.data_constraint import DataConstraint
from service.core.constraints.util import is_categorical_outlier


class CategoricalDistributionConstraint(DataConstraint):
    def __init__(self):
        super().__init__(ConstraintName.CATEGORICAL_DISTRIBUTION_CONSTRAINT,
                         ConstraintKind.SINGLE_COLUMN)

    def learn_constraints(self, column: DataColumn, training_data: pd.DataFrame):
        self.columns = [column.name]
        self.content["frequency_distribution"] = column.value_counts.sort_index().to_dict()
        self.constraint_learned = True

    def _check_violations(self, payload: pd.DataFrame, result_df: pd.DataFrame):
        conditions = payload[self.columns[0]].apply(
            lambda x: is_categorical_outlier(x, self.content.get("frequency_distribution")))

        if sum(conditions):
            outliers = payload.drop(payload[~conditions].index)
            result_df.loc[result_df["scoring_id"].isin(
                outliers["scoring_id"]), self.id] = 1

            return self.get_violation_info("AIQDD9006E", self.columns)
        
        return {}

    def to_json(self):
        return {
            "name": self.name.value,
            "id": self.id,
            "kind": self.kind.value,
            "columns": self.columns,
            "content": self.content
        }

    def from_json(self, json_obj):
        super().from_json(json_obj)
