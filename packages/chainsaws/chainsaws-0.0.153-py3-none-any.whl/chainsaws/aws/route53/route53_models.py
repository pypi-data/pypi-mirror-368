from typing import Literal, List, Optional
from dataclasses import dataclass

from chainsaws.aws.shared.config import APIConfig


@dataclass
class Route53APIConfig(APIConfig):
    """Configuration for Route53 client."""
    pass


@dataclass
class DNSRecordSet:
    """DNS record set configuration."""

    name: str  # DNS record name (e.g., 'example.com.')
    type: Literal["A", "AAAA", "CNAME", "MX", "TXT",
                  "NS", "SOA", "SRV", "PTR"]  # DNS record type
    records: List[str]  # Record values
    ttl: int = 300  # Time to live in seconds


@dataclass
class DNSRecordChange:
    """DNS record change request."""

    action: Literal["CREATE", "DELETE", "UPSERT"]  # Change action
    record_set: DNSRecordSet  # Record set to change


@dataclass
class HealthCheckConfig:
    """Health check configuration."""

    type: Literal["HTTP", "HTTPS", "TCP"]  # Health check type
    ip_address: Optional[str] = None  # IP address to check
    port: Optional[int] = None  # Port to check (1-65535)
    resource_path: Optional[str] = None  # Resource path for HTTP(S) checks
    fqdn: Optional[str] = None  # Fully qualified domain name to check
    search_string: Optional[str] = None  # String to search for in response
    request_interval: int = 30  # Check interval in seconds (10-30)
    failure_threshold: int = 3  # Number of consecutive failures needed (1-10)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.port is not None and not 1 <= self.port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        if not 10 <= self.request_interval <= 30:
            raise ValueError("request_interval must be between 10 and 30")
        if not 1 <= self.failure_threshold <= 10:
            raise ValueError("failure_threshold must be between 1 and 10")


@dataclass
class HealthCheckResponse:
    """Health check creation response."""

    id: str  # Health check ID
    status: str  # Current health check status


@dataclass
class FailoverConfig:
    """DNS failover configuration."""

    is_primary: bool  # Whether this is the primary record
    health_check_id: Optional[str] = None  # Associated health check ID


@dataclass
class WeightedConfig:
    """Weighted routing configuration."""

    weight: int  # Routing weight (0-255)
    set_identifier: str  # Unique identifier for this weighted record set

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 0 <= self.weight <= 255:
            raise ValueError("weight must be between 0 and 255")


@dataclass
class LatencyConfig:
    """Latency-based routing configuration."""

    region: str  # AWS region for this endpoint
    set_identifier: str  # Unique identifier for this latency record set


@dataclass
class RoutingConfig:
    """DNS routing configuration."""

    policy: Literal["WEIGHTED", "LATENCY"]  # Routing policy type
    weighted: Optional[WeightedConfig] = None  # Weighted routing configuration
    latency: Optional[LatencyConfig] = None  # Latency-based routing configuration
    health_check_id: Optional[str] = None  # Optional health check ID


@dataclass
class AliasTarget:
    """AWS service alias target configuration."""

    hosted_zone_id: str  # Hosted zone ID of the AWS service
    dns_name: str  # DNS name of the AWS service
    evaluate_target_health: bool = True  # Whether to evaluate target health


@dataclass
class ExtendedDNSRecordSet:
    """Extended DNS record set configuration with alias and routing support."""

    name: str  # DNS record name (e.g., 'example.com.')
    # DNS record type (only A, AAAA, CNAME supported for alias)
    type: Literal["A", "AAAA", "CNAME"]
    # Time to live in seconds (not used for alias records)
    ttl: Optional[int] = None
    # Record values (not used for alias records)
    records: Optional[List[str]] = None
    alias_target: Optional[AliasTarget] = None  # Alias target configuration
    failover: Optional[FailoverConfig] = None  # Failover configuration
    routing: Optional[RoutingConfig] = None  # Routing configuration
