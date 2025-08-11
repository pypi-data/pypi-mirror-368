import logging
import uuid
from typing import Any, Literal, List, Dict, Optional

import boto3

from chainsaws.aws.route53.route53_models import (
    AliasTarget,
    DNSRecordChange,
    DNSRecordSet,
    HealthCheckConfig,
    HealthCheckResponse,
    Route53APIConfig,
)

logger = logging.getLogger(__name__)


class Route53:
    def __init__(
        self,
        boto3_session: boto3.Session,
        config: Optional[Route53APIConfig] = None,
    ) -> None:
        self.config = config or Route53APIConfig()
        self.client = boto3_session.client("route53")

    def get_hosted_zone_id(self, domain_name: str) -> str:
        """Get hosted zone ID for domain."""
        try:
            response = self.client.list_hosted_zones_by_name(
                DNSName=domain_name)
            for zone in response["HostedZones"]:
                if zone["Name"] == f"{domain_name}." or zone["Name"] == domain_name:
                    return zone["Id"].split("/")[-1]

            msg = f"No hosted zone found for domain: {domain_name}"
            raise ValueError(msg)
        except Exception as ex:
            logger.exception(f"Failed to get hosted zone ID: {ex!s}")
            raise

    def get_record_sets(
        self,
        hosted_zone_id: str,
        record_name: Optional[str] = None,
        record_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get DNS record sets."""
        try:
            params = {"HostedZoneId": hosted_zone_id}
            if record_name:
                params["StartRecordName"] = record_name
            if record_type:
                params["StartRecordType"] = record_type

            response = self.client.list_resource_record_sets(**params)
            return response["ResourceRecordSets"]
        except Exception as ex:
            logger.exception(f"Failed to get record sets: {ex!s}")
            raise

    def add_record(
        self,
        hosted_zone_id: str,
        record: DNSRecordSet,
    ) -> str:
        """Add a single DNS record.

        Args:
            hosted_zone_id: The hosted zone ID
            record: The DNS record to add

        Returns:
            Change ID for tracking the change

        Example:
            >>> record = DNSRecordSet(
            ...     name="api.example.com.",
            ...     type="A",
            ...     ttl=300,
            ...     records=["192.0.2.1"]
            ... )
            >>> route53.add_record(zone_id, record)

        """
        change = DNSRecordChange(action="CREATE", record_set=record)
        return self.change_record_sets(hosted_zone_id, [change])

    def add_records(
        self,
        hosted_zone_id: str,
        records: List[DNSRecordSet],
    ) -> str:
        """Add multiple DNS records in a single batch.

        Args:
            hosted_zone_id: The hosted zone ID
            records: List of DNS records to add

        Returns:
            Change ID for tracking the change

        Example:
            >>> records = [
            ...     DNSRecordSet(
            ...         name="api.example.com.",
            ...         type="A",
            ...         ttl=300,
            ...         records=["192.0.2.1"]
            ...     ),
            ...     DNSRecordSet(
            ...         name="www.example.com.",
            ...         type="CNAME",
            ...         ttl=300,
            ...         records=["api.example.com"]
            ...     )
            ... ]
            >>> route53.add_records(zone_id, records)

        """
        changes = [
            DNSRecordChange(action="CREATE", record_set=record)
            for record in records
        ]
        return self.change_record_sets(hosted_zone_id, changes)

    def create_alias_record(
        self,
        name: str,
        type: Literal["A", "AAAA"],
        target_dns_name: str,
        target_hosted_zone_id: str,
        evaluate_target_health: bool = True,
    ) -> str:
        """Create an alias record pointing to an AWS service.

        Args:
            name: Record name
            type: Record type (A or AAAA)
            target_dns_name: DNS name of the target AWS service
            target_hosted_zone_id: Hosted zone ID of the target service
            evaluate_target_health: Whether to evaluate target health

        Example:
            >>> # Alias to CloudFront distribution
            >>> route53.create_alias_record(
            ...     name="www.example.com.",
            ...     type="A",
            ...     target_dns_name="d123456789.cloudfront.net",
            ...     target_hosted_zone_id=Route53API.AWS_SERVICE_HOSTED_ZONES['cloudfront']
            ... )

        """
        record = DNSRecordSet(
            name=name,
            type=type,
            alias_target=AliasTarget(
                hosted_zone_id=target_hosted_zone_id,
                dns_name=target_dns_name,
                evaluate_target_health=evaluate_target_health,
            ),
        )

        change = DNSRecordChange(action="CREATE", record_set=record)
        return self.route53.change_record_sets(self.hosted_zone_id, [change])

    def change_record_sets(
        self,
        hosted_zone_id: str,
        changes: List[DNSRecordChange],
    ) -> str:
        """Apply DNS record changes."""
        try:
            change_batch = {
                "Changes": [],
            }

            for change in changes:
                record_set = change.record_set
                record_set_config = {
                    "Name": record_set.name,
                    "Type": record_set.type,
                }

                # Handle alias records
                if record_set.alias_target:
                    record_set_config["AliasTarget"] = {
                        "HostedZoneId": record_set.alias_target.hosted_zone_id,
                        "DNSName": record_set.alias_target.dns_name,
                        "EvaluateTargetHealth": record_set.alias_target.evaluate_target_health,
                    }
                else:
                    record_set_config["TTL"] = record_set.ttl
                    record_set_config["ResourceRecords"] = [
                        {"Value": value} for value in record_set.records
                    ]

                # DNS Routing Config
                if record_set.routing:
                    if record_set.routing.policy == "WEIGHTED":
                        record_set_config["Weight"] = record_set.routing.weighted.weight
                        record_set_config["SetIdentifier"] = record_set.routing.weighted.set_identifier
                    elif record_set.routing.policy == "LATENCY":
                        record_set_config["Region"] = record_set.routing.latency.region
                        record_set_config["SetIdentifier"] = record_set.routing.latency.set_identifier

                    if record_set.routing.health_check_id:
                        record_set_config["HealthCheckId"] = record_set.routing.health_check_id

                change_batch["Changes"].append({
                    "Action": change.action,
                    "ResourceRecordSet": record_set_config,
                })

            response = self.client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch=change_batch,
            )

            return response["ChangeInfo"]["Id"]
        except Exception as ex:
            logger.exception(f"Failed to change record sets: {ex!s}")
            raise

    def create_health_check(
        self,
        config: HealthCheckConfig,
    ) -> HealthCheckResponse:
        """Create a health check."""
        try:
            health_check_config = {
                "Type": config.type,
                "RequestInterval": config.request_interval,
                "FailureThreshold": config.failure_threshold,
            }

            if config.ip_address:
                health_check_config["IPAddress"] = config.ip_address
            if config.port:
                health_check_config["Port"] = config.port
            if config.resource_path:
                health_check_config["ResourcePath"] = config.resource_path
            if config.fqdn:
                health_check_config["FullyQualifiedDomainName"] = config.fqdn
            if config.search_string:
                health_check_config["SearchString"] = config.search_string

            response = self.client.create_health_check(
                CallerReference=str(uuid.uuid4()),
                HealthCheckConfig=health_check_config,
            )

            return HealthCheckResponse(
                id=response["HealthCheck"]["Id"],
                status=response["HealthCheck"]["HealthCheckConfig"]["Type"],
            )

        except Exception as ex:
            logger.exception(f"Failed to create health check: {ex!s}")
            raise

    def delete_health_check(self, health_check_id: str) -> None:
        """Delete a health check."""
        try:
            self.client.delete_health_check(HealthCheckId=health_check_id)
        except Exception as ex:
            logger.exception(f"Failed to delete health check: {ex!s}")
            raise

    def get_health_check_status(self, health_check_id: str) -> str:
        """Get current status of a health check."""
        try:
            response = self.client.get_health_check_status(
                HealthCheckId=health_check_id,
            )
            return response["HealthCheckObservations"][0]["StatusReport"]["Status"]
        except Exception as ex:
            logger.exception(f"Failed to get health check status: {ex!s}")
            raise
