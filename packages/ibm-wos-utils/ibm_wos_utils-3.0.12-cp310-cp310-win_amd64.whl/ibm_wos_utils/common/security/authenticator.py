# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import re
from threading import RLock

import jwt
from jwt.api_jwk import PyJWK

from ibm_wos_utils.joblib.utils.environment import Environment as Env
from ibm_wos_utils.joblib.utils.rest_util import RestUtil
from ibm_wos_utils.joblib.utils.constants import SERVICE_ID
from cachetools import cached, TTLCache

ALL_ASYMMETRIC_ALGORITHMS = ["RS256", "RS384",
                             "RS512", "ES256", "ES384", "ES512"]
INTERNAL_SERVICE = "internal-service"
AIOS_SERVICE_CREDENTIALS_PATH = "/etc/.secrets/svc-pwd"


class Authenticator():
    """Class to authenticate the user token."""

    def __init__(self, bearer_token, verify_exp: bool=True):
        self.access_token = bearer_token
        self.is_cpd = Env.is_cpd()
        self.iam_public_keys_url = Env.get_cpd_iam_public_keys_url(
        ) if self.is_cpd else Env.get_cloud_iam_public_keys_url()
        self.verify_exp = verify_exp

    @property
    def access_token(self):
        return self.__access_token

    @access_token.setter
    def access_token(self, bearer_token):
        if not bearer_token:
            raise ValueError("The IAM token is invalid.")

        token = re.search("[B|b]earer(.*)", bearer_token)
        if not token:
            raise ValueError("The IAM token is invalid.")

        self.__access_token = token.group(1).strip()

    @property
    def iam_public_keys_url(self):
        return self.__iam_public_keys_url

    @iam_public_keys_url.setter
    def iam_public_keys_url(self, iam_public_keys_url):
        if not iam_public_keys_url:
            raise ValueError("The IAM public keys url is invalid.")

        self.__iam_public_keys_url = iam_public_keys_url

    def authenticate(self):
        try:
            if self.is_cpd:
                authenticator = CPDTokenAuthenticator(access_token=self.access_token,
                                                      iam_public_keys_url=self.iam_public_keys_url, verify_exp=self.verify_exp)
            else:
                authenticator = CloudTokenAuthenticator(access_token=self.access_token,
                                                        iam_public_keys_url=self.iam_public_keys_url, verify_exp=self.verify_exp)

            return authenticator.validate()
        except jwt.ExpiredSignatureError as e:
            raise ValueError("The IAM Token expired.")
        except (jwt.InvalidAlgorithmError, TypeError, UnboundLocalError) as e:
            raise ValueError("The IAM token is invalid.")


class CloudTokenAuthenticator():
    """Class to authenticate the access token in Cloud environment."""

    def __init__(self, access_token, iam_public_keys_url, verify_exp: bool=True):
        self.access_token = access_token
        self.iam_public_keys_url = iam_public_keys_url
        self.verify_exp = verify_exp

    def validate(self):
        pubkey = get_cloud_pubkey(
            self.access_token, self.iam_public_keys_url)
        options = {
            "verify_iat": False,
            "verify_exp": self.verify_exp,
            "verify_aud": False
        }
        return jwt.decode(jwt=self.access_token,
                          key=pubkey,
                          algorithms=ALL_ASYMMETRIC_ALGORITHMS,
                          options=options)


class CPDTokenAuthenticator():
    """Class to authenticate the access token in CPD environment."""

    def __init__(self, access_token, iam_public_keys_url, verify_exp: bool=True):
        self.access_token = access_token
        self.iam_public_keys_url = iam_public_keys_url
        self.verify_exp = verify_exp

    def validate(self):
        user_info = {}
        # Check whether the token starts with aios in CPD environment
        if self.access_token.startswith("aios-"):
            with open(AIOS_SERVICE_CREDENTIALS_PATH, "r") as f:
                service_creds = f.read()

            if self.access_token != service_creds:
                raise ValueError("The service access token is invalid.")

            user_info.update({"name": INTERNAL_SERVICE,
                              "email": INTERNAL_SERVICE,
                              "sub": INTERNAL_SERVICE,
                              "sub_type": SERVICE_ID,
                              "iam_id": INTERNAL_SERVICE,
                              "account": {"bss": INTERNAL_SERVICE}
                              })
        else:
            pubkey = get_cpd_pubkey(self.iam_public_keys_url)
            options = {
                "verify_iat": False,
                "verify_aud": False,
                "verify_exp": self.verify_exp
            }
            payload = jwt.decode(jwt=self.access_token,
                                 key=pubkey,
                                 algorithms=ALL_ASYMMETRIC_ALGORITHMS,
                                 options=options)

            user_info.update({"name": payload.get("username"),
                              "email": payload.get("email"),
                              "sub": payload.get("sub"),
                              "iam_id": payload.get("uid"),
                              "account": {"bss": payload.get("uid")},
                              "iat": payload.get("iat"),
                              "exp": payload.get("exp"),
                              })

        return user_info


cloud_pubkey_cache_lock = RLock()


@cached(cache=TTLCache(maxsize=1024, ttl=7200), lock=cloud_pubkey_cache_lock)
def get_cloud_pubkey(access_token, iam_public_keys_url):
    jwt_header = jwt.get_unverified_header(access_token)

    try:
        kid = jwt_header["kid"]
    except Exception as e:
        raise ValueError("The IAM token is invalid.")

    # fetch public keys by making Http request to jwks url
    response = RestUtil.request_with_retry(
        verify_ssl=True).get(iam_public_keys_url)
    if response.ok:
        fetched_keys = []
        
        fetched_resp = response.json()
        if fetched_resp is not None and isinstance(fetched_resp, list):
            fetched_keys = fetched_resp
        if fetched_resp is not None and isinstance(fetched_resp, dict):
            if fetched_resp.get("keys"):
                fetched_keys = fetched_resp.get("keys")

        signing_key = next(
            (key for key in fetched_keys if key["kid"] == kid), None)

        # It can happen that the expected "kid" is not found in the list
        if signing_key is None or signing_key["n"] is None or signing_key["e"] is None:
            raise ValueError("The IAM token is invalid.")

        py_signing_key = PyJWK(signing_key, algorithm=signing_key["alg"])
        return py_signing_key.key

    else:
        raise Exception("Failed while getting IAM public keys.")


cpd_pubkey_cache_lock = RLock()


@cached(cache=TTLCache(maxsize=1024, ttl=7200), lock=cpd_pubkey_cache_lock)
def get_cpd_pubkey(iam_public_keys_url):
    # fetch public keys by making Http request to jwks url
    response = RestUtil.request_with_retry(
        verify_ssl=False).get(iam_public_keys_url)
    if response.ok:
        return response.content.decode("utf-8")

    raise Exception("Failed while getting IAM public keys.")
