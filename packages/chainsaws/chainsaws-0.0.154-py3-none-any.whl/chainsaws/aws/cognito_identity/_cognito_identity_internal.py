import logging
from typing import Optional

from boto3.session import Session
from botocore.config import Config
from botocore.exceptions import ClientError

from chainsaws.aws.cognito_identity.cognito_identity_models import (
    CognitoIdentityAPIConfig,
)
from chainsaws.aws.cognito_identity.request.CreateIdentityPoolRequest import CreateIdentityPoolRequest
from chainsaws.aws.cognito_identity.request.SetIdentityPoolRolesRequest import SetIdentityPoolRolesRequest
from chainsaws.aws.cognito_identity.request.GetIdRequest import GetIdRequest
from chainsaws.aws.cognito_identity.request.GetCredentialsForIdentityRequest import (
    GetCredentialsForIdentityRequest,
)
from chainsaws.aws.cognito_identity.request.LookupDeveloperIdentityRequest import LookupDeveloperIdentityRequest
from chainsaws.aws.cognito_identity.request.MergeDeveloperIdentitiesRequest import MergeDeveloperIdentitiesRequest
from chainsaws.aws.cognito_identity.request.UnlinkDeveloperIdentityRequest import UnlinkDeveloperIdentityRequest
from chainsaws.aws.cognito_identity.cognito_identity_exception import (
    CognitoIdentityException,
    CognitoIdentityInvalidParameterException,
    CognitoIdentityResourceNotFoundException,
    CognitoIdentityNotAuthorizedException,
    CognitoIdentityTooManyRequestsException,
    CognitoIdentityInternalErrorException,
    CognitoIdentityLimitExceededException,
    CognitoIdentityExternalServiceException,
    CognitoIdentityDeveloperUserAlreadyRegisteredException,
    CognitoIdentityResourceConflictException,
    CognitoIdentityInvalidIdentityPoolConfigurationException,
)

logger = logging.getLogger(__name__)


class CognitoIdentity:
    """Low-level thin wrapper over boto3 cognito-identity client."""

    def __init__(self, boto3_session: Session, config: Optional[CognitoIdentityAPIConfig] = None) -> None:
        self.config = config or CognitoIdentityAPIConfig()
        client_config = Config(region_name=self.config.region)
        self.client = boto3_session.client("cognito-identity", config=client_config, region_name=self.config.region)

    def create_identity_pool(self, cfg: CreateIdentityPoolRequest) -> dict:
        try:
            return self.client.create_identity_pool(**cfg)  # type: ignore[arg-type]
        except ClientError as e:
            raise self._map_client_error(e)

    def set_identity_pool_roles(self, cfg: SetIdentityPoolRolesRequest) -> None:
        try:
            self.client.set_identity_pool_roles(**cfg)  # type: ignore[arg-type]
        except ClientError as e:
            raise self._map_client_error(e)

    def describe_identity_pool(self, identity_pool_id: str) -> dict:
        try:
            return self.client.describe_identity_pool(IdentityPoolId=identity_pool_id)
        except ClientError as e:
            raise self._map_client_error(e)

    def delete_identity_pool(self, identity_pool_id: str) -> None:
        try:
            self.client.delete_identity_pool(IdentityPoolId=identity_pool_id)
        except ClientError as e:
            raise self._map_client_error(e)

    def get_id(self, req: GetIdRequest) -> dict:
        try:
            return self.client.get_id(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def get_credentials_for_identity(self, req: GetCredentialsForIdentityRequest) -> dict:
        try:
            return self.client.get_credentials_for_identity(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def lookup_developer_identity(self, req: LookupDeveloperIdentityRequest) -> dict:
        try:
            return self.client.lookup_developer_identity(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def merge_developer_identities(self, req: MergeDeveloperIdentitiesRequest) -> dict:
        try:
            return self.client.merge_developer_identities(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def unlink_developer_identity(self, req: UnlinkDeveloperIdentityRequest) -> None:
        try:
            self.client.unlink_developer_identity(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def _map_client_error(self, err: ClientError) -> CognitoIdentityException:
        code = err.response.get("Error", {}).get("Code", "")
        mapping: dict[str, type[CognitoIdentityException]] = {
            "InvalidParameterException": CognitoIdentityInvalidParameterException,
            "ResourceNotFoundException": CognitoIdentityResourceNotFoundException,
            "NotAuthorizedException": CognitoIdentityNotAuthorizedException,
            "TooManyRequestsException": CognitoIdentityTooManyRequestsException,
            "InternalErrorException": CognitoIdentityInternalErrorException,
            "LimitExceededException": CognitoIdentityLimitExceededException,
            "ExternalServiceException": CognitoIdentityExternalServiceException,
            "DeveloperUserAlreadyRegisteredException": CognitoIdentityDeveloperUserAlreadyRegisteredException,
            "ResourceConflictException": CognitoIdentityResourceConflictException,
            "InvalidIdentityPoolConfigurationException": CognitoIdentityInvalidIdentityPoolConfigurationException,
        }
        exc_cls = mapping.get(code, CognitoIdentityException)
        return exc_cls(str(err))


