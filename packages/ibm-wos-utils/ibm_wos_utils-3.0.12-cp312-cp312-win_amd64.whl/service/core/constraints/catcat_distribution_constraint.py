# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
from collections import OrderedDict

import pandas as pd

from service.core.constraints.column import DataColumn
from service.core.constraints.constants import ConstraintKind, ConstraintName
from service.core.constraints.data_constraint import DataConstraint

CATEGORY_PROPORTION_THRESHOLD = 0.1  # 1/10th of full training data


class CatCatDistributionConstraint(DataConstraint):
    """
        Class responsible to generate categorical - categorical constraint
    """

    def __init__(self):
        super().__init__(ConstraintName.CAT_CAT_DISTRIBUTION_CONSTRAINT, ConstraintKind.TWO_COLUMN)
        self.src_col_name = None
        self.trgt_col_name = None
        self.rare_combinations = OrderedDict()

    def __get_support(self, category_counts: dict, totals_rows: int):
        category_support = dict()
        for category, counts in category_counts.items():
            support = counts/totals_rows
            category_support[category] = support
        return category_support

    def __get_lift(self, src_col_support: dict, trgt_col_support: dict):
        association_lift = dict()
        for src_category, src_support in src_col_support.items():
            src_target_lift = {target_cat: (src_support * target_cat_support)
                               for target_cat, target_cat_support in trgt_col_support.items()}
            association_lift[src_category] = src_target_lift
        return association_lift

    def __get_expected_joint_counts(self, src_unique_counts: dict, trgt_unique_counts: dict, total_rows: int):
        expected_joint_count = dict()
        # 1. Get support for source and target categories
        src_col_support = self.__get_support(src_unique_counts, total_rows)
        target_col_support = self.__get_support(trgt_unique_counts, total_rows)

        # 2. Get lift for each source and target category combination
        src_trgt_associated_lift = self.__get_lift(
            src_col_support, target_col_support)

        # 3. Get expected row count for the unique combination of source category can target
        for src_category, trgt_lift in src_trgt_associated_lift.items():
            src_target_exp_joint_count = {target_cat: int(
                src_trgt_lift * CATEGORY_PROPORTION_THRESHOLD * total_rows) for target_cat, src_trgt_lift in trgt_lift.items()}
            expected_joint_count[src_category] = src_target_exp_joint_count
        return expected_joint_count

    def learn_constraints(self, source_column: DataColumn, target_column: DataColumn, training_data: pd.DataFrame):
        self.src_col_name = source_column.name
        self.trgt_col_name = target_column.name
        self.columns = [self.src_col_name, self.trgt_col_name]

        src_col_name = self.src_col_name
        trgt_col_name = self.trgt_col_name
        total_row_count = len(training_data)

        # Retain source/target column values
        src_col_values = training_data[src_col_name].dropna()
        trgt_col_values = training_data[trgt_col_name].dropna()

        # Get unique counts
        src_unique_counts = source_column.value_counts.sort_index().to_dict()
        trgt_unique_counts = target_column.value_counts.sort_index().to_dict()

        # Get the expected joint count
        expected_joint_count = self.__get_expected_joint_counts(
            src_unique_counts, trgt_unique_counts, total_row_count)

        # Group rows of the source column
        df = pd.DataFrame()
        df[src_col_name] = src_col_values
        df[trgt_col_name] = trgt_col_values
        src_grouped_df = df.groupby(src_col_name)

        # Set record count thresholds
        lower_threshold = 2
        # 2% of full training data
        upper_threshold = int(0.02 * total_row_count)

        #freq_dist = []
        self.rare_combinations = []
        for category, rows in src_grouped_df:
            category_details = dict()
            target_counts_per_category = rows[trgt_col_name].value_counts(
            ).to_dict()

            # Get source category expected joint count
            src_cat_expected_joint_count = expected_joint_count[category]

            # Check and add constraint
            target_values = []
            for trgt_cat, exp_count in src_cat_expected_joint_count.items():

                # Set the joint count to 0 as default that indicates that combination does not exist in training data
                joint_count_from_training_data = target_counts_per_category.get(
                    trgt_cat, 0)

                if exp_count > lower_threshold and exp_count < upper_threshold:
                    if joint_count_from_training_data < exp_count:
                        target_values.append(trgt_cat)

            # Check and add to main list
            if target_values is not None and len(target_values) != 0:
                category_details["source_value"] = category
                category_details["target_values"] = sorted(target_values)
                self.rare_combinations.append(category_details)

        if self.rare_combinations:
            self.constraint_learned = True
            self.content["source_column"] = self.src_col_name
            self.content["target_column"] = self.trgt_col_name
            self.content["rare_combinations"] = sorted(
                self.rare_combinations, key=lambda x: x["source_value"])

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
        self.src_col_name = self.content.get("source_column")
        self.trgt_col_name = self.content.get("target_column")
        self.rare_combinations = self.content.get("rare_combinations")

    def _check_violations(self, payload: pd.DataFrame, result_df: pd.DataFrame):
        violated_score_id_list = []
        for rare_pair in self.rare_combinations:
            src_value = rare_pair.get("source_value")
            for trgt_value in rare_pair.get("target_values"):
                # Find all the rare combinations in payload
                violated_score_id_list_per_trgt_value = payload[(payload[self.src_col_name] == src_value) & (
                    payload[self.trgt_col_name] == trgt_value)]["scoring_id"].copy()

                # Mark them as violated in the result_df
                if len(violated_score_id_list_per_trgt_value) > 0:
                    result_df.loc[result_df["scoring_id"].isin(
                        violated_score_id_list_per_trgt_value), self.id] = 1
                    violated_score_id_list.append(
                        violated_score_id_list_per_trgt_value)

        if len(violated_score_id_list) > 0:
            return self.get_violation_info("AIQDD9001E", self.columns)

        return {}
