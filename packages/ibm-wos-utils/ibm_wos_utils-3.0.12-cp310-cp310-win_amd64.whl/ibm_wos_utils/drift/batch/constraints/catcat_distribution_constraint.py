# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


import numpy as np
import pandas as pd
from ibm_wos_utils.drift.batch.constraints.column import DataColumn
from ibm_wos_utils.drift.batch.constraints.data_constraint import \
    DataConstraint
from ibm_wos_utils.drift.batch.util.constants import (
    CATEGORY_PROPORTION_THRESHOLD, ConstraintKind, ConstraintName)


class CatCatDistributionConstraint(DataConstraint):
    """
        Class responsible to generate categorical - categorical constraint
    """

    def __init__(self):
        super().__init__(
            ConstraintName.CAT_CAT_DISTRIBUTION_CONSTRAINT,
            ConstraintKind.TWO_COLUMN)
        self.source_column = None
        self.target_column = None

    def learn_constraints(
            self,
            source_column: DataColumn,
            target_column: DataColumn,
            training_data,
            total_rows):
        """Learn constraints

        Spark Operations:
        1. For each categorical-categorical combination, it does:
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

        source_support = (source_column.value_counts / total_rows)
        source_support_values = source_support.values.reshape(
            (source_support.shape[0], 1))
        target_support = target_column.value_counts / total_rows
        target_support_values = target_support.values.reshape(
            (1, target_support.shape[0]))

        # Calculate expected counts for each source-value:target-value
        # combination in source-column:target-column
        expected_counts = pd.DataFrame(
            (np.multiply(
                source_support_values,
                target_support_values) *
                total_rows *
                CATEGORY_PROPORTION_THRESHOLD).astype(int),
            index=source_support.index,
            columns=target_support.index)

        # Calculate actual counts for each source-value:target-value combination in source-column:target-column
        # 1. Get actual counts using groupby
        actual_counts = training_data.groupBy(
            self.source_column, self.target_column).count()
        # 2. Sort the result and drop nulls
        actual_counts.sort(
            self.source_column,
            self.target_column).dropna(
            subset=[
                self.source_column,
                self.target_column])
        # 3. Convert to Pandas DataFrame and then Pivot Table for
        # better access
        actual_counts = actual_counts.toPandas().pivot_table(
            index=self.source_column,
            columns=self.target_column,
            values="count",
            fill_value=0)

        rare_combinations = []
        for source_value in expected_counts.index:
            target_values = expected_counts.loc[source_value][(expected_counts.loc[source_value] > 2) & (
                expected_counts.loc[source_value] < 0.02 * total_rows)]
            rare_target_values = []
            if len(target_values) > 0:
                rare_target_values = target_values[target_values >
                                                   actual_counts.loc[source_value].loc[target_values.index]].index.to_list()
            if len(rare_target_values) > 0:
                rare_combination = {
                    "source_value": source_value,
                    "target_values": rare_target_values
                }
                rare_combinations.append(rare_combination)
        if len(rare_combinations) > 0:
            self.constraint_learned = True
            self.content["rare_combinations"] = rare_combinations

    def _check_violations(
            self,
            payload: pd.DataFrame,
            result_df: pd.DataFrame):

        for combination in self.content["rare_combinations"]:
            result_df[self.id] = result_df[self.id] | ((payload[self.source_column] == combination["source_value"]) & (
                payload[self.target_column].isin(combination["target_values"])))

    def to_json(self):
        return {
            "name": self.name.value,
            "id": self.id,
            "kind": self.kind.value,
            "columns": self.columns,
            "content": self.content
        }

    def from_json(self, json_obj: dict):
        super().from_json(json_obj)
        self.source_column = self.content.get("source_column")
        self.target_column = self.content.get("target_column")
        self.rare_combinations = self.content.get("rare_combinations")
