"""Unified Redshift Control Plane API."""

import logging
import time
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from chainsaws.aws.redshift.control_plane.models import (
    # Cluster related
    BackupConfig,
    ClusterConfig,
    ClusterStatus,
    MaintenanceWindow,
    # Security related
    GrantConfig,
    Group,
    IamRole,
    InboundRule,
    SecurityGroup,
    SecurityGroupConfig,
    User,
    # Parameter related
    ApplyStatus,
    ParameterGroupConfig,
    ParameterGroupFamily,
    ParameterGroupStatus,
    ParameterModification,
    ParameterValue,
)

logger = logging.getLogger(__name__)


class RedshiftControlAPI:
    """High-level Redshift Control Plane API with cluster, security, and parameter management."""

    def __init__(
        self,
        region_name: Optional[str] = None,
    ) -> None:
        """Initialize with optional region name.

        Args:
            region_name: AWS region name. If None, uses default region from AWS configuration.
        """
        self.redshift = boto3.client("redshift", region_name=region_name)
        self.ec2 = boto3.client("ec2", region_name=region_name)
        self.iam = boto3.client("iam", region_name=region_name)

    # Cluster Management Methods
    def create_cluster(self, config: ClusterConfig) -> ClusterStatus:
        """Create a new Redshift cluster with specified configuration.

        Args:
            config: Configuration object containing all necessary parameters for cluster creation
                   including network settings, security groups, maintenance windows, etc.

        Returns:
            ClusterStatus object containing the created cluster's details and current status

        Raises:
            ClientError: If cluster creation fails due to invalid parameters or AWS API issues
        """
        try:
            params = {
                "ClusterIdentifier": config.cluster_identifier,
                "NodeType": config.node_type,
                "MasterUsername": config.master_username,
                "MasterUserPassword": config.master_user_password,
                "DBName": config.database_name,
                "NumberOfNodes": config.number_of_nodes,
                "Port": config.port,
                "VpcSecurityGroupIds": config.network.security_group_ids,
                "ClusterSubnetGroupName": config.network.subnet_ids[0],
                "PubliclyAccessible": config.network.publicly_accessible,
                "Encrypted": config.encrypted,
            }

            if config.maintenance_window:
                params["PreferredMaintenanceWindow"] = (
                    f"{config.maintenance_window.day_of_week}:"
                    f"{config.maintenance_window.start_time}:"
                    f"{config.maintenance_window.duration_hours}"
                )

            if config.backup:
                params.update({
                    "AutomatedSnapshotRetentionPeriod": (
                        config.backup.retention_period_days
                    ),
                    "PreferredSnapshotWindow": (
                        config.backup.automated_snapshot_start_time
                    ),
                })

            if config.kms_key_id:
                params["KmsKeyId"] = config.kms_key_id

            if config.tags:
                params["Tags"] = [
                    {"Key": k, "Value": v} for k, v in config.tags.items()
                ]

            response = self.redshift.create_cluster(**params)
            return self._convert_to_cluster_status(response["Cluster"])

        except ClientError as e:
            logger.error("Failed to create cluster: %s", e)
            raise

    def get_cluster(self, cluster_identifier: str) -> ClusterStatus:
        """Get details of a specific Redshift cluster.

        Args:
            cluster_identifier: Unique identifier of the cluster to retrieve

        Returns:
            ClusterStatus object containing the cluster's current configuration and status

        Raises:
            ClientError: If cluster retrieval fails or cluster doesn't exist
        """
        try:
            response = self.redshift.describe_clusters(
                ClusterIdentifier=cluster_identifier
            )
            return self._convert_to_cluster_status(response["Clusters"][0])

        except ClientError as e:
            logger.error("Failed to get cluster: %s", e)
            raise

    def list_clusters(
        self,
        name_pattern: Optional[str] = None,
        max_records: int = 100,
    ) -> List[ClusterStatus]:
        """List all Redshift clusters or those matching a pattern.

        Args:
            name_pattern: Optional pattern to filter cluster names
            max_records: Maximum number of records to return (default: 100)

        Returns:
            List of ClusterStatus objects containing details of matching clusters

        Raises:
            ClientError: If listing clusters fails
        """
        try:
            params = {"MaxRecords": max_records}
            if name_pattern:
                params["Marker"] = name_pattern

            response = self.redshift.describe_clusters(**params)
            return [
                self._convert_to_cluster_status(c)
                for c in response["Clusters"]
            ]

        except ClientError as e:
            logger.error("Failed to list clusters: %s", e)
            raise

    def update_cluster(
        self,
        cluster_identifier: str,
        node_type: Optional[str] = None,
        number_of_nodes: Optional[int] = None,
        master_user_password: Optional[str] = None,
        cluster_type: Optional[str] = None,
        cluster_security_groups: Optional[List[str]] = None,
        vpc_security_groups: Optional[List[str]] = None,
        maintenance_window: Optional[MaintenanceWindow] = None,
        backup_config: Optional[BackupConfig] = None,
        allow_version_upgrade: Optional[bool] = None,
        encrypted: Optional[bool] = None,
        kms_key_id: Optional[str] = None,
    ) -> ClusterStatus:
        """Update configuration of an existing Redshift cluster.

        Args:
            cluster_identifier: Unique identifier of the cluster to modify
            node_type: New node type for the cluster
            number_of_nodes: New number of nodes in the cluster
            master_user_password: New password for the master user
            cluster_type: New cluster type (single-node or multi-node)
            cluster_security_groups: List of cluster security group names
            vpc_security_groups: List of VPC security group IDs
            maintenance_window: New maintenance window configuration
            backup_config: New backup configuration
            allow_version_upgrade: Whether to allow version upgrades
            encrypted: Whether to enable encryption
            kms_key_id: KMS key ID for encryption

        Returns:
            ClusterStatus object containing the updated cluster configuration

        Raises:
            ClientError: If cluster modification fails
        """
        try:
            params = {"ClusterIdentifier": cluster_identifier}

            if node_type:
                params["NodeType"] = node_type
            if number_of_nodes:
                params["NumberOfNodes"] = number_of_nodes
            if master_user_password:
                params["MasterUserPassword"] = master_user_password
            if cluster_type:
                params["ClusterType"] = cluster_type
            if cluster_security_groups:
                params["ClusterSecurityGroups"] = cluster_security_groups
            if vpc_security_groups:
                params["VpcSecurityGroupIds"] = vpc_security_groups
            if maintenance_window:
                params["PreferredMaintenanceWindow"] = (
                    f"{maintenance_window.day_of_week}:"
                    f"{maintenance_window.start_time}:"
                    f"{maintenance_window.duration_hours}"
                )
            if backup_config:
                params.update({
                    "AutomatedSnapshotRetentionPeriod": (
                        backup_config.retention_period_days
                    ),
                    "PreferredSnapshotWindow": (
                        backup_config.automated_snapshot_start_time
                    ),
                })
            if allow_version_upgrade is not None:
                params["AllowVersionUpgrade"] = allow_version_upgrade
            if encrypted is not None:
                params["Encrypted"] = encrypted
            if kms_key_id:
                params["KmsKeyId"] = kms_key_id

            response = self.redshift.modify_cluster(**params)
            return self._convert_to_cluster_status(response["Cluster"])

        except ClientError as e:
            logger.error("Failed to modify cluster: %s", e)
            raise

    def delete_cluster(
        self,
        cluster_identifier: str,
        skip_final_snapshot: bool = False,
        final_snapshot_identifier: Optional[str] = None,
    ) -> None:
        """Delete a Redshift cluster.

        Args:
            cluster_identifier: Unique identifier of the cluster to delete
            skip_final_snapshot: If True, skips taking a final snapshot
            final_snapshot_identifier: Identifier for the final snapshot if taken

        Raises:
            ClientError: If cluster deletion fails
        """
        try:
            params = {
                "ClusterIdentifier": cluster_identifier,
                "SkipFinalSnapshot": skip_final_snapshot,
            }

            if not skip_final_snapshot:
                if not final_snapshot_identifier:
                    final_snapshot_identifier = (
                        f"{cluster_identifier}-final-{int(time.time())}"
                    )
                params["FinalClusterSnapshotIdentifier"] = final_snapshot_identifier

            self.redshift.delete_cluster(**params)

        except ClientError as e:
            logger.error("Failed to delete cluster: %s", e)
            raise

    def reboot_cluster(self, cluster_identifier: str) -> None:
        """Reboot a Redshift cluster.

        Args:
            cluster_identifier: Unique identifier of the cluster to reboot

        Raises:
            ClientError: If cluster reboot fails
        """
        try:
            self.redshift.reboot_cluster(ClusterIdentifier=cluster_identifier)
        except ClientError as e:
            logger.error("Failed to reboot cluster: %s", e)
            raise

    # Security Group Methods
    def create_security_group(self, config: SecurityGroupConfig) -> SecurityGroup:
        """Create a new security group for Redshift cluster.

        Args:
            config: Security group configuration including name, description,
                   VPC ID, tags, and inbound rules

        Returns:
            SecurityGroup object containing the created security group details

        Raises:
            ClientError: If security group creation fails
        """
        try:
            response = self.ec2.create_security_group(
                GroupName=config.group_name,
                Description=config.description,
                VpcId=config.vpc_id,
            )
            group_id = response["GroupId"]

            if config.tags:
                self.ec2.create_tags(
                    Resources=[group_id],
                    Tags=[{"Key": k, "Value": v}
                          for k, v in config.tags.items()],
                )

            if config.inbound_rules:
                for rule in config.inbound_rules:
                    ip_permissions = {
                        "IpProtocol": rule.protocol,
                        "FromPort": rule.from_port,
                        "ToPort": rule.to_port,
                    }

                    if rule.cidr_blocks:
                        ip_permissions["IpRanges"] = [
                            {"CidrIp": cidr, "Description": rule.description or ""}
                            for cidr in rule.cidr_blocks
                        ]

                    if rule.security_group_ids:
                        ip_permissions["UserIdGroupPairs"] = [
                            {"GroupId": sg_id}
                            for sg_id in rule.security_group_ids
                        ]

                    self.ec2.authorize_security_group_ingress(
                        GroupId=group_id,
                        IpPermissions=[ip_permissions],
                    )

            response = self.ec2.describe_security_groups(GroupIds=[group_id])
            sg_data = response["SecurityGroups"][0]

            return SecurityGroup(
                group_id=sg_data["GroupId"],
                group_name=sg_data["GroupName"],
                vpc_id=sg_data["VpcId"],
                description=sg_data["Description"],
                tags={t["Key"]: t["Value"] for t in sg_data.get("Tags", [])},
            )

        except ClientError as e:
            logger.error("Failed to create security group: %s", e)
            raise

    def get_security_group(self, group_id: str) -> SecurityGroup:
        """Get details of a specific security group.

        Args:
            group_id: ID of the security group to retrieve

        Returns:
            SecurityGroup object containing the security group details

        Raises:
            ClientError: If security group retrieval fails
        """
        try:
            response = self.ec2.describe_security_groups(GroupIds=[group_id])
            sg_data = response["SecurityGroups"][0]
            return SecurityGroup(
                group_id=sg_data["GroupId"],
                group_name=sg_data["GroupName"],
                vpc_id=sg_data["VpcId"],
                description=sg_data["Description"],
                tags={t["Key"]: t["Value"] for t in sg_data.get("Tags", [])},
            )
        except ClientError as e:
            logger.error("Failed to get security group: %s", e)
            raise

    def list_security_groups(
        self,
        vpc_id: Optional[str] = None,
        name_pattern: Optional[str] = None,
    ) -> List[SecurityGroup]:
        """List security groups with optional filtering.

        Args:
            vpc_id: Optional VPC ID to filter security groups
            name_pattern: Optional pattern to filter security group names

        Returns:
            List of SecurityGroup objects matching the filter criteria

        Raises:
            ClientError: If listing security groups fails
        """
        try:
            filters = []
            if vpc_id:
                filters.append({"Name": "vpc-id", "Values": [vpc_id]})
            if name_pattern:
                filters.append(
                    {"Name": "group-name", "Values": [name_pattern]})

            response = self.ec2.describe_security_groups(Filters=filters)
            return [
                SecurityGroup(
                    group_id=sg["GroupId"],
                    group_name=sg["GroupName"],
                    vpc_id=sg["VpcId"],
                    description=sg["Description"],
                    tags={t["Key"]: t["Value"] for t in sg.get("Tags", [])},
                )
                for sg in response["SecurityGroups"]
            ]
        except ClientError as e:
            logger.error("Failed to list security groups: %s", e)
            raise

    def update_security_group_rules(
        self,
        group_id: str,
        add_rules: Optional[List[InboundRule]] = None,
        remove_rules: Optional[List[InboundRule]] = None,
    ) -> None:
        """Update inbound rules of a security group.

        Args:
            group_id: ID of the security group to modify
            add_rules: List of inbound rules to add
            remove_rules: List of inbound rules to remove

        Raises:
            ClientError: If updating security group rules fails
        """
        try:
            if add_rules:
                for rule in add_rules:
                    ip_permissions = {
                        "IpProtocol": rule.protocol,
                        "FromPort": rule.from_port,
                        "ToPort": rule.to_port,
                    }

                    if rule.cidr_blocks:
                        ip_permissions["IpRanges"] = [
                            {"CidrIp": cidr, "Description": rule.description or ""}
                            for cidr in rule.cidr_blocks
                        ]

                    if rule.security_group_ids:
                        ip_permissions["UserIdGroupPairs"] = [
                            {"GroupId": sg_id}
                            for sg_id in rule.security_group_ids
                        ]

                    self.ec2.authorize_security_group_ingress(
                        GroupId=group_id,
                        IpPermissions=[ip_permissions],
                    )

            if remove_rules:
                for rule in remove_rules:
                    ip_permissions = {
                        "IpProtocol": rule.protocol,
                        "FromPort": rule.from_port,
                        "ToPort": rule.to_port,
                    }

                    if rule.cidr_blocks:
                        ip_permissions["IpRanges"] = [
                            {"CidrIp": cidr}
                            for cidr in rule.cidr_blocks
                        ]

                    if rule.security_group_ids:
                        ip_permissions["UserIdGroupPairs"] = [
                            {"GroupId": sg_id}
                            for sg_id in rule.security_group_ids
                        ]

                    self.ec2.revoke_security_group_ingress(
                        GroupId=group_id,
                        IpPermissions=[ip_permissions],
                    )

        except ClientError as e:
            logger.error("Failed to modify security group rules: %s", e)
            raise

    def delete_security_group(self, group_id: str) -> None:
        """Delete a security group.

        Args:
            group_id: ID of the security group to delete

        Raises:
            ClientError: If security group deletion fails
        """
        try:
            self.ec2.delete_security_group(GroupId=group_id)
        except ClientError as e:
            logger.error("Failed to delete security group: %s", e)
            raise

    # IAM Role Methods
    def create_iam_role(
        self,
        role_name: str,
        trust_policy: Dict,
        policy_arns: Optional[List[str]] = None,
    ) -> IamRole:
        """Create an IAM role for Redshift with specified permissions.

        Args:
            role_name: Name of the IAM role to create
            trust_policy: Trust policy document as a dictionary
            policy_arns: List of policy ARNs to attach to the role

        Returns:
            IamRole object containing the created role details

        Raises:
            ClientError: If role creation fails
        """
        try:
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=trust_policy,
            )
            role_arn = response["Role"]["Arn"]

            if policy_arns:
                for policy_arn in policy_arns:
                    self.iam.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn,
                    )

            return IamRole(
                role_arn=role_arn,
                feature_name=None,
            )

        except ClientError as e:
            logger.error("Failed to create IAM role: %s", e)
            raise

    def get_iam_role(self, role_name: str) -> IamRole:
        """Get details of a specific IAM role.

        Args:
            role_name: Name of the IAM role to retrieve

        Returns:
            IamRole object containing the role details

        Raises:
            ClientError: If role retrieval fails
        """
        try:
            response = self.iam.get_role(RoleName=role_name)
            return IamRole(
                role_arn=response["Role"]["Arn"],
                feature_name=None,
            )
        except ClientError as e:
            logger.error("Failed to get IAM role: %s", e)
            raise

    def list_iam_roles(
        self,
        path_prefix: Optional[str] = None,
    ) -> List[IamRole]:
        """List IAM roles with optional path prefix filter.

        Args:
            path_prefix: Optional path prefix to filter roles

        Returns:
            List of IamRole objects matching the filter criteria

        Raises:
            ClientError: If listing roles fails
        """
        try:
            params = {}
            if path_prefix:
                params["PathPrefix"] = path_prefix

            response = self.iam.list_roles(**params)
            return [
                IamRole(
                    role_arn=role["Arn"],
                    feature_name=None,
                )
                for role in response["Roles"]
            ]
        except ClientError as e:
            logger.error("Failed to list IAM roles: %s", e)
            raise

    def delete_iam_role(self, role_name: str) -> None:
        """Delete an IAM role and detach all attached policies.

        Args:
            role_name: Name of the IAM role to delete

        Raises:
            ClientError: If role deletion fails
        """
        try:
            response = self.iam.list_attached_role_policies(RoleName=role_name)
            for policy in response["AttachedPolicies"]:
                self.iam.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy["PolicyArn"],
                )

            self.iam.delete_role(RoleName=role_name)

        except ClientError as e:
            logger.error("Failed to delete IAM role: %s", e)
            raise

    # User Methods
    def create_user(self, user: User) -> None:
        """Create a new database user in Redshift.

        Args:
            user: User object containing username, password, and permissions

        Raises:
            ClientError: If user creation fails
        """
        try:
            params = {
                "DbUser": user.username,
                "CreateDb": user.create_database,
            }

            if user.password:
                params["DbPassword"] = user.password
            if user.connection_limit != -1:
                params["ConnectionLimit"] = user.connection_limit
            if user.valid_until:
                params["ValidUntil"] = user.valid_until

            self.redshift.create_cluster_user(**params)

        except ClientError as e:
            logger.error("Failed to create user: %s", e)
            raise

    def get_user(self, username: str) -> User:
        """Get details of a specific database user.

        Args:
            username: Name of the user to retrieve

        Returns:
            User object containing the user details

        Raises:
            ClientError: If user retrieval fails
        """
        try:
            response = self.redshift.describe_cluster_users(
                DbUser=username
            )
            user_data = response["Users"][0]
            return User(
                username=user_data["DbUser"],
                connection_limit=user_data.get("ConnectionLimit", -1),
                create_database=user_data.get("CreateDb", False),
                superuser=user_data.get("Superuser", False),
            )
        except ClientError as e:
            logger.error("Failed to get user: %s", e)
            raise

    def list_users(
        self,
        name_pattern: Optional[str] = None,
    ) -> List[User]:
        """List database users with optional name pattern filter.

        Args:
            name_pattern: Optional pattern to filter usernames

        Returns:
            List of User objects matching the filter criteria

        Raises:
            ClientError: If listing users fails
        """
        try:
            params = {}
            if name_pattern:
                params["DbUserNamePattern"] = name_pattern

            response = self.redshift.describe_cluster_users(**params)
            return [
                User(
                    username=u["DbUser"],
                    connection_limit=u.get("ConnectionLimit", -1),
                    create_database=u.get("CreateDb", False),
                    superuser=u.get("Superuser", False),
                )
                for u in response["Users"]
            ]
        except ClientError as e:
            logger.error("Failed to list users: %s", e)
            raise

    def update_user(
        self,
        username: str,
        new_password: Optional[str] = None,
        connection_limit: Optional[int] = None,
        valid_until: Optional[str] = None,
    ) -> None:
        """Update database user configuration.

        Args:
            username: Name of the user to modify
            new_password: Optional new password for the user
            connection_limit: Optional new connection limit
            valid_until: Optional expiration timestamp

        Raises:
            ClientError: If user modification fails
        """
        try:
            params = {"DbUser": username}

            if new_password:
                params["NewDbPassword"] = new_password
            if connection_limit is not None:
                params["ConnectionLimit"] = connection_limit
            if valid_until:
                params["ValidUntil"] = valid_until

            self.redshift.modify_cluster_user(**params)

        except ClientError as e:
            logger.error("Failed to modify user: %s", e)
            raise

    def delete_user(self, username: str) -> None:
        """Delete a database user.

        Args:
            username: Name of the user to delete

        Raises:
            ClientError: If user deletion fails
        """
        try:
            self.redshift.delete_cluster_user(DbUser=username)
        except ClientError as e:
            logger.error("Failed to delete user: %s", e)
            raise

    # Group Methods
    def create_group(self, group: Group) -> None:
        """Create a new database group.

        Args:
            group: Group object containing group name and initial users

        Raises:
            ClientError: If group creation fails
        """
        try:
            self.redshift.create_cluster_group(
                GroupName=group.group_name,
                Users=group.users,
            )
        except ClientError as e:
            logger.error("Failed to create group: %s", e)
            raise

    def get_group(self, group_name: str) -> Group:
        """Get details of a specific database group.

        Args:
            group_name: Name of the group to retrieve

        Returns:
            Group object containing the group details

        Raises:
            ClientError: If group retrieval fails
        """
        try:
            response = self.redshift.describe_cluster_groups(
                GroupName=group_name
            )
            group_data = response["Groups"][0]
            return Group(
                group_name=group_data["GroupName"],
                users=group_data.get("Users", []),
            )
        except ClientError as e:
            logger.error("Failed to get group: %s", e)
            raise

    def list_groups(
        self,
        name_pattern: Optional[str] = None,
    ) -> List[Group]:
        """List database groups with optional name pattern filter.

        Args:
            name_pattern: Optional pattern to filter group names

        Returns:
            List of Group objects matching the filter criteria

        Raises:
            ClientError: If listing groups fails
        """
        try:
            params = {}
            if name_pattern:
                params["GroupNamePattern"] = name_pattern

            response = self.redshift.describe_cluster_groups(**params)
            return [
                Group(
                    group_name=g["GroupName"],
                    users=g.get("Users", []),
                )
                for g in response["Groups"]
            ]
        except ClientError as e:
            logger.error("Failed to list groups: %s", e)
            raise

    def update_group(
        self,
        group_name: str,
        add_users: Optional[List[str]] = None,
        remove_users: Optional[List[str]] = None,
    ) -> None:
        """Update database group membership.

        Args:
            group_name: Name of the group to modify
            add_users: List of usernames to add to the group
            remove_users: List of usernames to remove from the group

        Raises:
            ClientError: If group modification fails
        """
        # ... existing modify_group implementation ...

    def delete_group(self, group_name: str) -> None:
        """Delete a database group.

        Args:
            group_name: Name of the group to delete

        Raises:
            ClientError: If group deletion fails
        """
        # ... existing implementation ...

    # Permission Methods
    def grant_permissions(self, grant_config: GrantConfig) -> None:
        """Grant permissions to a user or group.

        Args:
            grant_config: Configuration object containing grantee and permissions

        Raises:
            ClientError: If granting permissions fails
        """
        try:
            for permission in grant_config.permissions:
                params = {
                    "Grantee": grant_config.grantee,
                    "GranteeType": grant_config.grantee_type,
                    "Database": permission.database,
                    "Permissions": permission.permissions,
                }

                if permission.schema:
                    params["Schema"] = permission.schema
                if permission.table:
                    params["Table"] = permission.table

                self.redshift.grant_cluster_permissions(**params)

        except ClientError as e:
            logger.error("Failed to grant permissions: %s", e)
            raise

    def revoke_permissions(self, grant_config: GrantConfig) -> None:
        """Revoke permissions from a user or group.

        Args:
            grant_config: Configuration object containing grantee and permissions

        Raises:
            ClientError: If revoking permissions fails
        """
        try:
            for permission in grant_config.permissions:
                params = {
                    "Grantee": grant_config.grantee,
                    "GranteeType": grant_config.grantee_type,
                    "Database": permission.database,
                    "Permissions": permission.permissions,
                }

                if permission.schema:
                    params["Schema"] = permission.schema
                if permission.table:
                    params["Table"] = permission.table

                self.redshift.revoke_cluster_permissions(**params)

        except ClientError as e:
            logger.error("Failed to revoke permissions: %s", e)
            raise

    # Parameter Group Methods
    def create_parameter_group(
        self,
        config: ParameterGroupConfig,
    ) -> ParameterGroupStatus:
        """Create a new parameter group with specified configuration.

        Args:
            config: Configuration object containing parameter group settings

        Returns:
            ParameterGroupStatus object containing the created group's details

        Raises:
            ClientError: If parameter group creation fails
        """
        try:
            self.redshift.create_cluster_parameter_group(
                ParameterGroupName=config.name,
                ParameterGroupFamily=config.family,
                Description=config.description,
                Tags=[
                    {"Key": k, "Value": v}
                    for k, v in config.tags.items()
                ] if config.tags else [],
            )

            if config.parameters:
                self.redshift.modify_cluster_parameter_group(
                    ParameterGroupName=config.name,
                    Parameters=[
                        {"ParameterName": k, "ParameterValue": v}
                        for k, v in config.parameters.items()
                    ],
                )

            return self.get_parameter_group(config.name)

        except ClientError as e:
            logger.error("Failed to create parameter group: %s", e)
            raise

    def get_parameter_group(self, name: str) -> ParameterGroupStatus:
        """Get details of a specific parameter group.

        Args:
            name: Name of the parameter group to retrieve

        Returns:
            ParameterGroupStatus object containing the group details

        Raises:
            ClientError: If parameter group retrieval fails
        """
        try:
            response = self.redshift.describe_cluster_parameter_groups(
                ParameterGroupName=name
            )
            pg_data = response["ParameterGroups"][0]

            response = self.redshift.describe_cluster_parameters(
                ParameterGroupName=name
            )
            parameters = {
                p["ParameterName"]: ParameterValue(
                    name=p["ParameterName"],
                    value=p["ParameterValue"],
                    description=p["Description"],
                    source=p["Source"],
                    data_type=p["DataType"],
                    allowed_values=p.get("AllowedValues", ""),
                    apply_type=p["ApplyType"],
                    is_modifiable=p["IsModifiable"],
                    minimum_engine_version=p.get("MinimumEngineVersion", ""),
                )
                for p in response["Parameters"]
            }

            return ParameterGroupStatus(
                name=pg_data["ParameterGroupName"],
                family=pg_data["ParameterGroupFamily"],
                description=pg_data["Description"],
                parameters=parameters,
                tags={t["Key"]: t["Value"] for t in pg_data.get("Tags", [])},
            )

        except ClientError as e:
            logger.error("Failed to get parameter group: %s", e)
            raise

    def list_parameter_groups(
        self,
        name_pattern: Optional[str] = None,
        max_records: int = 100,
    ) -> List[ParameterGroupStatus]:
        """List parameter groups with optional filtering.

        Args:
            name_pattern: Optional pattern to filter group names
            max_records: Maximum number of records to return (default: 100)

        Returns:
            List of ParameterGroupStatus objects matching the filter criteria

        Raises:
            ClientError: If listing parameter groups fails
        """
        try:
            params = {"MaxRecords": max_records}
            if name_pattern:
                params["Marker"] = name_pattern

            response = self.redshift.describe_cluster_parameter_groups(
                **params)
            return [
                self.get_parameter_group(pg["ParameterGroupName"])
                for pg in response["ParameterGroups"]
            ]

        except ClientError as e:
            logger.error("Failed to list parameter groups: %s", e)
            raise

    def update_parameters(
        self,
        group_name: str,
        parameters: Dict[str, str],
    ) -> ApplyStatus:
        """Update parameter values in a parameter group.

        Args:
            group_name: Name of the parameter group to modify
            parameters: Dictionary mapping parameter names to new values

        Returns:
            ApplyStatus object containing the results of the parameter updates

        Raises:
            ClientError: If parameter modification fails
        """
        try:
            response = self.redshift.modify_cluster_parameter_group(
                ParameterGroupName=group_name,
                Parameters=[
                    {"ParameterName": k, "ParameterValue": v}
                    for k, v in parameters.items()
                ],
            )

            return ApplyStatus(
                parameters_to_apply=response.get("ParametersToApply", []),
                parameters_applied=response.get("ParametersApplied", []),
                parameters_with_errors=response.get("ParameterErrors", {}),
                requires_reboot=any(
                    p["ApplyType"] == "static"
                    for p in response.get("Parameters", [])
                ),
            )

        except ClientError as e:
            logger.error("Failed to modify parameters: %s", e)
            raise

    def delete_parameter_group(self, name: str) -> None:
        """Delete a parameter group.

        Args:
            name: Name of the parameter group to delete

        Raises:
            ClientError: If parameter group deletion fails
        """
        try:
            self.redshift.delete_cluster_parameter_group(
                ParameterGroupName=name
            )
        except ClientError as e:
            logger.error("Failed to delete parameter group: %s", e)
            raise

    def reset_parameters(
        self,
        group_name: str,
        parameter_names: Optional[List[str]] = None,
        all_parameters: bool = False,
    ) -> ApplyStatus:
        """Reset parameters to their default values.

        Args:
            group_name: Name of the parameter group
            parameter_names: List of parameters to reset
            all_parameters: If True, resets all parameters

        Returns:
            ApplyStatus object containing the results of the reset operation

        Raises:
            ClientError: If parameter reset fails
        """
        try:
            params = {
                "ParameterGroupName": group_name,
                "ResetAllParameters": all_parameters,
            }

            if parameter_names and not all_parameters:
                params["Parameters"] = [
                    {"ParameterName": name, "ParameterValue": "default"}
                    for name in parameter_names
                ]

            response = self.redshift.reset_cluster_parameter_group(**params)

            return ApplyStatus(
                parameters_to_apply=response.get("ParametersToApply", []),
                parameters_applied=response.get("ParametersApplied", []),
                parameters_with_errors=response.get("ParameterErrors", {}),
                requires_reboot=any(
                    p["ApplyType"] == "static"
                    for p in response.get("Parameters", [])
                ),
            )

        except ClientError as e:
            logger.error("Failed to reset parameters: %s", e)
            raise

    def list_parameter_group_families(self) -> List[ParameterGroupFamily]:
        """List available parameter group families.

        Returns:
            List of ParameterGroupFamily objects containing available families

        Raises:
            ClientError: If listing parameter group families fails
        """
        try:
            response = self.redshift.describe_cluster_parameter_group_families()
            return [
                ParameterGroupFamily(
                    name=f["ParameterGroupFamily"],
                    description=f["Description"],
                    engine=f["Engine"],
                    engine_version=f["EngineVersion"],
                )
                for f in response["ParameterGroupFamilies"]
            ]

        except ClientError as e:
            logger.error("Failed to list parameter group families: %s", e)
            raise

    def get_pending_modifications(
        self,
        group_name: str,
    ) -> List[ParameterModification]:
        """Get pending parameter modifications.

        Args:
            group_name: Name of the parameter group

        Returns:
            List of ParameterModification objects containing pending modifications

        Raises:
            ClientError: If getting pending modifications fails
        """
        try:
            response = self.redshift.describe_cluster_parameters(
                ParameterGroupName=group_name,
                Source="pending",
            )

            return [
                ParameterModification(
                    parameter_name=p["ParameterName"],
                    current_value=p["ParameterValue"],
                    new_value=p.get("PendingValue", ""),
                    modification_state=p.get("ModificationState", "pending"),
                    modification_time=p.get("ModificationTime", ""),
                )
                for p in response["Parameters"]
            ]

        except ClientError as e:
            logger.error("Failed to get pending modifications: %s", e)
            raise

    # Helper Methods
    def _convert_to_cluster_status(self, cluster_data: Dict) -> ClusterStatus:
        """Convert API response to ClusterStatus model."""
        return ClusterStatus(
            cluster_identifier=cluster_data["ClusterIdentifier"],
            status=cluster_data["ClusterStatus"],
            node_type=cluster_data["NodeType"],
            number_of_nodes=cluster_data["NumberOfNodes"],
            availability_zone=cluster_data["AvailabilityZone"],
            vpc_id=cluster_data.get("VpcId"),
            publicly_accessible=cluster_data["PubliclyAccessible"],
            encrypted=cluster_data["Encrypted"],
            database_name=cluster_data["DBName"],
            master_username=cluster_data["MasterUsername"],
            endpoint_address=cluster_data.get("Endpoint", {}).get("Address"),
            endpoint_port=cluster_data.get("Endpoint", {}).get("Port"),
            cluster_create_time=cluster_data.get("ClusterCreateTime"),
            automated_snapshot_retention_period=cluster_data[
                "AutomatedSnapshotRetentionPeriod"
            ],
            cluster_security_groups=[
                g["ClusterSecurityGroupName"]
                for g in cluster_data.get("ClusterSecurityGroups", [])
            ],
            vpc_security_groups=[
                g["VpcSecurityGroupId"]
                for g in cluster_data.get("VpcSecurityGroups", [])
            ],
            pending_modified_values=cluster_data.get(
                "PendingModifiedValues", {}),
            preferred_maintenance_window=cluster_data[
                "PreferredMaintenanceWindow"
            ],
            node_type_parameters=cluster_data.get("NodeTypeParameters", {}),
            cluster_version=cluster_data["ClusterVersion"],
            allow_version_upgrade=cluster_data["AllowVersionUpgrade"],
            number_of_nodes_ready=cluster_data.get("NumberOfNodesReady"),
            total_storage_capacity_in_mega_bytes=cluster_data[
                "TotalStorageCapacityInMegaBytes"
            ],
            aqua_configuration_status=cluster_data["AquaConfigurationStatus"],
            default_iam_role_arn=cluster_data.get("DefaultIamRoleArn"),
            maintenance_track_name=cluster_data["MaintenanceTrackName"],
            elastic_resize_number_of_node_options=cluster_data.get(
                "ElasticResizeNumberOfNodeOptions"
            ),
            deferred_maintenance_windows=cluster_data.get(
                "DeferredMaintenanceWindows", []
            ),
            snapshot_schedule_state=cluster_data["SnapshotScheduleState"],
            expected_next_snapshot_schedule_time=cluster_data.get(
                "ExpectedNextSnapshotScheduleTime"
            ),
            expected_next_snapshot_schedule_time_status=cluster_data[
                "ExpectedNextSnapshotScheduleTimeStatus"
            ],
            next_maintenance_window_start_time=cluster_data.get(
                "NextMaintenanceWindowStartTime"
            ),
        )
