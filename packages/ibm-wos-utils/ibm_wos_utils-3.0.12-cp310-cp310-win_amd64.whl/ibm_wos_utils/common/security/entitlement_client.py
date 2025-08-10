# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023, 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.joblib.utils.rest_util import RestUtil
from ibm_wos_utils.joblib.utils.python_utils import get


class EntitlementClient:

    def __init__(self, bearer_token, data_mart_id, accept_language, project_id, space_id, enable_task_credentials=None):
        self.bearer_token = bearer_token
        self.data_mart_id = data_mart_id
        self.project_id = project_id
        self.space_id = space_id
        self.accept_language = accept_language
        self.entitlements_url = "{}/v1/entitlements".format(
            Env.get_gateway_url())
        self.enable_task_credentials = enable_task_credentials

    def get_entitlement(self):
        query_params = self.__get_query_params()
        url = "{}?{}".format(self.entitlements_url, query_params)
        response = RestUtil.request_with_retry(verify_ssl=True).get(url,
                                                                    headers=self.__get_headers())
        if not response.ok:
            raise Exception("Failed while getting user entitlement.")

        entitlements = []
        os_entitlements = get(
            response.json(), "entitlements.ai_openscale", None)
        if os_entitlements:
            entitlements = [
                i for i in os_entitlements if i.get("id") == self.data_mart_id]
            if not entitlements:
                entitlements = [i for i in os_entitlements if i.get(
                    "service_instance_guid") == self.data_mart_id]

        if len(entitlements) == 0:
            raise Exception("The user entitlement does not exist.")

        return entitlements[0]

    def __get_query_params(self):
        query_params = ["instance_id="+self.data_mart_id]
        if self.project_id:
            query_params.append("project_id="+self.project_id)
        if self.space_id:
            query_params.append("space_id="+self.space_id)
        if self.enable_task_credentials:
            query_params.append("enable_task_credentials="+str(self.enable_task_credentials).lower())
        return "&".join(query_params)

    def __get_headers(self):
        headers = {"Authorization": self.bearer_token,
                   "Accept": "application/json",
                   "Content-Type": "application/json",
                   "Accept-Language": self.accept_language}
        return headers
