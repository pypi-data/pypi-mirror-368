# AWS Lambda Handler Utilities

A collection of utilities for AWS Lambda handlers that provides structured request handling, error management, and response formatting.

## Features

- **Simplified Lambda Handler Development**

  - Automatic request parsing and validation
  - Standardized response formatting
  - Comprehensive error handling
  - Built-in logging and monitoring support

- **Type Safety**

  - Full type hints support
  - Dataclass validation
  - IDE-friendly development

- **Error Management**
  - Structured error responses
  - External error notification support
  - Configurable error tracking
  - Traceback management

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.utils.handler_utils import aws_lambda_handler, get_body

@aws_lambda_handler()
def handler(event, context):
    # Automatically parses and validates the request body
    body = get_body(event)

    return {
        "message": "Success",
        "data": body
    }
```

## Core Components

### Event Model (LambdaEvent)

The `LambdaEvent` class provides a structured way to handle AWS Lambda event inputs:

```python
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class LambdaEvent:
    body: Optional[str]                    # Request body (raw string)
    headers: Dict[str, str]                # HTTP headers
    requestContext: RequestContext         # Request context with identity info

    # Additional fields are handled by __init__
    def __init__(self, **kwargs):
        self.body = kwargs.get('body')
        self.headers = kwargs.get('headers', {})
        self.requestContext = kwargs.get('requestContext')
        self._extra = {k: v for k, v in kwargs.items()
                      if k not in ['body', 'headers', 'requestContext']}
```

Example usage:

```python
@aws_lambda_handler()
def handler(event, context):
    # Parse event
    event_data = LambdaEvent(**event)

    # Access event data
    body = event_data.get_json_body()      # Parsed JSON body
    headers = event_data.headers           # Request headers
    source_ip = event_data.requestContext.get_source_ip()  # Client IP

    return {"data": process_request(body)}
```

### Response Model (LambdaResponse)

The `LambdaResponse` class handles response formatting with proper headers and structure:

```python
from dataclasses import dataclass

@dataclass
class LambdaResponse:
    statusCode: int = 200                  # HTTP status code
    headers: ResponseHeaders               # Response headers with CORS
    body: str                             # Response body (JSON string)
    isBase64Encoded: bool = False         # Base64 encoding flag
```

Response creation:

```python
# Automatic creation via decorator
@aws_lambda_handler()
def handler(event, context):
    return {
        "data": "success",                 # Will be automatically formatted
        "meta": {"count": 42}
    }

    # Manual creation
    response = LambdaResponse.create(
        body={"message": "success"},
        content_type='application/json',
        status_code=200,
        charset='UTF-8'
    )
```

### WebSocket Support

The library provides comprehensive support for WebSocket APIs through API Gateway, including connection management and event handling.

#### Connection Management

The `APIGatewayWSConnectionManager` class provides connection state management using DynamoDB:

```python
from chainsaws.aws.lambda_client.event_handler.websocket_connection import APIGatewayWSConnectionManager
from chainsaws.aws.lambda_client.event_handler.websocket import WebSocketResolver

# Initialize connection manager
connection_manager = APIGatewayWSConnectionManager(
    table_name='websocket-connections',  # DynamoDB table name
    partition='websocket_status',        # Partition for connection records
    connection_ttl=7200                  # Connection TTL in seconds (2 hours)
)

# Initialize resolver
resolver = WebSocketResolver()
```

##### Connection Lifecycle

1. **Table Initialization**:

```python
# Initialize DynamoDB table (run once during deployment)
async def init_resources():
    await connection_manager.init_table()
```

2. **Connection Handling**:

```python
@resolver.on_connect()
async def handle_connect(event, context, connection_id):
    # Store client information
    client_data = {
        "user_agent": event.get("headers", {}).get("User-Agent"),
        "source_ip": event["requestContext"]["identity"]["sourceIp"]
    }
    return await connection_manager.connect(connection_id, client_data)

@resolver.on_disconnect()
async def handle_disconnect(event, context, connection_id):
    return await connection_manager.disconnect(connection_id)
```

3. **Connection Tracking**:

```python
@resolver.middleware
class ConnectionTrackingMiddleware(Middleware):
    async def __call__(self, event, context, next_handler):
        connection_id = event["requestContext"]["connectionId"]
        route_key = event["requestContext"]["routeKey"]

        # Skip for $connect events
        if route_key != "$connect":
            await connection_manager.update_last_seen(connection_id)

        return await next_handler(event, context)
