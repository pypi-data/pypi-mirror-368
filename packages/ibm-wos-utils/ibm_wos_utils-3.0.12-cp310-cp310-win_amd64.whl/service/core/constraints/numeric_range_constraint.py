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
from service.core.constraints.constants import RANGE_BUFFER_CONSTANT
from service.core.constraints.util import (get_numeric_ranges,
                                           get_primitive_value,
                                           get_min_max_buffer,
                                           is_min_max_outlier, 
                                           remove_outliers)


class NumericRangeConstraint(DataConstraint):
    def __init__(self):
        super().__init__(ConstraintName.NUMERIC_RANGE_CONSTRAINT,
                         ConstraintKind.SINGLE_COLUMN)

    def learn_constraints(self, column: DataColumn, training_data: pd.DataFrame):
        self.columns = [column.name]
        column_data = training_data[column.name].dropna()

        if not len(column_data):
            return

        self.content["ranges"] = get_numeric_ranges(column_data)
        self.constraint_learned = True

    def _check_violations(self, payload: pd.DataFrame, result_df: pd.DataFrame):
        temp_df = payload.copy()
        for idx, col_range in enumerate(self.content["ranges"]):
            conditions = temp_df[self.columns[0]].apply(lambda x: not is_min_max_outlier(
                x, col_min=col_range["min"], col_max=col_range["max"]))
            temp_df.drop(temp_df[conditions].index, inplace=True)

        if len(temp_df):
            result_df.loc[result_df["scoring_id"].isin(
                temp_df["scoring_id"]), self.id] = 1

            ranges = []
            for num_range in self.content["ranges"]:
                buffer = get_min_max_buffer(num_range["min"], num_range["max"])
                ranges.append((get_primitive_value(num_range["min"] - buffer), get_primitive_value(num_range["max"] + buffer)))

            return self.get_violation_info("AIQDD9003E", [self.columns[0], ranges])

        # No violations. Return empty dict
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
