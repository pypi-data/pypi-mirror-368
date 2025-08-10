# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2022
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import datetime
import json
import logging
import pandas as pd

from ibm_wos_utils.drift.batch.constraints.catcat_distribution_constraint import \
    CatCatDistributionConstraint
from ibm_wos_utils.drift.batch.constraints.categorical_distribution_constraint import \
    CategoricalDistributionConstraint
from ibm_wos_utils.drift.batch.constraints.catnum_range_constraint import \
    CategoricalNumericRangeConstraint
from ibm_wos_utils.drift.batch.constraints.custom_range import Range
from ibm_wos_utils.drift.batch.constraints.numeric_range_constraint import \
    NumericRangeConstraint

from ibm_wos_utils.drift.batch.util.constraint_utils import get_constraint_id, get_processed_key

logger = logging.getLogger(__name__)

class UnifiedConstraintLearner():

    def __init__(
        self,
        columns,
        bucket_columns,
        buckets,
        categorical_columns,
        categorical_categories,
        numerical_range_columns,
        catcat_distribution_columns) -> None:

        self.columns = columns
        self.bucket_columns = bucket_columns
        self.buckets = buckets

        self.cat_columns = categorical_columns
        self.categorical_categories = categorical_categories

        self.num_range_columns = numerical_range_columns
        self.catcat_distribution_columns = catcat_distribution_columns

    def __call__(self, data):
        logger.info("We are in partition function")
        from more_itertools import ichunked
        chunks = ichunked(data, 10000)

        result = []
        logger.debug("Columns: {}".format(self.columns))

        for chunk in chunks:
            training_data_df = pd.DataFrame(chunk, columns=self.columns)
            logger.info(len(training_data_df))

            logger.info(
                "Numeric Range Constraints: Start, {}.".format(
                    datetime.datetime.now().isoformat()))
            for column in self.bucket_columns:
                ranges_df = training_data_df.groupby(column).size().reset_index(name="counts")
                result.append({
                    "numeric_range_constraint": ranges_df.to_json(orient="records")
                })
            logger.info(
                "Numeric Range Constraints: Complete, {}.".format(
                    datetime.datetime.now().isoformat()))

            logger.info(
                "Categorical-Numeric Range Constraints: Start, {}.".format(
                    datetime.datetime.now().isoformat()))
            for column in self.cat_columns:
                if len(self.categorical_categories[column]) == 0:
                    continue

                unique_values = training_data_df[column].unique().tolist()
                for num_column in self.num_range_columns:
                    content = {}
                    content["source_column"] = column
                    content["ranges"] = {}
                    content["target_column"] = num_column.name

                    bucket_col = "{}_buckets".format(num_column.name)
                    if bucket_col not in self.bucket_columns:
                        logger.debug("{} not found in {}".format(bucket_col, self.bucket_columns))
                        continue

                    for value in unique_values:
                        if value not in self.categorical_categories[column]:
                            continue

                        ranges_df = training_data_df.groupby([column, bucket_col]).size().reset_index(name="count")

                        is_num_column_int = "int" in str(training_data_df[num_column.name].dtypes)
                        num_buckets = self.buckets[num_column.name]

                        ranges = ranges_df[ranges_df[column] == value].apply(lambda row: Range(
                            bounds=num_buckets[int(row[bucket_col])], count=int(row["count"])), axis=1).to_list()
                        content["is_integer"] = is_num_column_int
                        content["ranges"][str(value)] = [numrange.to_json() for numrange in ranges]

                    result.append({
                        "catnum_range_constraint": content
                    })
            logger.info(
                "Categorical-Numeric Range Constraints: Complete, {}.".format(
                    datetime.datetime.now().isoformat()))

            logger.info(
                "Categorical-Categorical Distribution Constraints: Start, {}.".format(
                    datetime.datetime.now().isoformat()))
            for idx, (src_col, tgt_col) in enumerate(self.catcat_distribution_columns):
                # Retain source/target column values
                src_col_values = training_data_df[src_col].dropna()
                trgt_col_values = training_data_df[tgt_col].dropna()

                # Get unique counts
                src_unique_counts = training_data_df[src_col].value_counts().sort_index().to_dict()
                trgt_unique_counts = training_data_df[tgt_col].value_counts().sort_index().to_dict()

                # Group rows of the source column
                df = pd.DataFrame()
                df[src_col] = src_col_values
                df[tgt_col] = trgt_col_values
                src_grouped_df = df.groupby(src_col)

                actual_joint_counts = {}
                for category, rows in src_grouped_df:
                    target_counts_per_category = rows[tgt_col].value_counts().to_dict()
                    actual_joint_counts[category] = target_counts_per_category

                result.append({
                    "catcat_distribution_constraint": {
                        "source_column": src_col,
                        "target_column": tgt_col,
                        "src_unique_counts": src_unique_counts,
                        "trgt_unique_counts": trgt_unique_counts,
                        "actual_joint_counts": actual_joint_counts,
                        "row_count": len(training_data_df)
                    }
                })
            logger.info(
                "Categorical-Categorical Distribution Constraints: Complete, {}.".format(
                    datetime.datetime.now().isoformat()))

        return result

    def get_categorical_distribution_constraint(self, categorical_columns):
        output_constraints = []

        # Categorical Distribution Constraint
        logger.info(
            "Adding categorical distribution constraints: Start, {}.".format(
                datetime.datetime.now().isoformat()))
        for idx, column in enumerate(categorical_columns):
            logger.info("Processing constraint for column: {}".format(column.name))

            constraint = CategoricalDistributionConstraint()
            constraint.columns = [column.name]
            constraint.id = get_constraint_id(
                constraint_name=constraint.name, columns=constraint.columns)

            constraint.content["frequency_distribution"] = {
                get_processed_key(key) : value for key, value in column.value_counts.to_dict().items()
            }
            constraint.constraint_learned = True

            output_constraints.append(constraint)
        logger.info(
            "Adding categorical distribution constraints: Complete, {}.".format(
                datetime.datetime.now().isoformat()))

        return output_constraints

    def get_numeric_range_constraints(self, result, buckets):
        logger.info(
            "Processing results for numeric range constraints: Start, {}.".format(
                datetime.datetime.now().isoformat()))
        numeric_range_constraints = []
        for obj in result:
            if obj.get("numeric_range_constraint"):
                numeric_range_constraints.append(obj.get("numeric_range_constraint"))

        ranges = {}
        for obj in numeric_range_constraints:
            result_json = json.loads(obj)
            for json_obj in result_json:
                keys = list(json_obj.keys())
                keys.remove("counts")

                column = keys[0]

                if column not in ranges.keys():
                    ranges[column] = {}

                index = int(json_obj[column])

                if index not in ranges[column].keys():
                    ranges[column][index] = json_obj["counts"]
                    continue

                ranges[column][index] = ranges[column][index] + json_obj["counts"]

        final_output = {}
        for key, value in buckets.items():
            column = key
            bucket_list = value

            final_output[column] = {}
            for key,value in ranges["{}_buckets".format(column)].items():
                final_output[column][bucket_list[key][0]] = value

        output_constraints = []
        for key,value in final_output.items():
            logger.info("Processing constraint for column: {}".format(key))
            constraint = NumericRangeConstraint()
            constraint.columns = [key]
            constraint.id = get_constraint_id(
                constraint_name=constraint.name, columns=constraint.columns)

            constraint.content["ranges"] = value
            constraint.constraint_learned = True

            output_constraints.append(constraint)
        logger.info(
            "Processing results for numeric range constraints: Complete, {}.".format(
                datetime.datetime.now().isoformat()))
        
        return output_constraints

    def get_catnum_range_constraints(self, result):
        logger.info(
            "Processing results for categorical-numeric range constraints: Start, {}.".format(
                datetime.datetime.now().isoformat()))
        catnum_range_constraints = []
        for obj in result:
            if obj.get("catnum_range_constraint"):
                catnum_range_constraints.append(obj.get("catnum_range_constraint"))

        # First Pass: Combine all under same source and target column
        import hashlib
        output = {}
        for json_obj in catnum_range_constraints:
            source_column = json_obj["source_column"]
            target_column = json_obj["target_column"]

            guid = hashlib.sha256("{}{}".format(source_column, target_column).encode())
            guid = guid.hexdigest()

            if guid in output.keys():
                ranges = json_obj["ranges"]
                output_ranges = output[guid]["ranges"]
                for key, value in ranges.items():
                    if key in output_ranges.keys():
                        # append value in existing stuff
                        output[guid]["ranges"][key].extend(value)
                        continue

                    output[guid]["ranges"][key] = value

                continue

            output[guid] = json_obj

        # Second Pass: combine same min max buckets for each key
        second_pass = {}
        for key, value in output.items():
            second_pass[key] = {
                "source_column": value["source_column"],
                "target_column": value["target_column"],
                "is_integer": value["is_integer"],
                "ranges": {}
            }

            ranges = {}
            for q, a in value["ranges"].items():
                ranges[q] = {}
                for item in a:
                    guid = hashlib.sha256("{}{}".format(item["min"], item["max"]).encode())
                    guid = guid.hexdigest()

                    if guid in ranges[q].keys():
                        ranges[q][guid]["count"] = ranges[q][guid]["count"] + item["count"]
                        continue

                    ranges[q][guid] = {
                        "min": item["min"],
                        "max": item["max"],
                        "count": item["count"]
                    }

            second_pass[key]["ranges"] = ranges

        # Third Pass: get rid of ids introduced
        third_pass = {}
        for key, value in second_pass.items():
            third_pass[key] = {
                "source_column": value["source_column"],
                "target_column": value["target_column"],
                "is_integer": value["is_integer"],
                "ranges": {}
            }

            ranges = {}
            for x, y in value["ranges"].items():
                ranges[x] = []
                for a, b in y.items():
                    ranges[x].append(b)

            third_pass[key]["ranges"] = ranges

        # Fourth Pass: Merge ranges
        def are_close(a_range, b_range, threshold=1):
            return not(
                (a_range["min"] > b_range["max"] + threshold) or (
                    a_range["max"] + threshold < b_range["min"]))

        def merge(y, is_integer, buffer):
            ranges = sorted(y, key=lambda val: val["min"])

            global_min = min(temp_range["min"] for temp_range in ranges)
            global_max = max(temp_range["max"] for temp_range in ranges)
            threshold = buffer * (global_max - global_min)

            import numpy as np
            from copy import deepcopy

            if is_integer:
                threshold = int(np.ceil(threshold))

            result = []
            for interval in ranges:
                if len(result) == 0 or not(are_close(result[-1], interval, threshold)):
                    result.append(deepcopy(interval))
                else:
                    min_value = result[-1]["min"]
                    max_value = result[-1]["max"]
                    count = result[-1]["count"]

                    result[-1] = {
                        "min": min(min_value, interval["min"]),
                        "max": max(max_value, interval["max"]),
                        "count": count + interval["count"]
                    }

            global_count = sum(temp_range["count"] for temp_range in ranges)
            result = [interval for interval in result if interval["count"] > 0.005 * global_count]

            return result

        fourth_pass = {}
        for key, value in third_pass.items():
            fourth_pass[key] = {
                "source_column": value["source_column"],
                "target_column": value["target_column"],
                "ranges": {}
            }

            ranges = {}
            for x, y in value["ranges"].items():
                ranges[x] = merge(y, value["is_integer"], 0.1)

            fourth_pass[key]["ranges"] = ranges

        # Final Pass: Remove generated ids
        constraints = []
        for key, value in fourth_pass.items():
            constraints.append(value)

        output_constraints = []
        for constraint in constraints:
            source_column = constraint["source_column"]
            target_column = constraint["target_column"]
            logger.info("Processing constraint for columns: {}, {}".format(
                source_column, target_column))

            catnum_constraint = CategoricalNumericRangeConstraint()
            catnum_constraint.source_column = source_column
            catnum_constraint.target_column = target_column
            catnum_constraint.columns = [source_column, target_column]
            catnum_constraint.id = get_constraint_id(
                constraint_name=catnum_constraint.name, columns=catnum_constraint.columns)

            catnum_constraint.content["source_column"] = source_column
            catnum_constraint.content["target_column"] = target_column
            catnum_constraint.content["ranges"] = constraint["ranges"]
            catnum_constraint.constraint_learned = True

            output_constraints.append(catnum_constraint)
        logger.info(
            "Processing results for categorical-numeric range constraints: Complete, {}.".format(
                datetime.datetime.now().isoformat()))

        return output_constraints

    def get_catcat_distribution_constraints(self, result):
        logger.info(
            "Processing results for categorical-categorical distribution constraints: Start, {}.".format(
                datetime.datetime.now().isoformat()))
        catcat_distribution_constraints = []
        for obj in result:
            if obj.get("catcat_distribution_constraint"):
                catcat_distribution_constraints.append(obj.get("catcat_distribution_constraint"))

        CATEGORY_PROPORTION_THRESHOLD = 0.1  # 1/10th of full training data
        def get_support(category_counts: dict, totals_rows: int):
            category_support = dict()
            for category, counts in category_counts.items():
                support = counts/totals_rows
                category_support[category] = support
            return category_support

        def get_lift(src_col_support: dict, trgt_col_support: dict):
            association_lift = dict()
            for src_category, src_support in src_col_support.items():
                src_target_lift = {target_cat: (src_support * target_cat_support)
                                    for target_cat, target_cat_support in trgt_col_support.items()}
                association_lift[src_category] = src_target_lift
            return association_lift

        def get_expected_joint_counts(src_unique_counts: dict, trgt_unique_counts: dict, total_rows: int):
            expected_joint_count = dict()
            # 1. Get support for source and target categories
            src_col_support = get_support(src_unique_counts, total_rows)
            target_col_support = get_support(trgt_unique_counts, total_rows)

            # 2. Get lift for each source and target category combination
            src_trgt_associated_lift = get_lift(
                src_col_support, target_col_support)

            # 3. Get expected row count for the unique combination of source category can target
            for src_category, trgt_lift in src_trgt_associated_lift.items():
                src_target_exp_joint_count = {target_cat: int(
                    src_trgt_lift * CATEGORY_PROPORTION_THRESHOLD * total_rows) for target_cat, src_trgt_lift in trgt_lift.items()}
                expected_joint_count[src_category] = src_target_exp_joint_count
            return expected_joint_count

        def merge_unique_counts(a_unique_counts, b_unique_counts):
            unique_counts = {}
            for a_key, a_value in a_unique_counts.items():
                value = a_value
                if a_key in b_unique_counts.keys():
                    value = value + b_unique_counts[a_key]

                unique_counts[a_key] = value

            for b_key, b_value in b_unique_counts.items():
                if b_key not in a_unique_counts.keys():
                    unique_counts[b_key] = b_value

            return unique_counts

        def merge_actual_counts(a_actual_counts, b_actual_counts):
            actual_counts = {}
            a_keys = list(a_actual_counts.keys())
            b_keys = list(b_actual_counts.keys())

            keys = list(set(a_keys + b_keys))

            for key in keys:
                value = None
                if key in a_keys:
                    value = a_actual_counts[key]

                if key in b_keys and not value:
                    value = b_actual_counts[key]

                if key in b_keys and value is not None:
                    for x, y in b_actual_counts[key].items():
                        if x in value.keys():
                            value[x] = value[x] + y
                            continue

                        value[x] = y

                actual_counts[key] = value

            return actual_counts

        import hashlib
        output = {}
        for json_obj in catcat_distribution_constraints:
            source_column = json_obj["source_column"]
            target_column = json_obj["target_column"]
            src_unique_counts = json_obj["src_unique_counts"]
            trgt_unique_counts = json_obj["trgt_unique_counts"]
            actual_joint_counts = json_obj["actual_joint_counts"]
            row_count = json_obj["row_count"]

            guid = hashlib.sha256("{}{}".format(source_column, target_column).encode())
            guid = guid.hexdigest()

            output_obj = {
                "source_column": source_column,
                "target_column": target_column
            }

            if guid in output.keys():
                src_unique_counts = merge_unique_counts(
                    a_unique_counts=src_unique_counts,
                    b_unique_counts=output[guid]["src_unique_counts"])

                trgt_unique_counts = merge_unique_counts(
                    a_unique_counts=trgt_unique_counts,
                    b_unique_counts=output[guid]["trgt_unique_counts"])

                actual_joint_counts = merge_actual_counts(
                    a_actual_counts=actual_joint_counts,
                    b_actual_counts=output[guid]["actual_joint_counts"])

                row_count = row_count + output[guid]["total_row_count"]

            output_obj["src_unique_counts"] = src_unique_counts
            output_obj["trgt_unique_counts"] = trgt_unique_counts
            output_obj["total_row_count"] = row_count
            output_obj["actual_joint_counts"] = actual_joint_counts
            output[guid] = output_obj

        # calculate expected counts using src_unique_counts and trgt_unique_counts
        new_output = {}
        for key, value in output.items():
            src_unique_counts = value["src_unique_counts"]
            trgt_unique_counts = value["trgt_unique_counts"]
            total_row_count = value["total_row_count"]

            expected_joint_count = get_expected_joint_counts(
                src_unique_counts, trgt_unique_counts, total_row_count)

            new_output[key] = {
                "source_column": value["source_column"],
                "target_column": value["target_column"],
                "expected_joint_count": expected_joint_count,
                "actual_joint_counts": value["actual_joint_counts"],
                "total_row_count": total_row_count
            }

        final_output = []
        for key, value in new_output.items():
            # Set record count thresholds
            lower_threshold = 2
            # 2% of full training data
            upper_threshold = int(0.02 * value["total_row_count"])

            rare_combinations = []
            for category, target_counts_per_category in value["actual_joint_counts"].items():
                category_details = dict()
                # Get source category expected joint count
                src_cat_expected_joint_count = value["expected_joint_count"][category]

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
                    rare_combinations.append(category_details)

            if len(rare_combinations) > 0:
                final_output.append({
                    "source_column": value["source_column"],
                    "target_column": value["target_column"],
                    "rare_combinations": rare_combinations
                })

        output_constraints = []
        for json_obj in final_output:
            source_column = json_obj["source_column"]
            target_column = json_obj["target_column"]
            logger.info("Processing constraint for columns: {}, {}".format(
                source_column, target_column))

            constraint = CatCatDistributionConstraint()
            constraint.source_column = source_column
            constraint.target_column = target_column
            constraint.columns = [source_column, target_column]

            constraint.id = get_constraint_id(
                constraint_name=constraint.name, columns=constraint.columns)

            constraint.content["source_column"] = source_column
            constraint.content["target_column"] = target_column
            constraint.content["rare_combinations"] = json_obj["rare_combinations"]

            constraint.constraint_learned = True

            output_constraints.append(constraint)

        logger.info(
            "Processing results for categorical-categorical distribution constraints: Complete, {}.".format(
                datetime.datetime.now().isoformat()))

        return output_constraints