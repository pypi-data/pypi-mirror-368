import logging

from boto3.session import Session

from chainsaws.aws.sts.sts_models import (
    AssumedRoleCredentials,
    AssumeRoleConfig,
    FederationTokenCredentials,
    GetCallerIdentityResponse,
    GetFederationTokenConfig,
    STSAPIConfig,
    AssumeRoleWithWebIdentityConfig,
    AssumeRoleWithWebIdentityResponse,
)

logger = logging.getLogger(__name__)


class STS:
    """Internal STS operations."""

    def __init__(self, boto3_session: Session, config: STSAPIConfig | None = None) -> None:
        self.config = config or STSAPIConfig()
        self.client = boto3_session.client("sts")

    def assume_role(self, config: AssumeRoleConfig) -> AssumedRoleCredentials:
        """Assume an IAM role."""
        try:
            response = self.client.assume_role(
                RoleArn=config.role_arn,
                RoleSessionName=config.role_session_name,
                DurationSeconds=config.duration_seconds,
                ExternalId=config.external_id,
                Policy=config.policy,
                Tags=[{"Key": k, "Value": v}
                      for k, v in (config.tags or {}).items()],
            )

            credentials = response["Credentials"]
            return AssumedRoleCredentials(
                access_key_id=credentials["AccessKeyId"],
                secret_access_key=credentials["SecretAccessKey"],
                session_token=credentials["SessionToken"],
                expiration=credentials["Expiration"].isoformat(),
            )
        except Exception:
            logger.exception("Failed to assume role")
            raise

    def assume_role_with_web_identity(
        self, config: AssumeRoleWithWebIdentityConfig
    ) -> AssumeRoleWithWebIdentityResponse:
        """Assume an IAM role using web identity federation.

        Args:
            config: Configuration for role assumption with web identity.
                   If using OAuth 2.0 access tokens, provider_id must be either
                   'www.amazon.com' or 'graph.facebook.com'.
                   Do not specify provider_id for OpenID Connect ID tokens.

        Returns:
            AssumeRoleWithWebIdentityResponse containing temporary credentials

        Raises:
            Exception: If role assumption fails
        """
        try:
            params = {
                "RoleArn": config.role_arn,
                "RoleSessionName": config.role_session_name,
                "WebIdentityToken": config.web_identity_token,
                "DurationSeconds": config.duration_seconds,
            }

            if config.provider_id:
                params["ProviderId"] = config.provider_id

            if config.policy:
                params["Policy"] = config.policy

            if config.tags:
                params["Tags"] = [{"Key": k, "Value": v} for k, v in config.tags.items()]

            response = self.client.assume_role_with_web_identity(**params)
            return AssumeRoleWithWebIdentityResponse.from_response(response)
        except Exception:
            logger.exception("Failed to assume role with web identity")
            raise

    def get_caller_identity(self) -> GetCallerIdentityResponse:
        """Get details about the IAM user or role making the call."""
        try:
            response = self.client.get_caller_identity()
            return GetCallerIdentityResponse(
                account=response["Account"],
                arn=response["Arn"],
                user_id=response["UserId"],
            )
        except Exception:
            logger.exception("Failed to get caller identity")
            raise

    def get_federation_token(
        self,
        config: GetFederationTokenConfig,
    ) -> FederationTokenCredentials:
        """Get temporary credentials for federated users."""
        try:
            response = self.client.get_federation_token(
                Name=config.name,
                DurationSeconds=config.duration_seconds,
                Policy=config.policy,
                Tags=[{"Key": k, "Value": v}
                      for k, v in (config.tags or {}).items()],
            )

            credentials = response["Credentials"]
            return FederationTokenCredentials(
                access_key_id=credentials["AccessKeyId"],
                secret_access_key=credentials["SecretAccessKey"],
                session_token=credentials["SessionToken"],
                expiration=credentials["Expiration"].isoformat(),
                federated_user_arn=response["FederatedUser"]["Arn"],
                federated_user_id=response["FederatedUser"]["FederatedUserId"],
            )
        except Exception:
            logger.exception("Failed to get federation token")
            raise
