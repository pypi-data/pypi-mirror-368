import logging
from typing import Optional

from chainsaws.aws.shared import session
from chainsaws.aws.cognito_identity._cognito_identity_internal import CognitoIdentity
from chainsaws.aws.cognito_identity.cognito_identity_models import CognitoIdentityAPIConfig
from chainsaws.aws.cognito_identity.request.CreateIdentityPoolRequest import CreateIdentityPoolRequest
from chainsaws.aws.cognito_identity.request.SetIdentityPoolRolesRequest import SetIdentityPoolRolesRequest
from chainsaws.aws.cognito_identity.response.CreateIdentityPoolResponse import CreateIdentityPoolResponse
from chainsaws.aws.cognito_identity.response.SetIdentityPoolRolesResponse import SetIdentityPoolRolesResponse
from chainsaws.aws.cognito_identity.response.GetIdentityPoolResponse import GetIdentityPoolResponse
from chainsaws.aws.cognito_identity.request.GetIdRequest import GetIdRequest
from chainsaws.aws.cognito_identity.response.GetIdResponse import GetIdResponse
from chainsaws.aws.cognito_identity.request.GetCredentialsForIdentityRequest import GetCredentialsForIdentityRequest
from chainsaws.aws.cognito_identity.response.GetCredentialsForIdentityResponse import GetCredentialsForIdentityResponse
from chainsaws.aws.cognito_identity.request.LookupDeveloperIdentityRequest import LookupDeveloperIdentityRequest
from chainsaws.aws.cognito_identity.response.LookupDeveloperIdentityResponse import LookupDeveloperIdentityResponse
from chainsaws.aws.cognito_identity.request.MergeDeveloperIdentitiesRequest import MergeDeveloperIdentitiesRequest
from chainsaws.aws.cognito_identity.response.MergeDeveloperIdentitiesResponse import MergeDeveloperIdentitiesResponse
from chainsaws.aws.cognito_identity.request.UnlinkDeveloperIdentityRequest import UnlinkDeveloperIdentityRequest

logger = logging.getLogger(__name__)


class CognitoIdentityAPI:
    def __init__(self, config: Optional[CognitoIdentityAPIConfig] = None) -> None:
        self.config = config or CognitoIdentityAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.identity = CognitoIdentity(self.boto3_session, config=self.config)

    def create_identity_pool(self, cfg: CreateIdentityPoolRequest) -> CreateIdentityPoolResponse:
        resp = self.identity.create_identity_pool(cfg)
        result: CreateIdentityPoolResponse = {
            "IdentityPoolId": resp.get("IdentityPoolId", ""),
            "IdentityPoolName": resp.get("IdentityPoolName", ""),
            "AllowUnauthenticatedIdentities": resp.get("AllowUnauthenticatedIdentities", False),
        }
        for key in (
            "CognitoIdentityProviders",
            "DeveloperProviderName",
            "SupportedLoginProviders",
            "OpenIdConnectProviderARNs",
            "SamlProviderARNs",
            "IdentityPoolTags",
        ):
            if key in resp:
                result[key] = resp[key]
        return result

    def set_identity_pool_roles(self, cfg: SetIdentityPoolRolesRequest) -> SetIdentityPoolRolesResponse:
        self.identity.set_identity_pool_roles(cfg)
        return {"Success": True}

    def get_identity_pool(self, identity_pool_id: str) -> GetIdentityPoolResponse:
        resp = self.identity.describe_identity_pool(identity_pool_id)
        result: GetIdentityPoolResponse = {
            "IdentityPoolId": resp.get("IdentityPoolId", ""),
            "IdentityPoolName": resp.get("IdentityPoolName", ""),
            "AllowUnauthenticatedIdentities": resp.get("AllowUnauthenticatedIdentities", False),
        }
        for key in (
            "CognitoIdentityProviders",
            "DeveloperProviderName",
            "SupportedLoginProviders",
            "OpenIdConnectProviderARNs",
            "SamlProviderARNs",
            "IdentityPoolTags",
        ):
            if key in resp:
                result[key] = resp[key]
        return result

    def delete_identity_pool(self, identity_pool_id: str) -> None:
        self.identity.delete_identity_pool(identity_pool_id)

    # Credentials flow helpers
    def get_id(self, req: GetIdRequest) -> GetIdResponse:
        resp = self.identity.get_id(req)
        return {"IdentityId": resp.get("IdentityId", "")}

    def get_credentials_for_identity(self, req: GetCredentialsForIdentityRequest) -> GetCredentialsForIdentityResponse:
        resp = self.identity.get_credentials_for_identity(req)
        creds = resp.get("Credentials", {})
        return {
            "IdentityId": resp.get("IdentityId", ""),
            "Credentials": {
                "AccessKeyId": creds.get("AccessKeyId", ""),
                "SecretKey": creds.get("SecretKey", ""),
                "SessionToken": creds.get("SessionToken", ""),
                "Expiration": creds.get("Expiration", 0.0).timestamp() if hasattr(creds.get("Expiration", None), "timestamp") else creds.get("Expiration", 0.0),
            },
        }

    # Developer identity APIs
    def lookup_developer_identity(self, req: LookupDeveloperIdentityRequest) -> LookupDeveloperIdentityResponse:
        resp = self.identity.lookup_developer_identity(req)
        result: LookupDeveloperIdentityResponse = {
            "IdentityId": resp.get("IdentityId", ""),
        }
        if "DeveloperUserIdentifierList" in resp:
            result["DeveloperUserIdentifierList"] = resp["DeveloperUserIdentifierList"]
        if "NextToken" in resp:
            result["NextToken"] = resp["NextToken"]
        return result

    def merge_developer_identities(self, req: MergeDeveloperIdentitiesRequest) -> MergeDeveloperIdentitiesResponse:
        resp = self.identity.merge_developer_identities(req)
        return {"IdentityId": resp.get("IdentityId", "")}

    def unlink_developer_identity(self, req: UnlinkDeveloperIdentityRequest) -> None:
        self.identity.unlink_developer_identity(req)


