# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or otherwise divested of its trade
# secrets, irrespective of what has been deposited with the U.S. Copyright Office.
# ----------------------------------------------------------------------------------------------------

import pandas as pd
import statistics
import os
import numpy as np
import datetime
import time

from service.runtime.indirect_bias.utils import indirect_bias_constants
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics


class CoRelationsUtil:
    '''
    Class for utility methods related to finding co-related attributes of a given protected attribute
    '''
    @classmethod
    def pre_processing_df(cls, dataset, protected_attribute, target):
        headers = dataset.columns.values.tolist()
        headers.remove(target)
        int_df = dataset.select_dtypes(include=['int64']).copy()
        float_df = dataset.select_dtypes(include=['float64']).copy()
        obj_df = dataset.select_dtypes(include=['object']).copy()
        obj_df_headers = obj_df.columns.values.tolist()
        for header in obj_df_headers:
            obj_df[header] = obj_df[header].astype('category').cat.codes
        final_dataset = pd.concat([int_df, float_df, obj_df], axis=1)
        return final_dataset, headers, obj_df_headers

    @classmethod
    def category_finder(cls, protected_attribute, obj_df_headers):
        pa_type = "continuous"
        if protected_attribute in obj_df_headers:
            return "categorical"
        return pa_type

    @classmethod
    def find_correlation_coefficient(cls, dataset, protected_attribute, target, pa_type):
        '''
        Builds logistic regression for categorical protected_attribute and linear regression for numerical protected_attribute and returns co-relation coefficients of all the features
        '''
        headers = dataset.columns.values.tolist()
        if protected_attribute in headers:
            headers.remove(protected_attribute)
        if target in headers:
            headers.remove(target)
        X = dataset[headers]
        Y = dataset[protected_attribute]
        x_train, x_test, y_train, y_test = train_test_split(
            X, Y, test_size=0.20, random_state=0, shuffle=False)

        if pa_type == "categorical":
            classifier = LogisticRegression()
            classifier.fit(X, Y)
            coef = [abs(x) for x in classifier.coef_[0]]
            # Compute the model accuracy
            y_pred = classifier.predict(x_test)
            accuracy = metrics.accuracy_score(y_test, y_pred)
            return coef, accuracy
        if pa_type == "continuous":
            classifier = LinearRegression()
            classifier.fit(x_train, y_train)
            coef = [abs(x) for x in classifier.coef_]
            y_pred = classifier.predict(x_test)
            # Compute root mean squared error(RMSE) for the model, normalise it by dividing with standard deviation
            rmse = np.sqrt(metrics.mean_squared_error(y_test, y_pred))
            std_deviation = statistics.stdev(y_test)
            return coef, rmse/std_deviation

    @classmethod
    def co_related_attributes_identifier(cls, final_dataset, headers, obj_df_headers, protected_attribute, target):
        '''
        A model is built to identify co-related attributes for given protected attribute, with all the attributes as features and protected attribute as the label column
        Co-related attributes based on their co_relation coefficient in the model built.
        '''
        pa_type = cls.category_finder(protected_attribute, obj_df_headers)
        if pa_type == "categorical":
            coef, accuracy = cls.find_correlation_coefficient(
                final_dataset, protected_attribute, target, pa_type)
            if accuracy < indirect_bias_constants.MODEL_ACCURACY_THRESHOLD:
                return []
        else:
            coef, normalised_rmse = cls.find_correlation_coefficient(
                final_dataset, protected_attribute, target, pa_type)
            if normalised_rmse > 1:
                return []
        coef = [float(i)/sum(coef) for i in coef]

        headers = final_dataset.columns.values.tolist()
        if protected_attribute in headers:
            headers.remove(protected_attribute)
        if target in headers:
            headers.remove(target)
        meu = statistics.mean(coef)
        sigma = statistics.stdev(coef)

        if meu-sigma > 0:
            tau = meu-sigma
        else:
            tau = meu+sigma

        correlated_features_info = {}

        for idx, col in enumerate(headers):
            if coef[idx] > tau:
                correlated_features_info[col] = coef[idx]

        # Sort the attributes in decreasing order of coefficient
        correlated_features_info = dict(
            sorted(correlated_features_info.items(), key=lambda x: x[1], reverse=True))
        correlated_features_info = {k: round(float(v), 4) for k, v in list(
            correlated_features_info.items())[0:5]}
        updated_correlated_features_info = {k: v for k, v in correlated_features_info.items(
        ) if v >= indirect_bias_constants.CO_RELATED_ATTR_COEFF_THRESHOLD}

        co_related_features = {}
        # If some features exist with co-relation coefficient > 0.25(threshold), they are picked as co_related_features
        # Otherwise if cumulative co-relation coefficient of attributes(max 5) exceeds 0.75, then they are picked as co_related_features
        if len(updated_correlated_features_info) > 0:
            co_related_features = updated_correlated_features_info
        else:
            total_weight = 0
            index = 0
            for k, v in correlated_features_info.items():
                total_weight += v
                co_related_features[k] = v
                index += 1
                if index > 4 or total_weight >= indirect_bias_constants.CUMULATIVE_CO_RELATION_COEFF_THRESHOLD:
                    break
            if total_weight < indirect_bias_constants.CUMULATIVE_CO_RELATION_COEFF_THRESHOLD:
                co_related_features = {}
        co_relation_information = cls.get_co_relation_information(
            co_related_features)
        return co_relation_information

    @classmethod
    def get_co_relation_information(cls, co_related_features):
        co_relation_information = []
        if len(co_related_features) > 0:
            for feature, value in co_related_features.items():
                feature_info = {}
                feature_info["feature"] = feature
                feature_info["correlation_value"] = value
                co_relation_information.append(feature_info)
        return co_relation_information

    @classmethod
    def get_co_related_attributes_list(cls, correlations):
        attributes_list = []
        for correlation in correlations:
            attributes_list.append(correlation.get("feature"))
        return attributes_list

    @classmethod
    def find_co_related_attributes(cls, dataset, protected_attribute, target):
        start_time = time.time()
        final_dataset, final_headers, obj_df_headers = cls.pre_processing_df(
            dataset, protected_attribute, target)
        co_related_attributes = cls.co_related_attributes_identifier(
            final_dataset, final_headers, obj_df_headers, protected_attribute, target)
        end_time = time.time()

        return co_related_attributes
