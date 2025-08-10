"""Internal EC2 operations."""

import logging
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from boto3.session import Session

from chainsaws.aws.ec2.ec2_models import (
    EC2APIConfig,
    Instance,
    Volume,
    SecurityGroup,
    NetworkInterface,
    Image,
    Snapshot,
    Tag,
    CreateVolumeConfig,
    CreateInstanceConfig,
)
from chainsaws.aws.ec2.ec2_types import (
    InstanceType,
    InstanceState,
    SecurityGroupRuleType,
    MetricAlarmConfig,
    ArchitectureType,
    HealthStatusType,
    CostEstimateType,
)
from chainsaws.utils.list_utils.list_utils import listify

logger = logging.getLogger(__name__)


class EC2:
    """Internal EC2 operations."""

    def __init__(self, boto3_session: Session, config: EC2APIConfig | None = None) -> None:
        """Initialize EC2 client.

        Args:
            boto3_session: Boto3 session
            config: Optional EC2 configuration
        """
        self.config = config or EC2APIConfig()
        self.client = boto3_session.client("ec2")

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
            Exception: If instance description fails
        """
        try:
            params = {}
            if instance_ids:
                params["InstanceIds"] = instance_ids
            if filters:
                params["Filters"] = filters

            response = self.client.describe_instances(**params)
            instances = []
            for reservation in response["Reservations"]:
                instances.extend(
                    [Instance.from_response(instance) for instance in reservation["Instances"]]
                )
            return instances
        except Exception:
            logger.exception("Failed to describe instances")
            raise

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
            Exception: If volume description fails
        """
        try:
            params = {}
            if volume_ids:
                params["VolumeIds"] = volume_ids
            if filters:
                params["Filters"] = filters

            response = self.client.describe_volumes(**params)
            return [Volume.from_response(volume) for volume in response["Volumes"]]
        except Exception:
            logger.exception("Failed to describe volumes")
            raise

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
            Exception: If security group description fails
        """
        try:
            params = {}
            if group_ids:
                params["GroupIds"] = group_ids
            if group_names:
                params["GroupNames"] = group_names
            if filters:
                params["Filters"] = filters

            response = self.client.describe_security_groups(**params)
            return [SecurityGroup.from_response(group) for group in response["SecurityGroups"]]
        except Exception:
            logger.exception("Failed to describe security groups")
            raise

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
            Exception: If network interface description fails
        """
        try:
            params = {}
            if network_interface_ids:
                params["NetworkInterfaceIds"] = network_interface_ids
            if filters:
                params["Filters"] = filters

            response = self.client.describe_network_interfaces(**params)
            return [NetworkInterface.from_response(interface) for interface in response["NetworkInterfaces"]]
        except Exception:
            logger.exception("Failed to describe network interfaces")
            raise

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
            Exception: If image description fails
        """
        try:
            params = {}
            if image_ids:
                params["ImageIds"] = image_ids
            if owners:
                params["Owners"] = owners
            if filters:
                params["Filters"] = filters

            response = self.client.describe_images(**params)
            return [Image.from_response(image) for image in response["Images"]]
        except Exception:
            logger.exception("Failed to describe images")
            raise

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
            Exception: If snapshot description fails
        """
        try:
            params = {}
            if snapshot_ids:
                params["SnapshotIds"] = snapshot_ids
            if owner_ids:
                params["OwnerIds"] = owner_ids
            if filters:
                params["Filters"] = filters

            response = self.client.describe_snapshots(**params)
            return [Snapshot.from_response(snapshot) for snapshot in response["Snapshots"]]
        except Exception:
            logger.exception("Failed to describe snapshots")
            raise

    def start_instances(self, instance_ids: List[str]) -> List[Instance]:
        """Start EC2 instances.

        Args:
            instance_ids: List of instance IDs to start

        Returns:
            List of started instances

        Raises:
            Exception: If instance start fails
        """
        try:
            response = self.client.start_instances(InstanceIds=instance_ids)
            started_instances = []
            for instance in response['StartingInstances']:
                started_instances.append(Instance.from_response(instance))
            return started_instances
        except Exception:
            logger.exception("Failed to start instances")
            raise

    def stop_instances(self, instance_ids: List[str]) -> List[Instance]:
        """Stop EC2 instances.

        Args:
            instance_ids: List of instance IDs to stop

        Returns:
            List of stopped instances

        Raises:
            Exception: If instance stop fails
        """
        try:
            response = self.client.stop_instances(InstanceIds=instance_ids)
            stopped_instances = []
            for instance in response['StoppingInstances']:
                stopped_instances.append(Instance.from_response(instance))
            return stopped_instances
        except Exception:
            logger.exception("Failed to stop instances")
            raise

    def terminate_instances(self, instance_ids: List[str]) -> List[Instance]:
        """Terminate EC2 instances.

        Args:
            instance_ids: List of instance IDs to terminate

        Returns:
            List of terminated instances

        Raises:
            Exception: If instance termination fails
        """
        try:
            response = self.client.terminate_instances(InstanceIds=instance_ids)
            terminated_instances = []
            for instance in response['TerminatingInstances']:
                terminated_instances.append(Instance.from_response(instance))
            return terminated_instances
        except Exception:
            logger.exception("Failed to terminate instances")
            raise

    def reboot_instances(self, instance_ids: List[str]) -> None:
        """Reboot EC2 instances.

        Args:
            instance_ids: List of instance IDs to reboot

        Raises:
            Exception: If instance reboot fails
        """
        try:
            self.client.reboot_instances(InstanceIds=instance_ids)
        except Exception:
            logger.exception("Failed to reboot instances")
            raise

    def create_instances(self, config: CreateInstanceConfig) -> List[Instance]:
        """Create new EC2 instances.

        Args:
            config: Instance creation configuration

        Returns:
            List of created instances

        Raises:
            Exception: If instance creation fails
        """
        try:
            response = self.client.run_instances(**config.to_dict())
            created_instances = []
            for instance in response['Instances']:
                created_instances.append(Instance.from_response(instance))
            return created_instances
        except Exception:
            logger.exception("Failed to create instances")
            raise

    def create_volume(self, config: CreateVolumeConfig) -> Volume:
        """Create a new EC2 volume.

        Args:
            config: Volume creation configuration

        Returns:
            Created volume

        Raises:
            Exception: If volume creation fails
        """
        try:
            response = self.client.create_volume(**config.to_dict())
            return Volume.from_response(response)
        except Exception:
            logger.exception("Failed to create volume")
            raise

    def delete_volume(self, volume_id: str) -> None:
        """Delete an EC2 volume.

        Args:
            volume_id: ID of the volume to delete

        Raises:
            Exception: If volume deletion fails
        """
        try:
            self.client.delete_volume(VolumeId=volume_id)
        except Exception:
            logger.exception("Failed to delete volume")
            raise

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
            Exception: If volume attachment fails
        """
        try:
            self.client.attach_volume(
                VolumeId=volume_id,
                InstanceId=instance_id,
                Device=device,
            )
        except Exception:
            logger.exception("Failed to attach volume")
            raise

    def detach_volume(self, volume_id: str) -> None:
        """Detach a volume from an instance.

        Args:
            volume_id: ID of the volume to detach

        Raises:
            Exception: If volume detachment fails
        """
        try:
            self.client.detach_volume(VolumeId=volume_id)
        except Exception:
            logger.exception("Failed to detach volume")
            raise

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
            Exception: If volume modification fails
        """
        try:
            params = {'VolumeId': volume_id}
            if size is not None:
                params['Size'] = size
            if volume_type is not None:
                params['VolumeType'] = volume_type
            if iops is not None:
                params['Iops'] = iops

            response = self.client.modify_volume(**params)
            return Volume.from_response(response['VolumeModification'])
        except Exception:
            logger.exception("Failed to modify volume")
            raise

    def create_security_group(
        self,
        group_name: str,
        description: str,
        vpc_id: Optional[str] = None,
        tags: Optional[List[Tag]] = None,
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
            Exception: If security group creation fails
        """
        try:
            params = {
                'GroupName': group_name,
                'Description': description,
            }
            if vpc_id:
                params['VpcId'] = vpc_id
            if tags:
                params['TagSpecifications'] = [{
                    'ResourceType': 'security-group',
                    'Tags': [tag.to_dict() for tag in tags],
                }]

            response = self.client.create_security_group(**params)
            return SecurityGroup.from_response(response)
        except Exception:
            logger.exception("Failed to create security group")
            raise

    def delete_security_group(self, group_id: str) -> None:
        """Delete a security group.

        Args:
            group_id: ID of the security group to delete

        Raises:
            Exception: If security group deletion fails
        """
        try:
            self.client.delete_security_group(GroupId=group_id)
        except Exception:
            logger.exception("Failed to delete security group")
            raise

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
            Exception: If rule addition fails
        """
        try:
            self.client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=ip_permissions,
            )
        except Exception:
            logger.exception("Failed to authorize security group ingress")
            raise

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
            Exception: If rule removal fails
        """
        try:
            self.client.revoke_security_group_ingress(
                GroupId=group_id,
                IpPermissions=ip_permissions,
            )
        except Exception:
            logger.exception("Failed to revoke security group ingress")
            raise

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
            Exception: If rule addition fails
        """
        try:
            self.client.authorize_security_group_egress(
                GroupId=group_id,
                IpPermissions=ip_permissions,
            )
        except Exception:
            logger.exception("Failed to authorize security group egress")
            raise

    def create_snapshot(
        self,
        volume_id: str,
        description: Optional[str] = None,
        tags: Optional[List[Tag]] = None,
    ) -> Snapshot:
        """Create a new snapshot.

        Args:
            volume_id: ID of the volume to snapshot
            description: Optional description of the snapshot
            tags: Optional list of tags to apply

        Returns:
            Created snapshot

        Raises:
            Exception: If snapshot creation fails
        """
        try:
            params = {'VolumeId': volume_id}
            if description:
                params['Description'] = description
            if tags:
                params['TagSpecifications'] = [{
                    'ResourceType': 'snapshot',
                    'Tags': [tag.to_dict() for tag in tags],
                }]

            response = self.client.create_snapshot(**params)
            return Snapshot.from_response(response)
        except Exception:
            logger.exception("Failed to create snapshot")
            raise

    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete a snapshot.

        Args:
            snapshot_id: ID of the snapshot to delete

        Raises:
            Exception: If snapshot deletion fails
        """
        try:
            self.client.delete_snapshot(SnapshotId=snapshot_id)
        except Exception:
            logger.exception("Failed to delete snapshot")
            raise

    def copy_snapshot(
        self,
        source_snapshot_id: str,
        source_region: str,
        description: Optional[str] = None,
        tags: Optional[List[Tag]] = None,
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
            Exception: If snapshot copy fails
        """
        try:
            params = {
                'SourceSnapshotId': source_snapshot_id,
                'SourceRegion': source_region,
            }
            if description:
                params['Description'] = description
            if tags:
                params['TagSpecifications'] = [{
                    'ResourceType': 'snapshot',
                    'Tags': [tag.to_dict() for tag in tags],
                }]

            response = self.client.copy_snapshot(**params)
            return Snapshot.from_response(response)
        except Exception:
            logger.exception("Failed to copy snapshot")
            raise

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
            Exception: If metric retrieval fails
        """
        try:
            response = self.client.get_metric_data(
                MetricDataQueries=[{
                    'Id': 'm1',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/EC2',
                            'MetricName': metric_name,
                            'Dimensions': [{
                                'Name': 'InstanceId',
                                'Value': instance_id,
                            }],
                        },
                        'Period': period,
                        'Stat': 'Average',
                    },
                    'StartTime': start_time,
                    'EndTime': end_time,
                }],
            )
            return response['MetricDataResults']
        except Exception:
            logger.exception("Failed to get instance metrics")
            raise

    def enable_instance_monitoring(self, instance_ids: List[str]) -> None:
        """Enable monitoring for instances.

        Args:
            instance_ids: List of instance IDs to enable monitoring for

        Raises:
            Exception: If monitoring enablement fails
        """
        try:
            self.client.monitor_instances(InstanceIds=listify(instance_ids))
        except Exception:
            logger.exception("Failed to enable instance monitoring")
            raise

    def disable_instance_monitoring(self, instance_ids: List[str]) -> None:
        """Disable monitoring for instances.

        Args:
            instance_ids: List of instance IDs to disable monitoring for

        Raises:
            Exception: If monitoring disablement fails
        """
        try:
            self.client.unmonitor_instances(InstanceIds=listify(instance_ids))
        except Exception:
            logger.exception("Failed to disable instance monitoring")
            raise

    def create_backup(
        self,
        instance_id: str,
        description: Optional[str] = None,
        tags: Optional[List[Tag]] = None,
    ) -> Dict[str, Any]:
        """Create a backup of an instance.

        Args:
            instance_id: ID of the instance to backup
            description: Optional description of the backup
            tags: Optional list of tags to apply

        Returns:
            Backup information

        Raises:
            Exception: If backup creation fails
        """
        try:
            params = {'InstanceId': instance_id}
            if description:
                params['Description'] = description
            if tags:
                params['TagSpecifications'] = [{
                    'ResourceType': 'backup',
                    'Tags': [tag.to_dict() for tag in tags],
                }]

            response = self.client.create_backup(**params)
            return response['Backup']
        except Exception:
            logger.exception("Failed to create backup")
            raise

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
            Exception: If instance restoration fails
        """
        try:
            params = {'BackupId': backup_id}
            if instance_type:
                params['InstanceType'] = instance_type
            if subnet_id:
                params['SubnetId'] = subnet_id

            response = self.client.restore_from_backup(**params)
            return Instance.from_response(response['Instance'])
        except Exception:
            logger.exception("Failed to restore from backup")
            raise

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
            Exception: If timeout occurs or state check fails
        """
        try:
            start_time = time.time()
            while True:
                instances = self.describe_instances(instance_ids=[instance_id])
                if not instances:
                    raise ValueError(f"Instance {instance_id} not found")
                
                instance = instances[0]
                if instance.state == target_state:
                    return instance

                if time.time() - start_time > timeout:
                    raise TimeoutError(
                        f"Timeout waiting for instance {instance_id} to reach state {target_state}"
                    )

                time.sleep(check_interval)
        except Exception:
            logger.exception(f"Failed to wait for instance {instance_id} state")
            raise

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
            Exception: If timeout occurs or state check fails
        """
        try:
            start_time = time.time()
            while True:
                volumes = self.describe_volumes(volume_ids=[volume_id])
                if not volumes:
                    raise ValueError(f"Volume {volume_id} not found")
                
                volume = volumes[0]
                if volume.state == target_state:
                    return volume

                if time.time() - start_time > timeout:
                    raise TimeoutError(
                        f"Timeout waiting for volume {volume_id} to reach state {target_state}"
                    )

                time.sleep(check_interval)
        except Exception:
            logger.exception(f"Failed to wait for volume {volume_id} state")
            raise

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
            Exception: If AMI lookup fails
        """
        try:
            filters = [
                {"Name": "name", "Values": ["amzn2-ami-hvm-*"]},
                {"Name": "architecture", "Values": [architecture]},
                {"Name": "virtualization-type", "Values": ["hvm"]},
                {"Name": "state", "Values": ["available"]},
                {"Name": "root-device-type", "Values": ["ebs"]},
            ]

            images = self.describe_images(
                owners=["amazon"],
                filters=filters
            )

            if not images:
                raise ValueError("No Amazon Linux 2 AMI found")

            # Sort by creation date and get the latest
            return sorted(
                images,
                key=lambda x: x.creation_date,
                reverse=True
            )[0]
        except Exception:
            logger.exception("Failed to get latest Amazon Linux AMI")
            raise

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
            Exception: If instance lookup fails
        """
        try:
            filters = [
                {"Name": "tag:Name", "Values": [name]},
                {"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]}
            ]

            instances = self.describe_instances(filters=filters)
            return instances[0] if instances else None
        except Exception:
            logger.exception(f"Failed to get instance by name {name}")
            raise

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
            Exception: If rule addition fails
        """
        try:
            ip_permission: SecurityGroupRuleType = {
                "IpProtocol": protocol,
                "FromPort": port,
                "ToPort": port,
                "IpRanges": [{"CidrIp": cidr}]
            }

            if description:
                ip_permission["IpRanges"][0]["Description"] = description

            if is_ingress:
                self.authorize_security_group_ingress(
                    group_id=group_id,
                    ip_permissions=[ip_permission]
                )
            else:
                self.authorize_security_group_egress(
                    group_id=group_id,
                    ip_permissions=[ip_permission]
                )
        except Exception:
            logger.exception("Failed to add security group rule")
            raise

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
            Exception: If rule removal fails
        """
        try:
            ip_permission: SecurityGroupRuleType = {
                "IpProtocol": protocol,
                "FromPort": port,
                "ToPort": port,
                "IpRanges": [{"CidrIp": cidr}]
            }

            if is_ingress:
                self.revoke_security_group_ingress(
                    group_id=group_id,
                    ip_permissions=[ip_permission]
                )
            else:
                self.revoke_security_group_egress(
                    group_id=group_id,
                    ip_permissions=[ip_permission]
                )
        except Exception:
            logger.exception("Failed to remove security group rule")
            raise

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
            Exception: If instance resize fails
        """
        try:
            instance = self.describe_instances(instance_ids=[instance_id])[0]
            
            if instance.state == "running" and not allow_reboot:
                raise ValueError("Instance is running and reboot is not allowed")

            if instance.state == "running":
                self.stop_instances([instance_id])
                self.wait_for_instance_state(instance_id, "stopped")

            self.client.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={"Value": new_instance_type}
            )

            if instance.state == "running":
                self.start_instances([instance_id])
                return self.wait_for_instance_state(instance_id, "running")

            return self.describe_instances(instance_ids=[instance_id])[0]
        except Exception:
            logger.exception("Failed to resize instance")
            raise

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
            Exception: If health status check fails
        """
        try:
            response = self.client.describe_instance_status(
                InstanceIds=[instance_id],
                IncludeAllInstances=True
            )

            if not response["InstanceStatuses"]:
                raise ValueError(f"No status information found for instance {instance_id}")

            status = response["InstanceStatuses"][0]
            return {
                "Status": status["InstanceState"]["Name"],
                "Details": status.get("Details", []),
                "SystemStatus": status["SystemStatus"],
                "InstanceStatus": status["InstanceStatus"]
            }
        except Exception:
            logger.exception("Failed to get instance health status")
            raise

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
            Exception: If alarm setup fails
        """
        try:
            for alarm in metric_alarms:
                self.client.put_metric_alarm(
                    AlarmName=f"{instance_id}-{alarm['MetricName']}",
                    MetricName=alarm["MetricName"],
                    Namespace="AWS/EC2",
                    Dimensions=[{
                        "Name": "InstanceId",
                        "Value": instance_id
                    }],
                    Threshold=alarm["Threshold"],
                    ComparisonOperator=alarm["ComparisonOperator"],
                    Period=alarm["Period"],
                    EvaluationPeriods=alarm["EvaluationPeriods"],
                    Statistic=alarm["Statistic"],
                    ActionsEnabled=alarm.get("ActionsEnabled", True),
                    AlarmActions=alarm.get("AlarmActions", [])
                )
        except Exception:
            logger.exception("Failed to setup instance alerts")
            raise

    def get_instance_cost_estimate(
        self,
        instance_type: InstanceType,
        hours: int = 730
    ) -> CostEstimateType:
        """Get cost estimate for an instance type.

        Args:
            instance_type: Instance type
            hours: Number of hours to estimate for

        Returns:
            Cost estimate information

        Raises:
            Exception: If cost estimation fails
        """
        try:
            pricing = self.boto3_session.client('pricing', region_name=self.config.region)
            
            response = pricing.get_products(
                ServiceCode='AmazonEC2',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                    {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': self.config.region},
                    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                    {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                    {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
                ]
            )

            if not response['PriceList']:
                raise ValueError(f"No pricing found for {instance_type} in {self.config.region}")

            price_data = response['PriceList'][0]
            hourly_cost = float(price_data['terms']['OnDemand'][0]['priceDimensions'][0]['pricePerUnit']['USD'])
            
            return {
                "InstanceType": instance_type,
                "Region": self.config.region,
                "HourlyCost": hourly_cost,
                "MonthlyCost": hourly_cost * hours,
                "Currency": "USD"
            }
        except Exception:
            logger.exception("Failed to get instance cost estimate")
            raise

    def list_unused_resources(self) -> Dict[str, List[str]]:
        """List unused EC2 resources.

        Returns:
            Dictionary of unused resource IDs by type

        Raises:
            Exception: If resource listing fails
        """
        try:
            unused = {
                "volumes": [],
                "snapshots": [],
                "security_groups": [],
                "network_interfaces": []
            }

            # Find unused volumes
            volumes = self.describe_volumes(
                filters=[{"Name": "status", "Values": ["available"]}]
            )
            unused["volumes"] = [v.volume_id for v in volumes]

            # Find unused snapshots (older than 30 days)
            snapshots = self.describe_snapshots(owner_ids=["self"])
            thirty_days_ago = datetime.now() - timedelta(days=30)
            unused["snapshots"] = [
                s.snapshot_id for s in snapshots
                if s.start_time < thirty_days_ago
            ]

            # Find unused security groups
            security_groups = self.describe_security_groups()
            used_sg_ids = set()
            instances = self.describe_instances()
            for instance in instances:
                for sg in instance.security_groups:
                    used_sg_ids.add(sg["GroupId"])
            
            unused["security_groups"] = [
                sg.group_id for sg in security_groups
                if sg.group_id not in used_sg_ids and sg.group_name != "default"
            ]

            # Find unused network interfaces
            network_interfaces = self.describe_network_interfaces(
                filters=[{"Name": "status", "Values": ["available"]}]
            )
            unused["network_interfaces"] = [
                ni.network_interface_id for ni in network_interfaces
            ]

            return unused
        except Exception:
            logger.exception("Failed to list unused resources")
            raise 