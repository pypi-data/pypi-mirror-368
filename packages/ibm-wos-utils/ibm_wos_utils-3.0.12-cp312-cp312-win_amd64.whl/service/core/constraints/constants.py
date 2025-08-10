# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from enum import Enum

RANGE_BUFFER_CONSTANT = 0.05


class ConstraintKind(Enum):
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "two_column"


class ColumnType(Enum):
    NUMERIC_DISCRETE = "numeric_discrete"
    NUMERIC_CONTINUOUS = "numeric_continuous"
    CATEGORICAL = "categorical"


class ConstraintName(Enum):
    NUMERIC_DISTRIBUTION_CONSTRAINT = "numeric_distribution_constraint"
    NUMERIC_RANGE_CONSTRAINT = "numeric_range_constraint"
    CATEGORICAL_DISTRIBUTION_CONSTRAINT = "categorical_distribution_constraint"
    CAT_CAT_DISTRIBUTION_CONSTRAINT = "catcat_distribution_constraint"
    CAT_NUM_DISTRIBUTION_CONSTRAINT = "catnum_distribution_constraint"
    CAT_NUM_RANGE_CONSTRAINT = "catnum_range_constraint"
