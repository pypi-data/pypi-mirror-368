# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd

from service.core.constraints.constants import ColumnType
from service.core.constraints.util import remove_outliers, get_primitive_value


class DataColumn(object):
    def __init__(self, name: str, dtype: ColumnType):
        """
        Arguments:
            name {str} -- human readable constraint name without any whitespaces
            dtype {ColumnType} -- the data type of the column
        """
        self.name = name
        self.dtype = dtype
        self.sparse = False
        self.skip_learning = False

    def compute_stats(self, training_data: pd.DataFrame):
        self.count = len(training_data)

        if self.dtype in (ColumnType.NUMERIC_CONTINUOUS, ColumnType.NUMERIC_DISCRETE):
            self.set_numeric_stats(training_data)

        if self.dtype in (ColumnType.CATEGORICAL, ColumnType.NUMERIC_DISCRETE):
            column_data = training_data[self.name].dropna()
            self.value_counts = column_data.value_counts()

    def set_numeric_stats(self, training_data: pd.DataFrame):
        column_data = training_data[self.name].dropna()
        self.percentiles = column_data.quantile(
            q=[0.25, 0.5, 0.75]).values.tolist()
        self.sparse = all(elem == self.percentiles[0] for elem in self.percentiles)
        column_data = remove_outliers(column_data, self.percentiles)
        column_data.sort_values(inplace=True)
        self.min = get_primitive_value(np.min(column_data))
        self.max = get_primitive_value(np.max(column_data))
        self.mean = get_primitive_value(np.mean(column_data))
        self.std = get_primitive_value(np.std(column_data))

        # Storing the actual count after dropping NAs and outliers
        self.count_actual = len(column_data)
        # Updated the percentiles with reduced data
        self.percentiles = column_data.quantile(
            q=[0.25, 0.5, 0.75]).values.tolist()

    def to_json(self):
        column_json = {
            "name": self.name,
            "dtype": self.dtype.value,
            "count": self.count,
            "sparse": self.sparse,
            "skip_learning": self.skip_learning
        }
        if self.dtype in (ColumnType.NUMERIC_CONTINUOUS, ColumnType.NUMERIC_DISCRETE):
            column_json["min"] = self.min
            column_json["max"] = self.max
            column_json["mean"] = self.mean
            column_json["std"] = self.std
            column_json["percentiles"] = self.percentiles
            column_json["count_actual"] = self.count_actual

        return column_json

    def from_json(self, json_obj):
        self.count = json_obj.get("count")
        self.sparse = json_obj.get("sparse")
        self.skip_learning = json_obj.get("skip_learning")
        if self.skip_learning is None:
            self.skip_learning = False

        if self.dtype in (ColumnType.NUMERIC_CONTINUOUS, ColumnType.NUMERIC_DISCRETE):
            self.min = json_obj.get("min")
            self.max = json_obj.get("max")
            self.mean = json_obj.get("mean")
            self.std = json_obj.get("std")
            self.percentiles = json_obj.get("percentiles")
            self.count_actual = json_obj.get("count_actual")
            if self.sparse is None:
                self.sparse = all(elem == self.percentiles[0] for elem in self.percentiles)
