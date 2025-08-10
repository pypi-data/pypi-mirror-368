from typing import Literal, Optional, Any
from dataclasses import dataclass, field, asdict

from chainsaws.aws.shared.config import APIConfig


@dataclass
class CloudFrontAPIConfig(APIConfig):
    """Configuration for CloudFront client."""


@dataclass
class OriginConfig:
    """Origin configuration for CloudFront distribution."""

    domain_name: str  # Origin domain name
    origin_id: str  # Unique identifier for the origin
    origin_path: str | None = ""  # Path to request content from
    custom_headers: dict[str, str] | None = field(
        default_factory=dict)  # Custom headers to send to origin
    s3_origin_access_identity: str | None = None  # OAI for S3 bucket origin

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = asdict(self)
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class BehaviorConfig:
    """Cache behavior configuration."""

    target_origin_id: str  # ID of target origin
    path_pattern: str | None = "*"  # Path pattern this behavior applies to
    viewer_protocol_policy: Literal["redirect-to-https", "https-only",
                                    "allow-all"] = "redirect-to-https"  # Protocol policy for viewers
    allowed_methods: list[str] = field(
        default_factory=lambda: ["GET", "HEAD"])  # Allowed HTTP methods
    cached_methods: list[str] = field(
        default_factory=lambda: ["GET", "HEAD"])  # Methods to cache
    cache_policy_id: str | None = None  # Cache policy ID
    origin_request_policy_id: str | None = None  # Origin request policy ID
    response_headers_policy_id: str | None = None  # Response headers policy ID
    function_associations: list[dict[str, str]] | None = field(
        default_factory=list)  # CloudFront function associations

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = asdict(self)
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class DistributionConfig:
    """CloudFront distribution configuration."""

    origins: list[OriginConfig]  # Origin configurations
    default_behavior: BehaviorConfig  # Default cache behavior
    comment: str | None = ""  # Distribution comment
    enabled: bool = True  # Distribution enabled state
    aliases: list[str] | None = field(
        default_factory=list)  # Alternate domain names (CNAMEs)
    default_root_object: str | None = "index.html"  # Default root object
    custom_behaviors: list[BehaviorConfig] | None = field(
        default_factory=list)  # Custom cache behaviors
    price_class: Literal["PriceClass_All", "PriceClass_200",
                         "PriceClass_100"] = "PriceClass_100"  # Distribution price class
    # ACM certificate ARN for custom domain
    certificate_arn: Optional[str] = None
    web_acl_id: Optional[str] = None  # WAF web ACL ID

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        result = {
            "origins": [o.to_dict() for o in self.origins],
            "defaultBehavior": self.default_behavior.to_dict(),
            "enabled": self.enabled,
            "priceClass": self.price_class,
        }
        if self.comment:
            result["comment"] = self.comment
        if self.aliases:
            result["aliases"] = self.aliases
        if self.default_root_object:
            result["defaultRootObject"] = self.default_root_object
        if self.custom_behaviors:
            result["customBehaviors"] = [b.to_dict()
                                         for b in self.custom_behaviors]
        if self.certificate_arn:
            result["certificateArn"] = self.certificate_arn
        if self.web_acl_id:
            result["webAclId"] = self.web_acl_id
        return result


@dataclass
class DistributionSummary:
    """Summary of CloudFront distribution."""

    id: str
    domain_name: str
    enabled: bool
    status: str
    aliases: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format expected by AWS API."""
        return asdict(self)
