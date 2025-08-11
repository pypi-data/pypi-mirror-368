"""Models for AWS EC2 operations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List

from chainsaws.aws.shared.config import APIConfig
from chainsaws.aws.ec2.ec2_types import (
    InstanceType,
    InstanceState,
    VolumeType,
    VolumeState,
    ImageState,
    SnapshotState,
)


@dataclass
class EC2APIConfig(APIConfig):
    """Configuration for EC2 API."""

    credentials: Optional[Dict[str, str]] = None
    region: Optional[str] = None
    profile_name: Optional[str] = None


@dataclass
class Tag:
    """EC2 resource tag."""

    key: str
    value: str

    @classmethod
    def from_response(cls, response: Dict[str, str]) -> 'Tag':
        """Create tag from API response."""
        return cls(
            key=response['Key'],
            value=response['Value'],
        )

    def to_dict(self) -> Dict[str, str]:
        """Convert tag to API request format."""
        return {
            'Key': self.key,
            'Value': self.value,
        }


@dataclass
class Instance:
    """EC2 instance."""

    instance_id: str
    instance_type: InstanceType
    state: InstanceState
    public_ip_address: Optional[str]
    private_ip_address: Optional[str]
    tags: List[Tag]
    launch_time: datetime
    state_transition_reason: Optional[str] = None
    state_code: Optional[int] = None

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'Instance':
        """Create instance from API response."""
        return cls(
            instance_id=response['InstanceId'],
            instance_type=response['InstanceType'],
            state=response['State']['Name'],
            public_ip_address=response.get('PublicIpAddress'),
            private_ip_address=response.get('PrivateIpAddress'),
            tags=[Tag.from_response(tag) for tag in response.get('Tags', [])],
            launch_time=response['LaunchTime'],
            state_transition_reason=response.get('StateTransitionReason'),
            state_code=response.get('StateCode'),
        )


@dataclass
class Volume:
    """EC2 volume."""

    volume_id: str
    size: int
    volume_type: VolumeType
    state: VolumeState
    availability_zone: str
    tags: List[Tag]
    create_time: datetime
    iops: Optional[int] = None
    snapshot_id: Optional[str] = None
    encrypted: bool = False
    kms_key_id: Optional[str] = None
    multi_attach_enabled: bool = False
    throughput: Optional[int] = None

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'Volume':
        """Create volume from API response."""
        return cls(
            volume_id=response['VolumeId'],
            size=response['Size'],
            volume_type=response['VolumeType'],
            state=response['State'],
            availability_zone=response['AvailabilityZone'],
            tags=[Tag.from_response(tag) for tag in response.get('Tags', [])],
            create_time=response['CreateTime'],
            iops=response.get('Iops'),
            snapshot_id=response.get('SnapshotId'),
            encrypted=response.get('Encrypted', False),
            kms_key_id=response.get('KmsKeyId'),
            multi_attach_enabled=response.get('MultiAttachEnabled', False),
            throughput=response.get('Throughput'),
        )


@dataclass
class CreateVolumeConfig:
    """Configuration for creating a new volume."""

    availability_zone: str
    size: int
    volume_type: VolumeType = "gp3"
    iops: Optional[int] = None
    snapshot_id: Optional[str] = None
    encrypted: bool = False
    kms_key_id: Optional[str] = None
    tags: Optional[List[Tag]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to API request format."""
        params = {
            'AvailabilityZone': self.availability_zone,
            'Size': self.size,
            'VolumeType': self.volume_type,
        }
        if self.iops:
            params['Iops'] = self.iops
        if self.snapshot_id:
            params['SnapshotId'] = self.snapshot_id
        if self.encrypted:
            params['Encrypted'] = True
        if self.kms_key_id:
            params['KmsKeyId'] = self.kms_key_id
        if self.tags:
            params['TagSpecifications'] = [{
                'ResourceType': 'volume',
                'Tags': [tag.to_dict() for tag in self.tags],
            }]
        return params


