"""API Gateway Lambda Authorizer event types for AWS Lambda."""

from typing import Any, Dict, Literal, List, TypedDict


class APIGatewayTokenAuthorizerEvent(TypedDict):
    """Event sent to a Token-based Lambda authorizer.

    Args:
        type (str): The type of authorizer.
        authorizationToken (str): The token sent by the client.
        methodArn (str): The ARN of the method being authorized.
    """
    type: str
    authorizationToken: str
    methodArn: str


class APIGatewayRequestAuthorizerEvent(TypedDict):
    """Event sent to a Request-based Lambda authorizer.

    Args:
        type (str): Must be 'REQUEST'.
        methodArn (str): The ARN of the method being authorized.
        resource (str): The API Gateway resource path.
        path (str): The request path.
        httpMethod (str): The HTTP method of the request.
        headers (Dict[str, str]): The request headers.
        queryStringParameters (Dict[str, str]): Query string parameters.
        pathParameters (Dict[str, str]): Path parameters.
        stageVariables (Dict[str, str]): Stage variables.
        requestContext (Dict[str, Any]): Request context information.

    Reference:
        https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-lambda-authorizer-input.html
    """
    type: Literal["REQUEST"]
    methodArn: str
    resource: str
    path: str
    httpMethod: str
    headers: Dict[str, str]
    queryStringParameters: Dict[str, str]
    pathParameters: Dict[str, str]
    stageVariables: Dict[str, str]
    requestContext: Dict[str, Any]


class APIGatewayHTTPRequestInfo(TypedDict):
    method: Literal["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
    path: str
    protocol: str
    sourceIp: str
    userAgent: str


class APIGatewayHTTPRequestContext(TypedDict):
    accountId: str
    apiId: str
    authentication: Dict[str, Any]
    domainName: str
    domainPrefix: str
    http: APIGatewayHTTPRequestInfo
    requestId: str
    routeKey: str
    stage: str
    time: str
    timeEpoch: int


class APIGatewayHTTPAuthorizerV2Event(TypedDict):
    """
    APIGatewayHTTPAuthorizerEvent
    https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html#http-api-lambda-authorizer.payload-format
    """
    version: Literal["2.0"]
    type: Literal["REQUEST"]
    identitySource: List[str]
    routeArn: str
    routeKey: str
    rawPath: str
    rawQueryString: str
    cookies: List[str]
    headers: Dict[str, str]
    queryStringParameters: Dict[str, str]
    requestContext: APIGatewayHTTPRequestContext
    pathParameters: Dict[str, str]
    stageVariables: Dict[str, str]
