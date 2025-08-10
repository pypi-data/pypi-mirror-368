# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023, 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from ibm_wos_utils.common.activity_tracking.activity_tracker import ActivityTracker
from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.common.security.authenticator import Authenticator
from ibm_wos_utils.common.security.user import User
from ibm_wos_utils.common.security.entitlement_client import EntitlementClient


class Auth:
    """Class to validate the user and user permissions for the operation.

    Arguments:
        data_mart_id: The data mart id
        request: The request object. Below attributes are used from the request object
            endpoint: The request endpoint
            method: The HTTP request method
            headers: The HTTP request headers
            args: The arguments from URL
        endpoints_roles_map: The dictionary with request endpoint as key and roles permission as value
            Eg: {
                    "api.ExplanationTasks_explanation_tasks": {
                        "permissions": {
                            "administrator": ["get","post", "put","delete"],
                            "editor": ["get", "put", "delete"],
                            "viewer": ["get"]
                        }
                    }
                }
        service_ids_allowlist: The list of service ids allowed to perform the operation
        environment: The environment variables dictionary. Can be passed instead of setting in the environment
        Environment variables to be set
        ENABLE_ICP
        IAM_PUBLIC_KEYS_URL: Required if ENABLE_ICP is false
        ICP4D_JWT_PUBLIC_KEY_URL: Required if ENABLE_ICP is true
        AIOS_GATEWAY_URL
    """

    def __init__(self, data_mart_id, request, endpoints_roles_map, service_ids_allowlist, environment={}, is_fast_api: bool=False) -> None:
        self.data_mart_id = data_mart_id
        self.request_method = request.method
        if is_fast_api:
            self.request_endpoint = request.url.path
            self.request_path = request.url.path
        else:
            self.request_endpoint = request.endpoint
            self.request_path = request.path
        self.request_user_agent = request.headers.get("user-agent")
        if is_fast_api:
            self.bearer_token = request.headers.get("authorization")
        else:
            self.bearer_token = request.headers.get("Authorization")
        self.delegated_by = request.headers.get("X-IBM-DELEGATED-BY")
        self.accept_language = request.headers.get("Accept-Language", "en")
        if is_fast_api:
            query_params = request.query_params._dict
            self.project_id = query_params.get("project_id")
            self.space_id = query_params.get("space_id")
        else:
            self.project_id = request.args.get("project_id")
            self.space_id = request.args.get("space_id")
        self.endpoints_roles_map = endpoints_roles_map or {}
        self.service_ids_allowlist = service_ids_allowlist or []
        self.activity_tracker = ActivityTracker(self.data_mart_id)
        Env.set_environment(environment)

    def validate(self):
        """Validate the user and user permissions"""
        user = self.authenticate()
        return self.authorize(user=user)

    def authenticate(self):
        """Validates the user and returns the User object."""
        authenticator = Authenticator(self.bearer_token)
        return User(authenticator.authenticate())

    def authorize(self, user):
        """Validate the user permissions and return the User object."""
        try:
            if self.project_id and self.space_id:
                raise Exception(
                    "Both the project id and space id are provided in the request. Please provide only one of them.")

            if user.is_service_id:
                if not Env.is_cpd():
                    if not (self.service_ids_allowlist and user.sub in self.service_ids_allowlist):
                        raise Exception("The service user is not authorized.")
            else:
                self.__is_user_entitled(
                    bearer_token=self.bearer_token, user=user)

        except Exception as e:
            self.activity_tracker.log(user, "auth", "authorize", False,
                                      str(e), "ibm-wos-utils-api", "failed",
                                      self.request_path, self.request_method, 401, self.request_user_agent)
            raise e

        return user

    @property
    def data_mart_id(self):
        return self.__data_mart_id

    @data_mart_id.setter
    def data_mart_id(self, data_mart_id):
        if not data_mart_id:
            raise ValueError("The data mart id value is invalid.")

        self.__data_mart_id = data_mart_id

    @property
    def request_method(self):
        return self.__request_method

    @request_method.setter
    def request_method(self, request_method):
        if not request_method:
            raise ValueError("The request method value is invalid.")

        self.__request_method = request_method

    @property
    def request_endpoint(self):
        return self.__request_endpoint

    @request_endpoint.setter
    def request_endpoint(self, request_endpoint):
        if not request_endpoint:
            raise ValueError("The request endpoint value is invalid.")

        self.__request_endpoint = request_endpoint

    @property
    def bearer_token(self):
        return self.__bearer_token

    @bearer_token.setter
    def bearer_token(self, bearer_token):
        if not bearer_token:
            raise ValueError("The bearer token value is invalid.")

        self.__bearer_token = bearer_token

    def __is_user_entitled(self, bearer_token, user):
        entitlement_client = EntitlementClient(bearer_token=bearer_token,
                                               data_mart_id=self.data_mart_id,
                                               accept_language=self.accept_language,
                                               project_id=self.project_id,
                                               space_id=self.space_id,
                                               enable_task_credentials=Env.get_property_value("ENABLE_TASK_CREDENTIALS"))
        entitlement = entitlement_client.get_entitlement()

        endpoint_roles_map = self.endpoints_roles_map.get(
            self.request_endpoint) or {}
        endpoint_permissions = endpoint_roles_map.get("permissions") or {}
        allowed_methods = []
        for r in entitlement.get("roles"):
            role_permissions = endpoint_permissions.get(r.lower()) or []
            allowed_methods.extend(role_permissions)

        if self.request_method.lower() not in set(allowed_methods):
            raise Exception("The user is not authorized.")

        # Update user object with details from entitlement
        user.plan_name = entitlement.get("plan_name")
        user.crn = entitlement.get("crn")
        user.plan_id = entitlement.get("plan_id")
