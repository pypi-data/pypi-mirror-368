"""Lambda execution context types."""
from typing import Dict, TypedDict


class Identity(TypedDict):
    """Cognito identity information.

    Args:
        cognito_identity_id (str): The authenticated Amazon Cognito identity.
        cognito_identity_pool_id (str): The Amazon Cognito identity pool that 
            authorized the invocation.
    """
    cognito_identity_id: str
    cognito_identity_pool_id: str


class Client(TypedDict):
    """Mobile client application information.

    Args:
        installation_id (str): Unique identifier for the app installation.
        app_title (str): Application name.
        app_version_name (str): Application version name.
        app_version_code (str): Application version code.
        app_package_name (str): Application package identifier.
    """
    installation_id: str
    app_title: str
    app_version_name: str
    app_version_code: str
    app_package_name: str


class ClientContext(TypedDict):
    """Mobile client context information.

    Args:
        client (Client): Information about the client application.
        custom (Dict): Custom values set by the mobile client application.
        env (Dict): Environment information provided by the AWS SDK.
    """
    client: Client
    custom: Dict
    env: Dict


class Context(TypedDict):
    """Lambda function execution context.

    This object provides information about the invocation, function, and runtime 
    environment. It is passed to your function by Lambda at runtime.

    Args:
        function_name (str): The name of the Lambda function.
        function_version (str): The version of the function.
        invoked_function_arn (str): The ARN used to invoke the function.
            Indicates if the invoker specified a version number or alias.
        memory_limit_in_mb (str): The amount of memory allocated for the function.
        aws_request_id (str): The identifier of the invocation request.
        log_group_name (str): The log group for the function.
        log_stream_name (str): The log stream for the function instance.
        identity (Identity): Information about the Cognito identity that 
            authorized the request.
        client_context (ClientContext): Client context provided by the client 
            application.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """
    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: str
    aws_request_id: str
    log_group_name: str
    log_stream_name: str
    identity: Identity
    client_context: ClientContext
