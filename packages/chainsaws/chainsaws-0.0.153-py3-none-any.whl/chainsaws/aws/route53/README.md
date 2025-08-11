# Route53 API

High-level AWS Route53 client providing simplified interface for DNS operations.

## Features

- DNS Record Management (A, AAAA, CNAME records)
- AWS Service Alias Records
  - CloudFront
  - S3 Website
  - API Gateway
  - AppSync
  - Elastic Load Balancers (ALB, NLB, CLB)
  - Elastic Beanstalk
- Advanced Routing Policies
  - Weighted Routing
  - Latency-based Routing
- Health Checks
  - HTTP/HTTPS/TCP checks
  - Custom failure thresholds
  - Status monitoring

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.aws.route53 import Route53API

# Initialize client
route53 = Route53API("example.com")

# Create standard A record
route53.create_record(
    name="api.example.com.",
    type="A",
    ttl=300,
    records=["192.0.2.1"]
)

# Create CloudFront alias
route53.create_cloudfront_alias(
    name="www.example.com.",
    distribution_domain="d123456789.cloudfront.net"
)
```

## AWS Service Aliases

Create alias records pointing to various AWS services:

```python
# CloudFront Distribution
route53.create_cloudfront_alias(
    name="www.example.com.",
    distribution_domain="d123456789.cloudfront.net"
)

# S3 Static Website
route53.create_s3_website_alias(
    name="static.example.com.",
    bucket_website_domain="my-bucket.s3-website.ap-northeast-2.amazonaws.com",
    region="ap-northeast-2"
)

# API Gateway
route53.create_api_gateway_alias(
    name="api.example.com.",
    api_domain="d-abcdef123.execute-api.ap-northeast-2.amazonaws.com",
    region="ap-northeast-2"
)

# AppSync API
route53.create_appsync_alias(
    name="graphql.example.com.",
    appsync_domain="abcdef123.appsync-api.ap-northeast-2.amazonaws.com",
    region="ap-northeast-2"
)

# Elastic Beanstalk Environment
route53.create_elasticbeanstalk_alias(
    name="app.example.com.",
    eb_domain="my-env.ap-northeast-2.elasticbeanstalk.com",
    region="ap-northeast-2"
)

# Classic Load Balancer (CLB)
# Application Load Balancer (ALB)
route53.create_elb_alias(
    name="app.example.com.",
    elb_domain="my-clb.ap-northeast-2.elb.amazonaws.com",
    region="ap-northeast-2"
)

# Network Load Balancer (NLB)
route53.create_nlb_alias(
    name="app.example.com.",
    nlb_domain="my-nlb.ap-northeast-2.elb.amazonaws.com",
    region="ap-northeast-2"
)
```

## Advanced Routing

### Weighted Routing

```python
route53.create_weighted_records(
    name="api.example.com.",
    type="A",
    weighted_records=[
        (["192.0.2.1"], 70, "primary"),
        (["192.0.2.2"], 30, "secondary")
    ]
)
```

### Latency-based Routing

```python
route53.create_latency_records(
    name="api.example.com.",
    type="A",
    latency_records=[
        (["192.0.2.1"], "ap-northeast-2", "usw2"),
        (["192.0.2.2"], "eu-west-1", "euw1")
    ]
)
```

## Health Checks

```python
# Create health check
health_check = route53.create_health_check(
    HealthCheckConfig(
        ip_address="192.0.2.1",
        port=443,
        type="HTTPS",
        resource_path="/health",
        request_interval=30,
        failure_threshold=3
    )
)

# Get health check status
status = route53.get_health_check_status(health_check.id)
```

## Configuration

Custom configuration can be provided:

```python
from chainsaws.aws.route53 import Route53API, Route53APIConfig

config = Route53APIConfig(
    credentials={
        "aws_access_key_id": "YOUR_ACCESS_KEY",
        "aws_secret_access_key": "YOUR_SECRET_KEY",
        "region_name": "ap-northeast-2"
    }
)

route53 = Route53API("example.com", config=config)
```

## Supported Record Types

- A (IPv4 address)
- AAAA (IPv6 address)
- CNAME (Canonical name)
- Alias (AWS services)

## Error Handling

The API uses proper error handling and logging:

```python
import logging
logging.basicConfig(level=logging.INFO)

try:
    route53.create_record(...)
except Exception as e:
    print(f"Failed to create record: {str(e)}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
