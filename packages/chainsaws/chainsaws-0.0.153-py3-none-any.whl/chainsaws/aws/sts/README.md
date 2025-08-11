# AWS STS Wrapper

A high-level Python wrapper for AWS Security Token Service (STS) that simplifies handling temporary credentials and role assumptions. This wrapper provides an intuitive interface for common STS operations while implementing AWS security best practices.

## Features

### Role Management

- Assume IAM roles with customizable session duration
- Support for external IDs and session tags
- Custom IAM policy attachments for assumed roles

### Identity Operations

- Get caller identity information
- Federation token management
- Session credential handling

### Security

- Secure credential management
- Support for role assumption chains
- Session tag support for enhanced security

## Installation

```bash
pip install chainsaws
```

## Usage Examples

### Assume an IAM Role

```python
from chainsaws.aws.sts import STSAPI

sts = STSAPI()

# Simple role assumption
credentials = sts.assume_role(
    role_arn="arn:aws:iam::123456789012:role/MyRole",
    role_session_name="MySession"
)

# Advanced role assumption with custom duration and external ID
credentials = sts.assume_role(
    role_arn="arn:aws:iam::123456789012:role/MyRole",
    role_session_name="MySession",
    duration_seconds=3600,
    external_id="UniqueId123",
    tags={"Environment": "Production"}
)
```

### Get Caller Identity

```python
# Get information about the current IAM user/role
identity = sts.get_caller_identity()
print(f"Account: {identity.account}")
print(f"ARN: {identity.arn}")
print(f"UserID: {identity.user_id}")
```

### Get Federation Token

```python
# Get temporary credentials for federated users
fed_credentials = sts.get_federation_token(
    name="FederatedUser",
    duration_seconds=43200,  # 12 hours
    tags={"Department": "Engineering"}
)
```

## Configuration

```python
from chainsaws.aws.sts import STSAPI, STSAPIConfig
from chainsaws.aws.shared.config import AWSCredentials

config = STSAPIConfig(
    credentials=AWSCredentials(
        aws_access_key_id="YOUR_ACCESS_KEY",
        aws_secret_access_key="YOUR_SECRET_KEY",
        aws_region="us-east-1"
    )
)

sts = STSAPI(config)
```

## Features and Benefits

1. **Simple Interface**: Clean, intuitive API for STS operations
2. **Type Safety**: Full type hints and dataclass validation
3. **Error Handling**: Comprehensive error handling and logging
4. **Security**: Implements AWS security best practices
5. **Flexibility**: Support for all major STS features

## Common Use Cases

1. **Cross-Account Access**: Assume roles in different AWS accounts
2. **Temporary Credentials**: Generate short-lived credentials for applications
3. **Federation**: Create temporary credentials for external users
4. **Identity Verification**: Verify current IAM identity
5. **Enhanced Security**: Use external IDs and session tags
