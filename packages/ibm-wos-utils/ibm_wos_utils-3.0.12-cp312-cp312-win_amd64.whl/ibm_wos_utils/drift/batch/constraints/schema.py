# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import uuid

from ibm_wos_utils.drift.batch.constraints.entity import DataConstraintSet
from ibm_wos_utils.drift.batch.util.constants import (
    ConstraintName, DriftTableColumnType)


class TableColumn(object):
    def __init__(
            self,
            name: str,
            col_type: DriftTableColumnType = None,
            length: int = None,
            not_null: bool = False,
            unique: bool = False,
            default_value=None):
        self.name = name
        self.type = col_type
        self.length = length
        self.not_null = not_null
        self.unique = unique
        self.default_value = default_value

    def to_json(self):
        column_json = {
            "type": self.type.value,
            "not_null": self.not_null,
            "unique": self.unique
        }

        if self.length is not None:
            column_json["length"] = self.length

        if self.default_value is not None:
            column_json["default"] = self.default_value

        return {
            self.name: column_json
        }

    def from_json(self, json_obj):
        self.type = DriftTableColumnType(json_obj.get("type"))
        self.length = json_obj.get("length")
        self.not_null = json_obj.get("not_null")
        self.unique = json_obj.get("unique")
        self.default_value = json_obj.get("default")


class DriftedTransactionsSchema(object):

    def __init__(self, max_constraints_per_column: int = 1000000):
        """Init.

        Keyword Arguments:
            max_constraints_per_column {int} -- Maximum number of constraints per bitmap column (default: {1000000})
        """
        self.id = None
        self.max_constraints_per_column = max_constraints_per_column
        self.columns = []
        self.bitmap = {}
        self.categorical_distribution_columns = []
        self.numeric_range_columns = []
        self.catcat_distribution_columns = []
        self.catnum_range_columns = []

    def generate(self, record_id_column: str, record_timestamp_column: str = None, constraint_set: DataConstraintSet = None):
        self.id = constraint_set.id if constraint_set is not None else uuid.uuid4()

        self.columns.append(
            TableColumn(
                record_id_column,
                DriftTableColumnType.STRING,
                length=64,
                not_null=True,
                unique=True))
        if record_timestamp_column:
            self.columns.append(
                TableColumn(
                    record_timestamp_column,
                    DriftTableColumnType.TIMESTAMP,
                    not_null=True))

        self.columns.append(
            TableColumn(
                "constraints_generation_id",
                DriftTableColumnType.STRING,
                length=40,
                not_null=True))

        self.columns.append(
            TableColumn(
                "run_id",
                DriftTableColumnType.STRING,
                length=40,
                not_null=True))

        self.columns.append(
            TableColumn(
                "is_model_drift",
                DriftTableColumnType.BOOLEAN,
                not_null=True,
                default_value=False))
        self.columns.append(
            TableColumn(
                "drift_model_confidence",
                DriftTableColumnType.FLOAT))

        self.columns.append(
            TableColumn(
                "is_data_drift",
                DriftTableColumnType.BOOLEAN,
                not_null=True,
                default_value=False))

        self.set_categorical_distribution_constraints(constraint_set)
        self.set_numeric_range_constraints(constraint_set)
        self.set_catcat_distribution_constraints(constraint_set)
        self.set_catnum_range_constraints(constraint_set)

    def __set_constraints_helper(
            self,
            constraint_name: ConstraintName,
            constraints: dict):
        """Does the following:
        1. Adds constraint type columns to drifted transactions schema
        2. Adds the bitmap information - Constraint Type columns to Constraint ID mappings.

        Arguments:
            constraint_name {ConstraintName} -- Name of constraint
            constraints {dict} -- All the constraints with above name
        """
        count = len(constraints)

        is_multiple = count > self.max_constraints_per_column
        names = []

        if not is_multiple:
            column = TableColumn(
                constraint_name.value,
                DriftTableColumnType.STRING,
                length=self.max_constraints_per_column)
            self.columns.append(column)
            names = [column.name]
        else:
            index = 0
            while count > 0:
                column = TableColumn(
                    "{}_{:03d}".format(
                        constraint_name.value,
                        index),
                    DriftTableColumnType.STRING,
                    length=self.max_constraints_per_column)
                self.columns.append(column)
                names.append(column.name)
                index += 1
                count -= self.max_constraints_per_column

        constraint_ids = list(constraints.keys())

        if len(constraint_ids) > 0:
            # Add a sliced chunk (of length self.max_constraints_per_column) with
            # bitmap column name generated above
            from more_itertools import sliced
            self.bitmap.update(
                dict(zip(names, sliced(constraint_ids, self.max_constraints_per_column))))
        else:
            self.bitmap.update({constraint_name.value: []})

    def set_categorical_distribution_constraints(
            self, constraint_set: DataConstraintSet):
        constraints = constraint_set.get_categorical_distribution_constraints(
        ) if constraint_set is not None else {}
        self.__set_constraints_helper(
            ConstraintName.CATEGORICAL_DISTRIBUTION_CONSTRAINT, constraints)

    def set_numeric_range_constraints(self, constraint_set: DataConstraintSet):
        constraints = constraint_set.get_numeric_range_constraints(
        ) if constraint_set is not None else {}
        self.__set_constraints_helper(
            ConstraintName.NUMERIC_RANGE_CONSTRAINT, constraints)

    def set_catcat_distribution_constraints(
            self, constraint_set: DataConstraintSet):
        constraints = constraint_set.get_catcat_distribution_constraints(
        ) if constraint_set is not None else {}
        self.__set_constraints_helper(
            ConstraintName.CAT_CAT_DISTRIBUTION_CONSTRAINT, constraints)

    def set_catnum_range_constraints(self, constraint_set: DataConstraintSet):
        constraints = constraint_set.get_catnum_range_constraints(
        ) if constraint_set is not None else {}
        self.__set_constraints_helper(
            ConstraintName.CAT_NUM_RANGE_CONSTRAINT, constraints)

    def to_json(self):
        columns_json = {}
        for column in self.columns:
            columns_json.update(column.to_json())

        schema_json = {
            "id": str(self.id),
            "columns": columns_json
        }

        schema_json["bitmap"] = self.bitmap

        return schema_json

    def from_json(self, json_obj):
        self.id = json_obj.get("id")

        for name, column_json in json_obj.get("columns").items():
            column = TableColumn(name)
            column.from_json(column_json)
            self.columns.append(column)

        self.bitmap = json_obj.get("bitmap")
