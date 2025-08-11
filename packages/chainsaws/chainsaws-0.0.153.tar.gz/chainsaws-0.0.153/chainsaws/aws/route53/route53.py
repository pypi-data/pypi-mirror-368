"""AWS Route53 high-level client providing simplified interface for DNS operations."""
import logging
from typing import Literal, List, Optional, Tuple, Dict

from chainsaws.aws.route53._route53_internal import Route53
from chainsaws.aws.route53.route53_constants import AWS_SERVICE_HOSTED_ZONES
from chainsaws.aws.route53.route53_models import (
    AliasTarget,
    DNSRecordChange,
    DNSRecordSet,
    FailoverConfig,
    HealthCheckConfig,
    HealthCheckResponse,
    LatencyConfig,
    Route53APIConfig,
    RoutingConfig,
    WeightedConfig,
)
from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)


class Route53API:
    """High-level Route53 API for DNS management."""

    def __init__(
        self,
        domain_name: str,
        config: Optional[Route53APIConfig] = None,
    ) -> None:
        """Initialize Route53 client.

        Args:
            domain_name: Domain name to manage
            config: Optional Route53 configuration

        """
        self.config = config or Route53APIConfig()
        self.domain_name = domain_name
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )
        self.route53 = Route53(
            boto3_session=self.boto3_session,
            config=config,
        )
        self.hosted_zone_id = self.route53.get_hosted_zone_id(domain_name)

    def get_records(
        self,
        record_name: Optional[str] = None,
        record_type: Optional[str] = None,
    ) -> List[DNSRecordSet]:
        """Get DNS records.

        Args:
            record_name: Optional record name filter
            record_type: Optional record type filter

        """
        records = self.route53.get_record_sets(
            self.hosted_zone_id,
            record_name,
            record_type,
        )

        return [
            DNSRecordSet(
                name=record["Name"],
                type=record["Type"],
                ttl=record.get("TTL", 300),
                records=[r["Value"] for r in record.get("ResourceRecords", [])],
            )
            for record in records
        ]

    def create_record(self, record: DNSRecordSet) -> str:
        """Create a new DNS record.

        Args:
            record: DNS record to create

        """
        change = DNSRecordChange(
            action="CREATE",
            record_set=record,
        )
        return self.route53.change_record_sets(self.hosted_zone_id, [change])

    def update_record(self, record: DNSRecordSet) -> str:
        """Update an existing DNS record.

        Args:
            record: DNS record to update

        """
        change = DNSRecordChange(
            action="UPSERT",
            record_set=record,
        )
        return self.route53.change_record_sets(self.hosted_zone_id, [change])

    def delete_record(self, record: DNSRecordSet) -> str:
        """Delete a DNS record.

        Args:
            record: DNS record to delete

        """
        change = DNSRecordChange(
            action="DELETE",
            record_set=record,
        )
        return self.route53.change_record_sets(self.hosted_zone_id, [change])

    def create_health_check(
        self,
        config: HealthCheckConfig,
    ) -> HealthCheckResponse:
        """Create a new health check.

        Args:
            config: Health check configuration

        Returns:
            Health check creation response

        """
        return self.route53.create_health_check(config)

    def delete_health_check(self, health_check_id: str) -> None:
        """Delete a health check.

        Args:
            health_check_id: ID of health check to delete

        """
        return self.route53.delete_health_check(health_check_id)

    def get_health_check_status(self, health_check_id: str) -> str:
        """Get current status of a health check.

        Args:
            health_check_id: ID of health check to query

        Returns:
            Current health check status

        """
        return self.route53.get_health_check_status(health_check_id)

    def create_failover_records(
        self,
        name: str,
        type: str,
        primary_records: List[str],
        secondary_records: List[str],
        health_check_config: Optional[HealthCheckConfig] = None,
        ttl: int = 300,
    ) -> str:
        """Create a failover DNS configuration with primary and secondary records.

        Args:
            name: Record name
            type: Record type
            primary_records: List of primary record values
            secondary_records: List of secondary record values
            health_check_config: Optional health check configuration for primary
            ttl: Time to live

        Returns:
            Change ID for the operation

        """
        # Create health check if configured
        health_check_id = None
        if health_check_config:
            health_check = self.create_health_check(health_check_config)
            health_check_id = health_check.id

        # Create primary and secondary records
        primary = DNSRecordSet(
            name=name,
            type=type,
            ttl=ttl,
            records=primary_records,
            failover=FailoverConfig(
                is_primary=True,
                health_check_id=health_check_id,
            ),
        )

        secondary = DNSRecordSet(
            name=name,
            type=type,
            ttl=ttl,
            records=secondary_records,
            failover=FailoverConfig(
                is_primary=False,
            ),
        )

        changes = [
            DNSRecordChange(action="CREATE", record_set=primary),
            DNSRecordChange(action="CREATE", record_set=secondary),
        ]

        return self.route53.change_record_sets(self.hosted_zone_id, changes)

    def create_weighted_records(
        self,
        name: str,
        type: str,
        weighted_records: List[Tuple[List[str], int, str]],
        ttl: int = 300,
        health_check_config: Optional[HealthCheckConfig] = None,
    ) -> str:
        """Create weighted DNS records for load balancing.

        Args:
            name: Record name
            type: Record type
            weighted_records: List of tuples (records, weight, identifier)
            ttl: Time to live
            health_check_config: Optional health check configuration

        Example:
            >>> route53.create_weighted_records(
            ...     name="api.example.com.",
            ...     type="A",
            ...     weighted_records=[
            ...         (["192.0.2.1"], 70, "primary"),
            ...         (["192.0.2.2"], 30, "secondary")
            ...     ]
            ... )

        """
        health_check_id = None
        if health_check_config:
            health_check = self.create_health_check(health_check_config)
            health_check_id = health_check.id

        changes = []
        for records, weight, identifier in weighted_records:
            record_set = DNSRecordSet(
                name=name,
                type=type,
                ttl=ttl,
                records=records,
                routing=RoutingConfig(
                    policy="WEIGHTED",
                    weighted=WeightedConfig(
                        weight=weight,
                        set_identifier=identifier,
                    ),
                    health_check_id=health_check_id,
                ),
            )
            changes.append(DNSRecordChange(
                action="CREATE",
                record_set=record_set,
            ))

        return self.route53.change_record_sets(self.hosted_zone_id, changes)

    def create_latency_records(
        self,
        name: str,
        type: str,
        regional_records: List[Tuple[List[str], str, str]],
        ttl: int = 300,
        health_check_configs: Optional[Dict[str, HealthCheckConfig]] = None,
    ) -> str:
        """Create latency-based DNS records for regional routing.

        Args:
            name: Record name
            type: Record type
            regional_records: List of tuples (records, region, identifier)
            ttl: Time to live
            health_check_configs: Optional dict of health check configs by identifier

        Example:
            >>> route53.create_latency_records(
            ...     name="api.example.com.",
            ...     type="A",
            ...     regional_records=[
            ...         (["192.0.2.1"], "ap-northeast-2", "seoul"),
            ...         (["192.0.2.2"], "us-west-2", "oregon")
            ...     ],
            ...     health_check_configs={
            ...         "seoul": HealthCheckConfig(...),
            ...         "oregon": HealthCheckConfig(...)
            ...     }
            ... )

        """
        health_checks = {}
        if health_check_configs:
            for identifier, config in health_check_configs.items():
                health_check = self.create_health_check(config)
                health_checks[identifier] = health_check.id

        changes = []
        for records, region, identifier in regional_records:
            record_set = DNSRecordSet(
                name=name,
                type=type,
                ttl=ttl,
                records=records,
                routing=RoutingConfig(
                    policy="LATENCY",
                    latency=LatencyConfig(
                        region=region,
                        set_identifier=identifier,
                    ),
                    health_check_id=health_checks.get(identifier),
                ),
            )
            changes.append(DNSRecordChange(
                action="CREATE",
                record_set=record_set,
            ))

        return self.route53.change_record_sets(self.hosted_zone_id, changes)

    def update_record_weight(
        self,
        name: str,
        type: str,
        identifier: str,
        new_weight: int,
    ) -> str:
        """Update the weight of a weighted record.

        Args:
            name: Record name
            type: Record type
            identifier: Set identifier
            new_weight: New weight value (0-255)

        """
        records = self.get_records(name, type)
        for record in records:
            if (record.routing and
                record.routing.policy == "WEIGHTED" and
                    record.routing.weighted.set_identifier == identifier):

                record.routing.weighted.weight = new_weight
                return self.update_record(record)

        msg = f"No weighted record found with identifier: {identifier}"
        raise ValueError(
            msg)

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

    def create_cloudfront_alias(
        self,
        name: str,
        distribution_domain: str,
        type: Literal["A", "AAAA"] = "A",
    ) -> str:
        """Create an alias record pointing to a CloudFront distribution.

        Args:
            name: Record name (e.g., 'www.example.com.')
            distribution_domain: CloudFront distribution domain
            type: Record type (A or AAAA)

        """
        return self.create_alias_record(
            name=name,
            type=type,
            target_dns_name=distribution_domain,
            target_hosted_zone_id=AWS_SERVICE_HOSTED_ZONES["cloudfront"],
        )

    def create_s3_website_alias(
        self,
        name: str,
        bucket_website_domain: str,
        region: str,
        type: Literal["A", "AAAA"] = "A",
    ) -> str:
        """Create an alias record pointing to an S3 static website.

        Args:
            name: Record name
            bucket_website_domain: S3 website endpoint
            region: AWS region
            type: Record type (A or AAAA)

        """
        return self.create_alias_record(
            name=name,
            type=type,
            target_dns_name=bucket_website_domain,
            target_hosted_zone_id=AWS_SERVICE_HOSTED_ZONES["s3_website"][region],
        )

    def create_api_gateway_alias(
        self,
        name: str,
        api_domain: str,
        region: str,
        type: Literal["A", "AAAA"] = "A",
    ) -> str:
        """Create an alias record pointing to an API Gateway endpoint.

        Args:
            name: Record name
            api_domain: API Gateway domain
            region: AWS region
            type: Record type (A or AAAA)

        """
        return self.create_alias_record(
            name=name,
            type=type,
            target_dns_name=api_domain,
            target_hosted_zone_id=AWS_SERVICE_HOSTED_ZONES["api_gateway"][region],
        )

    def create_elasticbeanstalk_alias(
        self,
        name: str,
        eb_domain: str,
        region: str,
        type: Literal["A", "AAAA"] = "A",
    ) -> str:
        """Create an alias record pointing to an Elastic Beanstalk environment.

        Args:
            name: Record name
            eb_domain: Elastic Beanstalk environment domain
            region: AWS region
            type: Record type (A or AAAA)

        """
        return self.create_alias_record(
            name=name,
            type=type,
            target_dns_name=eb_domain,
            target_hosted_zone_id=AWS_SERVICE_HOSTED_ZONES["elasticbeanstalk"][region],
        )

    def create_appsync_alias(
        self,
        name: str,
        appsync_domain: str,
        region: str,
        type: Literal["A", "AAAA"] = "A",
    ) -> str:
        """Create an alias record pointing to an AppSync API.

        Args:
            name: Record name
            appsync_domain: AppSync API domain
            region: AWS region
            type: Record type (A or AAAA)

        """
        return self.create_alias_record(
            name=name,
            type=type,
            target_dns_name=appsync_domain,
            target_hosted_zone_id=AWS_SERVICE_HOSTED_ZONES["appsync"][region],
        )

    def create_elb_alias(
        self,
        name: str,
        elb_domain: str,
        region: str,
        type: Literal["A", "AAAA"] = "A",
    ) -> str:
        """Create an alias record pointing to a Classic Load Balancer.

        Args:
            name: Record name
            elb_domain: Classic Load Balancer domain
            region: AWS region
            type: Record type (A or AAAA)

        """
        return self.create_alias_record(
            name=name,
            type=type,
            target_dns_name=elb_domain,
            target_hosted_zone_id=AWS_SERVICE_HOSTED_ZONES["elb"][region],
        )

    def create_nlb_alias(
        self,
        name: str,
        alb_domain: str,
        region: str,
        type: Literal["A", "AAAA"] = "A",
    ) -> str:
        """Create an alias record pointing to an Network Load Balancer.

        Args:
            name: Record name
            alb_domain: Network Load Balancer domain
            region: AWS region
            type: Record type (A or AAAA)

        """
        return self.create_alias_record(
            name=name,
            type=type,
            target_dns_name=alb_domain,
            target_hosted_zone_id=AWS_SERVICE_HOSTED_ZONES["nlb"][region],
        )
