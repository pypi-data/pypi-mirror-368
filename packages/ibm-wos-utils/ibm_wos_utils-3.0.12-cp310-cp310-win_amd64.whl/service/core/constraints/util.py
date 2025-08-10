# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import warnings
from typing import List, Optional

import numpy as np
import pandas as pd
import scipy.stats as st
from service.core.constraints.constants import RANGE_BUFFER_CONSTANT


def get_distribution_params(distribution):
    """Gets distribution specific parameters

    Arguments:
        distribution {scipy distribution} -- distribution

    Returns:
        list -- list of parameters
    """
    if getattr(distribution, "shapes"):
        parameters = [name.strip() for name in distribution.shapes.split(",")]
    else:
        parameters = []
    if distribution.name in st._discrete_distns._distn_names:
        parameters += ["loc"]
    elif distribution.name in st._continuous_distns._distn_names:
        parameters += ["loc", "scale"]
    return parameters


def remove_outliers(column, percentiles):
    """Removes outliers from a column based on distribution

    Arguments:
        column {pd.Series} -- column to remove outliers from
        percentiles {list} -- A list of 25th, 50th and 75th percentiles of the column

    Returns:
        pd.Series -- A copy of column with outliers removed.
    """
    new_column = column.copy()
    iqr = percentiles[-1] - percentiles[0]
    # TODO Figure out what to do when iqr = 0
    lower_bound = percentiles[0] - iqr * 1.5
    upper_bound = percentiles[-1] + iqr * 1.5
    new_column.drop(new_column[(new_column < lower_bound) | (
        new_column > upper_bound)].index, inplace=True)
    return new_column


def get_best_distribution(column):
    DISTRIBUTIONS = [
        st.uniform, st.expon, st.norm
    ]

    best_dist = {}

    best_p = 0.0
    dist_found = False
    for dist in DISTRIBUTIONS:
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                params = dist.fit(column)
                D, p = st.kstest(column, dist.name, args=params)
                if p > best_p and p > 0.05:
                    best_distribution = dist
                    best_params = params
                    best_p = p
                    dist_found = True
        except Exception as ex:
            print(ex)
            # TODO Do something
            pass

    if dist_found:
        best_param_names = get_distribution_params(best_distribution)
        best_dist["name"] = best_distribution.name
        best_dist["parameters"] = dict(zip(best_param_names, best_params))
        best_dist["p-value"] = best_p
        return best_dist

    return None


def get_min_max_buffer(col_min, col_max):
    buffer = RANGE_BUFFER_CONSTANT * (col_max - col_min)

    # If both col_min and col_max are integers, bump up the buffer to the next integer
    if np.issubdtype(type(col_min), np.integer) and np.issubdtype(type(col_max), np.integer):
        buffer = np.ceil(buffer).astype(int)

    return buffer


def is_min_max_outlier(value, col_min, col_max):
    buffer = get_min_max_buffer(col_min, col_max)
    # TODO Figure out what to do when buffer = 0
    return (value < col_min - buffer) or (value > col_max + buffer)


def is_uniform_outlier(value, loc, scale):
    return (value < loc) or (value > loc + scale)


def is_norm_outlier(value, loc, scale):
    return (value < (loc - 6 * scale)) or (value > (loc + 6 * scale))


def is_beta_outlier(value, loc, scale):
    return (value < loc) or (value > loc + scale)


def is_expon_outlier(value, loc, scale):
    return (value < (loc - 0.1 * scale)) or (value > (loc + 9.21 * scale))


def is_categorical_outlier(value, frequency_distribution: dict):
    return str(value) not in map(str, frequency_distribution.keys())


