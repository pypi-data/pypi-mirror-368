"""CloudFormation Custom Resource event types for AWS Lambda."""

from typing import Any, Dict, Literal, TypedDict, Union


class CloudFormationCustomResourceCommon(TypedDict):
    """Common fields for all CloudFormation Custom Resource events.

    Args:
        RequestId (str): Unique identifier for the request.
        ResponseURL (str): URL to send the response to.
        ResourceType (str): Type of the custom resource.
        LogicalResourceId (str): Template developer-chosen name to identify the resource.
        StackId (str): ARN that identifies the stack.
        ResourceProperties (Dict[str, Any]): Resource properties defined in the template.

    Reference:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requesttypes.html
    """
    ResourceType: str
    RequestId: str
    ResponseURL: str
    LogicalResourceId: str
    StackId: str
    ResourceProperties: Dict[str, Any]


class CloudFormationCustomResourceCreate(CloudFormationCustomResourceCommon):
    """Create event for CloudFormation Custom Resource.

    Args:
        RequestType (Literal["Create"]): Must be "Create".

    Reference:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requesttypes-create.html
    """
    RequestType: Literal["Create"]


class CloudFormationCustomResourceUpdate(CloudFormationCustomResourceCommon):
    """Update event for CloudFormation Custom Resource.

    Args:
        RequestType (Literal["Update"]): Must be "Update".
        PhysicalResourceId (str): The custom resource provider-defined physical ID.
        OldResourceProperties (Dict[str, Any]): Previous resource properties.

    Reference:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requesttypes-update.html
    """
    RequestType: Literal["Update"]
    PhysicalResourceId: str
    OldResourceProperties: Dict[str, Any]


class CloudFormationCustomResourceDelete(CloudFormationCustomResourceCommon):
    """Delete event for CloudFormation Custom Resource.

    Args:
        RequestType (Literal["Delete"]): Must be "Delete".
        PhysicalResourceId (str): The custom resource provider-defined physical ID.

    Reference:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requesttypes-delete.html
    """
    RequestType: Literal["Delete"]
    PhysicalResourceId: str


# Type alias for the union of all possible event types
CloudFormationCustomResourceEvent = Union[
    CloudFormationCustomResourceCreate,
    CloudFormationCustomResourceUpdate,
    CloudFormationCustomResourceDelete,
]
"""Union type for all CloudFormation Custom Resource events.

The event will be one of:
    - CloudFormationCustomResourceCreate: For resource creation
    - CloudFormationCustomResourceUpdate: For resource updates
    - CloudFormationCustomResourceDelete: For resource deletion

Reference:
    https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requesttypes.html
"""
