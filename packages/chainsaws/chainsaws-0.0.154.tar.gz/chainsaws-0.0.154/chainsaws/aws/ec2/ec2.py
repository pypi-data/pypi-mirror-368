"""High-level EC2 API for AWS EC2 operations."""

import logging
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from chainsaws.aws.shared import session
from chainsaws.aws.ec2._ec2_internal import EC2
from chainsaws.aws.ec2.ec2_models import (
    EC2APIConfig,
    Instance,
    Volume,
    SecurityGroup,
    NetworkInterface,
    Tag,
    Image,
    Snapshot,
    CreateVolumeConfig,
    CreateInstanceConfig,
)
from chainsaws.aws.ec2.ec2_exceptions import (
    EC2Error,
    InstanceError,
    VolumeError,
    SecurityGroupError,
    NetworkInterfaceError,
    ImageError,
    SnapshotError,
)
from chainsaws.aws.ec2.ec2_types import (
    InstanceType,
    InstanceState,
    MetricAlarmConfig,
    ArchitectureType,
    HealthStatusType,
    CostEstimateType,
    OperationScheduleType,
    AutomationScheduleType,
    BackupPolicyType,
    SecurityPolicyType,
)
from chainsaws.utils.list_utils.list_utils import listify

logger = logging.getLogger(__name__)

@dataclass
class CleanupProgress:
    """리소스 정리 진행 상황 추적"""
    total: int
    processed: int = 0
    deleted: Dict[str, List[str]] = None
    errors: Dict[str, List[str]] = None

    def __post_init__(self):
        if self.deleted is None:
            self.deleted = {
                "volumes": [],
                "snapshots": [],
                "security_groups": [],
                "network_interfaces": []
            }
        if self.errors is None:
            self.errors = {
                "volumes": [],
                "snapshots": [],
                "security_groups": [],
                "network_interfaces": []
            }

    def log_status(self):
        """현재 진행 상황 로깅"""
        logger.info(f"Progress: {self.processed}/{self.total} resources")
        if self.deleted:
            logger.info(f"Deleted: {sum(len(ids) for ids in self.deleted.values())} resources")
            for resource_type, ids in self.deleted.items():
                if ids:
                    logger.info(f"- {resource_type}: {len(ids)} resources")
        if self.errors:
            error_count = sum(len(ids) for ids in self.errors.values())
            if error_count > 0:
                logger.warning(f"Errors: {error_count} resources")
                for resource_type, ids in self.errors.items():
                    if ids:
                        logger.warning(f"- {resource_type}: {len(ids)} resources")

