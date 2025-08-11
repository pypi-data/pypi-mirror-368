"""AWS EC2 service module."""

from chainsaws.aws.ec2.ec2 import EC2API
from chainsaws.aws.ec2.ec2_exceptions import EC2Error

__all__ = ["EC2API", "EC2Error"] 