# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from collections import OrderedDict

import numpy as np
import pandas as pd

from service.core.constraints.column import DataColumn
from service.core.constraints.constants import (ColumnType, ConstraintKind,
                                                ConstraintName)
from service.core.constraints.data_constraint import DataConstraint
from service.core.constraints.util import (get_best_distribution,
                                           is_distribution_outlier,
                                           remove_outliers)


class CategoricalNumericDistributionConstraint(DataConstraint):
    def __init__(self):
        super().__init__(ConstraintName.CAT_NUM_DISTRIBUTION_CONSTRAINT,
                         ConstraintKind.TWO_COLUMN)
        self.source_column = None
        self.target_column = None

    def learn_constraints(self, source_column: DataColumn, target_column: DataColumn, training_data: pd.DataFrame):
        self.source_column = source_column.name
        self.target_column = target_column.name

        self.columns = [self.source_column, self.target_column]
        self.content["source_column"] = self.source_column
        self.content["target_column"] = self.target_column

        # Dropping all categories that have counts less than 2% of the total rows
        value_counts = source_column.value_counts.drop(
            source_column.value_counts[source_column.value_counts < 0.02 * len(training_data)].index)

        distribution = {}

        for value in value_counts.index:
            data = training_data[training_data[self.source_column]
                                 == value][self.target_column]
            data = data.dropna()

            if not len(data):
                continue

            percentiles = np.percentile(data, [25, 50, 75])
            data = remove_outliers(data, percentiles)
            cat_distribution = get_best_distribution(data)

            if not cat_distribution:
                continue

            distribution[value] = cat_distribution
            self.constraint_learned = True

        self.content["distribution"] = distribution

    def _check_violations(self, payload: pd.DataFrame, result_df: pd.DataFrame):
        distribution = self.content.get("distribution", {})
        violations_found = False

        for key in distribution:
            tmp_key = key
            if np.issubdtype(payload[self.source_column].dtype, np.integer):
                tmp_key = int(key)
            elif np.issubdtype(payload[self.source_column].dtype, np.number):
                tmp_key = float(key)

            temp_df = payload[payload[self.source_column] == tmp_key].copy()
            if len(temp_df):
                conditions = temp_df[self.target_column].apply(
                    lambda x: is_distribution_outlier(x, distribution[key]))

                if sum(conditions):
                    outliers = temp_df.drop(temp_df[~conditions].index)
                    result_df.loc[result_df["scoring_id"].isin(
                        outliers["scoring_id"]), self.id] = 1
                    violations_found = True

        if violations_found:
            return self.get_violation_info("AIQDD9004E", self.columns)

        # No violations. Return empty dict
        return {}

    def to_json(self):
        return {
            "name": self.name.value,
            "id": self.id,
            "kind": self.kind.value,
            "columns": [self.source_column, self.target_column],
            "content": self.content
        }

    def from_json(self, json_obj, columns: OrderedDict = {}):
        super().from_json(json_obj)
        self.source_column = self.content.get("source_column")
        self.target_column = self.content.get("target_column")
