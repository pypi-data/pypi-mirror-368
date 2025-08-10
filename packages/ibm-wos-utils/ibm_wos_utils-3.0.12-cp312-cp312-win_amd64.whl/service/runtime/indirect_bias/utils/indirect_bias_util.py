# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or otherwise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import ast
import json
import numpy as np

from service.runtime.utils import general_utils

class IndirectBiasUtil:

    @classmethod
    def get_protected_attributes(cls, fairness_config, subscription):
        # Check if columns with modeling role 'meta-field' are monitored for fairness
        protected_attributes = []
        features = fairness_config["features"]
        output_data_schema = subscription["entity"]["asset_properties"]["output_data_schema"]
        fields = output_data_schema["fields"]
        for feature in features:
            feature_name = feature["feature"]
            for field in fields:
                if field["name"] == feature_name:
                    if "metadata" in field and "modeling_role" in field["metadata"]:
                        if field["metadata"]["modeling_role"] == "meta-field":
                            protected_attributes.append(feature_name)
                    break
        return protected_attributes

    @classmethod
    def get_feature_details(cls, attribute, features):
        for feature in features:
            if feature["feature"] == attribute:
                return feature
        return None

    @classmethod
    def is_protected_attr_config_modified(cls, existing_config, new_config, protected_attributes):
        if protected_attributes is None or len(protected_attributes) == 0:
            if "protected_attributes" in existing_config:
                del existing_config["protected_attributes"]
            return False
        else:
            if "protected_attributes" in existing_config:
                existing_protected_attributes = existing_config["protected_attributes"]
                if len(existing_protected_attributes) == len(protected_attributes) and set(existing_protected_attributes) == set(protected_attributes):
                    for attribute in protected_attributes:
                        existing_feature_config = cls.get_feature_details(
                            attribute, existing_config["features"])
                        new_feature_config = cls.get_feature_details(
                            attribute, new_config["features"])
                        feature_fields = ["majority", "minority"]
                        for field in feature_fields:
                            if new_feature_config[field] != existing_feature_config[field]:
                                return True
                        # If feature configuration matches, just use existing corelation info instead of recomputing it
                        for field in existing_feature_config:
                            if field not in new_feature_config:
                                new_feature_config[field] = existing_feature_config[field]
                    return False
                else:
                    return True
            else:
                return True

    @classmethod
    def get_formatted_range(cls, range):
        return "{0}-{1}".format(str(range[0]), str(range[1]))

    @classmethod
    def is_protected_attribute(cls, fairness_configuration, fairness_attribute):
        if "protected_attributes" in fairness_configuration["parameters"]:
            if fairness_attribute in fairness_configuration["parameters"]["protected_attributes"]:
                return True
        return False

    @classmethod
    def co_related_attributes_exist(cls, fairness_configuration, fairness_attribute, feature_details=None):
        if not feature_details:
            feature_details = cls.get_feature_details(
                fairness_attribute, fairness_configuration["parameters"]["features"])
        if feature_details is not None and 'correlated_attributes' in feature_details and len(feature_details['correlated_attributes']) > 0:
            return True
        return False

    @classmethod
    def skip_perturbation(cls, fairness_configuration, fairness_attribute, feature_details=None):
        if cls.is_protected_attribute(fairness_configuration, fairness_attribute) and not cls.co_related_attributes_exist(fairness_configuration, fairness_attribute, feature_details=feature_details):
            return True
        return False

    @classmethod
    def compute_correlated_attr_distribution(cls, data, fairness_configuration, inputs, fairness_attribute, maj_min, is_majority=False):
        class_label = inputs["class_label"]
        fav_class = inputs["favourable_class"]
        unfav_class = inputs["unfavourable_class"]
        is_categorical = data[fairness_attribute].dtype == "object"
        is_boolean = data[fairness_attribute].dtype == "bool"
        if is_categorical:
            maj_min = str(maj_min)
        elif is_boolean:
            if maj_min == "True" or maj_min == "False":
                maj_min = bool(maj_min)
        else:
            # This is numeric attribute
            if type(maj_min) is str:  # Just a safe check
                maj_min = ast.literal_eval(maj_min)
        if data[fairness_attribute].dtype == np.int64 or data[fairness_attribute].dtype == np.float64:
            df = data.loc[(data[fairness_attribute] >= maj_min[0])
                          & (data[fairness_attribute] <= maj_min[1])]
            #maj_min = cls.get_formatted_range(maj_min)
        else:
            df = data.loc[data[fairness_attribute] == maj_min]
        if len(df) == 0:
            return {}
        df_fav = None
        feature_details = cls.get_feature_details(
            fairness_attribute, fairness_configuration["parameters"]["features"])
        correlated_attribute_distribution = {}
        maj_min_key = "correlated_minority"
        if is_majority:
            maj_min_key = "correlated_majority"
        if feature_details is not None and maj_min_key in feature_details:
            correlations = cls.get_correlations_for_maj_min_group(
                feature_details[maj_min_key], maj_min)
            #co_relation_map = feature_details[maj_min_key][maj_min]
            for correlation in correlations:
                attr_distribution = []
                attribute = correlation.get("feature")
                values = correlation.get("values")
                # In a rare scenario, training data does not contain any value for a specific majority/minority group
                # In this case, no correlations will be found for this specific group. So getting attribute values from payload/payload_perturb data to compute distribution. WI #17383
                if values is None or len(values) == 0:
                    values = cls.get_distinct_attribute_values(df, attribute)
                for value in values:
                    attr_value = value.get("feature_value")
                    if (df[attribute].dtype == np.int64 or df[attribute].dtype == np.float64) and type(attr_value) is list:
                        #attr_value = cls.get_numerical_range(attr_value)
                        df_attr = df.loc[(df[attribute] >= attr_value[0]) & (
                            df[attribute] <= attr_value[1])]
                    else:
                        df_attr = df.loc[df[attribute] == attr_value]
                    if len(df_attr) == 0:
                        continue
                    attr_rows = len(df_attr)
                    total_rows_percent = 100 * \
                        round(float(attr_rows/len(df)), 2)
                    for label in fav_class:
                        attr_value_distribution = cls.get_attr_value_disribution(
                            df_attr, attr_value, label, class_label, True, total_rows_percent)
                        if attr_value_distribution is not None:
                            attr_distribution.append(attr_value_distribution)
                    for label in unfav_class:
                        attr_value_distribution = cls.get_attr_value_disribution(
                            df_attr, attr_value, label, class_label, False, total_rows_percent)
                        if attr_value_distribution is not None:
                            attr_distribution.append(attr_value_distribution)
                correlated_attribute_distribution[attribute] = attr_distribution
        return correlated_attribute_distribution

    @classmethod
    def get_attr_value_disribution(cls, df, attr_value, label, label_column, is_favourable, total_rows_percent):
        if type(label) is list:
            df_attr_val = df.loc[(df[label_column] >= label[0]) & (
                df[label_column] <= label[1])]
        else:
            df_attr_val = df.loc[df[label_column] == label]
        if len(df_attr_val) == 0:
            return None
        attr_value_distribution = {}
        attr_value_distribution["correlated_feature_value"] = attr_value
        attr_value_distribution["count"] = len(df_attr_val)
        attr_value_distribution["label"] = label
        attr_value_distribution["total_rows_percent"] = total_rows_percent
        attr_value_distribution["is_favourable"] = is_favourable
        return attr_value_distribution

    @classmethod
    def get_numerical_range(cls, range_str):
        range_values = str(range_str).split("-")
        range_start = cls.get_numeric_value(range_values[0].strip())
        range_end = cls.get_numeric_value(range_values[1].strip())
        return [range_start, range_end]

    @classmethod
    def get_numeric_value(cls, value):
        float_value = float(value)
        if float_value.is_integer():
            return int(float_value)
        return float_value

    @classmethod
    def process_indirect_bias(cls, fairness_config, subscription):
        parameters = fairness_config["parameters"]
        if "process_indirect_bias" in parameters and str(parameters["process_indirect_bias"]).lower() == "true":
            return True
        protected_attributes = cls.get_protected_attributes(
            parameters, subscription)
        if protected_attributes is not None and len(protected_attributes) > 0:
            parameters["protected_attributes"] = protected_attributes
            # Checking if correlation information exists for each protected attribute in required format
            for attribute in protected_attributes:
                attr_details = cls.get_feature_details(
                    attribute, parameters["features"])
                attr_details["is_protected_attribute"] = True
                correlation_info_exists = cls.does_correlation_information_exist(
                    attr_details)
                if not correlation_info_exists:
                    return True
        return False

    @classmethod
    def does_correlation_information_exist(cls, attribute_details):
        # Make sure correlated_attributes contains map of correlation strengths
        correlated_attributes = attribute_details.get("correlated_attributes")
        correlated_attributes_exist = cls.validate_correlated_attributes(
            correlated_attributes)
        if not correlated_attributes_exist:
            return False
        if len(correlated_attributes) > 0:
            # Validate majority/minority mappings for current configuration. So if configuration is changed, it is recomputed
            majority_mapping_exists = cls.validate_maj_min_mapping(attribute_details.get(
                "correlated_majority"), attribute_details.get("majority"), correlated_attributes)
            if not majority_mapping_exists:
                return False
            minority_mapping_exists = cls.validate_maj_min_mapping(attribute_details.get(
                "correlated_minority"), attribute_details.get("minority"), correlated_attributes)
            if not minority_mapping_exists:
                return False
        return True

    @classmethod
    def validate_correlated_attributes(cls, correlated_attributes):
        if correlated_attributes is None:
            return False
        for attribute in correlated_attributes:
            if type(attribute) is not dict or attribute.get("correlation_value") is None:
                return False
        return True

    @classmethod
    def validate_maj_min_mapping(cls, correlated_maj_min, maj_min, correlated_attributes):
        if correlated_maj_min is None:
            return False
        if len(correlated_maj_min) != len(maj_min):
            return False
        # For each majority/minority group ensure that mapping exists in required format
        for maj_min_group in maj_min:
            mapping_exists = False
            correlations = cls.get_correlations_for_maj_min_group(
                correlated_maj_min, maj_min_group)
            # Validate correlations
            if correlations is not None and len(correlations) == len(correlated_attributes):
                attr_mapping_count = 0
                for attr in correlated_attributes:
                    for correlation in correlations:
                        if attr.get("feature") == correlation.get("feature"):
                            attr_mapping_count += 1
                            break
                if attr_mapping_count == len(correlated_attributes):
                    mapping_exists = True
            if not mapping_exists:
                return False
        return True

    @classmethod
    def get_correlations_for_maj_min_group(cls, correlated_maj_min, maj_min_group):
        if correlated_maj_min is not None:
            for correlation_map in correlated_maj_min:
                if maj_min_group == correlation_map.get("feature_value"):
                    return correlation_map.get("correlations")
        return None

    @classmethod
    def get_distinct_attribute_values(cls, df, attribute):
        attribute_values = []
        values = []
        dtype = df[attribute].dtype
        num_classes = 4
        if (dtype == np.int64 or dtype == np.float64) and len(df) > num_classes:
            values = general_utils.get_numerical_bins(df, attribute)
        else:
            values = df[attribute].unique()
        for value in values:
            value_json = {}
            value_json["feature_value"] = value
            attribute_values.append(value_json)
        return attribute_values

