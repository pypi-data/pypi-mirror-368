# ElastiCache API

A high-level Python API for AWS ElastiCache, supporting Redis, Memcached, and ValKey engines. Manage both provisioned instances and serverless caches with ease.

## Key Features

### Cluster Management

- Create/modify/delete provisioned clusters
- Create/modify/delete serverless caches
- Monitor cluster status
- Backup and restore
- Replication group management

### Parameter Group Management

- Create/modify/delete parameter groups
- Set and reset parameter values
- Monitor parameter group status

### Events and Monitoring

- Event subscription management
- Performance metrics collection
- CloudWatch integration

### Security and Networking

- Security group management
- Subnet group management
- Encryption settings (in-transit/at-rest)
- IAM integration

## Installation

```bash
pip install chainsaws
```

## Quick Start

### Initialize Serverless Cache

```python
from chainsaws.aws.elasticache import ElastiCacheAPI

api = ElastiCacheAPI()

# Creates cache if it doesn't exist, returns existing cache status if it does
status = api.init_serverless_cache(
    cache_name="my-cache",
    description="My Redis cache",
    major_engine_version="7.0",
    daily_backup_window="04:00-05:00",
    backup_retention_period=7,
    minimum_capacity=1.0,
    maximum_capacity=8.0,
    tags={"Environment": "Production"},
)

print(f"Cache status: {status.status}")
print(f"Endpoint: {status.endpoint}")
```

### Create Redis Cluster (Builder Pattern)

```python
builder = api.cluster_builder("my-redis", "redis")
builder.with_node_type("cache.t3.micro") \
       .with_version("6.x") \
       .with_auth("my-auth-token") \
       .with_encryption() \
       .with_availability() \
       .with_backup(retention_days=7) \
       .with_network("my-subnet-group", ["sg-123456"]) \
       .with_tags({"Environment": "prod"})

cluster = api.create_cluster_from_builder(builder)
```

### Create ValKey Cluster

```python
status = api.create_cluster(
    cluster_id="my-valkey",
    engine="valkey",
    instance_type="cache.r6g.xlarge",
    valkey_config=ValKeyConfig(
        version="1.0",
        auth_token="my-auth-token",
        enhanced_io=True,
        tls_offloading=True,
        enhanced_io_multiplexing=True
    )
)
```

### Parameter Group Management

```python
# Create parameter group
status = api.create_parameter_group(
    group_name="my-redis-params",
    group_family="redis6.x",
    description="Custom Redis parameters",
    parameters={
        "maxmemory-policy": "volatile-lru",
        "timeout": 0
    }
)

# Modify parameters
status = api.modify_parameter_group(
    group_name="my-redis-params",
    parameters={
        "maxmemory-policy": "allkeys-lru",
        "timeout": 300
    }
)
```

### Event Subscription

```python
status = api.create_event_subscription(
    subscription_name="my-events",
    sns_topic_arn="arn:aws:sns:region:account:topic",
    source_type="cache-cluster",
    source_ids=["my-redis"],
    event_categories=["failure", "maintenance"]
)
```

### Performance Metrics Collection

```python
from datetime import datetime, timedelta

end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=1)

response = api.get_metric_data(
    metric_name="CPUUtilization",
    cluster_id="my-redis",
    start_time=start_time,
    end_time=end_time,
    period=300,
    statistics=["Average", "Maximum"]
)
```

## Supported Node Types

### General Purpose

- M7g: `cache.m7g.large` to `cache.m7g.16xlarge`
- M6g: `cache.m6g.large` to `cache.m6g.16xlarge`
- M5: `cache.m5.large` to `cache.m5.24xlarge`
- M4: `cache.m4.large` to `cache.m4.10xlarge`
- T4g: `cache.t4g.micro` to `cache.t4g.medium`
- T3: `cache.t3.micro` to `cache.t3.medium`
- T2: `cache.t2.micro` to `cache.t2.medium`

### Memory Optimized

- R7g: `cache.r7g.large` to `cache.r7g.16xlarge`
- R6g: `cache.r6g.large` to `cache.r6g.16xlarge`
- R5: `cache.r5.large` to `cache.r5.24xlarge`
- R4: `cache.r4.large` to `cache.r4.16xlarge`

### Memory Optimized with Data Tiering

- R6gd: `cache.r6gd.xlarge` to `cache.r6gd.16xlarge`

### Network Optimized

- C7gn: `cache.c7gn.large` to `cache.c7gn.16xlarge`

### Serverless

- Capacity specified in ECU units (0.5 to 100.0)

## Supported Engines

### Redis

- Versions: 7.0, 6.x, 5.0.6
- Features: Replication, Auto-failover, Multi-AZ, Backup/Restore
- Encryption: In-transit and at-rest
- Authentication: Redis AUTH

### Memcached

- Versions: 1.6.17, 1.5.16
- Features: Multi-threading, Auto Discovery
- Parameter group support

### ValKey

- Version: 1.0
- Features: Enhanced I/O, TLS Offloading, Enhanced I/O Multiplexing
- Encryption: In-transit and at-rest
- Authentication: ValKey AUTH

## License

MIT
