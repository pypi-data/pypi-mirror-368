# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import io
import json
import os
import pickle
import sys
import tarfile
import time
import uuid
import warnings
from enum import Enum

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import (ParameterSampler, RandomizedSearchCV,
                                     StratifiedKFold, train_test_split)
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm

warnings.simplefilter("ignore", category=DeprecationWarning)


class DriftDetectionModel:

    RANDOM_STATE = 111
    np.random.seed(RANDOM_STATE)

    def __init__(self, label_column, feature_columns, categorical_columns=[]):
        """Init constructor

        Arguments:
            label_column {str} -- name of the label column in training data
            feature_columns {list} -- list of the feature columns in training data
            categorical_columns {list} -- list of the categorical columns in training data (default: {[]})
        """

        valid_version_prefixes = ["0.24.", "1.0.",
                                  "1.1.1", "1.1.2", "1.1.3", "1.3.2"]

        if all(not str(sklearn.__version__.startswith(prefix)) for prefix in valid_version_prefixes):
            raise DriftException(
                "Unsupported version {} of scikit-learn. Use 1.1.3.".format(sklearn.__version__))

        self.label_column = label_column
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        if self.categorical_columns == None:
            self.categorical_columns = []
        self.categorical_map = {}
        self.training_labels = []
        self.predicted_labels = []
        self.ddm_features = []
        self.dd_model = None
        self.base_client_accuracy = 0
        self.base_predicted_accuracy = 0

    def _validate_score_probabilities(self, probabilities, expected_rows):
        # 1. Validate if probabilities is a numpy array of shape (expected_rows, classes)
        if not (isinstance(probabilities, np.ndarray)):
            raise Exception(
                "The probabilities output of score function is not of type numpy.ndarray.")

        expected_shape = (expected_rows, len(self.training_labels))
        if probabilities.shape != expected_shape:
            raise Exception("The shape of probabilities output of score function is {} but should be {}".format(
                probabilities.shape, expected_shape))

        # 2. Try to convert probabilities to float
        try:
            probabilities = probabilities.astype(float)
        except ValueError:
            raise Exception("The probabilities output of score function is of type `{}` which can not be cast to float.".format(
                probabilities.dtype.name))

        # 3. Validate that all values of probabilities fall between 0 and 1 inclusive.
        if not (np.all(probabilities >= 0)) and not (np.all(probabilities <= 1)):
            raise Exception(
                "The probabilities output of score function does not lie between 0 and 1.")

        return probabilities

    def _validate_score_predictions(self, predictions, expected_rows):
        # 1. Validate if predictions is a numpy array of shape (batch_size, )
        if not (isinstance(predictions, np.ndarray)):
            raise Exception(
                "The predictions output of score function is not of type numpy.ndarray.")

        expected_shape = (expected_rows, )
        if predictions.shape != expected_shape:
            raise Exception("The shape of predictions output of score function is {} but should be {}".format(
                predictions.shape, expected_shape))

        # 2. Try to cast them in same dtype as classnames
        classnames_dtype = np.array(self.training_labels).dtype.name
        classnames_dtype = "str" if classnames_dtype == "object" else classnames_dtype
        predictions_dtype = predictions.dtype.name
        try:
            predictions = predictions.astype(classnames_dtype)
        except ValueError:
            raise Exception("The predictions output of score function is of type '{}' and can not be cast to training labels' type '{}'.".format(
                predictions_dtype, classnames_dtype))

        if len(self.training_labels):
            predicted_classes = np.unique(predictions)

            # Check if any value in prediction vector is not present in
            # training data class names. We are now doing string based comparison after
            # converting training labels and predicted classes to lowercase
            if pd.Series(self.training_labels).dtype == "object":
                temp_predicted_classes = list(
                    map(str.lower, map(str, predicted_classes)))
                training_labels = list(
                    map(str.lower, map(str, self.training_labels)))
            else:
                temp_predicted_classes = predicted_classes
                training_labels = self.training_labels
            if any(prediction not in training_labels for prediction in temp_predicted_classes):
                raise DriftException("The model predictions {} are different from class names {} in the training data".format(
                    predicted_classes, list(self.training_labels)))

        return predictions

    def _get_probability_dataframe(self, probabilities):
        # Add probabilities of the classes as columns to the dataframe
        prob_df = pd.DataFrame(probabilities, columns=["Probability of Class '{}'".format(
            predicted_label) for predicted_label in self.predicted_labels])
        sorted_probs = np.sort(probabilities)

        # Also add difference between highest probability and second highest
        # probability
        prob_df["Probability Difference Between Top Two Classes"] = sorted_probs[:, -
                                                                                 1:] - sorted_probs[:, -2:-1]
        return prob_df

    def _get_predicted_labels(self, probabilities, predictions):
        """Given probabilities array, total predictions and training labels, this method tries to map each training label
        to an index of the probability array of a prediction. For `n` training labels, this method iterates through probabilities
        and predictions till it finds `n-1` labels. So, for binary problems, it just needs to look at the first row of probabilities
        and predictions to figure out order of predictions. If there are more than 1 empty places left, this will assign the index
        at empty position as class name.

        Arguments:
            probabilities {numpy.ndarray} -- ndarray of shape (samples,features)
            predictions {numpy.ndarray} -- ndarray of shape (samples,)

        Returns:
            list -- List of predicted labels in the user model output.
        """
        predicted_labels = [None] * len(self.training_labels)

        for probability, prediction in zip(probabilities, predictions):
            max_index = np.argwhere(
                probability == np.amax(probability)).flatten()
            if len(max_index) > 1:
                continue

            if prediction not in predicted_labels:
                predicted_labels[max_index[0]] = prediction

            empty_values = sum(
                predicted_label is None for predicted_label in predicted_labels)
            if empty_values == 1:
                idx = predicted_labels.index(None)
                label = (set(self.training_labels) -
                         set(predicted_labels)).pop()
                predicted_labels[idx] = label
                break

        # If there are still None(s) in predicted_labels replace them with index
        predicted_labels = [predicted_label if predicted_label is not None else "Missing Label {}".format(uuid.uuid4()) for
                            predicted_label in predicted_labels]

        return predicted_labels

    def _balance_data(self, train, train_y):
        num_correct_predictions = len(train_y[train_y == 1])
        num_incorrect_predictions = len(train_y[train_y == 0])

        if num_incorrect_predictions == 0:
            raise DriftException("There are no incorrect predictions from the client model. The client model seems to be over-fitted."
                                 " Please retry this configuration after re-training client model.")

        if num_correct_predictions == 0:
            raise DriftException("There are no correct predictions from the client model. The client model seems to be under-fitted."
                                 " Please retry this configuration after re-training client model.")

        if num_correct_predictions > num_incorrect_predictions:
            supplemental_set = train.iloc[train_y[train_y == 0].index]
            supplemental_set_y = pd.Series([0] * len(supplemental_set))
            repeat_num = int(num_correct_predictions /
                             num_incorrect_predictions)
            remaining_num = num_correct_predictions - \
                num_incorrect_predictions * repeat_num
        else:
            supplemental_set = train.iloc[train_y[train_y == 1].index]
            supplemental_set_y = pd.Series([1] * len(supplemental_set))
            repeat_num = int(num_incorrect_predictions /
                             num_correct_predictions)
            remaining_num = num_incorrect_predictions - num_correct_predictions * repeat_num

        new_train = pd.concat(
            [train, supplemental_set.sample(remaining_num)], ignore_index=True, axis=0)

        new_train_y = pd.concat(
            [train_y, supplemental_set_y.sample(remaining_num)], ignore_index=True, axis=0)

        if repeat_num > 1:
            supplement_list_x = [supplemental_set] * (repeat_num - 1)

            new_train = pd.concat(
                [new_train] + supplement_list_x, ignore_index=True, axis=0)

            supplement_list_y = [supplemental_set_y] * (repeat_num - 1)
            new_train_y = pd.concat(
                [new_train_y] + supplement_list_y, ignore_index=True, axis=0)
        return new_train, new_train_y

    def _predict(self, input_df, probability_column_name):
        """Makes a prediction against the drift detection model

        Arguments:
            input_df {pandas.DataFrame} -- input dataframe to score/predict
            probability_column_name {str} -- name of probability column in input_df

        Returns:
            pandas.DataFrame -- output dataframe containing all columns from input_df plus `prediction` and `prediction_confidence`
        """
        new_input = input_df.dropna(subset=self.feature_columns)
        new_input.reset_index(drop=True, inplace=True)
        encoded_df = new_input.copy()

        for feature in self.categorical_columns:
            le = LabelEncoder()
            le.fit(self.categorical_map[feature])
            encoded_df.loc[:, feature] = le.transform(encoded_df[feature])

        prob_df = self._get_probability_dataframe(
            np.stack(encoded_df[probability_column_name]))
        encoded_df = pd.concat([encoded_df, prob_df], axis=1)

        output_df = pd.concat([new_input.copy(), prob_df], axis=1)
        output_df["prediction"] = self.dd_model.predict(
            encoded_df[self.ddm_features])
        output_df["prediction_confidence"] = np.max(
            self.dd_model.predict_proba(encoded_df[self.ddm_features]), axis=1)
        return output_df

    def _split_and_score(self, score, input_df, batch_size, progress_bar):
        """Splits the input dataframe into chunks of data dictated by `batch_size` and scores using `score` param

        Arguments:
            score {function} -- function to score
            input_df {pandas.DataFrame} -- training dataframe
            batch_size {int} -- Chunk size. A value of 1000 will mean at max 1000 rows are scored at a time
            progress_bar {bool} -- Flag to enable/disable the progress bar.

        Returns:
            tuple -- probabilities and predictions for entire dataframe
        """
        probabilities = None
        predictions = None
        start = 0
        end = min(batch_size, len(input_df))

        tqdm_bar = tqdm(total=len(input_df), desc="Scoring training dataframe...", file=sys.stdout,
                        unit="rows", dynamic_ncols=True, disable=not (progress_bar))

        while start < len(input_df):
            if probabilities is None and predictions is None:
                probabilities, predictions = score(input_df.iloc[start:end])
                probabilities = self._validate_score_probabilities(
                    probabilities, end-start)
                predictions = self._validate_score_predictions(
                    predictions, end-start)
            else:
                probability_array, prediction_vector = score(
                    input_df.iloc[start:end])
                probability_array = self._validate_score_probabilities(
                    probability_array, end-start)
                prediction_vector = self._validate_score_predictions(
                    prediction_vector, end-start)
                probabilities = np.vstack((probabilities, probability_array))
                predictions = np.hstack((predictions, prediction_vector))
            tqdm_bar.update(n=(end-start))
            start = end
            end = min(start + batch_size, len(input_df))

        tqdm_bar.close()

        return probabilities, predictions

    def generate(self, score, input_df, optimise=True,
                 callback=None, progress_bar=True, batch_size=5000):
        """Generates the drift detection model.

        Arguments:
            score {function} -- A function that accepts a dataframe with features as columns and returns a tuple of numpy array
                of probabilities array of shape `(n_samples,n_classes)` and numpy array of prediction vector of shape `(n_samples,)`
            input_df {pandas.DataFrame} -- a pandas dataframe containing the training data.

        Keyword Arguments:
            optimise {bool} -- If True, does hyperparameter optimisation for the drift detection model (default: {True})
            callback {function} -- A method to call after every iteration. (default: {None})
            progress_bar {bool} -- If True, shows progress bars. (default: {True})
            batch_size {int} -- Number of rows to score at a time. (default: {5000})
        """

        if not score:
            raise Exception(
                "The score function is invalid. Please send a valid function in input.")

        # train_df = input_df[sorted(self.feature_columns)]
        # Removed sorting as wml scoring fails due to order change of feature values for auto ai models

        original_training_labels = np.unique(input_df[self.label_column])
        new_input = input_df.dropna(subset=self.feature_columns)
        if new_input.empty:
            msg = "There are no rows left in the training data after dropping missing values. "
            msg += " Please fix the missing values in the training data."
            raise DriftException(msg)

        train_df = new_input[self.feature_columns]
        train_y_df = new_input[self.label_column]
        self.training_labels = np.unique(train_y_df)

        if len(self.training_labels) != len(original_training_labels):
            msg = f"The training labels {original_training_labels} do not match the labels "
            msg += f"{self.training_labels} after dropping missing values from training data."
            raise DriftException(msg)

        # Label encoding: Fit labels on entire dataset
        for feature in self.categorical_columns:
            le = LabelEncoder()
            le.fit(train_df[feature])
            self.categorical_map[feature] = le.classes_

        # Split 80 20
        train_df, test_df, train_y_df, test_y_df = train_test_split(
            train_df, train_y_df, test_size=0.2, stratify=train_y_df, random_state=DriftDetectionModel.RANDOM_STATE)
        train_df.reset_index(drop=True, inplace=True)
        test_df.reset_index(drop=True, inplace=True)
        train_y_df.reset_index(drop=True, inplace=True)
        test_y_df.reset_index(drop=True, inplace=True)

        # Score the training subset
        if callback:
            callback(DriftModelStage.SCORE_SPLIT_TRN_DATA.value)

        train_probabilities, train_predictions = self._split_and_score(
            score, train_df, batch_size, progress_bar)
        self.predicted_labels = self._get_predicted_labels(
            train_probabilities, train_predictions)

        # Label encoding: Transform training subset
        for feature in self.categorical_columns:
            le = LabelEncoder()
            le.fit(self.categorical_map[feature])
            train_df.loc[:, feature] = le.transform(train_df[feature])

        # Prepare training data for drift detection model.
        ddm_train = pd.concat(
            [train_df, self._get_probability_dataframe(train_probabilities)], axis=1)
        self.ddm_features = list(ddm_train.columns)

        if train_y_df.dtype == "object":
            ddm_train_y = pd.Series(pd.Series(train_predictions).str.lower(
            ) == train_y_df.str.lower()).replace(to_replace={True: 1, False: 0})
        else:
            ddm_train_y = pd.Series(train_predictions == train_y_df).replace(
                to_replace={True: 1, False: 0})

        # Balance the training data
        ddm_train, ddm_train_y = self._balance_data(ddm_train, ddm_train_y)

        if optimise:
            parameters = {
                "learning_rate": [0.1, 0.15, 0.2],
                "min_samples_split": np.linspace(0.005, 0.01, 5),
                "min_samples_leaf": np.linspace(0.0005, 0.001, 5),
                "max_leaf_nodes": list(range(3, 12, 2)),
                "max_features": ["log2", "sqrt"],
                "subsample": np.linspace(0.3, 0.9, 6),
                "n_estimators": range(100, 401, 50)
            }

            model_params = {
                "random_state": DriftDetectionModel.RANDOM_STATE,
                "verbose": 0
            }

            randomized_params = {
                "n_iter": 40,
                "scoring": "f1",
                "n_jobs": -1,
                "cv": StratifiedKFold(n_splits=3, shuffle=True, random_state=DriftDetectionModel.RANDOM_STATE),
                "verbose": 0,
                "random_state": DriftDetectionModel.RANDOM_STATE,
                "return_train_score": True,
                "callback": callback,
                "progress_bar": progress_bar,
                "model_stage": DriftModelStage.CREATE_OPTIMIZED_DRIFT_MODEL.value
            }

            classifier = GradientBoostingClassifier(**model_params)

            clf = CustomRandomSearch(
                classifier, parameters, **randomized_params)
            clf.fit(ddm_train, ddm_train_y)
            self.dd_model = clf.best_estimator_
        else:
            # If total elements are less than 1M, use 0.05 as learning rate
            # else 0.1
            learning_rate = 0.05 if ddm_train.shape[0] * \
                ddm_train.shape[1] < 1000000 else 0.1

            initial_parameters = {
                "random_state": DriftDetectionModel.RANDOM_STATE,
                "learning_rate": learning_rate,
                "n_estimators": 1500,
                "verbose": 0,
                "n_iter_no_change": 5,
                "min_samples_split": 0.005,
                "min_samples_leaf": 0.0005,
                "max_leaf_nodes": 10
            }

            if callback:
                callback(DriftModelStage.CREATE_DRIFT_MODEL.value)
            self.dd_model = GradientBoostingClassifier(**initial_parameters)

            self.dd_model.fit(ddm_train, ddm_train_y)

        # Score the test subset
        if callback:
            callback(DriftModelStage.SCORE_SPLIT_TEST_DATA.value)
        test_probabilities, test_predictions = self._split_and_score(
            score, test_df, batch_size, progress_bar)

        if train_y_df.dtype == "object":
            test_predictions = pd.Series(
                test_predictions).astype(str).str.lower()
            test_y_df = test_y_df.astype(str).str.lower()

        # Calculate base client model accuracy
        self.base_client_accuracy = accuracy_score(test_y_df, test_predictions)

        # Prepare the test data to score against drift detection model
        ddm_test = pd.concat(
            [test_df, self._get_probability_dataframe(test_probabilities)], axis=1)

        for feature in self.categorical_columns:
            le = LabelEncoder()
            le.fit(self.categorical_map[feature])
            ddm_test.loc[:, feature] = le.transform(ddm_test[feature])

        ddm_test_predictions = self.dd_model.predict(ddm_test)

        # Calculate base predicted accuracy
        self.base_predicted_accuracy = sum(
            ddm_test_predictions) / len(ddm_test_predictions)

    @staticmethod
    def create_model_tar(drift_detection_model, constraints=None, ddm_properties=None, path_prefix=".",
                         file_name="drift_detection_model.tar.gz"):
        """Creates a tar file with the drift detection model and constraints

        Arguments:
            drift_detection_model {DriftDetectionModel} -- the drift detection model to save
            constraints - column constraints
            ddm_properties - ddm properties to be referred in case of exceptions/warnings

        Keyword Arguments:
            path_prefix {str} -- path of the directory to save the file (default: {"."})
            file_name {str} -- name of the tar file (default: {"drift_detection_model.tar.gz"})

        Raises:
            Exception: If there is an issue while creating directory, pickling the model or creating the tar file
        """
        try:
            os.makedirs(path_prefix, exist_ok=True)

            with tarfile.open(file_name, mode="w:gz") as model_tar:
                if drift_detection_model:
                    model_pkl = io.BytesIO(pickle.dumps(drift_detection_model))
                    if model_pkl:
                        tarinfo = tarfile.TarInfo("drift_detection_model.pkl")
                        tarinfo.size = len(model_pkl.getvalue())
                        model_tar.addfile(tarinfo=tarinfo, fileobj=model_pkl)

                if ddm_properties is None:
                    ddm_properties = {}
                ddm_properties["drift_model_version"] = "scikit-learn-{}".format(
                    sklearn.__version__)

                ddm_properties_json = io.BytesIO(json.dumps(
                    ddm_properties, indent=4).encode('utf8'))
                tarinfo = tarfile.TarInfo("ddm_properties.json")
                tarinfo.size = len(ddm_properties_json.getvalue())
                model_tar.addfile(
                    tarinfo=tarinfo, fileobj=ddm_properties_json)

                if constraints:
                    constraints_json = io.BytesIO(json.dumps(
                        constraints, indent=4).encode('utf8'))
                    tarinfo = tarfile.TarInfo("data_drift_constraints.json")
                    tarinfo.size = len(constraints_json.getvalue())
                    model_tar.addfile(
                        tarinfo=tarinfo, fileobj=constraints_json)

        except (OSError, pickle.PickleError, tarfile.TarError):
            raise Exception(
                "There was a problem creating tar file for drift detection model.")


