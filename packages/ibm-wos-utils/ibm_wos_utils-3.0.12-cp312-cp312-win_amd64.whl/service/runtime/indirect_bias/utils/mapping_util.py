# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or otherwise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import jenkspy
import numpy as np
import time

from service.runtime.indirect_bias.utils import indirect_bias_constants
from service.runtime.indirect_bias.utils.indirect_bias_util import IndirectBiasUtil
from service.runtime.utils import general_utils

class MappingUtil:
    '''
    Class for utility methods related to computing indirect majority/minority of co-related attributes
    using majority/minority of protected attribute
    '''
    @classmethod
    def get_indirect_majority_minority_for_categorical_attr(cls, dataset, protected_attribute, co_related_attributes, majority, minority):
        '''
        Computes mapping of majority and minority for co-related attributes based on majority and minority of the categorical protected attribute
        - For each majority value, find rows from dataset where row value for protected_attribute equals the majority value
        - From this sub dataset, find frequency distibution and construct a map for each co-related feature
        - Similarly compute co-relation map for each minority value 
        '''
        start_time = time.time()
        co_related_majority = []
        co_related_minority = []
        columns = [protected_attribute] + co_related_attributes
        ds_sub = dataset[columns]

        for maj in majority:
            maj_dataset = ds_sub.loc[ds_sub[protected_attribute] == maj]
            maj_mapping = cls.get_mapping_for_co_related_attributes(
                maj_dataset, co_related_attributes)
            co_related_majority.append(
                cls.get_correlated_maj_min(maj, maj_mapping))

        for mino in minority:
            min_dataset = ds_sub.loc[ds_sub[protected_attribute] == mino]
            min_mapping = cls.get_mapping_for_co_related_attributes(
                min_dataset, co_related_attributes)
            co_related_minority.append(
                cls.get_correlated_maj_min(mino, min_mapping))
        end_time = time.time()
        return co_related_majority, co_related_minority

    @classmethod
    def get_mapping_for_co_related_attributes(cls, dataset, co_related_attributes, numerical_bins_map=None):
        '''
        Finds co-relation map for each co-related attribute
        The input dataset is the majority/minority dataset where row values of protected attribute are majority or minority
        - If co-related attribute is categorical, then from the dataset find frequency distribution of each value and construct a map
        - If co-related attribute is numerical, then from the dataset find frequency distribution of each numerical bin and construct a map
        '''
        correlations = []
        for attribute in co_related_attributes:
            attr_correlations = {}
            correlation_values = []
            if len(dataset) > 0:
                if dataset[attribute].dtype == np.int64 or dataset[attribute].dtype == np.float64:
                    if numerical_bins_map is not None and attribute in numerical_bins_map:
                        bins = numerical_bins_map[attribute]
                    else:
                        bins = None
                    correlation_values = cls.get_bins_mapping(
                        dataset, attribute, bins=bins)
                else:
                    attr_value_dist = (
                        dataset[attribute].value_counts()/len(dataset)).to_dict()
                    # Sort the mapped values based on the probablity
                    attr_value_dist = dict(
                        sorted(attr_value_dist.items(), key=lambda x: x[1], reverse=True))
                    # Pick top N values from the mappings
                    attr_value_dist = {k: round(float(v), 4) for k, v in list(
                        attr_value_dist.items())[0:10]}
                    attr_value_dist = {k: v for k, v in list(
                        attr_value_dist.items()) if v > 0}
                    correlation_values = cls.get_formatted_correlation_values(
                        attr_value_dist)

            attr_correlations["feature"] = attribute
            attr_correlations["values"] = correlation_values
            correlations.append(attr_correlations)
        return correlations

    @classmethod
    def get_bins_mapping(cls, dataset, attribute, bins=None, bins_count=4):
        values = []
        if len(dataset) < bins_count:
            # If a majority/minority group for numerical attribute contains very small training data so that bins can not be generated, returning empty correlations. WI #17526
            return values

        bins = general_utils.get_numerical_bins(dataset, attribute)

        for bin_range in bins:
            value_json = {}
            range_ds = dataset.loc[(dataset[attribute] >= bin_range[0]) & (
                dataset[attribute] <= bin_range[1])]
            correlation_value = len(range_ds)/len(dataset)
            correlation_value = round(float(correlation_value), 4)
            if correlation_value > 0:
                feature_value = bin_range
                if dataset[attribute].dtype == np.int64:
                    feature_value = [int(bin_range[0]), int(bin_range[1])]
                else:
                    feature_value = [round(float(bin_range[0]), 2), round(
                        float(bin_range[1]), 2)]
                value_json["feature_value"] = feature_value
                value_json["relative_weight"] = correlation_value
                values.append(value_json)

        return values

    @classmethod
    def get_indirect_majority_minority_for_numerical_attr(cls, dataset, protected_attribute, co_related_attributes, majority, minority):
        '''
        Computes mapping of majority and minority for co-related attributes based on majority and minority of the numerical protected attribute
        - For each majority range, find rows from dataset where row value for protected_attribute value falls in the majority range
        - From this sub dataset, find frequency distibution and construct a map for each co-related feature
        - Similarly compute co-relation map for each minority value 
        '''
        start_time = time.time()
        co_related_majority = []
        co_related_minority = []
        columns = [protected_attribute] + co_related_attributes
        ds_sub = dataset[columns]

        for maj in majority:
            maj_dataset = ds_sub.loc[(ds_sub[protected_attribute] >= maj[0]) & (
                ds_sub[protected_attribute] <= maj[1])]
            maj_mapping = cls.get_mapping_for_co_related_attributes(
                maj_dataset, co_related_attributes)
            co_related_majority.append(
                cls.get_correlated_maj_min(maj, maj_mapping))
        for mino in minority:
            min_dataset = ds_sub.loc[(ds_sub[protected_attribute] >= mino[0]) & (
                ds_sub[protected_attribute] <= mino[1])]
            min_mapping = cls.get_mapping_for_co_related_attributes(
                min_dataset, co_related_attributes)
            co_related_minority.append(
                cls.get_correlated_maj_min(mino, min_mapping))
        end_time = time.time()
        return co_related_majority, co_related_minority

    @classmethod
    def get_numerical_bins(cls, dataset, co_related_attributes, bins_count=10):
        numerical_bins = {}
        for attribute in co_related_attributes:
            if dataset[attribute].dtype == np.int64 or dataset[attribute].dtype == np.float64:
                breaks = jenkspy.jenks_breaks(
                    dataset[attribute], n_classes=bins_count)
                bins = []
                for i in range(len(breaks)-1):
                    bins.append([breaks[i]+1, breaks[i+1]])
                numerical_bins[attribute] = bins
        return numerical_bins

    @classmethod
    def get_formatted_correlation_values(cls, correlation_values):
        values = []
        for feature_value, correlation in correlation_values.items():
            value_json = {}
            value_json["feature_value"] = feature_value
            value_json["relative_weight"] = correlation
            values.append(value_json)
        return values

    @classmethod
    def get_correlated_maj_min(cls, maj_min_value, correlations):
        correlated_maj_min = {}
        correlated_maj_min["feature_value"] = maj_min_value
        correlated_maj_min["correlations"] = correlations
        return correlated_maj_min