@dataclass
class CreateInstanceConfig:
    """Configuration for creating a new instance."""

    image_id: str
    instance_type: InstanceType
    min_count: int = 1
    max_count: int = 1
    key_name: Optional[str] = None
    security_group_ids: Optional[List[str]] = None
    subnet_id: Optional[str] = None
    tags: Optional[List[Tag]] = None
    user_data: Optional[str] = None
    iam_instance_profile: Optional[Dict[str, str]] = None
    block_device_mappings: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to API request format."""
        params = {
            'ImageId': self.image_id,
            'InstanceType': self.instance_type,
            'MinCount': self.min_count,
            'MaxCount': self.max_count,
        }
        if self.key_name:
            params['KeyName'] = self.key_name
        if self.security_group_ids:
            params['SecurityGroupIds'] = self.security_group_ids
        if self.subnet_id:
            params['SubnetId'] = self.subnet_id
        if self.user_data:
            params['UserData'] = self.user_data
        if self.iam_instance_profile:
            params['IamInstanceProfile'] = self.iam_instance_profile
        if self.block_device_mappings:
            params['BlockDeviceMappings'] = self.block_device_mappings
        if self.tags:
            params['TagSpecifications'] = [{
                'ResourceType': 'instance',
                'Tags': [tag.to_dict() for tag in self.tags],
            }]
        return params


@dataclass
class SecurityGroup:
    """EC2 security group."""

    group_id: str
    group_name: str
    description: str
    vpc_id: Optional[str]
    tags: List[Tag]

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'SecurityGroup':
        """Create security group from API response."""
        return cls(
            group_id=response['GroupId'],
            group_name=response['GroupName'],
            description=response['Description'],
            vpc_id=response.get('VpcId'),
            tags=[Tag.from_response(tag) for tag in response.get('Tags', [])],
        )


@dataclass
class NetworkInterface:
    """EC2 network interface."""

    network_interface_id: str
    subnet_id: str
    vpc_id: str
    availability_zone: str
    description: Optional[str]
    private_ip_address: str
    mac_address: str
    state: str
    tags: List[Tag]

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'NetworkInterface':
        """Create network interface from API response."""
        return cls(
            network_interface_id=response['NetworkInterfaceId'],
            subnet_id=response['SubnetId'],
            vpc_id=response['VpcId'],
            availability_zone=response['AvailabilityZone'],
            description=response.get('Description'),
            private_ip_address=response['PrivateIpAddress'],
            mac_address=response['MacAddress'],
            state=response['Status'],
            tags=[Tag.from_response(tag) for tag in response.get('Tags', [])],
        )


@dataclass
class Image:
    """EC2 image."""

    image_id: str
    name: str
    description: Optional[str]
    state: ImageState
    architecture: str
    platform: Optional[str]
    tags: List[Tag]
    creation_date: datetime

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'Image':
        """Create image from API response."""
        return cls(
            image_id=response['ImageId'],
            name=response['Name'],
            description=response.get('Description'),
            state=response['State'],
            architecture=response['Architecture'],
            platform=response.get('Platform'),
            tags=[Tag.from_response(tag) for tag in response.get('Tags', [])],
            creation_date=response['CreationDate'],
        )


@dataclass
class Snapshot:
    """EC2 snapshot."""

    snapshot_id: str
    volume_id: str
    state: SnapshotState
    start_time: datetime
    progress: str
    owner_id: str
    description: Optional[str]
    tags: List[Tag]

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'Snapshot':
        """Create snapshot from API response."""
        return cls(
            snapshot_id=response['SnapshotId'],
            volume_id=response['VolumeId'],
            state=response['State'],
            start_time=response['StartTime'],
            progress=response['Progress'],
            owner_id=response['OwnerId'],
            description=response.get('Description'),
            tags=[Tag.from_response(tag) for tag in response.get('Tags', [])],
        ) 