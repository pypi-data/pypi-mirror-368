import json
import logging
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Optional, TypeVar

from botocore.exceptions import ClientError

from chainsaws.aws.lambda_client import LambdaAPI, LambdaAPIConfig
from chainsaws.aws.secrets_manager._secrets_manager_internal import SecretsManager
from chainsaws.aws.secrets_manager.secrets_manager_models import (
    BatchSecretOperation,
    RotationConfig,
    SecretBackupConfig,
    SecretConfig,
    SecretFilterConfig,
    SecretsManagerAPIConfig,
    GetSecretResponse
)
from chainsaws.aws.secrets_manager.secrets_manager_exception import (
    SecretAlreadyExistsException,
    SecretNotFoundException,
    SecretsManagerDeletionAlreadyScheduledException,
    SecretsManagerException
)
from chainsaws.aws.shared import session


logger = logging.getLogger(__name__)

SecretValueType = TypeVar(
    'SecretValueType')  # Remove bound to allow any type


class SecretsManagerAPI:
    """High-level AWS Secrets Manager operations."""

    def __init__(self, config: Optional[SecretsManagerAPIConfig] = None) -> None:
        self.config = config or SecretsManagerAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.secrets = SecretsManager(
            boto3_session=self.boto3_session, config=self.config)
        self._executor = ThreadPoolExecutor(
            thread_name_prefix="chainsaws-secrets-manager-")

    def create_secret(
        self,
        name: str,
        secret_value: str | bytes | dict,
        description: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Creates a new secret in AWS Secrets Manager.

        Args:
            name: The name of the secret.
            secret_value: The value to store in the secret. Can be a string, bytes, or dict.
            description: Optional description of the secret.
            tags: Optional dict of key-value pairs to tag the secret with.

        Returns:
            dict: The response from AWS containing details about the created secret.
                Contains keys like 'ARN', 'Name', 'VersionId'.

        Raises:
            SecretsManagerException: If there is an error creating the secret.
        """
        if isinstance(secret_value, dict):
            secret_value = json.dumps(secret_value)

        config = SecretConfig(
            name=name,
            description=description,
            secret_string=secret_value if isinstance(
                secret_value, str | dict) else None,
            secret_binary=secret_value if isinstance(
                secret_value, bytes) else None,
            tags=tags,
        )

        try:
            response = self.secrets.create_secret(config)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                msg = f"Secret `{name}` already exists"
                raise SecretAlreadyExistsException(msg) from e

            if e.response['Error']['Code'] == 'InvalidRequestException':
                msg = f"Secret `{name}` deletion already scheduled"
                raise SecretsManagerDeletionAlreadyScheduledException(
                    msg) from e

            msg = f"Unknown error occurred while creating secret `{name}`"
            logger.exception(msg)
            raise SecretsManagerException(msg) from e

        except Exception as ex:
            msg = f"Unknown error occurred while creating secret `{name}`"
            logger.exception(msg)
            raise SecretsManagerException(msg) from ex

        return response

    def get_secret(
        self,
        secret_id: str,
        version_id: Optional[str] = None,
        version_stage: Optional[str] = None,
    ) -> Optional[SecretValueType]:
        """Retrieves a secret value from AWS Secrets Manager.

        Args:
            secret_id: The identifier of the secret to retrieve. Can be the secret name or ARN.
            version_id: Optional specific version ID of the secret to retrieve.
            version_stage: Optional staging label of the version to retrieve (e.g. AWSCURRENT).

        Returns:
            The secret value as one of the following types:
                - TypedDict or dict: If the secret string is valid JSON
                - str: For non-JSON string secrets
                - bytes: For binary secrets
                - Any custom type that can be deserialized from JSON

        Raises:
            SecretNotFoundException: If the specified secret does not exist.
            SecretsManagerException: If any other error occurs while retrieving the secret.
            TypeError: If the secret value cannot be converted to the expected type.
        """
        try:
            response: GetSecretResponse = self.secrets.get_secret_value(
                secret_id=secret_id,
                version_id=version_id,
                version_stage=version_stage,
            )

            if response.get("SecretBinary"):
                value = response["SecretBinary"]
                if isinstance(value, (dict, str, bytes)):
                    return value  # type: ignore
                raise TypeError(
                    "Secret binary value cannot be converted to the expected type")

            if response.get("SecretString"):
                try:
                    value = json.loads(response["SecretString"])
                    if isinstance(value, (dict, str, bytes)):
                        return value  # type: ignore

                except json.JSONDecodeError:
                    value = response["SecretString"]
                    if isinstance(value, (dict, str, bytes)):
                        return value  # type: ignore

                raise TypeError(
                    "Secret string value cannot be converted to the expected type")

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                msg = f"Secret `{secret_id}` not found"
                raise SecretNotFoundException(msg) from e

            raise SecretsManagerException(
                f"Unknown error occurred while getting secret `{secret_id}`") from e

        except TypeError:
            raise

        except Exception as ex:
            msg = f"Unknown error occurred while getting secret `{secret_id}`"
            raise SecretsManagerException(msg) from ex

    def update_secret(
        self,
        secret_id: str,
        secret_value: str | bytes | dict,
        version_stages: list[str] | None = None,
    ) -> dict[str, Any]:
        """Updates a secret value in AWS Secrets Manager.

        Args:
            secret_id: The identifier of the secret to update. Can be secret name or ARN.
            secret_value: The new value to store. Can be string, bytes or dict.
            version_stages: Optional list of staging labels to attach to this version.

        Returns:
            dict: The response from AWS containing metadata about the updated secret.

        Raises:
            SecretNotFoundException: If the specified secret does not exist.
            SecretsManagerException: If any other error occurs while updating the secret.
        """
        try:
            response = self.secrets.put_secret_value(
                secret_id=secret_id,
                secret_value=secret_value,
                version_stages=version_stages,
            )

            return response

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                msg = f"Secret `{secret_id}` not found"
                raise SecretNotFoundException(msg) from e

            if e.response['Error']['Code'] == 'InvalidRequestException':
                msg = f"Secret `{secret_id}` deletion already scheduled"
                raise SecretsManagerDeletionAlreadyScheduledException(
                    msg) from e

            raise SecretsManagerException(
                f"Unknown error occurred while updating secret `{secret_id}`") from e

        except Exception as ex:
            msg = f"Unknown error occurred while updating secret `{secret_id}`"
            raise SecretsManagerException(msg) from ex

    def delete_secret(
        self,
        secret_id: str,
        force: bool = False,
        recovery_window_days: int | None = 30,
    ) -> dict[str, Any]:
        """Deletes a secret from AWS Secrets Manager.

        Args:
            secret_id: The identifier of the secret to delete. Can be secret name or ARN.
            force: If True, immediately deletes the secret without recovery window.
            recovery_window_days: Number of days before permanent deletion. Ignored if force=True.
                Defaults to 30 days.

        Returns:
            dict: The response from AWS containing metadata about the deleted secret.

        Raises:
            SecretNotFoundException: If the specified secret does not exist.
            SecretsManagerException: If any other error occurs while deleting the secret.
        """
        try:
            response = self.secrets.delete_secret(
                secret_id=secret_id,
                force_delete=force,
                recovery_window_in_days=None if force else recovery_window_days,
            )

            return response

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                msg = f"Secret `{secret_id}` not found"
                raise SecretNotFoundException(msg) from e

            if e.response['Error']['Code'] == 'InvalidRequestException':
                msg = f"Secret `{secret_id}` deletion already scheduled"
                raise SecretsManagerDeletionAlreadyScheduledException(
                    msg) from e

            raise SecretsManagerException(
                f"Unknown error occurred while deleting secret `{secret_id}`") from e

        except Exception as ex:
            msg = f"Unknown error occurred while deleting secret `{secret_id}`"
            raise SecretsManagerException(msg) from ex

    def setup_rotation(
        self,
        secret_id: str,
        lambda_arn: str,
        rotation_days: int,
        rotation_rules: dict[str, Any] | None = None,
        lambda_config: LambdaAPIConfig | None = None,
    ) -> dict[str, Any]:
        """Setup automatic secret rotation.

        Args:
            secret_id: Secret ID or ARN
            lambda_arn: Lambda function ARN for rotation
            rotation_days: Number of days between rotations
            rotation_rules: Additional rotation rules

        Returns:
            Dict containing rotation configuration

        Raises:
            ValueError: If lambda_arn is invalid or Lambda function doesn't exist
            Exception: If rotation setup fails

        """
        lambda_client = LambdaAPI(config=lambda_config)
        try:
            # Verify function exists
            lambda_client.get_function(function_name=lambda_arn)
        except Exception as ex:
            msg = f"Invalid or non-existent Lambda function ARN: {
                lambda_arn}. Error: {ex}"
            raise ValueError(
                msg) from ex

        config = RotationConfig(
            rotation_lambda_arn=lambda_arn,
            rotation_rules=rotation_rules or {},
            automatically_after_days=rotation_days,
        )

        return self.secrets.rotate_secret(secret_id, config)

    def list_all_secrets(
        self,
        max_results: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """List all secrets with pagination."""
        paginator = self.secrets.client.get_paginator("list_secrets")

        params = {}
        if max_results:
            params["PaginationConfig"] = {"MaxItems": max_results}

        for page in paginator.paginate(**params):
            yield from page.get("SecretList", [])

    def get_secret_metadata(self, secret_id: str) -> dict[str, Any]:
        """Get secret metadata."""
        try:
            return self.secrets.describe_secret(secret_id)
        except Exception as e:
            msg = f"Failed to get secret metadata for {secret_id}"
            logger.exception(msg)
            raise SecretsManagerException(msg) from e

    def get_secret_value_if_changed(
        self,
        secret_id: str,
        last_updated: datetime | None = None,
    ) -> str | dict | bytes | None:
        """Get secret value only if it has changed."""
        metadata = self.get_secret_metadata(secret_id)
        secret_updated = metadata.get("LastChangedDate")

        if not last_updated or (secret_updated and secret_updated > last_updated):
            return self.get_secret(secret_id)

        return None

    def batch_operation(self, batch_config: BatchSecretOperation) -> dict[str, Any]:
        """Execute batch operation on multiple secrets in parallel."""
        results = {
            "successful": [],
            "failed": [],
        }

        def execute_operation(secret_id: str) -> dict[str, Any]:
            try:
                if batch_config.operation == "delete":
                    self.delete_secret(secret_id, **batch_config.params)
                    return {"success": True, "secret_id": secret_id}
                if batch_config.operation == "rotate":
                    self.setup_rotation(secret_id, **batch_config.params)
                    return {"success": True, "secret_id": secret_id}
                if batch_config.operation == "update":
                    self.update_secret(secret_id, **batch_config.params)
                    return {"success": True, "secret_id": secret_id}
                return {
                    "success": False,
                    "secret_id": secret_id,
                    "error": f"Unknown operation: {batch_config.operation}",
                }
            except Exception as e:
                return {
                    "success": False,
                    "secret_id": secret_id,
                    "error": str(e),
                }

        with self._executor as executor:
            futures = [
                executor.submit(execute_operation, secret_id)
                for secret_id in batch_config.secret_ids
            ]

            # Collect results
            for future in futures:
                try:
                    result = future.result()
                    if result["success"]:
                        results["successful"].append(result["secret_id"])
                    else:
                        results["failed"].append({
                            "secret_id": result["secret_id"],
                            "error": result["error"],
                        })
                except Exception as e:
                    logger.exception(
                        f"Failed to get result from future: {e!s}")

        return results

    def backup_secrets(self, config: SecretBackupConfig) -> None:
        """Backup secrets to file in parallel.

        Note: This method saves secrets in unencrypted JSON format.
        For sensitive data, consider using AWS KMS for encryption or implementing
        your own encryption mechanism.
        """
        backup_data = {
            "secrets": [],
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0",
            },
        }

        def backup_secret(secret_id: str) -> dict[str, Any] | None:
            try:
                value = self.get_secret(secret_id)
                metadata = self.get_secret_metadata(secret_id)
                return {
                    "id": secret_id,
                    "value": value,
                    "metadata": metadata,
                }
            except Exception as e:
                logger.exception(f"Failed to backup secret {secret_id}: {e!s}")
                return None

        # Execute backups in parallel
        with self._executor as executor:
            futures = [
                executor.submit(backup_secret, secret_id)
                for secret_id in config.secret_ids
            ]

            # Collect results
            for future in futures:
                try:
                    result = future.result()
                    if result:
                        backup_data["secrets"].append(result)
                except Exception as e:
                    logger.exception(f"Failed to get backup result: {e!s}")

        # Save backup data as JSON
        with open(config.backup_path, "w") as f:
            json.dump(backup_data, f, indent=2)

    def restore_secrets(
        self,
        backup_path: str,
    ) -> dict[str, Any]:
        """Restore secrets from backup file."""
        try:
            with open(backup_path) as f:
                backup_data = json.load(f)

            results = {"restored": [], "failed": []}

            def restore_secret(secret: dict[str, Any]) -> dict[str, Any]:
                try:
                    self.create_secret(
                        name=secret["id"],
                        secret_value=secret["value"],
                        description=secret["metadata"].get("Description"),
                    )
                    return {"success": True, "secret_id": secret["id"]}
                except Exception as e:
                    return {
                        "success": False,
                        "secret_id": secret["id"],
                        "error": str(e),
                    }

            # Execute restores in parallel
            with self._executor as executor:
                futures = [
                    executor.submit(restore_secret, secret)
                    for secret in backup_data["secrets"]
                ]

                # Collect results
                for future in futures:
                    try:
                        result = future.result()
                        if result["success"]:
                            results["restored"].append(result["secret_id"])
                        else:
                            results["failed"].append({
                                "secret_id": result["secret_id"],
                                "error": result["error"],
                            })
                    except Exception as e:
                        logger.exception(
                            f"Failed to get restore result: {e!s}")

            return results

        except Exception as e:
            msg = f"Failed to restore secrets: {e}"
            raise Exception(msg) from e

    def filter_secrets(
        self,
        filter_config: SecretFilterConfig,
    ) -> Iterator[dict[str, Any]]:
        """Filter secrets based on criteria."""
        for secret in self.list_all_secrets():
            if filter_config.name_prefix and not secret["Name"].startswith(filter_config.name_prefix):
                continue

            if filter_config.tags:
                secret_tags = {t["Key"]: t["Value"]
                               for t in secret.get("Tags", [])}
                if not all(secret_tags.get(k) == v for k, v in filter_config.tags.items()):
                    continue

            if filter_config.created_after and secret["CreatedDate"] < filter_config.created_after:
                continue

            if filter_config.last_updated_after and secret.get("LastChangedDate", secret["CreatedDate"]) < filter_config.last_updated_after:
                continue

            yield secret

    def generate_random_password(
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
        Generate a random password.

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
            response = self.secrets.get_random_password(
                length=length,
                exclude_characters=exclude_characters,
                exclude_numbers=exclude_numbers,
                exclude_punctuation=exclude_punctuation,
                exclude_uppercase=exclude_uppercase,
                exclude_lowercase=exclude_lowercase,
                include_space=include_space,
                require_each_included_type=require_each_included_type,
            )
            return response["RandomPassword"]

        except ClientError:
            logger.exception("Failed to generate random password")
            raise
