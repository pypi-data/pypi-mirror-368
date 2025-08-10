import json
import logging
import time
from collections.abc import Iterator
from typing import Any, Union, Optional

from chainsaws.aws.lambda_client._lambda_internal import Lambda
from chainsaws.aws.lambda_client.lambda_models import (
    CreateFunctionRequest,
    FunctionConfiguration,
    InvocationType,
    LambdaAPIConfig,
    LambdaHandler,
    PythonRuntime,
    TriggerType,
    LambdaPackageType
)
from chainsaws.aws.lambda_client.lambda_utils import (
    get_trigger_config,
    validate_lambda_configuration,
    validate_source_arn,
)
from chainsaws.aws.lambda_client.lambda_exception import (
    LambdaCreateFunctionException,
)
from chainsaws.aws.lambda_client.ports.output._lambda_internal_response import (
    LambdaConfiguration
)
from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)

JSONValue = Union[dict, list, str, int, float, bool, None]


class LambdaAPI:
    """High-level AWS Lambda operations wrapper."""

    def __init__(self, config: Optional[LambdaAPIConfig] = None) -> None:
        self.config = config or LambdaAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.lambda_client = Lambda(
            boto3_session=self.boto3_session,
            config=self.config,
        )

    def invoke(
        self,
        function_name: str,
        payload: Optional[str | bytes | dict[str, JSONValue] | list[JSONValue]] = None,
        invocation_type: InvocationType = "RequestResponse",
    ) -> dict | str | None:
        """Invoke AWS Lambda function."""
        if payload is None:
            payload = {}

        if not isinstance(payload, str | bytes | dict | list | None):
            msg = (
                f"Payload must be str, bytes, dict, or list, not {
                    type(payload)}"
            )
            raise TypeError(
                msg,
            )

        if isinstance(payload, dict | list):
            try:
                payload = json.dumps(payload)
            except json.JSONDecodeError as ex:
                msg = "Failed to serialize payload to JSON"
                logger.exception(f"{msg}: {ex!s}")
                raise TypeError(msg) from ex

        if invocation_type == "Event":
            self.lambda_client.invoke_function(
                function_name, payload, invocation_type)
            return None

        response_payload = self.lambda_client.invoke_function(
            function_name,
            payload,
            invocation_type,
        )

        response_body = response_payload.read().decode("utf-8")

        try:
            return json.loads(response_body)
        except json.JSONDecodeError:
            return response_body

    def init_function(
        self,
        function_name: str,
        role: str,
        handler: LambdaHandler,
        runtime: PythonRuntime = PythonRuntime.PYTHON_311,
        code: Optional[bytes | str | dict[str, str]] = None,
        description: Optional[str] = None,
        timeout: int = 3,
        memory_size: int = 128,
        environment_variables: Optional[dict[str, str]] = None,
        tags: Optional[dict[str, str]] = None,
        architectures: Optional[list[str]] = None,
        package_type: LambdaPackageType = "Image",
        image_uri: Optional[str] = None,
    ) -> FunctionConfiguration:
        """Initialize Lambda function if it doesn't exist.

        Args:
            function_name: Name for the function
            role: ARN of the execution role
            handler: Lambda function handler
            runtime: Python runtime version
            code: Function code - can be:
                  - bytes: ZIP file content
                  - str: Path to local ZIP file
                  - dict: S3 location {'S3Bucket': '...', 'S3Key': '...'}
            description: Function description
            timeout: Function timeout in seconds (1-900)
            memory_size: Function memory in MB (128-10240)
            environment_variables: Environment variables
            tags: Function tags
            architectures: List of architectures ('x86_64' or 'arm64')
            package_type: Type of function deployment package ('Zip' or 'Image')
            image_uri: URI of container image (required if package_type is 'Image')

        Returns:
            FunctionConfiguration: Function configuration as TypedDict

        Raises:
            ValueError: If code is not provided or in wrong format
            Exception: If function creation fails
        """
        try:
            # Check if function already exists
            existing_config = self.get_function(function_name)
            logger.warning(
                f"Function {function_name} already exists, skipping creation")
            return existing_config
        except Exception:
            # Function doesn't exist, proceed with creation
            if package_type == "Zip":
                if isinstance(code, bytes):
                    function_code = {"ZipFile": code}
                elif isinstance(code, str) and code.endswith(".zip"):
                    with open(code, "rb") as f:
                        function_code = {"ZipFile": f.read()}
                elif isinstance(code, dict) and "S3Bucket" in code and "S3Key" in code:
                    function_code = {
                        "S3Bucket": code["S3Bucket"],
                        "S3Key": code["S3Key"]
                    }
                    if "S3ObjectVersion" in code:
                        function_code["S3ObjectVersion"] = code["S3ObjectVersion"]
                else:
                    msg = "Code must be ZIP file bytes, path to ZIP file, or S3 location dict"
                    raise LambdaCreateFunctionException(msg)
            else:  # Image
                if not image_uri:
                    msg = "image_uri is required when package_type is 'Image'"
                    raise LambdaCreateFunctionException(msg)
                function_code = {"ImageUri": image_uri}

            create_params = {
                "function_name": function_name,
                "runtime": runtime,
                "role": role,
                "handler": str(handler),
                "code": function_code,
                "timeout": timeout,
                "memory_size": memory_size,
                "description": description,
                "environment": {"Variables": environment_variables} if environment_variables else None,
                "tags": tags,
                "architectures": architectures or ["x86_64"],
                "package_type": package_type,
                "image_uri": image_uri,
            }

            request = CreateFunctionRequest(**create_params)
            response = self.lambda_client.create_function(request.to_dict())
            return response

    def delete_function(
        self,
        function_name: str,
        qualifier: Optional[str] = None,
    ) -> bool:
        """Delete Lambda function.

        Args:
            function_name: Name or ARN of the function
            qualifier: Version or alias to delete

        Returns:
            bool: True if deletion was successful

        Note:
            If qualifier is specified, it deletes a specific version.
            If not specified, it deletes the entire function.

        """
        try:
            params = {"FunctionName": function_name}
            if qualifier:
                params["Qualifier"] = qualifier

            self.lambda_client.delete_function(**params)
            return True
        except Exception as ex:
            logger.exception(f"Failed to delete function {
                function_name}: {ex!s}")
            return False

    def get_function(self, function_name: str) -> LambdaConfiguration:
        """Get Lambda function configuration.

        Args:
            function_name: Name or ARN of the Lambda function

        Returns:
            FunctionConfiguration: Function configuration details

        """
        response = self.lambda_client.get_function(function_name)
        return response['Configuration']

    def list_functions(
        self,
        max_items: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> Iterator[FunctionConfiguration]:
        """List Lambda functions with pagination.

        Args:
            max_items: Maximum number of items to return
            marker: Pagination token from previous response

        Yields:
            FunctionConfiguration for each Lambda function

        """
        while True:
            response = self.lambda_client.list_functions(max_items, marker)
            for function in response["Functions"]:
                yield FunctionConfiguration(**function)

            next_marker = response.get("NextMarker")
            if not next_marker:
                break
            marker = next_marker

    def update_function_code(
        self,
        function_name: str,
        zip_file: bytes,
    ) -> FunctionConfiguration:
        """Update Lambda function code.

        Args:
            function_name: Name or ARN of the Lambda function
            zip_file: ZIP file bytes containing the function code

        Returns:
            FunctionConfiguration: Updated function configuration

        """
        response = self.lambda_client.update_function_code(
            function_name,
            zip_file,
        )
        return FunctionConfiguration(**response)

    def update_function_configuration(
        self,
        function_name: str,
        description: Optional[str] = None,
        memory_size: Optional[int] = None,
        timeout: Optional[int] = None,
        environment_variables: Optional[dict[str, str]] = None,
        runtime: Optional[PythonRuntime] = None,
        handler: Optional[LambdaHandler] = None,
    ) -> FunctionConfiguration:
        """Update Lambda function configuration.

        Args:
            function_name: Name or ARN of the Lambda function
            memory_size: Memory size in MB. Defaults in 256 (256MB)
            timeout: Timeout in seconds. Defaults in 3 (3 seconds)
            environment_variables: Environment variables
            runtime: Runtime identifier
            handler: Function handler

        Returns:
            FunctionConfiguration: Updated function configuration

        """
        validate_lambda_configuration(
            memory_size=memory_size,
            timeout=timeout,
            environment_variables=environment_variables,
            handler=handler,
        )

        config = {}

        if memory_size is not None:
            config["MemorySize"] = memory_size
        if timeout is not None:
            config["Timeout"] = timeout
        if environment_variables is not None:
            config["Environment"] = {"Variables": environment_variables}
        if runtime is not None:
            config["Runtime"] = runtime.value
        if handler is not None:
            config["Handler"] = str(handler)
        if description is not None:
            config["Description"] = description

        response = self.lambda_client.update_function_configuration(
            function_name,
            config,
        )
        return FunctionConfiguration(**response)

    def list_versions(
        self,
        function_name: str,
        max_items: int | None = None,
    ) -> list[FunctionConfiguration]:
        """List all versions of a Lambda function.

        Args:
            function_name: Name or ARN of the Lambda function
            max_items: Maximum number of versions to return

        Returns:
            List[FunctionConfiguration]: List of function versions

        """
        versions = []
        marker = None

        while True:
            response = self.lambda_client.list_function_versions(
                function_name,
                marker,
                max_items,
            )

            for version in response["Versions"]:
                versions.append(FunctionConfiguration(**version))

            next_marker = response.get("NextMarker")
            if not next_marker or (max_items and len(versions) >= max_items):
                break
            marker = next_marker

        return versions[:max_items] if max_items else versions

    def get_concurrency(self, function_name: str) -> int | None:
        """Get reserved concurrency for a function.

        Args:
            function_name: Name or ARN of the Lambda function

        Returns:
            Optional[int]: Reserved concurrency value, None if not set

        """
        try:
            response = self.lambda_client.get_function_concurrency(
                function_name)
            return response.get("ReservedConcurrentExecutions")
        except Exception as ex:
            logger.exception(f"Failed to get function concurrency for {
                function_name}: {ex!s}")
            return None

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
        """Add permission to Lambda function policy.

        Args:
            function_name: Function name or ARN
            statement_id: Statement identifier
            action: Action to allow (e.g. 'lambda:InvokeFunction')
            principal: AWS service principal (e.g. 'logs.amazonaws.com')
            source_arn: Optional ARN of the source
            source_account: Optional source AWS account ID
            principal_org_id: Optional AWS organization ID
            revision_id: Optional policy revision ID
            qualifier: Optional function version or alias

        Returns:
            Dict containing the added statement

        Example:
            ```python
            # Allow CloudWatch Logs to invoke function
            lambda_api.add_permission(
                function_name="my-function",
                statement_id="CloudWatchLogs",
                action="lambda:InvokeFunction",
                principal="logs.amazonaws.com",
                source_arn=f"arn:aws:logs:{region}:{account}:log-group:*"
            )
            ```

        """
        return self.lambda_client.add_permission(
            function_name=function_name,
            statement_id=statement_id,
            action=action,
            principal=principal,
            source_arn=source_arn,
            source_account=source_account,
            principal_org_id=principal_org_id,
            revision_id=revision_id,
            qualifier=qualifier,
        )

    def remove_permission(
        self,
        function_name: str,
        statement_id: str,
        qualifier: Optional[str] = None,
        revision_id: Optional[str] = None,
    ) -> bool:
        """Remove permission from Lambda function policy.

        Args:
            function_name: Function name or ARN
            statement_id: Statement identifier to remove
            qualifier: Optional function version or alias
            revision_id: Optional policy revision ID

        Returns:
            bool: True if removal was successful

        Example:
            ```python
            # Remove CloudWatch Logs permission
            lambda_api.remove_permission(
                function_name="my-function",
                statement_id="CloudWatchLogs"
            )
            ```

        """
        try:
            self.lambda_client.remove_permission(
                function_name=function_name,
                statement_id=statement_id,
                qualifier=qualifier,
                revision_id=revision_id,
            )
            return True
        except Exception as ex:
            logger.exception(f"Failed to remove permission {
                statement_id} from function {function_name}: {ex!s}")
            return False

    def get_policy(
        self,
        function_name: str,
        qualifier: str | None = None,
    ) -> dict[str, Any] | None:
        """Get Lambda function policy.

        Args:
            function_name: Function name or ARN
            qualifier: Optional function version or alias

        Returns:
            Optional[Dict]: Function policy if exists, None otherwise

        Example:
            ```python
            # Get function policy
            policy = lambda_api.get_policy("my-function")
            if policy:
                print(f"Policy: {json.dumps(policy, indent=2)}")
            ```

        """
        try:
            response = self.lambda_client.get_policy(
                function_name=function_name,
                qualifier=qualifier,
            )
            return json.loads(response["Policy"])
        except Exception as ex:
            if "ResourceNotFoundException" in str(ex):
                return None
            logger.exception(f"Failed to get policy for function {
                function_name}: {ex!s}")
            raise

    def add_trigger(
        self,
        function_name: str,
        trigger_type: TriggerType,
        source_arn: str,
        statement_id: str | None = None,
    ) -> dict[str, Any]:
        """Add a trigger to Lambda function.

        This method adds necessary permissions and configurations to allow a service
        to trigger the Lambda function.

        Args:
            function_name: Name or ARN of the Lambda function
            trigger_type: Type of trigger to add (e.g., API_GATEWAY, S3, etc.)
            source_arn: ARN of the triggering service
            statement_id: Optional unique statement identifier
                        (defaults to '{TriggerType}-{timestamp}')

        Returns:
            Dict containing the added permission statement

        Example:
            ```python
            # Add API Gateway trigger
            lambda_api.add_trigger(
                function_name="my-function",
                trigger_type=TriggerType.API_GATEWAY,
                source_arn="arn:aws:execute-api:region:account:api-id/*"
            )

            # Add S3 trigger
            lambda_api.add_trigger(
                function_name="my-function",
                trigger_type=TriggerType.S3,
                source_arn="arn:aws:s3:::my-bucket"
            )
            ```

        Raises:
            ValueError: If the provided parameters are invalid
            Exception: If adding the trigger fails

        """
        try:
            validate_source_arn(trigger_type, source_arn)

            if statement_id is None:
                statement_id = f"{
                    trigger_type.value}-from-Lambda-{function_name}-{int(time.time())}"

            service_config = get_trigger_config(trigger_type)

            return self.add_permission(
                function_name=function_name,
                statement_id=statement_id,
                action=service_config["action"],
                principal=service_config["principal"],
                source_arn=source_arn,
            )

        except Exception as e:
            logger.exception(f"Failed to add {
                trigger_type.value} trigger to Lambda function: {e!s}")
            raise
