# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


import pandas as pd
from ibm_wos_utils.drift.batch.constraints.column import DataColumn
from ibm_wos_utils.drift.batch.constraints.custom_range import (Range,
                                                                merge_ranges)
from ibm_wos_utils.drift.batch.constraints.data_constraint import \
    DataConstraint
from ibm_wos_utils.drift.batch.util.constants import (ConstraintKind,
                                                      ConstraintName)
from ibm_wos_utils.drift.batch.util.constraint_utils import (
    get_limits_with_buffer, get_processed_key)


class CategoricalNumericRangeConstraint(DataConstraint):
    def __init__(self):
        super().__init__(ConstraintName.CAT_NUM_RANGE_CONSTRAINT,
                         ConstraintKind.TWO_COLUMN)
        self.source_column = None
        self.target_column = None
        self.content = {}

    def learn_constraints(
            self,
            source_column: DataColumn,
            target_column: DataColumn,
            training_data,
            total_rows):
        """Learn constraints

        Spark Operations:
        1. For each categorical-numerical combination, it does:
            - Frequency counts for each source-value:target-value combination
            - Drops null in resulting dataframe
            - Sorts the resulting dataframe based on categories.

        Arguments:
            source_column {DataColumn} -- Source Column
            target_column {DataColumn} -- Target Column
            training_data {pyspark.sql.dataframe.DataFrame} -- Training Data
            total_rows {int} -- Total Rows
        """
        self.source_column = source_column.name
        self.target_column = target_column.name

        self.columns = [self.source_column, self.target_column]
        self.generate_id()
        self.content["source_column"] = self.source_column
        self.content["target_column"] = self.target_column

        categories = source_column.value_counts[source_column.value_counts >=
                                                0.02 * source_column.count].index.tolist()
        if len(categories) == 0:
            return

        bucket_col = "{}_buckets".format(self.target_column)
        buckets = list(
            zip(target_column.splits, target_column.splits[1:]))

        # 1. Filter values where source column is in eligible categories
        ranges_df = training_data.where(
            training_data[self.source_column].isin(categories))
        # 2. Do a groupBy counts on source_column + bucket column
        ranges_df = ranges_df.groupBy(
            self.source_column, bucket_col).count()
        # 3. Drop nulls, sort dataframe, convert to pandas DataFrame
        ranges_df = ranges_df.dropna(subset=[bucket_col]).sort(
            [self.source_column, bucket_col]).toPandas()

        if target_column.is_tails_discarded:
            # If the target column, tails are discarded, then we need to also discard the buckets
            # we found for the cat num range for a better representation in the constraints.
            buckets = buckets[1:-1]
            ranges_df = ranges_df[ranges_df[bucket_col]
                                  != ranges_df[bucket_col].min()]
            ranges_df = ranges_df[ranges_df[bucket_col]
                                  != ranges_df[bucket_col].max()]
            ranges_df[bucket_col] = ranges_df[bucket_col] - 1

        # TODO Spend more time on refining the dropping rows logic
        # expected_counts = np.round(
        #     source_column.value_counts / (10 * target_column.summary.loc["bins"]))
        # ranges_df = ranges_df[ranges_df.apply(lambda row: row["count"] >= expected_counts[row[self.source_column]], axis=1)]

        self.content["ranges"] = {}
        for src_val in ranges_df[self.source_column].unique():
            ranges = ranges_df[ranges_df[self.source_column] == src_val].apply(lambda row: Range(
                bounds=buckets[int(row[bucket_col])], count=int(row["count"])), axis=1).to_list()
            self.content["ranges"][get_processed_key(src_val)] = [numrange.to_json() for numrange in merge_ranges(
                ranges, is_integer=target_column.is_integer, discard=True)]
        self.constraint_learned = True

    def _check_violations(
            self,
            payload: pd.DataFrame,
            result_df: pd.DataFrame):
        for src_val, ranges in self.content["ranges"].items():
            conditions = payload[self.columns[0]].astype(
                str) == src_val
            for numrange in ranges:
                lower_limit, upper_limit = get_limits_with_buffer(
                    numrange["min"], numrange["max"])
                conditions = conditions & ~payload[self.columns[1]].between(
                    lower_limit, upper_limit)
            result_df[self.id] = result_df[self.id] | conditions

    def to_json(self):
        return {
            "name": self.name.value,
            "id": self.id,
            "kind": self.kind.value,
            "columns": [self.source_column, self.target_column],
            "content": self.content
        }

    def from_json(self, json_obj):
        super().from_json(json_obj)
        self.source_column = self.content.get("source_column")
        self.target_column = self.content.get("target_column")
