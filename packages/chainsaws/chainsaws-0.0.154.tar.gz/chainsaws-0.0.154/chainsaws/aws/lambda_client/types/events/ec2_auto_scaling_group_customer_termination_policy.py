"""EC2 Auto Scaling Group Custom Termination Policy event types for AWS Lambda."""


from typing import List, Literal, TypedDict


class Capacity(TypedDict):
    """Capacity information for termination.

    Args:
        AvailabilityZone (str): The Availability Zone of the capacity to terminate.
        Capacity (int): The number of instances to terminate in this AZ.
        InstanceMarketOption (str): Whether the instances are on-demand or spot.
    """
    AvailabilityZone: str
    Capacity: int
    InstanceMarketOption: Literal[
        "on-demand",
        "spot",
    ]


class Instance(TypedDict):
    """Information about an EC2 instance in the Auto Scaling group.

    Args:
        AvailabilityZone (str): The Availability Zone of the instance.
        InstanceId (str): The ID of the EC2 instance.
        InstanceType (str): The instance type (e.g., t3.micro).
        InstanceMarketOption (str): Whether this is an on-demand or spot instance.
    """
    AvailabilityZone: str
    InstanceId: str
    InstanceType: str
    InstanceMarketOption: Literal[
        "on-demand",
        "spot",
    ]


class EC2ASGCustomTerminationPolicyEvent(TypedDict):
    """Event for EC2 Auto Scaling group custom termination policy.

    Args:
        AutoScalingGroupARN (str): The ARN of the Auto Scaling group.
        AutoScalingGroupName (str): The name of the Auto Scaling group.
        CapacityToTerminate (List[Capacity]): Details about the capacity that needs to be terminated.
        Instances (List[Instance]): List of all instances in the Auto Scaling group.
        Cause (str): The reason for the termination request.

    Reference:
        https://docs.aws.amazon.com/autoscaling/ec2/userguide/lambda-custom-termination-policy.html
    """
    AutoScalingGroupARN: str
    AutoScalingGroupName: str
    CapacityToTerminate: List[Capacity]
    Instances: List[Instance]
    Cause: Literal[
        "SCALE_IN",
        "INSTANCE_REFRESH",
        "MAX_INSTANCE_LIFETIME",
        "REBALANCE",
    ]
