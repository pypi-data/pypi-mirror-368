# AWS Systems Manager (SSM) Wrapper

A comprehensive Python wrapper for AWS Systems Manager that simplifies management operations and provides intuitive access to SSM features. This wrapper implements AWS best practices and provides a clean, type-safe interface for all major SSM functionalities.

## Features

### Parameter Store

- Secure parameter management
- Hierarchical parameter organization
- Automatic encryption handling
- Version tracking

### Session Manager

- Interactive shell sessions
- Port forwarding
- Session logging
- Access control

### Patch Management

- Patch baseline creation
- Compliance reporting
- Automated patching
- Cross-platform support

### State Manager

- Configuration management
- Association handling
- Scheduled state application
- Compliance tracking

### Maintenance Windows

- Scheduled operations
- Task management
- Resource targeting
- Execution control

### Inventory Management

- Custom inventory collection
- Resource tracking
- Schema management
- Inventory summarization

### Run Command

- Remote command execution
- Multi-instance targeting
- Output capture
- Status tracking

## Installation

```bash
pip install chainsaws
```

## Usage Examples

### Parameter Store Operations

```python
from chainsaws.aws.ssm import SSMAPI

ssm = SSMAPI()

# Store a secure parameter
ssm.put_parameter(
    name="/prod/db/password",
    value="secret123",
    param_type="SecureString"
)

# Retrieve a parameter
param = ssm.get_parameter("/prod/db/password")
print(f"Value: {param.value}")
```

### Session Management

```python
# Start an interactive session
session = ssm.start_session(
    instance_id="i-1234567890abcdef0",
    reason="Emergency maintenance"
)

# Terminate session
ssm.terminate_session(session.session_id)
```

### Patch Management

```python
# Create patch baseline
baseline_id = ssm.create_patch_baseline(
    name="Production-Baseline",
    operating_system="AMAZON_LINUX_2",
    approval_rules={
        "PatchRules": [{
            "PatchFilterGroup": {
                "PatchFilters": [{
                    "Key": "CLASSIFICATION",
                    "Values": ["SecurityUpdates"]
                }]
            },
            "ApproveAfterDays": 7
        }]
    }
)

# Check patch status
status = ssm.get_patch_status("i-1234567890abcdef0")
print(f"Missing critical patches: {status.critical_missing}")
```

### Maintenance Windows

```python
# Create maintenance window
window = ssm.create_maintenance_window(
    name="WeeklyPatching",
    schedule="cron(0 0 ? * SUN *)",
    duration=4,
    cutoff=1
)

# Add maintenance task
task = ssm.add_maintenance_task(
    window_id=window.window_id,
    task_type="RUN_COMMAND",
    targets=[{"Key": "tag:Environment", "Values": ["Production"]}],
    task_arn="AWS-RunPatchBaseline",
    service_role_arn="arn:aws:iam::123456789012:role/MaintenanceWindowRole"
)
```

### Inventory Management

```python
# Collect custom inventory
ssm.collect_inventory(
    instance_id="i-1234567890abcdef0",
    inventory_type="Custom:Applications",
    content={
        "ApplicationName": "MyApp",
        "Version": "1.0.0",
        "Status": "Running"
    }
)

# Get inventory summary
summary = ssm.summarize_inventory("AWS:Application")
print(f"Total applications: {summary['TotalItems']}")
```

## Configuration

```python
from chainsaws.aws.ssm import SSMAPI, SSMAPIConfig
from chainsaws.aws.shared.config import AWSCredentials

config = SSMAPIConfig(
    credentials=AWSCredentials(
        aws_access_key_id="YOUR_ACCESS_KEY",
        aws_secret_access_key="YOUR_SECRET_KEY",
        aws_region="us-east-1"
    )
)

ssm = SSMAPI(config)
```

## Features and Benefits

1. **Type Safety**: Full type hints and dataclass validation
2. **Error Handling**: Comprehensive error handling and logging
3. **Best Practices**: Implements AWS security best practices
4. **Documentation**: Detailed docstrings and examples
5. **Flexibility**: Support for all major SSM features
6. **Clean API**: Intuitive interface design