```

4. **Message Handling with Connection State**:

```python
@resolver.on_message("message")
async def handle_message(event, context, connection_id, body):
    # Verify connection exists
    connection = await connection_manager.get_connection(connection_id)
    if not connection:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid connection"})
        }

    # Access connection metadata
    client_info = connection.client_data
    print(f"Message from {client_info['source_ip']}")

    return {"message": "Processed"}
```

##### DynamoDB Schema

The connection manager uses the following DynamoDB structure:

- **Table Name**: (configurable)
- **Partition Key**: `connection_id` (String)
- **Sort Key**: `_crt` (Number, creation timestamp)
- **TTL Attribute**: `_ttl`

Additional attributes:

- `status`: Connection status
- `connected_at`: Connection timestamp
- `last_seen`: Last activity timestamp
- `client_data`: Client metadata (optional)

##### Error Handling

The connection manager provides comprehensive error handling:

```python
try:
    await connection_manager.connect(connection_id)
except DynamoDBError as e:
    logger.error(f"Connection failed: {e}")
    return {
        "statusCode": 500,
        "body": json.dumps({"message": "Internal error"})
    }
```

##### Configuration

Required IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/websocket-connections"
    }
  ]
}
```

Environment variables:

```bash
DYNAMODB_TABLE=websocket-connections  # DynamoDB table name
```

##### Best Practices

1. **Connection Initialization**:

   - Initialize the table before first use
   - Use meaningful partition names
   - Set appropriate TTL values

2. **Error Handling**:

   - Always handle DynamoDBError exceptions
   - Log errors for debugging
   - Return appropriate error responses

3. **Performance**:

   - Use the connection tracking middleware
   - Implement connection cleanup
   - Monitor table capacity

4. **Security**:
   - Validate client data
   - Implement authentication
   - Use secure WebSocket protocols

##### Complete Example

```python
import os
from chainsaws.aws.lambda_client.event_handler.websocket import WebSocketResolver
from chainsaws.aws.lambda_client.event_handler.websocket_connection import APIGatewayWSConnectionManager

# Initialize managers
connection_manager = APIGatewayWSConnectionManager(
    table_name=os.environ['DYNAMODB_TABLE'],
    partition='websocket_status'
)
resolver = WebSocketResolver()

# Connection tracking
@resolver.middleware
class ConnectionTrackingMiddleware(Middleware):
    async def __call__(self, event, context, next_handler):
        if event["requestContext"]["routeKey"] != "$connect":
            await connection_manager.update_last_seen(
                event["requestContext"]["connectionId"]
            )
        return await next_handler(event, context)

# Connection handlers
@resolver.on_connect()
async def handle_connect(event, context, connection_id):
    return await connection_manager.connect(
        connection_id,
        client_data={"ip": event["requestContext"]["identity"]["sourceIp"]}
    )

@resolver.on_disconnect()
async def handle_disconnect(event, context, connection_id):
    return await connection_manager.disconnect(connection_id)

# Message handlers
@resolver.on_message("message")
async def handle_message(event, context, connection_id, body):
    connection = await connection_manager.get_connection(connection_id)
    if not connection:
        return {"statusCode": 400, "message": "Invalid connection"}

    return {
        "message": "Message received",
        "client": connection.client_data
    }

# Lambda handler
def handler(event, context):
    return resolver.resolve(event, context)
```

### Utility Functions

```python
from chainsaws.utils.handler_utils import get_body, get_headers, get_source_ip

# Get parsed JSON body
body = get_body(event)                     # Returns Dict[str, Any] or None

# Get request headers
headers = get_headers(event)               # Returns Dict[str, str]

# Get client IP
client_ip = get_source_ip(event)          # Returns str
```

## Response Format

### Successful Response

```json
{
  "statusCode": 200,
  "headers": {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Credentials": true,
    "Content-Type": "application/json; charset=UTF-8"
  },
  "body": {
    "rslt_cd": "S00000",
    "rslt_msg": "Call Success",
    "duration": 0.001,
    "data": {
      "your": "response data"
    }
  },
  "isBase64Encoded": false
}
```

### Error Response

```json
{
  "statusCode": 200,
  "headers": {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Credentials": true,
    "Content-Type": "application/json; charset=UTF-8"
  },
  "body": {
    "rslt_cd": "S99999",
    "rslt_msg": "Error message",
    "duration": 0.002,
    "traceback": "Error traceback..."
  },
  "isBase64Encoded": false
}
```

## Advanced Usage

### Custom Error Handling

```python
from chainsaws.utils.error_utils import AppError

def notify_slack(error_message: str):
    # Your error notification logic
    slack_client.post_message(error_message)

@aws_lambda_handler(error_receiver=notify_slack)
def handler(event, context):
    try:
        # Validate request
        body = get_body(event)
        if not body:
            raise AppError("B00001", "Missing request body")

        # Process request
        result = process_data(body)
        return {"data": result}

    except ValueError as e:
        raise AppError("B00002", str(e))
```

