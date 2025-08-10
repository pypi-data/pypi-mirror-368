# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import pandas as pd

from ibm_wos_utils.drift.batch.constraints.column import DataColumn
from ibm_wos_utils.drift.batch.constraints.data_constraint import \
    DataConstraint
from ibm_wos_utils.drift.batch.util.constants import (ConstraintKind,
                                                      ConstraintName)
from ibm_wos_utils.drift.batch.util.constraint_utils import get_processed_key


class CategoricalDistributionConstraint(DataConstraint):
    def __init__(self):
        super().__init__(
            ConstraintName.CATEGORICAL_DISTRIBUTION_CONSTRAINT,
            ConstraintKind.SINGLE_COLUMN)

    def learn_constraints(
            self,
            column: DataColumn,
            training_data):
        self.columns = [column.name]
        self.generate_id()
        self.constraint_learned = True
        self.content["frequency_distribution"] = { get_processed_key(key) : value for key, value in column.value_counts.to_dict().items()}

    def _check_violations(
            self,
            payload: pd.DataFrame,
            result_df: pd.DataFrame):
        values = list(self.content["frequency_distribution"].keys())
        result_df[self.id] = ~payload[self.columns[0]].astype(
            str).isin(map(str, values))

        # If there are any NaNs in the column, then we have a violation
        result_df[self.id] = result_df[self.id].fillna(True)

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
