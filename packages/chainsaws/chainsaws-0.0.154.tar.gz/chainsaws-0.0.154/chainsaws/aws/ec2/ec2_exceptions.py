"""Exceptions for AWS EC2 operations."""


class EC2Error(Exception):
    """Base exception for EC2 operations."""

    pass


class InstanceError(EC2Error):
    """Exception raised for EC2 instance operations."""

    pass


class VolumeError(EC2Error):
    """Exception raised for EC2 volume operations."""

    pass


class SecurityGroupError(EC2Error):
    """Exception raised for EC2 security group operations."""

    pass


class NetworkInterfaceError(EC2Error):
    """Exception raised for EC2 network interface operations."""

    pass


class ImageError(EC2Error):
    """Exception raised for EC2 image operations."""

    pass


class SnapshotError(EC2Error):
    """Exception raised for EC2 snapshot operations."""

    pass 