class CustomRandomSearch(RandomizedSearchCV):
    _required_parameters = ["estimator", "param_distributions"]

    def __init__(self, estimator, param_distributions, progress_bar=True, callback=None, n_iter=10, scoring=None,
                 n_jobs=None, refit=True, cv="warn", verbose=0, pre_dispatch="2*n_jobs",
                 random_state=None, error_score="raise", return_train_score=False, model_stage=None):
        self.param_distributions = param_distributions
        self.n_iter = n_iter
        self.random_state = random_state
        self.progress_bar = progress_bar
        self.callback = callback
        self.model_stage = model_stage
        super().__init__(
            estimator=estimator, param_distributions=self.param_distributions,
            n_iter=self.n_iter, random_state=self.random_state,
            scoring=scoring,
            n_jobs=n_jobs, refit=refit, cv=cv, verbose=verbose,
            pre_dispatch=pre_dispatch, error_score=error_score,
            return_train_score=return_train_score)

    def _run_search(self, evaluate_candidates):
        """Search n_iter candidates from param_distributions"""
        params = list(ParameterSampler(self.param_distributions,
                                       self.n_iter, random_state=self.random_state))
        for idx, param in enumerate(tqdm(params, desc="Optimising Drift Detection Model...", file=sys.stdout,
                                         unit="models", dynamic_ncols=True, disable=not (self.progress_bar))):
            start_time = time.time() * 1000
            evaluate_candidates([param])
            if self.callback:
                stop = self.callback(self.model_stage, progress_step=idx+1,
                                     progress_total_count=len(params), start_time=start_time)  # idx starts at 0
                if stop:
                    break


class DriftModelStage(Enum):
    """Enumerated type for different stages involved in drift model creation."""
    READ_TRN_DATA = "READ_TRN_DATA"
    SCORE_SPLIT_TRN_DATA = "SCORE_SPLIT_TRN_DATA"
    SCORE_SPLIT_TEST_DATA = "SCORE_SPLIT_TEST_DATA"
    CREATE_DRIFT_MODEL = "CREATE_DRIFT_MODEL"
    CREATE_OPTIMIZED_DRIFT_MODEL = "CREATE_OPTIMIZED_DRIFT_MODEL"
    STORE_DRIFT_MODEL = "STORE_DRIFT_MODEL"
    DRIFT_MODEL_COMPLETE = "DRIFT_MODEL_COMPLETE"
    DRIFT_MODEL_TRAINING_FAILED = "DRIFT_MODEL_TRAINING_FAILED"
    POORLY_TRAINED_DRIFT_MODEL = "POORLY_TRAINED_DRIFT_MODEL"


class DriftException(Exception):
    pass