def is_distribution_outlier(value, distribution: dict):
    """
    Outlier detection logic
        | Distribution     |    Parameters        |              Non-Outlier Range                 |
        |:------------:    |:----------------:    |:------------------------------------------:    |
        |    Normal        |     loc, scale       |  loc - 6 * scale <= range <= loc + 6 * scale   |
        |    Uniform       |     loc, scale       |         loc <= range <= loc + scale            |
        |     Beta         | loc, scale, a, b     |          loc <= range <= loc + scale           |
        |  Exponential     |    loc, scale        |loc - 0.1 * scale <= range <= loc + 9.21 * scale|
    """

    name = distribution.get("name")
    parameters = distribution.get("parameters", {})

    if name == "beta":
        # We are ignoring violations for beta distribution currently.
        # Check https://github.ibm.com/aiopenscale/tracker/issues/13788 for details
        return False
        # return is_beta_outlier(
        #     value, loc=parameters["loc"], scale=parameters["scale"])

    if name == "expon":
        return is_expon_outlier(
            value, loc=parameters["loc"], scale=parameters["scale"])

    if name == "norm":
        return is_norm_outlier(
            value, loc=parameters["loc"], scale=parameters["scale"])

    if name == "uniform":
        return is_uniform_outlier(
            value, loc=parameters["loc"], scale=parameters["scale"])

    raise Exception("Unknown distribution {} encountered".format(name))


def get_numeric_ranges(data: pd.Series, buffer=0.1):
    """Gets numeric ranges in a list of values. Drops any ranges that contain less than 0.5% of total rows

    Arguments:
        data {pd.Series} -- Data to find ranges on
        buffer {float} -- A buffer between two adjacent ranges. Specified as a percentage of difference between maximum and minimum values in data

    Returns:
        [list of dict] -- A list of dictionaries with `min`, `max` and `count` in each range
    """
    new_data = data.dropna()
    new_data = new_data.sort_values().values

    threshold = buffer * (new_data[-1] - new_data[0])
    if issubclass(new_data.dtype.type, np.integer):
        # IF the dtype is integer, keep the threshold atleast 1
        threshold = np.ceil(threshold)
    ndiff = np.diff(new_data)
    ndiff = np.insert(ndiff, 0, 0)
    result = np.split(new_data, np.nonzero(ndiff > threshold)[0])
    ranges = [{"min": get_primitive_value(np.min(val)), "max": get_primitive_value(np.max(val)), "count": len(
        val)} for val in result if len(val) > 0.005 * len(new_data)]
    return ranges


def get_primitive_value(num):
    """Get the python numeric primitive value from numpy/python numeric values"""
    if type(num) in (int, float):
        return num

    return num.item()


def check_user_override(
        column_names: list, constraint_kind: str, user_overrides: Optional[List] = []):

    learn_distribution_constraint = True
    learn_range_constraint = True

    if not user_overrides:
        return learn_distribution_constraint, learn_range_constraint

    column_names = [x.upper() for x in column_names]
    input_constraint_kind = "single" if constraint_kind == "single_column" else "double"

    # iterate over configs provided by user and check if given input is one of them
    for config in user_overrides:
        # find the config user has overridden and return distribution and range constraint overrides if any
        config_constraint_kind = config.get("constraint_type")
        if config_constraint_kind != input_constraint_kind:
            continue

        config_features = config.get("features")

        if config_constraint_kind == "single":
            # convert all features to upper-case
            config_features = [x.upper() for x in config_features]

            # check if given column name is part of this config's features
            if set(column_names).issubset(set(config_features)):
                # found config
                # return values for "learn_distribution_constraint" and "learn_range_constraint"
                learn_distribution_constraint = config.get(
                    "learn_distribution_constraint")
                learn_range_constraint = config.get("learn_range_constraint")
                break

        if config_constraint_kind == "double":
            # sort input column names
            column_names.sort()

            # iterate over this config's feature pairs and identify if given input column(s) are part of it.
            for feature_pair in config_features:
                feature_pair = [x.upper() for x in feature_pair]
                feature_pair.sort()

                if len(feature_pair) == 1:
                    # single value means override is applicable to all constraints where this column is present
                    if set(feature_pair).issubset(set(column_names)):
                        learn_distribution_constraint = config.get(
                            "learn_distribution_constraint")
                        learn_range_constraint = config.get(
                            "learn_range_constraint")
                        break

                if column_names == feature_pair:
                    # found config
                    # return values for "learn_distribution_constraint" and "learn_range_constraint"
                    learn_distribution_constraint = config.get(
                        "learn_distribution_constraint")
                    learn_range_constraint = config.get(
                        "learn_range_constraint")
                    break

    learn_distribution_constraint = True \
        if learn_distribution_constraint is None or learn_distribution_constraint == True else False
    learn_range_constraint = True \
        if learn_range_constraint is None or learn_range_constraint == True else False

    return learn_distribution_constraint, learn_range_constraint
