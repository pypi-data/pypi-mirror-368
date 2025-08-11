import logging
import uuid
from typing import Any

import boto3

from chainsaws.aws.cloudfront.cloudfront_models import (
    BehaviorConfig,
    CloudFrontAPIConfig,
    DistributionConfig,
    DistributionSummary,
)
from chainsaws.aws.cloudfront.cloudfront_exception import (
    CloudFrontCreateDistributionException,
    CloudFrontGetDistributionException,
    CloudFrontUpdateDistributionException,
    CloudFrontDeleteDistributionException,
    CloudFrontCreateInvalidationException,
    CloudFrontCreateOriginAccessControlException,
    CloudFrontDeleteOriginAccessControlException
)

logger = logging.getLogger(__name__)


class CloudFront:
    def __init__(
        self,
        boto3_session: boto3.Session,
        config: CloudFrontAPIConfig | None = None,
    ) -> None:
        self.config = config or CloudFrontAPIConfig()
        self.client = boto3_session.client("cloudfront")

    def _build_distribution_config(self, config: DistributionConfig) -> dict[str, Any]:
        """Build CloudFront distribution configuration."""
        origins = []
        for origin in config.origins:
            origin_config = {
                "Id": origin.origin_id,
                "DomainName": origin.domain_name,
                "OriginPath": origin.origin_path,
                "CustomHeaders": {
                    "Quantity": len(origin.custom_headers),
                    "Items": [
                        {"HeaderName": k, "HeaderValue": v}
                        for k, v in origin.custom_headers.items()
                    ],
                },
            }

            if origin.s3_origin_access_identity:
                origin_config["S3OriginConfig"] = {
                    "OriginAccessIdentity": f"origin-access-identity/cloudfront/{origin.s3_origin_access_identity}",
                }
            else:
                origin_config["CustomOriginConfig"] = {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "https-only",
                    "OriginSslProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]},
                }

            origins.append(origin_config)

        distribution_config = {
            "Comment": config.comment,
            "Enabled": config.enabled,
            "Aliases": {
                "Quantity": len(config.aliases),
                "Items": config.aliases,
            },
            "DefaultRootObject": config.default_root_object,
            "Origins": {
                "Quantity": len(origins),
                "Items": origins,
            },
            "DefaultCacheBehavior": self._build_cache_behavior(config.default_behavior),
            "CacheBehaviors": {
                "Quantity": len(config.custom_behaviors),
                "Items": [
                    self._build_cache_behavior(behavior)
                    for behavior in config.custom_behaviors
                ],
            },
            "PriceClass": config.price_class,
            "ViewerCertificate": {
                "CloudFrontDefaultCertificate": True,
            },
        }

        if config.certificate_arn:
            distribution_config["ViewerCertificate"] = {
                "ACMCertificateArn": config.certificate_arn,
                "SSLSupportMethod": "sni-only",
                "MinimumProtocolVersion": "TLSv1.2_2021",
            }

        if config.web_acl_id:
            distribution_config["WebACLId"] = config.web_acl_id

        return distribution_config

    def _build_cache_behavior(self, behavior: BehaviorConfig) -> dict[str, Any]:
        """Build cache behavior configuration."""
        return {
            "PathPattern": behavior.path_pattern,
            "TargetOriginId": behavior.target_origin_id,
            "ViewerProtocolPolicy": behavior.viewer_protocol_policy,
            "AllowedMethods": {
                "Quantity": len(behavior.allowed_methods),
                "Items": behavior.allowed_methods,
                "CachedMethods": {
                    "Quantity": len(behavior.cached_methods),
                    "Items": behavior.cached_methods,
                },
            },
            "CachePolicyId": behavior.cache_policy_id,
            "OriginRequestPolicyId": behavior.origin_request_policy_id,
            "ResponseHeadersPolicyId": behavior.response_headers_policy_id,
            "FunctionAssociations": {
                "Quantity": len(behavior.function_associations),
                "Items": behavior.function_associations,
            },
        }

    def create_distribution(self, config: DistributionConfig) -> DistributionSummary:
        """Create new CloudFront distribution."""
        try:
            response = self.client.create_distribution(
                DistributionConfig=self._build_distribution_config(config),
            )
            distribution = response["Distribution"]

            return DistributionSummary(
                id=distribution["Id"],
                domain_name=distribution["DomainName"],
                enabled=distribution["Status"] == "Deployed",
                status=distribution["Status"],
                aliases=distribution["DistributionConfig"]["Aliases"].get(
                    "Items", []),
            )
        except Exception as ex:
            logger.exception(f"Failed to create distribution: {ex!s}")
            raise CloudFrontCreateDistributionException(
                f"Failed to create distribution: {ex!s}") from ex

    def get_distribution(self, distribution_id: str) -> DistributionSummary:
        """Get CloudFront distribution details."""
        try:
            response = self.client.get_distribution(Id=distribution_id)
            distribution = response["Distribution"]

            return DistributionSummary(
                id=distribution["Id"],
                domain_name=distribution["DomainName"],
                enabled=distribution["Status"] == "Deployed",
                status=distribution["Status"],
                aliases=distribution["DistributionConfig"]["Aliases"].get(
                    "Items", []),
            )
        except Exception as ex:
            logger.exception(f"Failed to get distribution: {ex!s}")
            raise CloudFrontGetDistributionException(
                f"Failed to get distribution: {ex!s}") from ex

    def update_distribution(
        self,
        distribution_id: str,
        config: DistributionConfig,
    ) -> DistributionSummary:
        """Update existing CloudFront distribution."""
        try:
            current = self.client.get_distribution(Id=distribution_id)
            etag = current["ETag"]

            response = self.client.update_distribution(
                Id=distribution_id,
                DistributionConfig=self._build_distribution_config(config),
                IfMatch=etag,
            )
            distribution = response["Distribution"]

            return DistributionSummary(
                id=distribution["Id"],
                domain_name=distribution["DomainName"],
                enabled=distribution["Status"] == "Deployed",
                status=distribution["Status"],
                aliases=distribution["DistributionConfig"]["Aliases"].get(
                    "Items", []),
            )
        except Exception as ex:
            logger.exception(f"Failed to update distribution: {ex!s}")
            raise CloudFrontUpdateDistributionException(
                f"Failed to update distribution: {ex!s}") from ex

    def delete_distribution(self, distribution_id: str) -> None:
        """Delete CloudFront distribution."""
        try:
            current = self.client.get_distribution(Id=distribution_id)
            etag = current["ETag"]

            if current["Distribution"]["Status"] != "Deployed":
                msg = "Distribution must be deployed before deletion"
                raise CloudFrontDeleteDistributionException(
                    msg)

            if current["Distribution"]["DistributionConfig"]["Enabled"]:
                # Disable distribution first
                config = current["Distribution"]["DistributionConfig"]
                config["Enabled"] = False
                self.client.update_distribution(
                    Id=distribution_id,
                    DistributionConfig=config,
                    IfMatch=etag,
                )

            self.client.delete_distribution(
                Id=distribution_id,
                IfMatch=etag,
            )
        except Exception as ex:
            logger.exception(f"Failed to delete distribution: {ex!s}")
            raise CloudFrontDeleteDistributionException(
                f"Failed to delete distribution: {ex!s}") from ex

    def invalidate_cache(
        self,
        distribution_id: str,
        paths: list[str],
    ) -> str:
        """Create cache invalidation."""
        try:
            response = self.client.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={
                    "Paths": {
                        "Quantity": len(paths),
                        "Items": paths,
                    },
                    "CallerReference": str(uuid.uuid4()),
                },
            )
            return response["Invalidation"]["Id"]
        except Exception as ex:
            logger.exception(f"Failed to create invalidation: {ex!s}")
            raise CloudFrontCreateInvalidationException(
                f"Failed to create invalidation: {ex!s}") from ex

    def create_origin_access_control(
        self,
        bucket_name: str,
    ) -> str:
        """Create Origin Access Control for S3 bucket.

        Args:
            bucket_name: S3 bucket name

        Returns:
            str: Origin Access Control ID

        Raises:
            Exception: If creation fails

        """
        try:
            response = self.client.create_origin_access_control(
                OriginAccessControlConfig={
                    "Name": f"OAC-{bucket_name}",
                    "Description": f"OAC for {bucket_name}",
                    "SigningProtocol": "sigv4",
                    "SigningBehavior": "always",
                    "OriginAccessControlOriginType": "s3",
                },
            )
            return response["OriginAccessControl"]["Id"]
        except Exception as ex:
            logger.exception("Failed to create Origin Access Control")
            raise CloudFrontCreateOriginAccessControlException(
                f"Failed to create Origin Access Control: {ex!s}") from ex

    def delete_origin_access_control(self, oac_id: str) -> None:
        """Delete Origin Access Control.

        Args:
            oac_id: Origin Access Control ID

        Raises:
            Exception: If deletion fails

        """
        try:
            self.client.delete_origin_access_control(Id=oac_id)
        except Exception as ex:
            logger.exception("Failed to delete Origin Access Control")
            raise CloudFrontDeleteOriginAccessControlException(
                f"Failed to delete Origin Access Control: {ex!s}") from ex
