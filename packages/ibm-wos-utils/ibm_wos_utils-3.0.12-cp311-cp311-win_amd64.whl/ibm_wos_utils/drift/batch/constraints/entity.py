# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import uuid
from collections import OrderedDict

from ibm_wos_utils.drift.batch.constraints.catcat_distribution_constraint import \
    CatCatDistributionConstraint
from ibm_wos_utils.drift.batch.constraints.categorical_distribution_constraint import \
    CategoricalDistributionConstraint
from ibm_wos_utils.drift.batch.constraints.catnum_range_constraint import \
    CategoricalNumericRangeConstraint
from ibm_wos_utils.drift.batch.constraints.column import DataColumn
from ibm_wos_utils.drift.batch.constraints.numeric_range_constraint import \
    NumericRangeConstraint
from ibm_wos_utils.drift.batch.util.constants import (
    ColumnType, ConstraintKind, ConstraintName)


class DataConstraintSet(object):
    """
    This holds all statistical data constraints of a structured dataset.
    The constraints are instances of DataConstraint.
    It also holds information of all the columns in the dataset.
    """

    def __init__(self):
        self.id = uuid.uuid4()
        
        self.version = "0.02_batch"
        
        # Version History

        # 0.02_batch: Change learner logic to discard off tails; Add two drift parameters
        # 0.01_batch: Initial version

        self.columns = OrderedDict()
        self.constraints = OrderedDict()
        self.summary_stats = None
        self.user_inputs = {}

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
            dict -- All the single column constraints in the constraint-set
        """
        return {cid: constraint for cid, constraint in self.constraints.items()
                if constraint.kind is ConstraintKind.SINGLE_COLUMN}

    def two_column_constraints(self):
        """Convenience method to query all the two column constraints in the constraint-set

        Returns:
            dict -- All the two column constraints in the constraint-set
        """
        return {cid: constraint for cid, constraint in self.constraints.items()
                if constraint.kind is ConstraintKind.TWO_COLUMN}

    def get_categorical_distribution_constraints(self):
        """Convenience method to query all the categorical distribution constraints in the constraint-set

        Returns:
            dict -- All the categorical distribution constraints in the constraint-set
        """
        return {cid: constraint for cid, constraint in self.constraints.items(
        ) if constraint.name is ConstraintName.CATEGORICAL_DISTRIBUTION_CONSTRAINT}

    def get_numeric_range_constraints(self):
        """Convenience method to query all the numeric range constraints in the constraint-set

        Returns:
            dict -- All the numeric range constraints in the constraint-set
        """
        return {cid: constraint for cid, constraint in self.constraints.items()
                if constraint.name is ConstraintName.NUMERIC_RANGE_CONSTRAINT}

    def get_catcat_distribution_constraints(self):
        """Convenience method to query all the catcat distribution constraints in the constraint-set

        Returns:
            dict -- All the catcat distribution constraints in the constraint-set
        """
        return {cid: constraint for cid, constraint in self.constraints.items(
        ) if constraint.name is ConstraintName.CAT_CAT_DISTRIBUTION_CONSTRAINT}

    def get_catnum_range_constraints(self):
        """Convenience method to query all the catnum range constraints in the constraint-set

        Returns:
            dict -- All the catnum range constraints in the constraint-set
        """
        return {cid: constraint for cid, constraint in self.constraints.items()
                if constraint.name is ConstraintName.CAT_NUM_RANGE_CONSTRAINT}

    def get_constraints_for_column(self, column):
        return {
            cid: constraint for cid,
            constraint in self.constraints.items() if column.lower() in map(
                lambda x: x.lower(),
                constraint.columns)}

    def get_constraints_for_name(self, name: ConstraintName):
        if name == ConstraintName.CATEGORICAL_DISTRIBUTION_CONSTRAINT:
            return self.get_categorical_distribution_constraints()

        if name == ConstraintName.NUMERIC_RANGE_CONSTRAINT:
            return self.get_numeric_range_constraints()

        if name == ConstraintName.CAT_NUM_RANGE_CONSTRAINT:
            return self.get_catnum_range_constraints()

        if name == ConstraintName.CAT_CAT_DISTRIBUTION_CONSTRAINT:
            return self.get_catcat_distribution_constraints()

    def to_json(self):
        # serialize using json dumps
        ctr_set_json = {
            "id": str(self.id),
            "version": self.version,
            "columns": [column.to_json() for column in self.columns.values()],
            "constraints": [
                constraint.to_json() for constraint in self.constraints.values() if constraint.to_json() is not None],
            "user_inputs": self.user_inputs
        }

        return ctr_set_json

    def from_json(self, json_obj):
        if not json_obj.get("version", "").endswith("batch"):
            raise Exception(
                "This version of constraints json - {} - is not supported.".format(json_obj.get("version")))

        self.id = json_obj.get("id")
        self.version = json_obj.get("version")
        self.user_inputs = json_obj.get("user_inputs", {})

        # Retain column information
        for column_json in json_obj.get("columns", []):
            column = DataColumn(column_json.get("name"),
                                ColumnType(column_json.get("dtype")))
            column.from_json(column_json)
            self.add_cl(column)

        # Retain single and two column constraint information
        for constraint_json in json_obj.get("constraints", []):
            constraint = None
            constraint_name = ConstraintName(
                constraint_json.get('name'))
            if constraint_name is ConstraintName.NUMERIC_RANGE_CONSTRAINT:
                constraint = NumericRangeConstraint()
            elif constraint_name is ConstraintName.CATEGORICAL_DISTRIBUTION_CONSTRAINT:
                constraint = CategoricalDistributionConstraint()
            elif constraint_name is ConstraintName.CAT_CAT_DISTRIBUTION_CONSTRAINT:
                constraint = CatCatDistributionConstraint()
            elif constraint_name is ConstraintName.CAT_NUM_RANGE_CONSTRAINT:
                constraint = CategoricalNumericRangeConstraint()

            if constraint is not None:
                constraint.from_json(constraint_json)
                self.add_ctr(constraint)