### Type Hints Support

```python
from typing import Dict, Any
from chainsaws.utils.handler_utils import LambdaEvent, LambdaResponse

def process_event(event_data: LambdaEvent) -> Dict[str, Any]:
    body = event_data.get_json_body()
    return {"processed": body}

def handler(event: Dict[str, Any], context: Any) -> LambdaResponse:
    event_data = LambdaEvent(**event)
    result = process_event(event_data)
    return {"data": result}
```

## Best Practices

1. **Use Type Validation**

   ```python
   from dataclasses import dataclass

   @dataclass
   class UserRequest:
       name: str
       age: int

   @aws_lambda_handler()
   def handler(event, context):
       body = get_body(event)
       user_data = UserRequest(**body)
       return {"user": user_data.to_dict()}
   ```

2. **Handle Different Content Types**

   ```python
   @aws_lambda_handler(content_type='application/xml')
   def handler(event, context):
       return {"data": "<root>XML response</root>"}
   ```

3. **Custom Error Handling**

   ```python
   @aws_lambda_handler(
       error_receiver=notify_slack,
       ignore_app_errors=[NOT_FOUND_ERROR]
   )
   def handler(event, context):
       try:
           return process_request(get_body(event))
       except ResourceNotFoundError:
           raise AppError("B00404", "Resource not found")
   ```

4. **Request Context Usage**
   ```python
   @aws_lambda_handler()
   def handler(event, context):
       event_data = LambdaEvent(**event)
       return {
           "client_ip": event_data.requestContext.get_source_ip(),
           "request_id": event_data.requestContext.request_id
       }
   ```

## API Documentation

### OpenAPI (Swagger) Documentation Support

`chainsaws` provides automatic API documentation for Lambda functions. It generates OpenAPI specifications from type information at build time and loads them from S3 at runtime.

### Quick Start

```python
from dataclasses import dataclass
from typing import List
from chainsaws.aws.lambda_client import (
    APIGatewayHttpResolver,
    response_model,
    response
)

# 1. Define Response Models
@response_model
@dataclass
class User:
    id: int
    name: str
    email: str

@response_model
@dataclass
class UserList:
    users: List[User]
    total: int

# 2. Configure API Resolver
resolver = APIGatewayHttpResolver(
    openapi_config={
        "title": "User API",
        "version": "1.0.0",
        "description": "API for user management",
        "servers": [
            {"url": "https://api.example.com/prod"}
        ],
        "tags": [
            {"name": "users", "description": "User management"}
        ],
        # S3 Configuration
        "s3_bucket": "my-schema-bucket",
        "s3_key": "openapi.json"
    }
)

# 3. Define Endpoints
@resolver.get(
    "/users/{user_id}",
    response_model=User,
    tags=["users"],
    summary="Get User",
    description="Retrieve user information by ID"
)
def get_user(event, context, path_parameters):
    user_id = path_parameters["user_id"]
    return User(id=user_id, name="John Doe", email="john@example.com")

@resolver.get(
    "/users",
    response_model=UserList,
    tags=["users"],
    summary="List Users",
    description="Retrieve all users"
)
def list_users(event, context):
    users = [
        User(id=1, name="John Doe", email="john@example.com"),
        User(id=2, name="Jane Doe", email="jane@example.com")
    ]
    return UserList(users=users, total=len(users))

# 4. Lambda Handler
def handler(event, context):
    return resolver.resolve(event, context)
```

### Documentation Access

API Gateway automatically creates the following endpoints:

- `/docs`: View API documentation using ReDoc UI
- `/openapi.json`: Access OpenAPI specification in JSON format

### Large Schema Handling

For large APIs with extensive schemas, `chainsaws` uses memory-efficient streaming:

1. **Streaming Upload**:

   ```python
   # Upload schemas to S3 in 5MB chunks
   ResponseSchemaRegistry.save_schemas()  # Called automatically at build time
   ```

2. **Streaming Download**:
   ```python
   # Load schemas from S3 in 1MB chunks
   schemas = ResponseSchemaRegistry.load_schemas()  # Called automatically at runtime
   ```

### Advanced Usage

#### 1. Custom Response Description

```python
@resolver.post(
    "/users",
    response_model=User,
    status_code=201,
    response_description="Created user information",
    summary="Create User",
    description="Create a new user"
)
def create_user(event, context, body):
    return User(**body)
```

#### 2. Response Decorator

