# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2023
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from ibm_wos_utils.joblib.utils.constants import SERVICE_ID


class User():
    """
    Class that holds the user information
    """

    def __init__(self, user):

        if user.get("authn"):
            self.iam_id = user.get("authn").get("iam_id")
            self.name = user.get("authn").get("name")
            self.email = user.get("authn").get(
                "email") or user.get("authn").get("sub")
            self.sub = user.get("authn").get("sub")
        else:
            self.iam_id = user.get("iam_id") or user.get("sub")
            self.name = user.get("displayName") or user.get("name")
            self.email = user.get("email") or user.get("sub")
            self.sub = user.get("sub")

        if user.get("account"):
            self.bss_account_id = user.get("account").get("bss")
        else:
            self.bss_account_id = user.get("accountId")

        self.identifier = user.get("identifier") or user.get("sub")
        if user.get("idp"):
            self.realm_name = user.get("idp").get("realmName")
        else:
            self.realm_name = user.get("realmid")
        
        self.is_service_id = user.get("sub_type") or user.get("entityType")
        self.iat = user.get("iat")
        self.exp = user.get("exp")
        self.plan_name = None
        self.plan_id = None
        self.crn = None

    @property
    def is_service_id(self):
        return self.__is_service_id

    @is_service_id.setter
    def is_service_id(self, type):
        if type and type.lower() == SERVICE_ID.lower():
            self.__is_service_id = True
        else:
            self.__is_service_id = False
