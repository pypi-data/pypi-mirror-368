# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd
from ibm_wos_utils.drift.batch.constraints.column import DataColumn
from ibm_wos_utils.drift.batch.constraints.custom_range import (Range,
                                                                merge_ranges)
from ibm_wos_utils.drift.batch.constraints.data_constraint import \
    DataConstraint
from ibm_wos_utils.drift.batch.util.constants import (ConstraintKind,
                                                      ConstraintName)
from ibm_wos_utils.drift.batch.util.constraint_utils import (
    get_limits_with_buffer, get_primitive_value)


class NumericRangeConstraint(DataConstraint):
    def __init__(self):
        super().__init__(ConstraintName.NUMERIC_RANGE_CONSTRAINT,
                         ConstraintKind.SINGLE_COLUMN)

    def learn_constraints(
            self,
            column: DataColumn,
            training_data):
        """Learn constraints

        Spark Operations:
        1. For the corresponding bucket column to the numerical column, this does:
            - Frequency counts
            - Drops null in resulting dataframe
            - Sorts the resulting dataframe based on buckets.

        Arguments:
            column {DataColumn} -- Column on which to learn constraint
            training_data {pyspark.sql.dataframe.DataFrame} -- Training Data
        """
        self.columns = [column.name]
        self.generate_id()
        bucket_col = "{}_buckets".format(column.name)
        buckets = list(zip(column.splits, column.splits[1:]))

        # 1. Do a groupby using bucket column
        ranges_df = training_data.groupBy(bucket_col).count()
        # 2. Drop null rows, sort and convert to Pandas DataFrame
        ranges_df = ranges_df.dropna(
            subset=[bucket_col]).sort(bucket_col).toPandas()

        # ranges_df.drop(ranges_df[ranges_df["count"] < column.summary.loc["expected"]].index, axis=0, inplace=True)
        ranges = ranges_df.apply(lambda row: Range(bounds=buckets[int(
            row[bucket_col])], count=int(row["count"])), axis=1).to_list()

        # self.content["ranges"] = [numrange.to_json() for numrange in merge_ranges(ranges, is_integer=column.is_integer, discard=True)]
        # Not merging the ranges due to feature imbalance work
        self.content["ranges"] = {
            get_primitive_value(numrange.min): numrange.count for numrange in ranges}
        self.constraint_learned = True

    def _check_violations(
            self,
            payload: pd.DataFrame,
            result_df: pd.DataFrame):
        # Convert string keys to int/float
        try:
            buckets = {
                int(key): value for key,
                value in self.content["ranges"].items()}
        except ValueError:
            buckets = {
                float(key): value for key,
                value in self.content["ranges"].items()}

        step_size = np.min(np.diff(list(buckets.keys())))
        ranges = merge_ranges([Range(bounds=(key,
                                             key + step_size),
                                     count=value) for key,
                               value in buckets.items()],
                              discard=True)
        for numrange in ranges:
            lower_limit, upper_limit = get_limits_with_buffer(
                numrange.min, numrange.max)
            result_df[self.id] = result_df[self.id] | payload[self.columns[0]].between(
                lower_limit, upper_limit)
        result_df[self.id] = ~result_df[self.id]

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
