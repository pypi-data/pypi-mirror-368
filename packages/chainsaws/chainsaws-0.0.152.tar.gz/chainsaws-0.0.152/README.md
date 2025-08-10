# Chainsaws

Chain your backend with simple AWS services

## Installation

### Basic Installation

```bash
pip install chainsaws
```

### Optional Features

Chainsaws provides optional features that can be installed based on your needs:

#### ElastiCache Support

Install with Redis, Memcached, and ValKey client support:

```bash
pip install chainsaws[elasticache]
```

#### Redshift Support

Install with Redshift database support:

```bash
pip install chainsaws[redshift]
```

#### All Features

Install all optional features:

```bash
pip install chainsaws[all]
```

## Features

Chainsaws provides high-level Python APIs for various AWS services:

- Core Services (included in basic installation)

  - IAM & STS
  - S3
  - DynamoDB
  - SNS & SQS
  - Lambda
  - CloudWatch
  - API Gateway
  - CloudFront
  - EventBridge

- Optional Services
  - ElastiCache (Redis, Memcached, ValKey) [requires `elasticache` extra]
  - Redshift [requires `redshift` extra]

Each service is designed to be simple to use while providing type safety and comprehensive error handling.
