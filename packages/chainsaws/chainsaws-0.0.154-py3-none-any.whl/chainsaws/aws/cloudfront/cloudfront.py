import logging
from typing import Literal, Optional

from chainsaws.aws.cloudfront._cloudfront_internal import CloudFront
from chainsaws.aws.cloudfront.cloudfront_models import (
    BehaviorConfig,
    CloudFrontAPIConfig,
    DistributionConfig,
    DistributionSummary,
    OriginConfig,
)
from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)


class CloudFrontAPI:
    """High-level CloudFront API for CDN management."""

    def __init__(self, config: Optional[CloudFrontAPIConfig] = None) -> None:
        """Initialize CloudFront client.

        Args:
            config: Optional CloudFront configuration

        """
        self.config = config or CloudFrontAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.cloudfront = CloudFront(
            boto3_session=self.boto3_session,
            config=config,
        )

    def create_s3_distribution(
        self,
        bucket_name: str,
        aliases: Optional[list[str]] = None,
        certificate_arn: Optional[str] = None,
        default_root_object: str = "index.html",
    ) -> DistributionSummary:
        """Create CloudFront distribution for S3 bucket with Origin Access Control (OAC).
        This method:
        1. Creates an Origin Access Control
        2. Updates S3 bucket policy to allow CloudFront access
        3. Creates CloudFront distribution.

        Args:
            bucket_name: S3 bucket name
            aliases: Optional list of alternate domain names
            certificate_arn: Optional ACM certificate ARN for custom domains
            default_root_object: Default root object (default: index.html)

        """
        try:
            oac_id = self.cloudfront.create_origin_access_control(bucket_name)
        except Exception:
            logger.exception("Failed to create Origin Access Control")
            raise

        from chainsaws.aws.s3 import S3API
        from chainsaws.aws.sts import STSAPI

        s3 = S3API(bucket_name, config=self.config)
        sts = STSAPI(config=self.config)

        try:
            identity = sts.get_caller_identity()
            account_id = identity.account
        except Exception:
            logger.exception("Failed to get caller identity")
            self.cloudfront.delete_origin_access_control(oac_id)
            raise

        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudfront.amazonaws.com",
                    },
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceArn": f"arn:aws:cloudfront::{account_id}:distribution/*",
                        },
                    },
                },
            ],
        }

        try:
            s3.put_bucket_policy(bucket_policy)
        except Exception:
            logger.exception("Failed to update bucket policy")
            # Clean up OAC if bucket policy update fails
            self.cloudfront.delete_origin_access_control(oac_id)
            raise

        # Create distribution with OAC
        origin = OriginConfig(
            domain_name=f"{bucket_name}.s3.amazonaws.com",
            origin_id=f"S3-{bucket_name}",
            origin_access_control_id=oac_id,
        )

        behavior = BehaviorConfig(
            target_origin_id=f"S3-{bucket_name}",
            viewer_protocol_policy="redirect-to-https",
            allowed_methods=["GET", "HEAD", "OPTIONS"],
            cached_methods=["GET", "HEAD", "OPTIONS"],
        )

        config = DistributionConfig(
            comment=f"Distribution for {bucket_name}",
            aliases=aliases or [],
            default_root_object=default_root_object,
            origins=[origin],
            default_behavior=behavior,
            certificate_arn=certificate_arn,
        )

        try:
            return self.cloudfront.create_distribution(config)
        except Exception:
            logger.exception("Failed to create distribution")
            # Clean up OAC if distribution creation fails
            self.cloudfront.delete_origin_access_control(oac_id)
            # Revert bucket policy
            s3.put_bucket_policy({
                "Version": "2012-10-17",
                "Statement": [],
            })
            raise

    def create_custom_distribution(
        self,
        origin_domain: str,
        origin_id: str,
        behaviors: Optional[list[BehaviorConfig]] = None,
        aliases: Optional[list[str]] = None,
        certificate_arn: Optional[str] = None,
        default_root_object: str = "index.html",
    ) -> DistributionSummary:
        """Create CloudFront distribution with custom origin.

        Args:
            origin_domain: Origin domain name
            origin_id: Origin identifier
            behaviors: Optional list of cache behaviors
            aliases: Optional list of alternate domain names
            certificate_arn: Optional ACM certificate ARN for custom domains
            default_root_object: Default root object (default: index.html)

        """
        origin = OriginConfig(
            domain_name=origin_domain,
            origin_id=origin_id,
        )

        default_behavior = BehaviorConfig(
            target_origin_id=origin_id,
            viewer_protocol_policy="redirect-to-https",
            allowed_methods=["GET", "HEAD", "OPTIONS",
                             "PUT", "POST", "PATCH", "DELETE"],
            cached_methods=["GET", "HEAD", "OPTIONS"],
        )

        config = DistributionConfig(
            comment=f"Distribution for {origin_domain}",
            aliases=aliases or [],
            default_root_object=default_root_object,
            origins=[origin],
            default_behavior=default_behavior,
            custom_behaviors=behaviors or [],
            certificate_arn=certificate_arn,
        )

        return self.cloudfront.create_distribution(config)

    def get_distribution(self, distribution_id: str) -> DistributionSummary:
        """Get CloudFront distribution details."""
        return self.cloudfront.get_distribution(distribution_id)

    def update_distribution(
        self,
        distribution_id: str,
        config: DistributionConfig,
    ) -> DistributionSummary:
        """Update existing CloudFront distribution."""
        return self.cloudfront.update_distribution(distribution_id, config)

    def delete_distribution(self, distribution_id: str) -> None:
        """Delete CloudFront distribution."""
        self.cloudfront.delete_distribution(distribution_id)

    def invalidate_cache(
        self,
        distribution_id: str,
        paths: list[str],
    ) -> str:
        """Create cache invalidation.

        Args:
            distribution_id: Distribution ID
            paths: List of paths to invalidate (e.g., ["/images/*", "/css/style.css"])

        """
        return self.cloudfront.invalidate_cache(distribution_id, paths)

    def invalidate_all_files(
        self,
        distribution_id: str,
    ) -> str:
        """Invalidate all files in the distribution.
        This is equivalent to invalidating '/*' path pattern.

        Note: Each invalidation request has a cost. Use this method carefully.

        Args:
            distribution_id: Distribution ID

        Returns:
            str: Invalidation ID

        """
        return self.cloudfront.invalidate_cache(
            distribution_id=distribution_id,
            paths=["/*"],
        )

    def update_cache_policy(
        self,
        distribution_id: str,
        cache_policy_id: str,
        path_pattern: Optional[str] = None,
        min_ttl: int = 0,
        default_ttl: int = 86400,  # 1 day
        max_ttl: int = 31536000,  # 1 year
        headers: Optional[list[str]] = None,
        cookies: Optional[list[str]] = None,
        query_strings: Optional[list[str]] = None,
    ) -> DistributionSummary:
        """Update cache policy for distribution.
        If path_pattern is not provided, updates the default cache behavior.

        Args:
            distribution_id: Distribution ID
            cache_policy_id: Cache policy ID or 'custom' for custom policy
            path_pattern: Optional path pattern to update specific behavior
            min_ttl: Minimum time to live (in seconds)
            default_ttl: Default time to live (in seconds)
            max_ttl: Maximum time to live (in seconds)
            headers: List of headers to include in cache key
            cookies: List of cookies to include in cache key
            query_strings: List of query strings to include in cache key

        Returns:
            Updated distribution summary

        """
        distribution = self.get_distribution(distribution_id)
        current_config = distribution.to_dict()

        if path_pattern:
            # Update specific cache behavior
            for behavior in current_config["custom_behaviors"]:
                if behavior["path_pattern"] == path_pattern:
                    behavior["cache_policy_id"] = cache_policy_id
                    if cache_policy_id == "custom":
                        behavior.update({
                            "min_ttl": min_ttl,
                            "default_ttl": default_ttl,
                            "max_ttl": max_ttl,
                            "headers": headers or [],
                            "cookies": cookies or [],
                            "query_strings": query_strings or [],
                        })
                    break
            else:
                msg = f"No behavior found for path pattern: {path_pattern}"
                raise ValueError(
                    msg)
        else:
            # Update default cache behavior
            current_config["default_behavior"]["cache_policy_id"] = cache_policy_id
            if cache_policy_id == "custom":
                current_config["default_behavior"].update({
                    "min_ttl": min_ttl,
                    "default_ttl": default_ttl,
                    "max_ttl": max_ttl,
                    "headers": headers or [],
                    "cookies": cookies or [],
                    "query_strings": query_strings or [],
                })

        config = DistributionConfig(**current_config)
        return self.update_distribution(distribution_id, config)

    def get_managed_cache_policies(self) -> dict[str, str]:
        """Get list of AWS managed cache policies.

        Returns:
            Dict mapping policy names to their IDs

        """
        return {
            "CachingOptimized": "658327ea-f89d-4fab-a63d-7e88639e58f6",
            "CachingOptimizedForUncompressedObjects": "b2884449-e4de-46a7-ac36-70bc7f1ddd6d",
            "CachingDisabled": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
            "Amplify": "2e54312d-136d-493c-8eb9-b001f22f67d2",
            "Elemental-MediaPackage": "08627262-05a9-4f76-9ded-b50ca2e3a84f",
        }

    def apply_managed_cache_policy(
        self,
        distribution_id: str,
        policy_name: Literal[
            "CachingOptimized",
            "CachingOptimizedForUncompressedObjects",
            "CachingDisabled",
            "Amplify",
            "Elemental-MediaPackage",
        ],
        path_pattern: Optional[str] = None
    ) -> DistributionSummary:
        """Apply an AWS managed cache policy to distribution.

        Managed Policies:
            CachingOptimized:
                - Designed for optimal caching
                - Caches based on: None (only URL)
                - TTL: Min 1 second, Default 24 hours, Max 1 year
                - Gzip/Brotli compression enabled
                - Best for static assets (images, css, js)

            CachingOptimizedForUncompressedObjects:
                - Similar to CachingOptimized but without compression
                - Caches based on: None (only URL)
                - TTL: Min 1 second, Default 24 hours, Max 1 year
                - Best for already compressed assets

            CachingDisabled:
                - Prevents caching completely
                - All requests pass directly to origin
                - TTL: 0 seconds
                - Best for dynamic content or debugging

            Amplify:
                - Optimized for AWS Amplify applications
                - Caches based on: Authorization, Accept headers
                - Includes common SPA query strings
                - TTL: Min 2 seconds, Default 600 seconds, Max 600 seconds
                - Best for Amplify-powered applications

            Elemental-MediaPackage:
                - Optimized for video streaming
                - Caches based on: Origin, Host headers
                - Includes common media query parameters
                - TTL: Min 0 seconds, Default 24 hours, Max 1 year
                - Best for MediaPackage video delivery

        Args:
            distribution_id: Distribution ID
            policy_name: Name of managed policy to apply
            path_pattern: Optional path pattern for specific behavior

        Returns:
            Updated distribution summary

        Example:
            ```python
            # Apply optimized caching for static assets
            cloudfront.apply_managed_cache_policy(
                distribution_id="DIST123",
                policy_name="CachingOptimized",
                path_pattern="/static/*"
            )

            # Disable caching for API endpoints
            cloudfront.apply_managed_cache_policy(
                distribution_id="DIST123",
                policy_name="CachingDisabled",
                path_pattern="/api/*"
            )
            ```

        """
        policies = self.get_managed_cache_policies()
        if policy_name not in policies:
            msg = f"Unknown managed policy: {policy_name}"
            raise ValueError(msg)

        return self.update_cache_policy(
            distribution_id=distribution_id,
            cache_policy_id=policies[policy_name],
            path_pattern=path_pattern,
        )

    def add_custom_domain(
        self,
        distribution_id: str,
        domain_name: str,
        certificate_arn: str,
    ) -> DistributionSummary:
        """Add custom domain to distribution.

        Args:
            distribution_id: Distribution ID
            domain_name: Custom domain name
            certificate_arn: ACM certificate ARN

        """
        distribution = self.get_distribution(distribution_id)
        current_config = distribution.to_dict()

        # Add new alias
        current_config["aliases"].append(domain_name)

        # Update certificate
        current_config["certificate_arn"] = certificate_arn

        config = DistributionConfig(**current_config)
        return self.update_distribution(distribution_id, config)

    def add_origin(
        self,
        distribution_id: str,
        origin: OriginConfig,
        behavior: Optional[BehaviorConfig] = None,
    ) -> DistributionSummary:
        """Add new origin to distribution.

        Args:
            distribution_id: Distribution ID
            origin: Origin configuration
            behavior: Optional cache behavior for the origin

        """
        distribution = self.get_distribution(distribution_id)
        current_config = distribution.to_dict()

        # Add new origin
        current_config["origins"].append(origin)

        # Add behavior if provided
        if behavior:
            current_config["custom_behaviors"].append(behavior)

        config = DistributionConfig(**current_config)
        return self.update_distribution(distribution_id, config)

    def enable_waf(
        self,
        distribution_id: str,
        web_acl_id: str,
    ) -> DistributionSummary:
        """Enable WAF for distribution.

        Args:
            distribution_id: Distribution ID
            web_acl_id: WAF web ACL ID

        """
        distribution = self.get_distribution(distribution_id)
        current_config = distribution.to_dict()

        current_config["web_acl_id"] = web_acl_id

        config = DistributionConfig(**current_config)
        return self.update_distribution(distribution_id, config)
