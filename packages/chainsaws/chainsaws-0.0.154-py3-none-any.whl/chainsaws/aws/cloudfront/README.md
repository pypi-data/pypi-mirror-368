# AWS CloudFront Wrapper

A high-level Python wrapper for AWS CloudFront that simplifies CDN management operations. This wrapper provides an intuitive interface for common CloudFront operations while handling AWS best practices and security configurations automatically.

## Features

### Distribution Management

- Create S3-backed distributions with Origin Access Control (OAC)
- Create custom origin distributions
- Manage multiple origins and behaviors
- Update existing distributions
- Delete distributions

### Security

- Automatic Origin Access Control (OAC) setup for S3 buckets
- Automatic S3 bucket policy configuration
- WAF integration support
- SSL/TLS certificate management

### Cache Management

- Create cache invalidations
- Invalidate specific paths
- Bulk invalidate all files
- Configure cache behaviors

### Domain Management

- Add custom domains
- Configure alternate domain names (CNAMEs)
- SSL/TLS certificate association

## Installation

```bash
pip install chainsaws
```

## Usage Examples

### Create S3-backed Distribution

```python
from chainsaws.aws.cloudfront import CloudFrontAPI

cloudfront = CloudFrontAPI()

# Create distribution for S3 bucket
distribution = cloudfront.create_s3_distribution(
    bucket_name="my-bucket",
    aliases=["cdn.example.com"],
    certificate_arn="arn:aws:acm:ap-northeast-2:123456789012:certificate/xxx",
    default_root_object="index.html"
)
```

### Create Custom Origin Distribution

```python
from chainsaws.aws.cloudfront import CloudFrontAPI, BehaviorConfig

cloudfront = CloudFrontAPI()

# Define custom cache behavior
api_behavior = BehaviorConfig(
    path_pattern="/api/*",
    target_origin_id="my-api",
    viewer_protocol_policy="https-only",
    allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"],
    cached_methods=["GET", "HEAD", "OPTIONS"]
)

# Create distribution with custom origin
distribution = cloudfront.create_custom_distribution(
    origin_domain="api.example.com",
    origin_id="my-api",
    behaviors=[api_behavior],
    aliases=["cdn.example.com"],
    certificate_arn="arn:aws:acm:ap-northeast-2:123456789012:certificate/xxx"
)
```

### Cache Management

```python
# Invalidate specific paths
invalidation_id = cloudfront.invalidate_cache(
    distribution_id="EDFDVBD6EXAMPLE",
    paths=["/images/*", "/css/main.css"]
)

# Invalidate all files
invalidation_id = cloudfront.invalidate_all_files(
    distribution_id="EDFDVBD6EXAMPLE"
)
```

### Add Custom Domain

```python
distribution = cloudfront.add_custom_domain(
    distribution_id="EDFDVBD6EXAMPLE",
    domain_name="cdn.example.com",
    certificate_arn="arn:aws:acm:ap-northeast-2:123456789012:certificate/xxx"
)
```

### Enable WAF Protection

```python
distribution = cloudfront.enable_waf(
    distribution_id="EDFDVBD6EXAMPLE",
    web_acl_id="arn:aws:wafv2:ap-northeast-2:123456789012:global/webacl/xxx"
)
```

## Configuration

```python
from chainsaws.aws.cloudfront import CloudFrontAPI, CloudFrontAPIConfig
from chainsaws.aws.shared.config import AWSCredentials

config = CloudFrontAPIConfig(
    credentials=AWSCredentials(
        aws_access_key_id="YOUR_ACCESS_KEY",
        aws_secret_access_key="YOUR_SECRET_KEY",
        aws_region="ap-northeast-2"
    )
)

cloudfront = CloudFrontAPI(config)
```
