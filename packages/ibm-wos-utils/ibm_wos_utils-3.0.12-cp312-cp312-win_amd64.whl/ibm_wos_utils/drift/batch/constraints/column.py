# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


import logging

import numpy as np
from ibm_wos_utils.drift.batch.util.constants import ColumnType
from ibm_wos_utils.drift.batch.util.constraint_utils import (
    get_primitive_value, get_tail_thresholds)

logger = logging.getLogger(__name__)

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
        self.summary = None
        self.splits = []
        self.is_integer = False
        self.count = 0
        self.approx_count_distinct = 0
        self.is_tails_discarded = False
        self.tail_thresholds = None
        self.skip_learning_reason = None

    def compute_stats(
            self,
            training_data,
            total_rows: int,
            max_bins_for_range_constraint: int,
            tail_discard_threshold: float = 0.01):
        """Computes statistics for columns

        Spark Operations:
        1. For categorical + discrete columns, this does:
            - Frequency counts
            - Drops null in resulting dataframe
            - Sorts the resulting dataframe based on categories.

        Arguments:
            training_data {pyspark.sql.dataframe.DataFrame} -- Training Data
            total_rows {int} -- Total rows in the training data
        """
        if self.skip_learning:
            self.count = total_rows
            return

        if self.dtype in (
                ColumnType.CATEGORICAL,
                ColumnType.NUMERIC_DISCRETE):
            # Get value counts for the column as pandas Series
            self.value_counts = training_data.groupBy(self.name)\
                .count().dropna().sort(self.name)\
                .withColumnRenamed("count", "frequency")\
                .toPandas().set_index(self.name)["frequency"]
            self.count = int(self.value_counts.sum())
        else:
            self.is_integer = "int" in dict(
                training_data.dtypes)[self.name]
            self.set_numeric_stats(max_bins_for_range_constraint, tail_discard_threshold)

    def set_numeric_stats(self,
            max_bins_for_range_constraint: int,
            tail_discard_threshold: float
    ):
        self.count = int(self.summary["count"])
        self.min = self.summary["min"]
        self.max = self.summary["max"]
        self.mean = self.summary["mean"]
        self.std = self.summary["stddev"]
        self.percentiles = [
            self.summary["25%"],
            self.summary["50%"],
            self.summary["75%"]]
        self.sparse = bool(self.summary["25%"] == self.summary["75%"])
        self.tail_thresholds = { threshold: self.summary[threshold] 
                                    for threshold in get_tail_thresholds(tail_discard_threshold) }

        if self.sparse:
            self.skip_learning = True
            self.skip_learning_reason = "Sparse data. 25th and 75th percentiles are same."
            logger.info("{} is sparse. Skipping learning.".format(self.name))
            logger.info(self.skip_learning_reason)
            return

        if self.skip_learning:
            return

        minimum = self.summary["min"]
        maximum = self.summary["max"]
        bins = int(np.ceil(self.summary["bins"]))
        logger.info("For column {}: bins = {}, min = {}, max = {}".format(
            self.name, bins, minimum, maximum))

        if bins > max_bins_for_range_constraint:
            logger.info("Discarding tails for column {} since {} bins > {} limit".format(self.name, bins, max_bins_for_range_constraint))
            minimum = self.summary[get_tail_thresholds(tail_discard_threshold)[0]]
            maximum = self.summary[get_tail_thresholds(tail_discard_threshold)[1]]

            bins = int(np.ceil((maximum - minimum) / self.summary["bin_width"]))
            logger.info("For column {}: bins = {}, min = {}, max = {}".format(
                self.name, bins, minimum, maximum))

            if bins > max_bins_for_range_constraint:
                self.skip_learning = True
                self.skip_learning_reason = "Total bins[{}] are more than the specified limit[{}] even after discarding off tails. ".format(bins, max_bins_for_range_constraint)
                self.skip_learning_reason += "Please consider changing the tail_discard_threshold parameter."

                logger.info(self.skip_learning_reason)
                logger.info("Not able to reduce bins for column {}. Skipped learning.".format(self.name))
                return
            
            self.is_tails_discarded = True

        if self.is_integer:
            self.bin_width = np.ceil(
                self.summary.loc["bin_width"]).astype(int)
            self.splits = np.arange(
                start=minimum,
                stop=maximum +
                self.bin_width,
                step=self.bin_width,
                dtype=int)
        else:
            self.splits, self.bin_width = np.linspace(
                minimum, maximum, bins, retstep=True)

        if self.is_tails_discarded:
            # Add the minimum and maximum values to the splits
            # because Bucketizer needs absolute bounds on data
            self.splits = self.splits.tolist()
            if self.splits[0] != self.min:
                self.splits = [self.min] + self.splits
            if self.splits[-1] != self.max:
                self.splits = self.splits + [self.max]

    def to_json(self):
        column_json = {
            "name": self.name,
            "dtype": self.dtype.value,
            "count": get_primitive_value(
                self.count),
            "approx_count_distinct": get_primitive_value(
                self.approx_count_distinct),
            "sparse": self.sparse,
            "skip_learning": self.skip_learning
        }
        if (not self.skip_learning) and (
                self.dtype is ColumnType.NUMERIC_CONTINUOUS):
            column_json["min"] = get_primitive_value(self.min)
            column_json["max"] = get_primitive_value(self.max)
            column_json["mean"] = get_primitive_value(self.mean)
            column_json["std"] = get_primitive_value(self.std)
            column_json["percentiles"] = list(
                map(get_primitive_value, self.percentiles))
            if (not self.sparse):
                column_json["bin_width"] = get_primitive_value(self.bin_width)

            column_json["is_tails_discarded"] = self.is_tails_discarded
            column_json["tail_thresholds"] = self.tail_thresholds

        if self.skip_learning_reason is not None:
            column_json["skip_learning_reason"] = self.skip_learning_reason
        return column_json

    def from_json(self, json_obj):
        self.count = json_obj.get("count")
        self.sparse = json_obj.get("sparse")
        self.skip_learning = json_obj.get("skip_learning")

        if self.dtype in (
                ColumnType.NUMERIC_CONTINUOUS,
                ColumnType.NUMERIC_DISCRETE):
            self.min = json_obj.get("min")
            self.max = json_obj.get("max")
            self.mean = json_obj.get("mean")
            self.std = json_obj.get("std")
            self.percentiles = json_obj.get("percentiles")
            self.count_actual = json_obj.get("count_actual")

        if "bin_width" in json_obj:
            self.bin_width = json_obj.get("bin_width")

        if "tail_thresholds" in json_obj:
            self.tail_thresholds = json_obj.get("tail_thresholds")
        
        self.is_tails_discarded = False
        if "is_tails_discarded" in json_obj:
            self.is_tails_discarded = json_obj.get("is_tails_discarded")

        self.skip_learning_reason = json_obj.get("skip_learning_reason")
