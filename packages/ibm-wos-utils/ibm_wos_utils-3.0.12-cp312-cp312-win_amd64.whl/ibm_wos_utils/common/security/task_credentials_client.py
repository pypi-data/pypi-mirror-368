# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2024
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.joblib.utils.rest_util import RestUtil
from ibm_wos_utils.joblib.exceptions.client_errors import *

class TaskCredentialsClient:

    def __init__(self, bearer_token, account_id, iam_id):
        self.bearer_token = bearer_token
        self.apikey_url = "{}/openscale/v2/credentials/{}?iam_id={}".format(
        Env.get_gateway_url(), account_id, iam_id)

    def get_apikey(self):

        headers = {
            "Authorization": "bearer {}".format(self.bearer_token)
        }

        response = RestUtil.request().get(
            url=self.apikey_url, headers=headers)

        if response.ok:
            apikey = response.json().get("api_key")
        else:
            if response.status_code == 401:
                raise AuthenticationError(
                    "The credentials provided to get apiKey are invalid.", response)
            elif response.status_code == 404:
                raise ObjectNotFoundError(
                    "ApiKey is not found", response)
            else:
                raise DependentServiceError(
                    "Getting apiKey has failed", response)

        return apikey
