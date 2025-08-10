import base64
import json
import logging
from typing import Any, Optional

from boto3.session import Session
from botocore.config import Config
from botocore.exceptions import ClientError

from chainsaws.aws.secrets_manager.secrets_manager_models import (
    RotationConfig,
    SecretConfig,
    SecretsManagerAPIConfig,
)

logger = logging.getLogger(__name__)


class SecretsManager:
    """Low-level Secrets Manager client wrapper."""

    def __init__(
        self,
        boto3_session: Session,
        config: SecretsManagerAPIConfig | None = None,
    ) -> None:
        self.config = config or SecretsManagerAPIConfig()

        client_config = Config(
            region_name=self.config.region,
            retries={"max_attempts": self.config.max_retries},
            connect_timeout=self.config.timeout,
            read_timeout=self.config.timeout,
        )

        self.client = boto3_session.client(
            "secretsmanager",
            config=client_config,
            region_name=self.config.region,
        )

    def create_secret(self, config: SecretConfig) -> dict[str, Any]:
        """Create a new secret."""
        try:
            params = {
                "Name": config.name,
                "Description": config.description,
            }

            if config.tags:
                params["Tags"] = [
                    {"Key": k, "Value": v}
                    for k, v in config.tags.items()
                ]

            if config.secret_string is not None:
                if isinstance(config.secret_string, dict):
                    params["SecretString"] = json.dumps(config.secret_string)
                else:
                    params["SecretString"] = config.secret_string
            elif config.secret_binary is not None:
                params["SecretBinary"] = config.secret_binary

            return self.client.create_secret(**params)

        except ClientError as e:
            logger.exception(f"Failed to create secret '{config.name}': {e!s}")
            raise

    def get_secret_value(
        self,
        secret_id: str,
        version_id: str | None = None,
        version_stage: str | None = None,
    ) -> dict[str, Any]:
        """Get secret value."""
        try:
            params = {"SecretId": secret_id}
            if version_id:
                params["VersionId"] = version_id
            if version_stage:
                params["VersionStage"] = version_stage

            response = self.client.get_secret_value(**params)

            # Handle binary secrets
            if "SecretBinary" in response:
                response["SecretBinary"] = base64.b64decode(
                    response["SecretBinary"])

            return response

        except ClientError as e:
            logger.exception(f"Failed to get secret value for '{
                secret_id}': {e!s}")
            raise

    def put_secret_value(
        self,
        secret_id: str,
        secret_value: str | bytes | dict,
        version_stages: list[str] | None = None,
    ) -> dict[str, Any]:
        """Put a new secret value."""
        try:
            params = {"SecretId": secret_id}

            if isinstance(secret_value, str | dict):
                params["SecretString"] = (
                    secret_value if isinstance(secret_value, str)
                    else json.dumps(secret_value)
                )
            else:
                params["SecretBinary"] = secret_value

            if version_stages:
                params["VersionStages"] = version_stages

            return self.client.put_secret_value(**params)

        except ClientError as e:
            logger.exception(f"Failed to put secret value for '{
                secret_id}': {e!s}")
            raise

    def delete_secret(
        self,
        secret_id: str,
        force_delete: bool = False,
        recovery_window_in_days: int | None = None,
    ) -> dict[str, Any]:
        """Delete a secret."""
        try:
            params = {"SecretId": secret_id}

            if force_delete:
                params["ForceDeleteWithoutRecovery"] = True
            elif recovery_window_in_days:
                params["RecoveryWindowInDays"] = recovery_window_in_days

            return self.client.delete_secret(**params)

        except ClientError as e:
            logger.exception(f"Failed to delete secret '{secret_id}': {e!s}")
            raise

    def rotate_secret(
        self,
        secret_id: str,
        config: RotationConfig,
    ) -> dict[str, Any]:
        """Configure secret rotation."""
        try:
            params = {
                "SecretId": secret_id,
                "RotationLambdaARN": config.rotation_lambda_arn,
                "RotationRules": config.rotation_rules,
            }

            if config.automatically_after_days:
                params["RotationRules"] = {
                    "AutomaticallyAfterDays": config.automatically_after_days,
                }

            return self.client.rotate_secret(**params)

        except ClientError as e:
            logger.exception(f"Failed to configure rotation for '{
                secret_id}': {e!s}")
            raise

    def describe_secret(self, secret_id: str) -> dict[str, Any]:
        """Get secret metadata."""
        try:
            return self.client.describe_secret(SecretId=secret_id)
        except ClientError as e:
            logger.exception(f"Failed to describe secret '{secret_id}': {e!s}")
            raise

    def list_secrets(
        self,
        max_results: int | None = None,
        next_token: str | None = None,
    ) -> dict[str, Any]:
        """List secrets."""
        try:
            params = {}
            if max_results:
                params["MaxResults"] = max_results
            if next_token:
                params["NextToken"] = next_token

            return self.client.list_secrets(**params)

        except ClientError as e:
            logger.exception(f"Failed to list secrets: {e!s}")
            raise

    def tag_secret(
        self,
        secret_id: str,
        tags: dict[str, str],
    ) -> dict[str, Any]:
        """Add tags to a secret."""
        try:
            return self.client.tag_resource(
                SecretId=secret_id,
                Tags=[
                    {"Key": k, "Value": v}
                    for k, v in tags.items()
                ],
            )
        except ClientError as e:
            logger.exception(f"Failed to tag secret '{secret_id}': {e!s}")
            raise

    def untag_secret(
        self,
        secret_id: str,
        tag_keys: list[str],
    ) -> dict[str, Any]:
        """Remove tags from a secret."""
        try:
            return self.client.untag_resource(
                SecretId=secret_id,
                TagKeys=tag_keys,
            )
        except ClientError as e:
            logger.exception(f"Failed to untag secret '{secret_id}': {e!s}")
            raise

    def get_random_password(
        self,
        length: int = 32,
        exclude_characters: Optional[str] = None,
        exclude_numbers: bool = False,
        exclude_punctuation: bool = False,
        exclude_uppercase: bool = False,
        exclude_lowercase: bool = False,
        include_space: bool = False,
        require_each_included_type: bool = False,
    ) -> str:
        """
        Get a random password.

        Args:
            length: The length of the password (default: 32)
            exclude_characters: Characters to exclude from the password
            exclude_numbers: Whether to exclude numbers
            exclude_punctuation: Whether to exclude punctuation characters
            exclude_uppercase: Whether to exclude uppercase letters
            exclude_lowercase: Whether to exclude lowercase letters
            include_space: Whether to include space characters
            require_each_included_type: Whether to require at least one of each allowed character type

        Returns:
            str: Generated random password
        """
        try:
            params = {
                "PasswordLength": length,
                "ExcludeNumbers": exclude_numbers,
                "ExcludePunctuation": exclude_punctuation,
                "ExcludeUppercase": exclude_uppercase,
                "ExcludeLowercase": exclude_lowercase,
                "IncludeSpace": include_space,
                "RequireEachIncludedType": require_each_included_type,
                "ExcludeCharacters": exclude_characters or "",
            }

            return self.client.get_random_password(**params)

        except ClientError:
            logger.exception("Failed to generate random password")
            raise