```python
@response(status_code=201, description="Created user information")
@resolver.post("/users")
def create_user(event, context, body) -> User:
    return User(**body)
```

#### 3. Tag Grouping

```python
# Group APIs using Router
router = Router(prefix="/users", tags=["users"])

@router.get("/{user_id}")
def get_user(event, context, path_parameters):
    ...

# Add router to main resolver
resolver.include_router(router)
```

### Configuration

#### 1. Environment Variables

```bash
# Build time detection
export CHAINSAWS_BUILD_TIME=1  # Set when generating schemas

# S3 Configuration
export CHAINSAWS_SCHEMA_S3_BUCKET=my-schema-bucket
export CHAINSAWS_SCHEMA_S3_KEY=api-docs.json
```

#### 2. IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::my-schema-bucket/*"
    }
  ]
}
```

### Best Practices

1. **Schema Management**:

   - Define response models using dataclasses for type safety
   - Add type hints to all fields
   - Support complex nested models

2. **Performance Optimization**:

   - Use streaming for large schemas
   - Generate schemas only at build time
   - Use cached schemas at runtime

3. **Documentation**:

   - Add summary and description to all endpoints
   - Group APIs using tags
   - Specify response models and status codes

4. **Security**:
   - Configure S3 bucket policies
   - Manage CORS settings
   - Document authentication/authorization

### Troubleshooting

1. **Schema Generation Issues**:

   - Verify `CHAINSAWS_BUILD_TIME=1` environment variable
   - Check dataclass and type hint usage
   - Confirm `response_model` decorator application

2. **Memory Issues**:

   - Use S3 streaming upload/download
   - Adjust chunk sizes (default: 5MB upload, 1MB download)
   - Review Lambda memory configuration

3. **Documentation Access Issues**:
   - Check API Gateway configuration
   - Verify S3 bucket permissions
   - Review CORS settings

### Dependency Injection

`chainsaws` provides a FastAPI-style dependency injection system optimized for Lambda environments:

```python
from chainsaws.aws.lambda_client.event_handler import APIGatewayHttpResolver
from chainsaws.aws.lambda_client.event_handler.dependency_injection import Depends, container

# Define dependencies
class Database:
    def __init__(self):
        # Connection is reused across Lambda context
        self.connection = create_connection()
        
class UserRepository:
    def __init__(self, db: Database = Depends(Database)):
        self.db = db
        
class UserService:
    def __init__(self, repo: UserRepository = Depends(UserRepository)):
        self.repo = repo

# Register dependencies
container.register(Database, Database)

# Create resolver
resolver = APIGatewayHttpResolver()

@resolver.get("/users/{user_id}")
async def get_user(
    event: dict,
    context: Any,
    user_id: str,
    service: UserService = Depends()  # Automatic injection
):
    return await service.get_user(user_id)

def handler(event: dict, context: Any) -> dict:
    return resolver.resolve(event, context)
```

#### Features

1. **Lambda Context Optimization**:
   - Singleton instances are reused across Lambda execution contexts
   - Resource-heavy initializations happen only once
   - Efficient connection and resource management

2. **FastAPI-style Dependency System**:
   - Similar to FastAPI's `Depends`
   - Automatic dependency resolution
   - Support for nested dependencies
   - Request-scoped dependency caching

3. **Testing Support**:
   ```python
   # In tests
   mock_service = MockUserService()
   container.register_instance(UserService, mock_service)
   ```

4. **Performance Benefits**:
   - Cold start optimization
   - Connection pooling
   - Resource reuse

#### Best Practices

1. **Singleton Management**:
   ```python
   # Register singleton instance
   container.register_instance(Config, Config())
   
   # Or register factory for lazy initialization
   container.register(Database, lambda: Database(config))
   ```

2. **Request Scoping**:
   ```python
   class RequestContext:
       def __init__(self):
           self.request_id = str(uuid.uuid4())
   
   @resolver.get("/data")
   async def get_data(
       context: RequestContext = Depends(RequestContext)  # New instance per request
   ):
       return {"request_id": context.request_id}
   ```

3. **Resource Management**:
   ```python
   class DatabaseConnection:
       def __init__(self):
           # Expensive connection created once and reused
           self.pool = create_connection_pool()
   
   # Register as singleton
   container.register_instance(DatabaseConnection, DatabaseConnection())
   ```

4. **Testing**:
   ```python
   def test_handler():
       # Register test dependencies
       container.register_instance(Database, MockDatabase())
       container.register_instance(UserService, MockUserService())
       
       response = handler(test_event, test_context)
       assert response['statusCode'] == 200
   ```
