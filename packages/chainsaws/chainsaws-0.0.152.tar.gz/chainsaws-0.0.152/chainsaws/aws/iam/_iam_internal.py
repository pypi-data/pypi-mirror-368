import json
import logging
import time
from typing import Any

from boto3.session import Session
from botocore.config import Config

from chainsaws.aws.iam.iam_models import IAMAPIConfig, RoleConfig, RolePolicyConfig

logger = logging.getLogger(__name__)


class IAM:
    """Low-level IAM client wrapper."""

    def __init__(
        self,
        boto3_session: Session,
        config: IAMAPIConfig | None = None,
    ) -> None:
        self.config = config or IAMAPIConfig()

        client_config = Config(
            region_name=self.config.region,
            retries={"max_attempts": self.config.max_retries},
            connect_timeout=self.config.timeout,
            read_timeout=self.config.timeout,
        )

        self.client = boto3_session.client(
            "iam",
            config=client_config,
            region_name=self.config.region,
        )

    def wait_until_role_exists(self, role_name: str, max_attempts: int = 20) -> None:
        """Wait until IAM role exists and is accessible."""
        try:
            waiter = self.client.get_waiter("role_exists")
            waiter.wait(
                RoleName=role_name,
                WaiterConfig={"MaxAttempts": max_attempts},
            )
        except Exception as ex:
            logger.exception(f"Timeout waiting for role '{
                         role_name}' to exist: {ex}")
            msg = f"Role {role_name} did not become available in time"
            raise TimeoutError(
                msg) from ex

    def create_role(self, config: RoleConfig, wait: bool = True) -> dict[str, Any]:
        """Create IAM role."""
        try:
            result = self.client.create_role(
                RoleName=config.name,
                AssumeRolePolicyDocument=json.dumps(config.trust_policy),
                Description=config.description,
            )

            if wait:
                self.wait_until_role_exists(config.name)

            return result
        except Exception as ex:
            logger.exception(f"Failed to create role '{config.name}': {ex!s}")
            raise

    def wait_until_role_policy_exists(
        self,
        role_name: str,
        policy_name: str,
        max_attempts: int = 30,
    ) -> None:
        """Wait until inline policy exists on role."""
        try:
            for _ in range(max_attempts):
                try:
                    self.client.get_role_policy(
                        RoleName=role_name,
                        PolicyName=policy_name,
                    )
                    return
                except self.client.exceptions.NoSuchEntityException:
                    time.sleep(0.1)
            msg = (
                f"Policy {policy_name} was not attached to role {
                    role_name} in time"
            )
            raise TimeoutError(
                msg,
            )
        except Exception as ex:
            logger.exception(
                f"Error waiting for policy '{
                    policy_name}' on role '{role_name}': {ex!s}",
            )
            raise

    def put_role_policy(self, config: RolePolicyConfig, wait: bool = True) -> dict[str, Any]:
        """Put inline policy to IAM role."""
        try:
            result = self.client.put_role_policy(
                RoleName=config.role_name,
                PolicyName=config.policy_name,
                PolicyDocument=json.dumps(config.policy_document),
            )

            if wait:
                self.wait_until_role_policy_exists(
                    config.role_name,
                    config.policy_name,
                )

            return result
        except Exception as ex:
            logger.exception(
                f"Failed to put policy '{config.policy_name}' to role '{
                    config.role_name}': {ex!s}",
            )
            raise

    def get_role(self, role_name: str) -> dict[str, Any]:
        """Get IAM role."""
        try:
            return self.client.get_role(RoleName=role_name)
        except Exception as ex:
            logger.exception(f"Failed to get role '{role_name}': {ex!s}")
            raise
