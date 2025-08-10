# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


from copy import deepcopy

import numpy as np
from ibm_wos_utils.drift.batch.util.constraint_utils import get_primitive_value


class Range:
    def __init__(self, bounds, count):
        self.min = bounds[0]
        self.max = bounds[1]
        self.count = count

    def has(self, value, threshold=1):
        return self.min - threshold <= value <= self.max + threshold

    def is_close_to(self, another_range, threshold=1):
        return not(
            (self.min > another_range.max +
             threshold) or (
                self.max +
                threshold < another_range.min))

    def merge(self, another_range):
        self.min = min(self.min, another_range.min)
        self.max = max(self.max, another_range.max)
        self.count = self.count + another_range.count
        return self

    def to_json(self):
        return {
            "min": get_primitive_value(self.min),
            "max": get_primitive_value(self.max),
            "count": self.count}

    def __str__(self):
        return str(self.to_json())

    def __repr__(self):
        return str(self.to_json())


def merge_ranges(ranges, buffer=0.1, discard=False, is_integer=False):
    if len(ranges) == 0:
        return ranges
    global_min = min(temp_range.min for temp_range in ranges)
    global_max = max(temp_range.max for temp_range in ranges)
    threshold = buffer * (global_max - global_min)
    if is_integer:
        threshold = int(np.ceil(threshold))

    result = []
    ranges_copy = sorted(ranges, key=lambda val: val.min)

    for interval in ranges_copy:
        if len(result) == 0 or not(
                result[-1].is_close_to(interval, threshold)):
            result.append(deepcopy(interval))
        else:
            result[-1].merge(interval)

    if discard:
        global_count = sum(temp_range.count for temp_range in ranges)
        result = [
            interval for interval in result if interval.count > 0.005 *
            global_count]
    return result
