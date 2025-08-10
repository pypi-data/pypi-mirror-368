"""Application Load Balancer event types for AWS Lambda."""


from typing import Dict, TypedDict


class ELB(TypedDict):
    """Information about the Application Load Balancer target group.

    Args:
        targetGroupArn (str): The Amazon Resource Name (ARN) of the target group.
    """
    targetGroupArn: str


class ALBRequestContext(TypedDict):
    """Context information about the ALB request.

    Args:
        elb (ELB): Information about the Elastic Load Balancer.
    """
    elb: ELB


class ALBEvent(TypedDict, total=False):
    """Event sent by Application Load Balancer to Lambda.

    Args:
        requestContext (ALBRequestContext): Context information about the request.
        httpMethod (str): The HTTP method used in the request (GET, POST, etc.).
        path (str): The request path.
        queryStringParameters (Dict[str, str], optional): Query string parameters.
        headers (Dict[str, str], optional): HTTP request headers.
        isBase64Encoded (bool): Whether the body is base64 encoded.
        body (str, optional): The request body.

    Reference:
        https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html
    """
    requestContext: ALBRequestContext
    httpMethod: str
    path: str
    queryStringParameters: Dict[str, str]
    headers: Dict[str, str]
    isBase64Encoded: bool
    body: str
