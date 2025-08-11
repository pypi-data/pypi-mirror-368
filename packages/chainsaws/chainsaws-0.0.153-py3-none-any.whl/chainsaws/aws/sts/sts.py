import logging
from typing import Optional, Dict, Any

from chainsaws.aws.shared import session
from chainsaws.aws.sts._sts_internal import STS
from chainsaws.aws.sts.sts_models import (
    AssumedRoleCredentials,
    AssumeRoleConfig,
    FederationTokenCredentials,
    GetCallerIdentityResponse,
    GetFederationTokenConfig,
    STSAPIConfig,
    GetSessionTokenConfig,
    GetSessionTokenResponse,
    DecodeAuthorizationMessageConfig,
    DecodeAuthorizationMessageResponse,
    GetAccessKeyLastUsedConfig,
    GetAccessKeyLastUsedResponse,
    AssumeRoleWithWebIdentityConfig,
    AssumeRoleWithWebIdentityResponse,
    OAuthProviderId,
)
from chainsaws.aws.sts.sts_exceptions import (
    STSError,
    RoleAssumptionError,
    FederationTokenError,
    CallerIdentityError,
    SessionTokenError,
    AuthorizationMessageError,
    AccessKeyInfoError,
)

logger = logging.getLogger(__name__)


class STSAPI:
    """High-level STS API for AWS security token operations."""

    def __init__(self, config: Optional[STSAPIConfig] = None) -> None:
        """Initialize STS client.

        Args:
            config: Optional STS configuration

        Raises:
            STSError: If client initialization fails
        """
        try:
            self.config = config or STSAPIConfig()
            self.boto3_session = session.get_boto_session(
                self.config.credentials if self.config.credentials else None,
            )
            self.sts = STS(
                boto3_session=self.boto3_session,
                config=config,
            )
        except Exception as e:
            logger.error(f"Failed to initialize STS client: {str(e)}")
            raise STSError(f"STS client initialization failed: {str(e)}")

    def assume_role(
        self,
        role_arn: str,
        role_session_name: str,
        duration_seconds: int = 3600,
        external_id: str | None = None,
        policy: Dict[str, Any] | None = None,
        tags: Dict[str, str] | None = None,
    ) -> AssumedRoleCredentials:
        """Assume an IAM role.

        Args:
            role_arn: ARN of the role to assume
            role_session_name: Identifier for the assumed role session
            duration_seconds: Duration of the session (900-43200 seconds)
            external_id: Optional unique identifier for role assumption
            policy: Optional IAM policy to further restrict the assumed role
            tags: Optional session tags

        Returns:
            AssumedRoleCredentials containing temporary credentials

        Raises:
            RoleAssumptionError: If role assumption fails
        """
        try:
            config = AssumeRoleConfig(
                role_arn=role_arn,
                role_session_name=role_session_name,
                duration_seconds=duration_seconds,
                external_id=external_id,
                policy=policy,
                tags=tags,
            )
            return self.sts.assume_role(config)
        except Exception as e:
            logger.error(f"Failed to assume role {role_arn}: {str(e)}")
            raise RoleAssumptionError(f"Role assumption failed: {str(e)}")

    def assume_role_with_web_identity(
        self,
        role_arn: str,
        role_session_name: str,
        web_identity_token: str,
        provider_id: Optional[OAuthProviderId] = None,
        duration_seconds: int = 3600,
        policy: Dict[str, Any] | None = None,
        tags: Dict[str, str] | None = None,
    ) -> AssumeRoleWithWebIdentityResponse:
        """Assume an IAM role using web identity federation.

        Args:
            role_arn: ARN of the role to assume
            role_session_name: Identifier for the assumed role session
            web_identity_token: OAuth 2.0 access token or OpenID Connect ID token
            provider_id: Optional identifier for the OAuth 2.0 identity provider.
                        Required only for OAuth 2.0 access tokens.
                        Must be either 'www.amazon.com' or 'graph.facebook.com'.
                        Do not specify for OpenID Connect ID tokens.
            duration_seconds: Duration of the session (900-43200 seconds)
            policy: Optional IAM policy to further restrict the assumed role
            tags: Optional session tags

        Returns:
            AssumeRoleWithWebIdentityResponse containing temporary credentials

        Raises:
            RoleAssumptionError: If role assumption fails
        """
        try:
            config = AssumeRoleWithWebIdentityConfig(
                role_arn=role_arn,
                role_session_name=role_session_name,
                web_identity_token=web_identity_token,
                provider_id=provider_id,
                duration_seconds=duration_seconds,
                policy=policy,
                tags=tags,
            )
            return self.sts.assume_role_with_web_identity(config)
        except Exception as e:
            logger.error(f"Failed to assume role {role_arn} with web identity: {str(e)}")
            raise RoleAssumptionError(f"Role assumption with web identity failed: {str(e)}")

    def get_caller_identity(self) -> GetCallerIdentityResponse:
        """Get details about the IAM user or role making the call.

        Returns:
            GetCallerIdentityResponse containing caller details

        Raises:
            CallerIdentityError: If caller identity retrieval fails
        """
        try:
            return self.sts.get_caller_identity()
        except Exception as e:
            logger.error(f"Failed to get caller identity: {str(e)}")
            raise CallerIdentityError(f"Caller identity retrieval failed: {str(e)}")

    def get_federation_token(
        self,
        name: str,
        duration_seconds: int = 43200,
        policy: Dict[str, Any] | None = None,
        tags: Dict[str, str] | None = None,
    ) -> FederationTokenCredentials:
        """Get temporary credentials for federated users.

        Args:
            name: Name of the federated user
            duration_seconds: Duration of the credentials (900-129600 seconds)
            policy: Optional IAM policy for federated user
            tags: Optional session tags

        Returns:
            FederationTokenCredentials containing temporary credentials

        Raises:
            FederationTokenError: If federation token retrieval fails
        """
        try:
            config = GetFederationTokenConfig(
                name=name,
                duration_seconds=duration_seconds,
                policy=policy,
                tags=tags,
            )
            return self.sts.get_federation_token(config)
        except Exception as e:
            logger.error(f"Failed to get federation token for {name}: {str(e)}")
            raise FederationTokenError(f"Federation token retrieval failed: {str(e)}")

    def get_session_token(
        self,
        duration_seconds: int = 43200,
        serial_number: str | None = None,
        token_code: str | None = None,
    ) -> GetSessionTokenResponse:
        """Get temporary credentials for the current IAM user.

        Args:
            duration_seconds: Duration of the credentials (900-129600 seconds)
            serial_number: Serial number of the MFA device
            token_code: Token code from the MFA device

        Returns:
            GetSessionTokenResponse containing temporary credentials

        Raises:
            SessionTokenError: If session token retrieval fails
        """
        try:
            config = GetSessionTokenConfig(
                duration_seconds=duration_seconds,
                serial_number=serial_number,
                token_code=token_code,
            )
            return self.sts.get_session_token(config)
        except Exception as e:
            logger.error("Failed to get session token")
            raise SessionTokenError(f"Session token retrieval failed: {str(e)}")

    def decode_authorization_message(self, encoded_message: str) -> DecodeAuthorizationMessageResponse:
        """Decode an authorization message returned by AWS.

        Args:
            encoded_message: Encoded authorization message

        Returns:
            DecodeAuthorizationMessageResponse containing decoded message

        Raises:
            AuthorizationMessageError: If message decoding fails
        """
        try:
            config = DecodeAuthorizationMessageConfig(encoded_message=encoded_message)
            return self.sts.decode_authorization_message(config)
        except Exception as e:
            logger.error("Failed to decode authorization message")
            raise AuthorizationMessageError(f"Authorization message decoding failed: {str(e)}")

    def get_access_key_last_used(self, access_key_id: str) -> GetAccessKeyLastUsedResponse:
        """Get information about the last use of an access key.

        Args:
            access_key_id: ID of the access key

        Returns:
            GetAccessKeyLastUsedResponse containing access key usage information

        Raises:
            AccessKeyInfoError: If access key info retrieval fails
        """
        try:
            config = GetAccessKeyLastUsedConfig(access_key_id=access_key_id)
            return self.sts.get_access_key_last_used(config)
        except Exception as e:
            logger.error(f"Failed to get access key info for {access_key_id}")
            raise AccessKeyInfoError(f"Access key info retrieval failed: {str(e)}")
