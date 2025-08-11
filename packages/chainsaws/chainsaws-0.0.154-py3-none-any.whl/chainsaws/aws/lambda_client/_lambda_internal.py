import logging
from typing import Any, Optional

import boto3
from botocore.response import StreamingBody

from chainsaws.aws.lambda_client.lambda_models import InvocationType, LambdaAPIConfig
from chainsaws.aws.lambda_client.ports.output._lambda_internal_response import GetFunctionResponse

logger = logging.getLogger(__name__)


class Lambda:
    """Internal AWS Lambda operations."""

    def __init__(
        self,
        boto3_session: boto3.Session,
        config: LambdaAPIConfig,
    ) -> None:
        self.config = config or LambdaAPIConfig()
        self.client: boto3.client = boto3_session.client(
            service_name="lambda", region_name=self.config.region)

    def create_function(self, config: dict) -> dict:
        """Create new Lambda function."""
        try:
            return self.client.create_function(**config)
        except Exception as ex:
            logger.exception(
                f"[Lambda.create_function] Failed to create function: {ex!s}")
            raise

    def invoke_function(
        self,
        function_name: str,
        payload: Any,
        invocation_type: InvocationType = "RequestResponse"
    ) -> StreamingBody:
        """Invoke AWS Lambda function."""
        try:
            response = self.client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=payload,
            )
            return response["Payload"]
        except Exception as ex:
            logger.exception(
                f"[Lambda.invoke_function] Failed to invoke function: {ex!s}")
            raise

    def get_function(self, function_name: str) -> GetFunctionResponse:
        """Get Lambda function configuration."""
        try:
            return self.client.get_function(FunctionName=function_name)
        except Exception as ex:
            logger.exception(
                f"[Lambda.get_function] Failed to get function: {ex!s}")
            raise

    def list_functions(
        self,
        max_items: int | None = None,
        marker: str | None = None,
    ) -> dict:
        """List Lambda functions."""
        try:
            params = {}
            if max_items:
                params["MaxItems"] = max_items
            if marker:
                params["Marker"] = marker
            return self.client.list_functions(**params)
        except Exception as ex:
            logger.exception(
                f"[Lambda.list_functions] Failed to list functions: {ex!s}")
            raise

    def delete_function(self, function_name: str) -> dict:
        """Delete Lambda function."""
        try:
            return self.client.delete_function(FunctionName=function_name)
        except Exception as ex:
            logger.exception(
                f"[Lambda.delete_function] Failed to delete function: {ex!s}")
            raise

    def update_function_code(
        self,
        function_name: str,
        zip_file: bytes,
    ) -> dict:
        """Update Lambda function code."""
        try:
            return self.client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_file,
            )
        except Exception as ex:
            logger.exception(
                msg=f"[Lambda.update_function_code] Failed to update function code: {ex!s}")
            raise

    def update_function_configuration(
        self,
        function_name: str,
        config: dict,
    ) -> dict:
        """Update Lambda function configuration."""
        try:
            return self.client.update_function_configuration(
                FunctionName=function_name,
                **config,
            )
        except Exception as ex:
            logger.exception(
                f"[Lambda.update_function_configuration] Failed to update configuration: {ex!s}")
            raise

    def list_function_versions(
        self,
        function_name: str,
        marker: str | None = None,
        max_items: int | None = None,
    ) -> dict:
        """List Lambda function versions."""
        try:
            params = {"FunctionName": function_name}
            if marker:
                params["Marker"] = marker
            if max_items:
                params["MaxItems"] = max_items
            return self.client.list_versions_by_function(**params)
        except Exception as ex:
            logger.exception(
                f"[Lambda.list_function_versions] Failed to list versions: {ex!s}")
            raise

    def get_function_concurrency(self, function_name: str) -> dict:
        """Get Lambda function concurrency settings."""
        try:
            return self.client.get_function_concurrency(
                FunctionName=function_name,
            )
        except Exception as ex:
            logger.exception(
                f"[Lambda.get_function_concurrency] Failed to get concurrency: {ex!s}")
            raise

    def add_permission(
        self,
        function_name: str,
        statement_id: str,
        action: str,
        principal: str,
        source_arn: str | None = None,
        source_account: str | None = None,
        principal_org_id: str | None = None,
        revision_id: str | None = None,
        qualifier: str | None = None,
    ) -> dict[str, Any]:
        """Add permission to Lambda function."""
        try:
            params = {
                "FunctionName": function_name,
                "StatementId": statement_id,
                "Action": action,
                "Principal": principal,
            }

            if source_arn:
                params["SourceArn"] = source_arn
            if source_account:
                params["SourceAccount"] = source_account
            if principal_org_id:
                params["PrincipalOrgID"] = principal_org_id
            if revision_id:
                params["RevisionId"] = revision_id
            if qualifier:
                params["Qualifier"] = qualifier

            return self.client.add_permission(**params)
        except Exception as ex:
            logger.exception(
                f"[Lambda.add_permission] Failed to add permission: {ex!s}")
            raise

    def remove_permission(
        self,
        function_name: str,
        statement_id: str,
        qualifier: Optional[str] = None,
        revision_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Remove permission from Lambda function."""
        try:
            params = {
                "FunctionName": function_name,
                "StatementId": statement_id,
            }

            if qualifier:
                params["Qualifier"] = qualifier
            if revision_id:
                params["RevisionId"] = revision_id

            return self.client.remove_permission(**params)
        except Exception as ex:
            logger.exception(
                f"[Lambda.remove_permission] Failed to remove permission: {ex!s}")
            raise

    def get_policy(
        self,
        function_name: str,
        qualifier: str | None = None,
    ) -> dict[str, Any]:
        """Get Lambda function policy."""
        try:
            params = {"FunctionName": function_name}
            if qualifier:
                params["Qualifier"] = qualifier
            return self.client.get_policy(**params)
        except Exception as ex:
            logger.exception(
                f"[Lambda.get_policy] Failed to get policy: {ex!s}")
            raise