class EC2API:
    """High-level EC2 API for AWS EC2 operations."""

    def __init__(self, config: Optional[EC2APIConfig] = None) -> None:
        """Initialize EC2 client.

        Args:
            config: Optional EC2 configuration

        Raises:
            EC2Error: If client initialization fails
        """
        try:
            self.config = config or EC2APIConfig()
            self.boto3_session = session.get_boto_session(
                self.config.credentials if self.config.credentials else None,
            )
            self.ec2 = EC2(
                boto3_session=self.boto3_session,
                config=config,
            )
        except Exception as e:
            logger.error(f"Failed to initialize EC2 client: {str(e)}")
            raise EC2Error(f"EC2 client initialization failed: {str(e)}") from e

    def describe_instances(
        self,
        instance_ids: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Instance]:
        """Describe EC2 instances.

        Args:
            instance_ids: Optional list of instance IDs to describe
            filters: Optional list of filters to apply

        Returns:
            List of EC2 instances

        Raises:
            InstanceError: If instance description fails
        """
        try:
            return self.ec2.describe_instances(instance_ids=instance_ids, filters=filters)
        except Exception as e:
            logger.error(f"Failed to describe instances: {str(e)}")
            raise InstanceError(f"Instance description failed: {str(e)}")

    def describe_volumes(
        self,
        volume_ids: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Volume]:
        """Describe EC2 volumes.

        Args:
            volume_ids: Optional list of volume IDs to describe
            filters: Optional list of filters to apply

        Returns:
            List of EC2 volumes

        Raises:
            VolumeError: If volume description fails
        """
        try:
            return self.ec2.describe_volumes(volume_ids=volume_ids, filters=filters)
        except Exception as e:
            logger.error(f"Failed to describe volumes: {str(e)}")
            raise VolumeError(f"Volume description failed: {str(e)}")

    def describe_security_groups(
        self,
        group_ids: Optional[List[str]] = None,
        group_names: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> List[SecurityGroup]:
        """Describe EC2 security groups.

        Args:
            group_ids: Optional list of security group IDs to describe
            group_names: Optional list of security group names to describe
            filters: Optional list of filters to apply

        Returns:
            List of EC2 security groups

        Raises:
            SecurityGroupError: If security group description fails
        """
        try:
            return self.ec2.describe_security_groups(
                group_ids=group_ids,
                group_names=group_names,
                filters=filters,
            )
        except Exception as e:
            logger.error(f"Failed to describe security groups: {str(e)}")
            raise SecurityGroupError(f"Security group description failed: {str(e)}")

    def describe_network_interfaces(
        self,
        network_interface_ids: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> List[NetworkInterface]:
        """Describe EC2 network interfaces.

        Args:
            network_interface_ids: Optional list of network interface IDs to describe
            filters: Optional list of filters to apply

        Returns:
            List of EC2 network interfaces

        Raises:
            NetworkInterfaceError: If network interface description fails
        """
        try:
            return self.ec2.describe_network_interfaces(
                network_interface_ids=network_interface_ids,
                filters=filters,
            )
        except Exception as e:
            logger.error(f"Failed to describe network interfaces: {str(e)}")
            raise NetworkInterfaceError(f"Network interface description failed: {str(e)}")

    def describe_images(
        self,
        image_ids: Optional[List[str]] = None,
        owners: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Image]:
        """Describe EC2 images.

        Args:
            image_ids: Optional list of image IDs to describe
            owners: Optional list of image owners to describe
            filters: Optional list of filters to apply

        Returns:
            List of EC2 images

        Raises:
            ImageError: If image description fails
        """
        try:
            return self.ec2.describe_images(
                image_ids=image_ids,
                owners=owners,
                filters=filters,
            )
        except Exception as e:
            logger.error(f"Failed to describe images: {str(e)}")
            raise ImageError(f"Image description failed: {str(e)}")

    def describe_snapshots(
        self,
        snapshot_ids: Optional[List[str]] = None,
        owner_ids: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Snapshot]:
        """Describe EC2 snapshots.

        Args:
            snapshot_ids: Optional list of snapshot IDs to describe
            owner_ids: Optional list of snapshot owner IDs to describe
            filters: Optional list of filters to apply

        Returns:
            List of EC2 snapshots

        Raises:
            SnapshotError: If snapshot description fails
        """
        try:
            return self.ec2.describe_snapshots(
                snapshot_ids=snapshot_ids,
                owner_ids=owner_ids,
                filters=filters,
            )
        except Exception as e:
            logger.error(f"Failed to describe snapshots: {str(e)}")
            raise SnapshotError(f"Snapshot description failed: {str(e)}")

    def start_instances(self, instance_ids: List[str]) -> List[Instance]:
        """Start EC2 instances.

        Args:
            instance_ids: List of instance IDs to start

        Returns:
            List of started instances

        Raises:
            InstanceError: If instance start fails
        """
        try:
            return self.ec2.start_instances(instance_ids=instance_ids)
        except Exception as e:
            logger.error(f"Failed to start instances: {str(e)}")
            raise InstanceError(f"Instance start failed: {str(e)}") from e

    def stop_instances(self, instance_ids: List[str]) -> List[Instance]:
        """Stop EC2 instances.

        Args:
            instance_ids: List of instance IDs to stop

        Returns:
            List of stopped instances

        Raises:
            InstanceError: If instance stop fails
        """
        try:
            return self.ec2.stop_instances(instance_ids=instance_ids)
        except Exception as e:
            logger.error(f"Failed to stop instances: {str(e)}")
            raise InstanceError(f"Instance stop failed: {str(e)}") from e

    def terminate_instances(self, instance_ids: List[str]) -> List[Instance]:
        """Terminate EC2 instances.

        Args:
            instance_ids: List of instance IDs to terminate

        Returns:
            List of terminated instances

        Raises:
            InstanceError: If instance termination fails
        """
        try:
            return self.ec2.terminate_instances(instance_ids=instance_ids)
        except Exception as e:
            logger.error(f"Failed to terminate instances: {str(e)}")
            raise InstanceError(f"Instance termination failed: {str(e)}") from e

    def reboot_instances(self, instance_ids: List[str]) -> None:
        """Reboot EC2 instances.

        Args:
            instance_ids: List of instance IDs to reboot

        Raises:
            InstanceError: If instance reboot fails
        """
        try:
            self.ec2.reboot_instances(instance_ids=instance_ids)
        except Exception as e:
            logger.error(f"Failed to reboot instances: {str(e)}")
            raise InstanceError(f"Instance reboot failed: {str(e)}") from e

    def create_instances(
        self,
        image_id: str,
        instance_type: str,
        min_count: int = 1,
        max_count: int = 1,
        key_name: Optional[str] = None,
        security_group_ids: Optional[List[str]] = None,
        subnet_id: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
        user_data: Optional[str] = None,
        iam_instance_profile: Optional[Dict[str, str]] = None,
        block_device_mappings: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Instance]:
        """Create new EC2 instances.

        Args:
            image_id: ID of the AMI to use
            instance_type: Type of instance to launch
            min_count: Minimum number of instances to launch
            max_count: Maximum number of instances to launch
            key_name: Name of the key pair to use
            security_group_ids: List of security group IDs
            subnet_id: ID of the subnet to launch in
            tags: List of tags to apply to the instances
            user_data: User data to pass to the instances
            iam_instance_profile: IAM instance profile to use
            block_device_mappings: Block device mappings for the instances

        Returns:
            List of created instances

        Raises:
            InstanceError: If instance creation fails
        """
        try:
            config = CreateInstanceConfig(
                image_id=image_id,
                instance_type=instance_type,
                min_count=min_count,
                max_count=max_count,
                key_name=key_name,
                security_group_ids=security_group_ids,
                subnet_id=subnet_id,
                tags=[Tag(key=k, value=v) for k, v in tags] if tags else None,
                user_data=user_data,
                iam_instance_profile=iam_instance_profile,
                block_device_mappings=block_device_mappings,
            )
            return self.ec2.create_instances(config=config)
        except Exception as e:
            logger.error(f"Failed to create instances: {str(e)}")
            raise InstanceError(f"Instance creation failed: {str(e)}") from e

    def create_volume(
        self,
        availability_zone: str,
        size: int,
        volume_type: str = "gp3",
        iops: Optional[int] = None,
        snapshot_id: Optional[str] = None,
        encrypted: bool = False,
        kms_key_id: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> Volume:
        """Create a new EC2 volume.

        Args:
            availability_zone: Availability zone to create the volume in
            size: Size of the volume in GiB
            volume_type: Type of volume to create
            iops: IOPS for the volume (required for io1/io2)
            snapshot_id: ID of the snapshot to create from
            encrypted: Whether to encrypt the volume
            kms_key_id: KMS key ID for encryption
            tags: List of tags to apply to the volume

        Returns:
            Created volume

        Raises:
            VolumeError: If volume creation fails
        """
        try:
            config = CreateVolumeConfig(
                availability_zone=availability_zone,
                size=size,
                volume_type=volume_type,
                iops=iops,
                snapshot_id=snapshot_id,
                encrypted=encrypted,
                kms_key_id=kms_key_id,
                tags=[Tag(key=k, value=v) for k, v in tags] if tags else None,
            )
            return self.ec2.create_volume(config=config)
        except Exception as e:
            logger.error(f"Failed to create volume: {str(e)}")
            raise VolumeError(f"Volume creation failed: {str(e)}") from e

    def delete_volume(self, volume_id: str) -> None:
        """Delete an EC2 volume.

        Args:
            volume_id: ID of the volume to delete

        Raises:
            VolumeError: If volume deletion fails
        """
        try:
            self.ec2.delete_volume(volume_id=volume_id)
        except Exception as e:
            logger.error(f"Failed to delete volume: {str(e)}")
            raise VolumeError(f"Volume deletion failed: {str(e)}") from e

    def attach_volume(
        self,
        volume_id: str,
        instance_id: str,
        device: str,
    ) -> None:
        """Attach a volume to an instance.

        Args:
            volume_id: ID of the volume to attach
            instance_id: ID of the instance to attach to
            device: Device name (e.g., /dev/sdf)

        Raises:
            VolumeError: If volume attachment fails
        """
        try:
            self.ec2.attach_volume(
                volume_id=volume_id,
                instance_id=instance_id,
                device=device,
            )
        except Exception as e:
            logger.error(f"Failed to attach volume: {str(e)}")
            raise VolumeError(f"Volume attachment failed: {str(e)}") from e

    def detach_volume(self, volume_id: str) -> None:
        """Detach a volume from an instance.

        Args:
            volume_id: ID of the volume to detach

        Raises:
            VolumeError: If volume detachment fails
        """
        try:
            self.ec2.detach_volume(volume_id=volume_id)
        except Exception as e:
            logger.error(f"Failed to detach volume: {str(e)}")
            raise VolumeError(f"Volume detachment failed: {str(e)}") from e

    def modify_volume(
        self,
        volume_id: str,
        size: Optional[int] = None,
        volume_type: Optional[str] = None,
        iops: Optional[int] = None,
    ) -> Volume:
        """Modify an EC2 volume.

        Args:
            volume_id: ID of the volume to modify
            size: New size in GiB
            volume_type: New volume type
            iops: New IOPS value

        Returns:
            Modified volume

        Raises:
            VolumeError: If volume modification fails
        """
        try:
            return self.ec2.modify_volume(
                volume_id=volume_id,
                size=size,
                volume_type=volume_type,
                iops=iops,
            )
        except Exception as e:
            logger.error(f"Failed to modify volume: {str(e)}")
            raise VolumeError(f"Volume modification failed: {str(e)}") from e

    def create_security_group(
        self,
        group_name: str,
        description: str,
        vpc_id: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> SecurityGroup:
        """Create a new security group.

        Args:
            group_name: Name of the security group
            description: Description of the security group
            vpc_id: Optional VPC ID to create the group in
            tags: Optional list of tags to apply

        Returns:
            Created security group

        Raises:
            SecurityGroupError: If security group creation fails
        """
        try:
            return self.ec2.create_security_group(
                group_name=group_name,
                description=description,
                vpc_id=vpc_id,
                tags=[Tag(key=k, value=v) for k, v in tags] if tags else None,
            )
        except Exception as e:
            logger.error(f"Failed to create security group: {str(e)}")
            raise SecurityGroupError(f"Security group creation failed: {str(e)}") from e

    def delete_security_group(self, group_id: str) -> None:
        """Delete a security group.

        Args:
            group_id: ID of the security group to delete

        Raises:
            SecurityGroupError: If security group deletion fails
        """
        try:
            self.ec2.delete_security_group(group_id=group_id)
        except Exception as e:
            logger.error(f"Failed to delete security group: {str(e)}")
            raise SecurityGroupError(f"Security group deletion failed: {str(e)}") from e

    def authorize_security_group_ingress(
        self,
        group_id: str,
        ip_permissions: List[Dict[str, Any]],
    ) -> None:
        """Add inbound rules to a security group.

        Args:
            group_id: ID of the security group
            ip_permissions: List of IP permissions to add

        Raises:
            SecurityGroupError: If rule addition fails
        """
        try:
            self.ec2.authorize_security_group_ingress(
                group_id=group_id,
                ip_permissions=ip_permissions,
            )
        except Exception as e:
            logger.error(f"Failed to authorize security group ingress: {str(e)}")
            raise SecurityGroupError(f"Security group ingress authorization failed: {str(e)}") from e

    def revoke_security_group_ingress(
        self,
        group_id: str,
        ip_permissions: List[Dict[str, Any]],
    ) -> None:
        """Remove inbound rules from a security group.

        Args:
            group_id: ID of the security group
            ip_permissions: List of IP permissions to remove

        Raises:
            SecurityGroupError: If rule removal fails
        """
        try:
            self.ec2.revoke_security_group_ingress(
                group_id=group_id,
                ip_permissions=ip_permissions,
            )
        except Exception as e:
            logger.error(f"Failed to revoke security group ingress: {str(e)}")
            raise SecurityGroupError(f"Security group ingress revocation failed: {str(e)}") from e

    def authorize_security_group_egress(
        self,
        group_id: str,
        ip_permissions: List[Dict[str, Any]],
    ) -> None:
        """Add outbound rules to a security group.

        Args:
            group_id: ID of the security group
            ip_permissions: List of IP permissions to add

        Raises:
            SecurityGroupError: If rule addition fails
        """
        try:
            self.ec2.authorize_security_group_egress(
                group_id=group_id,
                ip_permissions=ip_permissions,
            )
        except Exception as e:
            logger.error(f"Failed to authorize security group egress: {str(e)}")
            raise SecurityGroupError(f"Security group egress authorization failed: {str(e)}") from e

    def create_snapshot(
        self,
        volume_id: str,
        description: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> Snapshot:
        """Create a new snapshot.

        Args:
            volume_id: ID of the volume to snapshot
            description: Optional description of the snapshot
            tags: Optional list of tags to apply

        Returns:
            Created snapshot

        Raises:
            SnapshotError: If snapshot creation fails
        """
        try:
            return self.ec2.create_snapshot(
                volume_id=volume_id,
                description=description,
                tags=[Tag(key=k, value=v) for k, v in tags] if tags else None,
            )
        except Exception as e:
            logger.error(f"Failed to create snapshot: {str(e)}")
            raise SnapshotError(f"Snapshot creation failed: {str(e)}") from e

    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete a snapshot.

        Args:
            snapshot_id: ID of the snapshot to delete

        Raises:
            SnapshotError: If snapshot deletion fails
        """
        try:
            self.ec2.delete_snapshot(snapshot_id=snapshot_id)
        except Exception as e:
            logger.error(f"Failed to delete snapshot: {str(e)}")
            raise SnapshotError(f"Snapshot deletion failed: {str(e)}") from e

    def copy_snapshot(
        self,
        source_snapshot_id: str,
        source_region: str,
        description: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> Snapshot:
        """Copy a snapshot to another region.

        Args:
            source_snapshot_id: ID of the source snapshot
            source_region: Region of the source snapshot
            description: Optional description of the copy
            tags: Optional list of tags to apply

        Returns:
            Copied snapshot

        Raises:
            SnapshotError: If snapshot copy fails
        """
        try:
            return self.ec2.copy_snapshot(
                source_snapshot_id=source_snapshot_id,
                source_region=source_region,
                description=description,
                tags=[Tag(key=k, value=v) for k, v in tags] if tags else None,
            )
        except Exception as e:
            logger.error(f"Failed to copy snapshot: {str(e)}")
            raise SnapshotError(f"Snapshot copy failed: {str(e)}") from e

    def get_instance_metrics(
        self,
        instance_id: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        period: int = 60,
    ) -> List[Dict[str, Any]]:
        """Get instance metrics.

        Args:
            instance_id: ID of the instance
            metric_name: Name of the metric to get
            start_time: Start time for the metrics
            end_time: End time for the metrics
            period: Period in seconds between data points

        Returns:
            List of metric data points

        Raises:
            InstanceError: If metric retrieval fails
        """
        try:
            return self.ec2.get_instance_metrics(
                instance_id=instance_id,
                metric_name=metric_name,
                start_time=start_time,
                end_time=end_time,
                period=period,
            )
        except Exception as e:
            logger.error(f"Failed to get instance metrics: {str(e)}")
            raise InstanceError(f"Instance metrics retrieval failed: {str(e)}") from e

    def enable_instance_monitoring(self, instance_ids: List[str]) -> None:
        """Enable monitoring for instances.

        Args:
            instance_ids: List of instance IDs to enable monitoring for

        Raises:
            InstanceError: If monitoring enablement fails
        """
        try:
            self.ec2.enable_instance_monitoring(instance_ids=listify(instance_ids))
        except Exception as e:
            logger.error(f"Failed to enable instance monitoring: {str(e)}")
            raise InstanceError(f"Instance monitoring enablement failed: {str(e)}") from e

    def disable_instance_monitoring(self, instance_ids: List[str]) -> None:
        """Disable monitoring for instances.

        Args:
            instance_ids: List of instance IDs to disable monitoring for

        Raises:
            InstanceError: If monitoring disablement fails
        """
        try:
            self.ec2.disable_instance_monitoring(instance_ids=listify(instance_ids))
        except Exception as e:
            logger.error(f"Failed to disable instance monitoring: {str(e)}")
            raise InstanceError(f"Instance monitoring disablement failed: {str(e)}") from e

    def create_backup(
        self,
        instance_id: str,
        description: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Create a backup of an instance.

        Args:
            instance_id: ID of the instance to backup
            description: Optional description of the backup
            tags: Optional list of tags to apply

        Returns:
            Backup information

        Raises:
            InstanceError: If backup creation fails
        """
        try:
            return self.ec2.create_backup(
                instance_id=instance_id,
                description=description,
                tags=[Tag(key=k, value=v) for k, v in tags] if tags else None,
            )
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            raise InstanceError(f"Backup creation failed: {str(e)}") from e

    def restore_from_backup(
        self,
        backup_id: str,
        instance_type: Optional[str] = None,
        subnet_id: Optional[str] = None,
    ) -> Instance:
        """Restore an instance from a backup.

        Args:
            backup_id: ID of the backup to restore from
            instance_type: Optional instance type for the restored instance
            subnet_id: Optional subnet ID to launch the instance in

        Returns:
            Restored instance

        Raises:
            InstanceError: If instance restoration fails
        """
        try:
            return self.ec2.restore_from_backup(
                backup_id=backup_id,
                instance_type=instance_type,
                subnet_id=subnet_id,
            )
        except Exception as e:
            logger.error(f"Failed to restore from backup: {str(e)}")
            raise InstanceError(f"Instance restoration failed: {str(e)}") from e

    def wait_for_instance_state(
        self,
        instance_id: str,
        target_state: InstanceState,
        timeout: int = 300,
        check_interval: int = 15
    ) -> Instance:
        """Wait for an instance to reach the target state.

        Args:
            instance_id: ID of the instance
            target_state: Target state to wait for
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds

        Returns:
            Instance in target state

        Raises:
            InstanceError: If timeout occurs or state check fails
        """
        try:
            return self.ec2.wait_for_instance_state(
                instance_id=instance_id,
                target_state=target_state,
                timeout=timeout,
                check_interval=check_interval
            )
        except Exception as e:
            logger.error(f"Failed to wait for instance state: {str(e)}")
            raise InstanceError(f"Instance state wait failed: {str(e)}") from e

    def wait_for_volume_state(
        self,
        volume_id: str,
        target_state: str,
        timeout: int = 300,
        check_interval: int = 15
    ) -> Volume:
        """Wait for a volume to reach the target state.

        Args:
            volume_id: ID of the volume
            target_state: Target state to wait for
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds

        Returns:
            Volume in target state

        Raises:
            VolumeError: If timeout occurs or state check fails
        """
        try:
            return self.ec2.wait_for_volume_state(
                volume_id=volume_id,
                target_state=target_state,
                timeout=timeout,
                check_interval=check_interval
            )
        except Exception as e:
            logger.error(f"Failed to wait for volume state: {str(e)}")
            raise VolumeError(f"Volume state wait failed: {str(e)}") from e

    def get_latest_amazon_linux_ami(
        self,
        architecture: ArchitectureType = "x86_64"
    ) -> Image:
        """Get the latest Amazon Linux 2 AMI.

        Args:
            architecture: CPU architecture

        Returns:
            Latest Amazon Linux 2 AMI

        Raises:
            ImageError: If AMI lookup fails
        """
        try:
            return self.ec2.get_latest_amazon_linux_ami(architecture=architecture)
        except Exception as e:
            logger.error(f"Failed to get latest Amazon Linux AMI: {str(e)}")
            raise ImageError(f"AMI lookup failed: {str(e)}") from e

    def get_instance_by_name(
        self,
        name: str
    ) -> Optional[Instance]:
        """Get an instance by its Name tag.

        Args:
            name: Value of the Name tag

        Returns:
            Instance if found, None otherwise

        Raises:
            InstanceError: If instance lookup fails
        """
        try:
            return self.ec2.get_instance_by_name(name=name)
        except Exception as e:
            logger.error(f"Failed to get instance by name: {str(e)}")
            raise InstanceError(f"Instance lookup failed: {str(e)}") from e

    def add_security_group_rule(
        self,
        group_id: str,
        protocol: str,
        port: int,
        cidr: str,
        description: Optional[str] = None,
        is_ingress: bool = True
    ) -> None:
        """Add a security group rule.

        Args:
            group_id: ID of the security group
            protocol: Protocol (tcp, udp, icmp, -1)
            port: Port number
            cidr: CIDR range
            description: Optional rule description
            is_ingress: True for ingress rule, False for egress

        Raises:
            SecurityGroupError: If rule addition fails
        """
        try:
            self.ec2.add_security_group_rule(
                group_id=group_id,
                protocol=protocol,
                port=port,
                cidr=cidr,
                description=description,
                is_ingress=is_ingress
            )
        except Exception as e:
            logger.error(f"Failed to add security group rule: {str(e)}")
            raise SecurityGroupError(f"Security group rule addition failed: {str(e)}") from e

    def remove_security_group_rule(
        self,
        group_id: str,
        protocol: str,
        port: int,
        cidr: str,
        is_ingress: bool = True
    ) -> None:
        """Remove a security group rule.

        Args:
            group_id: ID of the security group
            protocol: Protocol (tcp, udp, icmp, -1)
            port: Port number
            cidr: CIDR range
            is_ingress: True for ingress rule, False for egress

        Raises:
            SecurityGroupError: If rule removal fails
        """
        try:
            self.ec2.remove_security_group_rule(
                group_id=group_id,
                protocol=protocol,
                port=port,
                cidr=cidr,
                is_ingress=is_ingress
            )
        except Exception as e:
            logger.error(f"Failed to remove security group rule: {str(e)}")
            raise SecurityGroupError(f"Security group rule removal failed: {str(e)}") from e

    def resize_instance(
        self,
        instance_id: str,
        new_instance_type: InstanceType,
        allow_reboot: bool = False
    ) -> Instance:
        """Resize an EC2 instance.

        Args:
            instance_id: ID of the instance
            new_instance_type: New instance type
            allow_reboot: Whether to allow instance reboot

        Returns:
            Resized instance

        Raises:
            InstanceError: If instance resize fails
        """
        try:
            return self.ec2.resize_instance(
                instance_id=instance_id,
                new_instance_type=new_instance_type,
                allow_reboot=allow_reboot
            )
        except Exception as e:
            logger.error(f"Failed to resize instance: {str(e)}")
            raise InstanceError(f"Instance resize failed: {str(e)}") from e

    def get_instance_health_status(
        self,
        instance_id: str
    ) -> HealthStatusType:
        """Get detailed instance health status.

        Args:
            instance_id: ID of the instance

        Returns:
            Instance health status information

        Raises:
            InstanceError: If health status check fails
        """
        try:
            return self.ec2.get_instance_health_status(instance_id=instance_id)
        except Exception as e:
            logger.error(f"Failed to get instance health status: {str(e)}")
            raise InstanceError(f"Health status check failed: {str(e)}") from e

    def setup_instance_alerts(
        self,
        instance_id: str,
        metric_alarms: List[MetricAlarmConfig]
    ) -> None:
        """Setup CloudWatch alarms for an instance.

        Args:
            instance_id: ID of the instance
            metric_alarms: List of alarm configurations

        Raises:
            InstanceError: If alarm setup fails
        """
        try:
            self.ec2.setup_instance_alerts(
                instance_id=instance_id,
                metric_alarms=metric_alarms
            )
        except Exception as e:
            logger.error(f"Failed to setup instance alerts: {str(e)}")
            raise InstanceError(f"Alert setup failed: {str(e)}") from e

    def get_instance_cost_estimate(
        self,
        instance_type: InstanceType,
        region: str,
        hours: int = 730
    ) -> CostEstimateType:
        """Get cost estimate for an instance type.

        Args:
            instance_type: Instance type
            region: AWS region
            hours: Number of hours to estimate for

        Returns:
            Cost estimate information

        Raises:
            EC2Error: If cost estimation fails
        """
        try:
            return self.ec2.get_instance_cost_estimate(
                instance_type=instance_type,
                region=region,
                hours=hours
            )
        except Exception as e:
            logger.error(f"Failed to get instance cost estimate: {str(e)}")
            raise EC2Error(f"Cost estimation failed: {str(e)}") from e

    def list_unused_resources(self) -> Dict[str, List[str]]:
        """List unused EC2 resources.

        Returns:
            Dictionary of unused resource IDs by type

        Raises:
            EC2Error: If resource listing fails
        """
        try:
            return self.ec2.list_unused_resources()
        except Exception as e:
            logger.error(f"Failed to list unused resources: {str(e)}")
            raise EC2Error(f"Resource listing failed: {str(e)}") from e

    def add_tags_to_resource(
        self,
        resource_id: str,
        tags: List[Dict[str, str]],
    ) -> None:
        """Add tags to an EC2 resource.

        Args:
            resource_id: ID of the resource to tag
            tags: List of tags to add

        Raises:
            EC2Error: If tag addition fails
        """
        try:
            self.ec2.create_tags(
                Resources=[resource_id],
                Tags=[{"Key": k, "Value": v} for k, v in tags]
            )
        except Exception as e:
            logger.error(f"Failed to add tags to resource: {str(e)}")
            raise EC2Error(f"Tag addition failed: {str(e)}") from e

    def remove_tags_from_resource(
        self,
        resource_id: str,
        tag_keys: List[str],
    ) -> None:
        """Remove tags from an EC2 resource.

        Args:
            resource_id: ID of the resource
            tag_keys: List of tag keys to remove

        Raises:
            EC2Error: If tag removal fails
        """
        try:
            self.ec2.delete_tags(
                Resources=[resource_id],
                Tags=[{"Key": key} for key in tag_keys]
            )
        except Exception as e:
            logger.error(f"Failed to remove tags from resource: {str(e)}")
            raise EC2Error(f"Tag removal failed: {str(e)}") from e

    def get_resources_by_tag(
        self,
        tag_key: str,
        tag_value: Optional[str] = None,
        resource_types: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get EC2 resources by tag.

        Args:
            tag_key: Tag key to search for
            tag_value: Optional tag value to match
            resource_types: Optional list of resource types to search

        Returns:
            Dictionary of resources by type

        Raises:
            EC2Error: If resource search fails
        """
        try:
            filters = [{"Name": f"tag:{tag_key}", "Values": [tag_value]}] if tag_value else [{"Name": "tag-key", "Values": [tag_key]}]
            
            params = {
                "Filters": filters
            }
            if resource_types:
                params["ResourceTypes"] = resource_types

            response = self.ec2.describe_tags(**params)
            resources = {}
            for tag in response["Tags"]:
                resource_type = tag["ResourceType"]
                if resource_type not in resources:
                    resources[resource_type] = []
                resources[resource_type].append({
                    "ResourceId": tag["ResourceId"],
                    "ResourceType": tag["ResourceType"],
                    "Tags": [{"Key": tag["Key"], "Value": tag["Value"]}]
                })
            return resources
        except Exception as e:
            logger.error(f"Failed to get resources by tag: {str(e)}")
            raise EC2Error(f"Resource search failed: {str(e)}") from e

    def create_network_interface(
        self,
        subnet_id: str,
        description: Optional[str] = None,
        private_ip_address: Optional[str] = None,
        groups: Optional[List[str]] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> NetworkInterface:
        """Create a network interface.

        Args:
            subnet_id: ID of the subnet
            description: Optional description
            private_ip_address: Optional private IP address
            groups: Optional list of security group IDs
            tags: Optional list of tags

        Returns:
            Created network interface

        Raises:
            NetworkInterfaceError: If interface creation fails
        """
        try:
            params = {
                "SubnetId": subnet_id
            }
            if description:
                params["Description"] = description
            if private_ip_address:
                params["PrivateIpAddress"] = private_ip_address
            if groups:
                params["Groups"] = groups
            if tags:
                params["TagSpecifications"] = [{
                    "ResourceType": "network-interface",
                    "Tags": [{"Key": k, "Value": v} for k, v in tags]
                }]

            response = self.ec2.create_network_interface(**params)
            return NetworkInterface.from_response(response["NetworkInterface"])
        except Exception as e:
            logger.error(f"Failed to create network interface: {str(e)}")
            raise NetworkInterfaceError(f"Interface creation failed: {str(e)}") from e

    def delete_network_interface(
        self,
        network_interface_id: str
    ) -> None:
        """Delete a network interface.

        Args:
            network_interface_id: ID of the interface to delete

        Raises:
            NetworkInterfaceError: If interface deletion fails
        """
        try:
            self.ec2.delete_network_interface(NetworkInterfaceId=network_interface_id)
        except Exception as e:
            logger.error(f"Failed to delete network interface: {str(e)}")
            raise NetworkInterfaceError(f"Interface deletion failed: {str(e)}") from e

    def attach_network_interface(
        self,
        network_interface_id: str,
        instance_id: str,
        device_index: int,
    ) -> str:
        """Attach a network interface to an instance.

        Args:
            network_interface_id: ID of the interface
            instance_id: ID of the instance
            device_index: Device index for attachment

        Returns:
            Attachment ID

        Raises:
            NetworkInterfaceError: If interface attachment fails
        """
        try:
            response = self.ec2.attach_network_interface(
                NetworkInterfaceId=network_interface_id,
                InstanceId=instance_id,
                DeviceIndex=device_index
            )
            return response["AttachmentId"]
        except Exception as e:
            logger.error(f"Failed to attach network interface: {str(e)}")
            raise NetworkInterfaceError(f"Interface attachment failed: {str(e)}") from e

    def detach_network_interface(
        self,
        attachment_id: str,
        force: bool = False
    ) -> None:
        """Detach a network interface from an instance.

        Args:
            attachment_id: ID of the attachment
            force: Whether to force detachment

        Raises:
            NetworkInterfaceError: If interface detachment fails
        """
        try:
            self.ec2.detach_network_interface(
                AttachmentId=attachment_id,
                Force=force
            )
        except Exception as e:
            logger.error(f"Failed to detach network interface: {str(e)}")
            raise NetworkInterfaceError(f"Interface detachment failed: {str(e)}") from e

    def batch_create_instances(
        self,
        configs: List[CreateInstanceConfig]
    ) -> List[Instance]:
        """Create multiple instances in parallel.

        Args:
            configs: List of instance configurations

        Returns:
            List of created instances

        Raises:
            InstanceError: If instance creation fails
        """
        try:
            instances = []
            for config in configs:
                created = self.create_instances(**config.to_dict())
                instances.extend(created)
            return instances
        except Exception as e:
            logger.error(f"Failed to batch create instances: {str(e)}")
            raise InstanceError(f"Batch instance creation failed: {str(e)}") from e

    def batch_create_volumes(
        self,
        configs: List[CreateVolumeConfig]
    ) -> List[Volume]:
        """Create multiple volumes in parallel.

        Args:
            configs: List of volume configurations

        Returns:
            List of created volumes

        Raises:
            VolumeError: If volume creation fails
        """
        try:
            volumes = []
            for config in configs:
                volume = self.create_volume(**config.to_dict())
                volumes.append(volume)
            return volumes
        except Exception as e:
            logger.error(f"Failed to batch create volumes: {str(e)}")
            raise VolumeError(f"Batch volume creation failed: {str(e)}") from e

    def schedule_instance_operations(
        self,
        instance_id: str,
        schedule: OperationScheduleType
    ) -> None:
        """Schedule start/stop operations for an instance.

        Args:
            instance_id: ID of the instance
            schedule: Schedule configuration

        Raises:
            InstanceError: If schedule creation fails
        """
        try:
            self.ec2.put_scheduled_events(
                InstanceId=instance_id,
                StartSchedule=schedule["StartSchedule"],
                StopSchedule=schedule["StopSchedule"],
                TimeZone=schedule.get("TimeZone", "UTC")
            )
            logger.info(f"Successfully scheduled operations for instance {instance_id}")
        except Exception as e:
            logger.error(f"Failed to schedule instance operations: {str(e)}")
            raise InstanceError(f"Schedule creation failed: {str(e)}") from e

    def get_scheduled_operations(
        self,
        instance_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get scheduled operations for instances.

        Args:
            instance_id: Optional instance ID to filter by

        Returns:
            List of scheduled operations

        Raises:
            InstanceError: If schedule retrieval fails
        """
        try:
            params = {}
            if instance_id:
                params["InstanceId"] = instance_id

            response = self.ec2.describe_scheduled_events(**params)
            return response["ScheduledEvents"]
        except Exception as e:
            logger.error(f"Failed to get scheduled operations: {str(e)}")
            raise InstanceError(f"Schedule retrieval failed: {str(e)}") from e

    def create_instance_from_snapshot(
        self,
        snapshot_id: str,
        instance_type: str,
        subnet_id: Optional[str] = None,
        security_group_ids: Optional[List[str]] = None,
        tags: Optional[List[Dict[str, str]]] = None
    ) -> Instance:
        """Create a new instance from a snapshot.

        Args:
            snapshot_id: ID of the snapshot to use
            instance_type: Type of instance to launch
            subnet_id: Optional subnet ID
            security_group_ids: Optional security group IDs
            tags: Optional tags to apply

        Returns:
            Created instance

        Raises:
            InstanceError: If instance creation fails
        """
        try:
            # Get snapshot details
            snapshots = self.describe_snapshots(snapshot_ids=[snapshot_id])
            if not snapshots:
                raise ValueError(f"Snapshot {snapshot_id} not found")
            
            snapshot = snapshots[0]
            
            # Create volume from snapshot
            volume_config = CreateVolumeConfig(
                availability_zone=snapshot.availability_zone,
                snapshot_id=snapshot_id,
                volume_type="gp3"
            )
            volume = self.create_volume(**volume_config.to_dict())
            
            # Wait for volume to be available
            volume = self.wait_for_volume_state(volume.volume_id, "available")
            
            # Create instance
            instance_config = CreateInstanceConfig(
                instance_type=instance_type,
                subnet_id=subnet_id,
                security_group_ids=security_group_ids,
                tags=tags,
                block_device_mappings=[{
                    "DeviceName": "/dev/xvda",
                    "Ebs": {
                        "VolumeId": volume.volume_id,
                        "DeleteOnTermination": True
                    }
                }]
            )
            
            instances = self.create_instances(**instance_config.to_dict())
            return instances[0]
        except Exception as e:
            logger.error(f"Failed to create instance from snapshot: {str(e)}")
            raise InstanceError(f"Instance creation from snapshot failed: {str(e)}") from e

    def get_instance_status_summary(
        self,
        instance_id: str
    ) -> Dict[str, Any]:
        """Get a comprehensive status summary for an instance.

        Args:
            instance_id: ID of the instance

        Returns:
            Dictionary containing status summary

        Raises:
            InstanceError: If status retrieval fails
        """
        try:
            instance = self.describe_instances(instance_ids=[instance_id])[0]
            health = self.get_instance_health_status(instance_id)
            
            # Get recent metrics
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            cpu_metrics = self.get_instance_metrics(
                instance_id=instance_id,
                metric_name="CPUUtilization",
                start_time=start_time,
                end_time=end_time,
                period=300
            )
            
            memory_metrics = self.get_instance_metrics(
                instance_id=instance_id,
                metric_name="MemoryUtilization",
                start_time=start_time,
                end_time=end_time,
                period=300
            )
            
            return {
                "InstanceId": instance_id,
                "State": instance.state,
                "HealthStatus": health,
                "CPUUtilization": cpu_metrics[-1] if cpu_metrics else None,
                "MemoryUtilization": memory_metrics[-1] if memory_metrics else None,
                "LaunchTime": instance.launch_time,
                "PublicIpAddress": instance.public_ip_address,
                "PrivateIpAddress": instance.private_ip_address,
                "SecurityGroups": instance.security_groups,
                "Tags": instance.tags
            }
        except Exception as e:
            logger.error(f"Failed to get instance status summary: {str(e)}")
            raise InstanceError(f"Status summary retrieval failed: {str(e)}") from e

    def _validate_resource_age(self, resource: Any, cutoff_date: datetime) -> bool:
        """리소스 나이 검증

        Args:
            resource: 검증할 리소스
            cutoff_date: 기준 날짜

        Returns:
            bool: 리소스가 cutoff_date보다 오래되었으면 True
        """
        if hasattr(resource, 'create_time'):
            return resource.create_time < cutoff_date
        elif hasattr(resource, 'start_time'):
            return resource.start_time < cutoff_date
        return True

    def _delete_resource(self, resource_type: str, resource_id: str, 
                        delete_func: Callable, progress: CleanupProgress) -> bool:
        """단일 리소스 삭제

        Args:
            resource_type: 리소스 타입
            resource_id: 리소스 ID
            delete_func: 삭제 함수
            progress: 진행 상황 추적 객체

        Returns:
            bool: 삭제 성공 시 True
        """
        try:
            delete_func(resource_id)
            progress.deleted[resource_type].append(resource_id)
            return True
        except Exception as e:
            logger.warning(f"Failed to delete {resource_type} {resource_id}: {str(e)}")
            progress.errors[resource_type].append(resource_id)
            return False

    def _delete_resources_parallel(self, resource_type: str, resource_ids: List[str],
                                 delete_func: Callable, progress: CleanupProgress,
                                 max_workers: int = 5) -> None:
        """병렬 리소스 삭제 처리

        Args:
            resource_type: 리소스 타입
            resource_ids: 삭제할 리소스 ID 리스트
            delete_func: 삭제 함수
            progress: 진행 상황 추적 객체
            max_workers: 최대 동시 작업자 수
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self._delete_resource, 
                    resource_type, 
                    rid, 
                    delete_func,
                    progress
                ): rid for rid in resource_ids
            }
            for future in futures:
                future.result()
                progress.processed += 1
                if progress.processed % 10 == 0:
                    progress.log_status()

    def cleanup_unused_resources(
        self,
        older_than_days: int = 30,
        dry_run: bool = True,
    ) -> Dict[str, List[str]]:
        """Clean up unused EC2 resources.

        Args:
            older_than_days: Delete resources older than this many days
            dry_run: If True, only list resources that would be deleted

        Returns:
            Dictionary of deleted resource IDs by type

        Raises:
            EC2Error: If cleanup fails
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            unused = self.list_unused_resources()
            
            # Initialize progress tracking
            total_resources = sum(len(resources) for resources in unused.values())
            progress = CleanupProgress(total=total_resources)
            
            if not dry_run:
                # Define resource deletion order and their corresponding delete functions
                resource_order = [
                    ("network_interfaces", self.delete_network_interface),
                    ("volumes", self.delete_volume),
                    ("snapshots", self.delete_snapshot),
                    ("security_groups", self.delete_security_group)
                ]

                # Process each resource type in order
                for resource_type, delete_func in resource_order:
                    if unused[resource_type]:
                        logger.info(f"Processing {resource_type}...")
                        # Filter resources by age
                        to_delete = []
                        for resource_id in unused[resource_type]:
                            try:
                                resource = getattr(self, f"describe_{resource_type}")(
                                    **{f"{resource_type[:-1]}_ids": [resource_id]}
                                )[0]
                                if self._validate_resource_age(resource, cutoff_date):
                                    to_delete.append(resource_id)
                            except Exception as e:
                                logger.warning(f"Failed to describe {resource_type} {resource_id}: {str(e)}")
                                progress.errors[resource_type].append(resource_id)
                                progress.processed += 1

                        # Delete filtered resources in parallel
                        if to_delete:
                            self._delete_resources_parallel(
                                resource_type,
                                to_delete,
                                delete_func,
                                progress,
                                max_workers=None
                            )

                # Log final status
                logger.info("Cleanup completed.")
                progress.log_status()

            return progress.deleted if not dry_run else unused
        except Exception as e:
            logger.error(f"Failed to cleanup unused resources: {str(e)}")
            raise EC2Error(f"Resource cleanup failed: {str(e)}") from e

    def create_instance_schedule(
        self,
        instance_id: str,
        schedule_config: AutomationScheduleType
    ) -> str:
        """Create an automated schedule for instance operations.

        Args:
            instance_id: ID of the instance
            schedule_config: Schedule configuration including start/stop times,
                           timezone, and optional notification settings

        Returns:
            str: ID of the created schedule

        Raises:
            InstanceError: If schedule creation fails
        """
        try:
            response = self.ec2.create_instance_schedule(
                InstanceId=instance_id,
                **schedule_config
            )
            logger.info(f"Created schedule for instance {instance_id}")
            return response["ScheduleId"]
        except Exception as e:
            logger.error(f"Failed to create instance schedule: {str(e)}")
            raise InstanceError(f"Schedule creation failed: {str(e)}") from e

    def create_auto_scaling_policy(
        self,
        instance_id: str,
        policy_config: Dict[str, Any]
    ) -> str:
        """Create an auto-scaling policy for an instance.

        Args:
            instance_id: ID of the instance
            policy_config: Configuration for auto-scaling including metrics,
                          thresholds, and instance types for scaling

        Returns:
            str: ID of the created policy

        Raises:
            InstanceError: If policy creation fails
        """
        try:
            response = self.ec2.create_auto_scaling_policy(
                InstanceId=instance_id,
                **policy_config
            )
            logger.info(f"Created auto-scaling policy for instance {instance_id}")
            return response["PolicyId"]
        except Exception as e:
            logger.error(f"Failed to create auto-scaling policy: {str(e)}")
            raise InstanceError(f"Policy creation failed: {str(e)}") from e

    def create_automated_backup_policy(
        self,
        instance_id: str,
        backup_config: BackupPolicyType
    ) -> str:
        """Create an automated backup policy for an instance.

        Args:
            instance_id: ID of the instance
            backup_config: Backup configuration including frequency,
                          retention period, and cross-region settings

        Returns:
            str: ID of the created backup policy

        Raises:
            InstanceError: If backup policy creation fails
        """
        try:
            response = self.ec2.create_backup_policy(
                InstanceId=instance_id,
                **backup_config
            )
            logger.info(f"Created backup policy for instance {instance_id}")
            return response["PolicyId"]
        except Exception as e:
            logger.error(f"Failed to create backup policy: {str(e)}")
            raise InstanceError(f"Backup policy creation failed: {str(e)}") from e

    def restore_instance_point_in_time(
        self,
        instance_id: str,
        timestamp: datetime,
        restore_config: Optional[Dict[str, Any]] = None
    ) -> Instance:
        """Restore an instance to a specific point in time.

        Args:
            instance_id: ID of the instance
            timestamp: Point in time to restore to
            restore_config: Optional configuration for the restored instance

        Returns:
            Instance: Restored instance

        Raises:
            InstanceError: If restoration fails
        """
        try:
            params = {
                "InstanceId": instance_id,
                "Timestamp": timestamp
            }
            if restore_config:
                params.update(restore_config)
            
            response = self.ec2.restore_instance(
                **params
            )
            logger.info(f"Restored instance {instance_id} to {timestamp}")
            return Instance.from_response(response["Instance"])
        except Exception as e:
            logger.error(f"Failed to restore instance: {str(e)}")
            raise InstanceError(f"Instance restoration failed: {str(e)}") from e

    def create_disaster_recovery_config(
        self,
        instance_id: str,
        dr_config: Dict[str, Any]
    ) -> str:
        """Create a disaster recovery configuration for an instance.

        Args:
            instance_id: ID of the instance
            dr_config: Disaster recovery configuration including target region
                      and recovery objectives

        Returns:
            str: ID of the created configuration

        Raises:
            InstanceError: If configuration creation fails
        """
        try:
            response = self.ec2.create_dr_config(
                InstanceId=instance_id,
                **dr_config
            )
            logger.info(f"Created DR configuration for instance {instance_id}")
            return response["ConfigId"]
        except Exception as e:
            logger.error(f"Failed to create DR configuration: {str(e)}")
            raise InstanceError(f"DR configuration failed: {str(e)}") from e

    def audit_security_groups(
        self,
        audit_config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform a security audit of security groups.

        Args:
            audit_config: Optional configuration for the audit

        Returns:
            List[Dict[str, Any]]: Audit findings

        Raises:
            SecurityGroupError: If audit fails
        """
        try:
            params = {}
            if audit_config:
                params.update(audit_config)
            
            response = self.ec2.audit_security_groups(**params)
            logger.info("Completed security group audit")
            return response["Findings"]
        except Exception as e:
            logger.error(f"Failed to audit security groups: {str(e)}")
            raise SecurityGroupError(f"Security audit failed: {str(e)}") from e

    def create_security_policy(
        self,
        policy_config: SecurityPolicyType
    ) -> str:
        """Create a security policy.

        Args:
            policy_config: Security policy configuration including rules
                          and compliance requirements

        Returns:
            str: ID of the created policy

        Raises:
            SecurityGroupError: If policy creation fails
        """
        try:
            response = self.ec2.create_security_policy(**policy_config)
            logger.info(f"Created security policy: {policy_config['name']}")
            return response["PolicyId"]
        except Exception as e:
            logger.error(f"Failed to create security policy: {str(e)}")
            raise SecurityGroupError(f"Security policy creation failed: {str(e)}") from e

    def setup_security_monitoring(
        self,
        instance_id: str,
        monitoring_config: Dict[str, Any]
    ) -> str:
        """Set up security monitoring for an instance.

        Args:
            instance_id: ID of the instance
            monitoring_config: Monitoring configuration including log types
                             and alert settings

        Returns:
            str: ID of the created monitoring configuration

        Raises:
            InstanceError: If monitoring setup fails
        """
        try:
            response = self.ec2.setup_security_monitoring(
                InstanceId=instance_id,
                **monitoring_config
            )
            logger.info(f"Set up security monitoring for instance {instance_id}")
            return response["ConfigId"]
        except Exception as e:
            logger.error(f"Failed to setup security monitoring: {str(e)}")
            raise InstanceError(f"Security monitoring setup failed: {str(e)}") from e 