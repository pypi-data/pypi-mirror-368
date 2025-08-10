# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2019, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import io
import json
import logging
import pickle
import sklearn
import tarfile
import warnings

from io import BytesIO

from service.core.constraints.manager import DataConstraintMgr
from service.core.entity.drift_detection_model import DriftDetectionModel


class DriftTrainer():
    """
        Wrapper class to validate the input and provide methods to train drift model and archive it. This class is packaged in ibm_wos_utils library and used in notebook.
    """

    def __init__(self, training_dataframe, drift_detection_input):
        self.enable_drift = drift_detection_input.get("enable_drift", True)
        if not self.enable_drift:
            return

        initial_level = logging.getLogger().getEffectiveLevel()

        updated_level = logging.getLogger().getEffectiveLevel()

        if initial_level != updated_level:
            logging.basicConfig(level=initial_level)

        self._enable_model_drift = False
        self._enable_data_drift = False

        self._validate_drift_input(training_dataframe, drift_detection_input)
        self.training_data_frame = training_dataframe

        self.label_column = drift_detection_input.get("label_column")
        self.feature_columns = drift_detection_input.get("feature_columns")
        self.categorical_columns = drift_detection_input.get(
            "categorical_columns")

        self.drift_detection_model = None
        self.constraints = None

        self.ddm_message = None
        self.ddm_properties = None

        # model drift
        model_drift_parameters = drift_detection_input.get("model_drift", {})
        self.optimise = model_drift_parameters.get("optimise", True)
        self.score = model_drift_parameters.get("score")
        self.batch_size = model_drift_parameters.get("batch_size", 5000)

        self.check_for_ddm_quality = model_drift_parameters.get("check_for_ddm_quality")
        self.check_for_ddm_quality = False if \
            self.check_for_ddm_quality in [False, "false", "False", 0] else True
        self.ddm_quality_check_threshold = model_drift_parameters.get("ddm_quality_check_threshold", 0.3)

        # data drift
        data_drift_parameters = drift_detection_input.get("data_drift", {})
        self.two_column_learner_limit = data_drift_parameters.get("two_column_learner_limit", 200)
        self.categorical_unique_threshold = data_drift_parameters.get("categorical_unique_threshold", 0.8)
        self.user_overrides = data_drift_parameters.get("user_overrides", [])

    def _validate_drift_input(self, training_data_frame, drift_detection_input):
        problem_type = drift_detection_input.get("problem_type")
        model_drift_supported_problem_types = ["binary", "multiclass"]
        data_drift_supported_problem_types = [
            "binary", "multiclass", "regression"]

        if problem_type in model_drift_supported_problem_types:
            self._enable_model_drift = True
            # set check_for_ddm_quality toggle
            if self._enable_model_drift:
                self.check_for_ddm_quality = drift_detection_input.get(
                    "check_for_ddm_quality")

        if problem_type in data_drift_supported_problem_types:
            self._enable_data_drift = True

        if not self._enable_model_drift and not self._enable_data_drift:
            raise Exception(
                "Drift detection is not supported for {}. Supported types for model drift are: {}. "
                "Supported types for data drift are: {}".format(problem_type, model_drift_supported_problem_types, data_drift_supported_problem_types))

        columns_from_data_frame = list(training_data_frame.columns.values)
        label_column = drift_detection_input.get("label_column")
        if label_column not in columns_from_data_frame:
            raise Exception(
                "'label_column':{} missing in training data".format(label_column))

        feature_columns = drift_detection_input.get(
            "feature_columns")
        if feature_columns is None or type(feature_columns) is not list or len(feature_columns) == 0:
            raise Exception("'feature_columns should be a non empty list")

        check_feature_column_existence = list(
            set(feature_columns) - set(columns_from_data_frame))
        if len(check_feature_column_existence) > 0:
            raise Exception("Feature columns missing in training data.Details:{}".format(
                check_feature_column_existence))

        categorical_columns = drift_detection_input.get(
            "categorical_columns")

        if categorical_columns is not None and type(categorical_columns) is not list:
            raise Exception(
                "'categorical_columns' should be a list of values")

        # Verify existence of  categorical columns in feature columns
        if categorical_columns is not None and len(categorical_columns) > 0:
            check_cat_col_existence = list(
                set(categorical_columns) - set(feature_columns))
            if len(check_cat_col_existence) > 0:
                raise Exception("'categorical_columns' should be subset of feature columns.Details:{}".format(
                    check_cat_col_existence))

    def generate_drift_detection_model(self, score, optimise=True,
                                       callback=None, progress_bar=True, batch_size=5000, check_for_ddm_quality=True, ddm_quality_check_threshold=0.3):
        """Generates the drift detection model.

        Arguments:
            score {function} -- A function that accepts a dataframe with features as columns and returns a tuple of numpy array
                of probabilities array of shape `(n_samples,n_classes)` and numpy array of prediction vector of shape `(n_samples,)`

        Keyword Arguments:
            optimise {bool} -- If True, does hyperparameter optimisation for the drift detection model (default: {True})
            callback {function} -- A method to call after every iteration. (default: {None})
            progress_bar {bool} -- If True, shows progress bars. (default: {True})
            batch_size {int} -- Number of rows to score at a time. (default: {5000})
            check_for_ddm_quality {bool} -- If True, check for DDM training quality. (default: {True})
            ddm_quality_check_threshold {int} -- DDM quality threshold check. (default: {0.3})
        """

        if self._enable_model_drift:
            input_df = self.training_data_frame.copy()
            self.drift_detection_model = DriftDetectionModel(self.label_column,
                                                             self.feature_columns, self.categorical_columns)
            self.drift_detection_model.generate(
                score, input_df, optimise, callback, progress_bar, batch_size)

            # Check for ddm training quality if flag is set
            if check_for_ddm_quality and (abs(self.drift_detection_model.base_client_accuracy - self.drift_detection_model.base_predicted_accuracy) > ddm_quality_check_threshold):
                self.ddm_message = "The trained drift detection model did not meet quality standards . Drop in accuracy cannot be detected."
                # Create ddm json only for case of classification models and if data drift id also enabled
                if self._enable_data_drift:
                    self.ddm_properties = {
                        "model_drift_enabled": "false",
                        "base_model_accuracy": self.drift_detection_model.base_client_accuracy,
                        "base_predicted_accuracy": self.drift_detection_model.base_predicted_accuracy,
                        "message": self.ddm_message
                    }

                self.drift_detection_model = None
                self._enable_model_drift = False

                # Warn user
                warnings.warn(self.ddm_message)

    def learn_constraints(self, progress_bar=True, two_column_learner_limit=200, categorical_unique_threshold=0.8, debug=False, user_overrides=[]):
        """Learn constraints

        Keyword Arguments:
            progress_bar {bool} -- Controls the display of progress bar. (default: {True})
            two_column_learner_limit {int} -- Column limit to learn two column constraints. (default: {200})
            categorical_unique_threshold {float} -- Used to discard columns with large number of unique values relative to total rows in the column. Should be between 0 and 1. (default: {0.8})
            debug {bool} -- Prints debug information. If set to True, hides the progress bar. (default: {False})
            user_overrides {list} -- Used to override constraints to be learned on single and two columns.
        """
        if self._enable_data_drift:
            constraints_mgr = DataConstraintMgr()
            # By default column limit to generate two column constraint is 200 , column limit is provided to
            # allow user to configure the feature column count
            enable_two_col_learner = True if len(
                self.feature_columns) <= two_column_learner_limit else False
            self.constraints = constraints_mgr.learn_constraints(
                self.training_data_frame, self.feature_columns, self.categorical_columns, progress_bar, enable_two_col_learner=enable_two_col_learner, categorical_unique_threshold=categorical_unique_threshold, debug=debug, user_overrides=user_overrides)

    def create_archive(self, path_prefix=".", file_name="drift_detection_model.tar.gz"):
        """Creates a tar file with the drift detection model and constraints

        Arguments:
            path_prefix {str} -- path of the directory to save the file (default: {"."})
            file_name {str} -- name of the tar file (default: {"drift_detection_model.tar.gz"})

        Raises:
            Exception: If there is an issue while creating directory, pickling the model or creating the tar file
        """
        # Check if the archive entries exist before creating a tar
        if not self.drift_detection_model and not self.constraints:
            raise Exception(
                "Archive creation cannot proceed as drift detection model or constraints json does not exist")

        # Proceed with creating a archive
        DriftDetectionModel.create_model_tar(
            self.drift_detection_model, self.constraints.to_json() if self.constraints else None, self.ddm_properties, path_prefix, file_name)

    def run(
            self,
            persist_archive: bool = False,
            path_prefix: str = ".",
            file_name: str ="drift_detection_model.tar.gz",
            callback = None,
            debug: bool = False,
            progress_bar: bool = True):
        if not self.enable_drift:
            return

        self.generate_drift_detection_model(
            score=self.score,
            batch_size=self.batch_size,
            check_for_ddm_quality=self.check_for_ddm_quality,
            ddm_quality_check_threshold=self.ddm_quality_check_threshold,
            optimise=self.optimise,
            callback=callback,
            progress_bar=progress_bar)

        self.learn_constraints(
            two_column_learner_limit=self.two_column_learner_limit,
            categorical_unique_threshold=self.categorical_unique_threshold,
            debug=debug,
            user_overrides=self.user_overrides,
            progress_bar=progress_bar)

        if not persist_archive:
            return self.get_archive()

        self.create_archive(
            path_prefix=path_prefix,
            file_name=file_name)

    def get_archive(self):
        if not self.drift_detection_model and not self.constraints:
            return None

        archive_data = None
        with BytesIO() as archive:
            with tarfile.open(fileobj=archive, mode="w:gz") as model_tar:
                if self.drift_detection_model:
                    model_pkl = io.BytesIO(pickle.dumps(self.drift_detection_model))
                    if model_pkl:
                        tarinfo = tarfile.TarInfo("drift_detection_model.pkl")
                        tarinfo.size = len(model_pkl.getvalue())
                        model_tar.addfile(tarinfo=tarinfo, fileobj=model_pkl)

                if self.ddm_properties is None:
                    self.ddm_properties = {}
                self.ddm_properties["drift_model_version"] = "scikit-learn-{}".format(sklearn.__version__)

                self.ddm_properties_json = io.BytesIO(json.dumps(
                    self.ddm_properties, indent=4).encode('utf8'))
                tarinfo = tarfile.TarInfo("ddm_properties.json")
                tarinfo.size = len(self.ddm_properties_json.getvalue())
                model_tar.addfile(
                    tarinfo=tarinfo, fileobj=self.ddm_properties_json)

                if self.constraints:
                    constraints_json = io.BytesIO(json.dumps(
                        self.constraints.to_json(), indent=4).encode('utf8'))
                    tarinfo = tarfile.TarInfo("data_drift_constraints.json")
                    tarinfo.size = len(constraints_json.getvalue())
                    model_tar.addfile(
                        tarinfo=tarinfo, fileobj=constraints_json)
            archive_data = archive.getvalue()

        return archive_data

    @staticmethod
    def create_model_tar(drift_detection_model, constraints=None, path_prefix=".",
                         file_name="drift_detection_model.tar.gz"):
        warnings.warn(
            "Call to deprecated method. This method will be removed in the next release.", DeprecationWarning)
        DriftDetectionModel.create_model_tar(
            drift_detection_model, constraints.to_json() if constraints else None, path_prefix, file_name)