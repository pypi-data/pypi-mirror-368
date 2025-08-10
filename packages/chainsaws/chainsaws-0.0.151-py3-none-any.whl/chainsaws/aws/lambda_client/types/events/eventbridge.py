"""EventBridge event types for AWS Lambda."""


from typing import Dict, List, TypedDict


class EventBridgeEvent(TypedDict):
    """Event sent by Amazon EventBridge (CloudWatch Events) to Lambda.

    Args:
        version (str): The version of the event schema.
        id (str): A unique ID for the event.
        detail_type (str): A string describing the event type.
        source (str): The service or custom source that generated the event.
        account (str): The 12-digit AWS account ID that generated the event.
        time (str): The event timestamp.
        region (str): The AWS region where the event originated.
        resources (List[str]): ARNs of AWS resources associated with the event.
        detail (Dict): The event detail schema varies by service and event type.

    References:
        - https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-events.html
        - https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents.html
    """
    version: str
    id: str
    detail_type: str
    source: str
    account: str
    time: str
    region: str
    resources: List[str]
    detail: Dict
