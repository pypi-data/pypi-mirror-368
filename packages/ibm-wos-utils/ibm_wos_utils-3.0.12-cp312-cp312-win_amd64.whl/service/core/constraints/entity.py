# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from collections import OrderedDict

from service.core.constraints.catcat_distribution_constraint import \
    CatCatDistributionConstraint
from service.core.constraints.categorical_distribution_constraint import \
    CategoricalDistributionConstraint
from service.core.constraints.catnum_distribution_constraint import \
    CategoricalNumericDistributionConstraint
from service.core.constraints.catnum_range_constraint import \
    CategoricalNumericRangeConstraint
from service.core.constraints.column import DataColumn
from service.core.constraints.constants import (ColumnType, ConstraintKind,
                                                ConstraintName)
from service.core.constraints.data_constraint import DataConstraint
from service.core.constraints.numeric_distribution_constraint import \
    NumericDistributionConstraint
from service.core.constraints.numeric_range_constraint import \
    NumericRangeConstraint


class DataConstraintSet(object):
    """
    This holds all statistical data constraints of a structured dataset.
    The constraints are instances of DataConstraint.
    It also holds information of all the columns in the dataset.
    """

    def __init__(self):
        self.version = "0.04"
        self.columns = OrderedDict()
        self.constraints = OrderedDict()

    def add_ctr(self, ct):
        """Adds a constraint to the constraint-set

        Arguments:
            ct {DataConstraint} -- the inferred constraint object. Constraint
            insertion order is remembered.
        """
        if ct.constraint_learned:
            self.constraints[ct.id] = ct

    def del_ctr(self, id):
        """Deletes a constraint from the constraint-set

        Arguments:
            id {str} -- the id of the constraint to be deleted
        """
        del self.constraints[id]

    def add_cl(self, cl):
        """Adds column information to constraint-set

        Arguments:
            cl {DataColumn} -- column information of a structured dataset. Column
            insertion order is remembered.
        """
        self.columns[cl.name] = cl

    def del_cl(self, name):
        """Deletes  column information to constraint-set

        Arguments:
            name {str} -- the name of the column to be deleted
        """
        del self.columns[name]

    def single_column_constraints(self):
        """Convenience method to query all the single column constraints in the constraint-set

        Returns:
            list -- All the single column constraints in the constraint-set
        """
        return [constraint for constraint in self.constraints.values() if constraint.kind is ConstraintKind.SINGLE_COLUMN]

    def two_column_constraints(self):
        """Convenience method to query all the two column constraints in the constraint-set

        Returns:
            list -- All the two column constraints in the constraint-set
        """
        return [constraint for constraint in self.constraints.values() if constraint.kind is ConstraintKind.TWO_COLUMN]

    def to_json(self):
        # serialize using json dumps

        return {
            "version": self.version,
            "columns": [column.to_json() for column in self.columns.values()],
            "constraints": [constraint.to_json() for constraint in self.constraints.values() if constraint.to_json() is not None]
        }

    def from_json(self, json_obj):
        self.version = json_obj.get("version")

        # Retain column information
        for column_json in json_obj.get("columns", []):
            column = DataColumn(column_json.get("name"),
                                ColumnType(column_json.get("dtype")))
            column.from_json(column_json)
            self.add_cl(column)

        # Retain single and two column constraint information
        for constraint_json in json_obj.get("constraints", []):
            constraint = None
            constraint_name = ConstraintName(constraint_json.get('name'))
            if constraint_name is ConstraintName.NUMERIC_DISTRIBUTION_CONSTRAINT:
                constraint = NumericDistributionConstraint()
            elif constraint_name is ConstraintName.NUMERIC_RANGE_CONSTRAINT:
                constraint = NumericRangeConstraint()
            elif constraint_name is ConstraintName.CATEGORICAL_DISTRIBUTION_CONSTRAINT:
                constraint = CategoricalDistributionConstraint()
            elif constraint_name is ConstraintName.CAT_CAT_DISTRIBUTION_CONSTRAINT:
                constraint = CatCatDistributionConstraint()
            elif constraint_name is ConstraintName.CAT_NUM_DISTRIBUTION_CONSTRAINT:
                constraint = CategoricalNumericDistributionConstraint()
            elif constraint_name is ConstraintName.CAT_NUM_RANGE_CONSTRAINT:
                constraint = CategoricalNumericRangeConstraint()

            if constraint is not None:
                constraint.from_json(constraint_json)
                self.add_ctr(constraint)
