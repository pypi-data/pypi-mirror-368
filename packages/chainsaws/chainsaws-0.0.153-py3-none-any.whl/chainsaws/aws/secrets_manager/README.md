# AWS Secrets Manager Client

A high-level Python client for AWS Secrets Manager that provides secure and efficient secrets management with additional features like batch operations, backup/restore, and filtering.

## Features

- **Complete Secrets Management**

  - Create, read, update, and delete secrets
  - Support for string, binary, and JSON secret values
  - Version control and staging
  - Automatic secret rotation setup

- **Advanced Operations**

  - Parallel batch operations
  - Backup and restore functionality
  - Filtered secret listing
  - Tag management
  - Change detection

- **Performance & Security**
  - Thread-based parallel processing
  - Automatic retry handling
  - AWS KMS integration for encryption
  - Comprehensive error handling
  - AWS credentials management

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.aws.secrets_manager import SecretsManagerAPI

# Initialize the client
secrets = SecretsManagerAPI()

# Create a secret
secret = secrets.create_secret(
    name="my-app/dev/api-key",
    secret_value={"api_key": "secret123"},
    description="API Key for Dev Environment",
    tags={"Environment": "dev"}
)

# Get a secret
value = secrets.get_secret("my-app/dev/api-key")

# Update a secret
secrets.update_secret(
    secret_id="my-app/dev/api-key",
    secret_value={"api_key": "new-secret"}
)

# Delete a secret
secrets.delete_secret(
    secret_id="my-app/dev/api-key",
    force=False,  # Optional recovery window
    recovery_window_days=7
)
```

## Advanced Usage

### Batch Operations

```python
from chainsaws.aws.secrets_manager import BatchSecretOperation

# Delete multiple secrets in parallel
batch_config = BatchSecretOperation(
    secret_ids=["secret1", "secret2", "secret3"],
    operation="delete",
    params={"force": True}
)

results = secrets.batch_operation(batch_config)
print(f"Successful: {results['successful']}")
print(f"Failed: {results['failed']}")
```

### Backup and Restore

```python
from chainsaws.aws.secrets_manager import SecretBackupConfig

# Backup secrets
backup_config = SecretBackupConfig(
    secret_ids=["secret1", "secret2"],
    backup_path="secrets_backup.json"
)

secrets.backup_secrets(backup_config)

# Note: For sensitive data, it's recommended to use AWS KMS for encryption
# or implement your own encryption mechanism before storing the backup

# Restore secrets
restore_results = secrets.restore_secrets(
    backup_path="secrets_backup.json"
)
```

### Filtering Secrets

```python
from chainsaws.aws.secrets_manager import SecretFilterConfig
from datetime import datetime, timedelta

# Filter secrets by criteria
filter_config = SecretFilterConfig(
    name_prefix="my-app/dev/",
    tags={"Environment": "dev"},
    created_after=datetime.now() - timedelta(days=30)
)

for secret in secrets.filter_secrets(filter_config):
    print(f"Found secret: {secret['Name']}")
```

### Secret Rotation

```python
# Setup automatic rotation
secrets.setup_rotation(
    secret_id="my-app/db-password",
    lambda_arn="arn:aws:lambda:region:account:function:rotation-function",
    rotation_days=30
)
```

## Configuration

```python
from chainsaws.aws.secrets_manager import SecretsManagerAPIConfig

config = SecretsManagerAPIConfig(
    region="us-west-2",
    max_retries=5,
    timeout=30,
    retry_modes={
        "max_attempts": 3,
        "mode": "adaptive"
    }
)

secrets = SecretsManagerAPI(config)
```

## Error Handling

The client provides comprehensive error handling and logging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    secret = secrets.get_secret("non-existent-secret")
except Exception as e:
    print(f"Error: {str(e)}")
```
