# Lambda Client

A module for easily invoking and managing AWS Lambda functions. Provides event handling, response formatting, error handling, and more.

## Key Features

- Lambda function invocation and management
- API Gateway event handling (REST API v1, HTTP API v2)
- Response formatting
- Error handling
- CORS configuration
- Middleware support

## Usage Examples

### Basic Handler Usage

```python
from chainsaws.aws.lambda_client.event_handler import aws_lambda_handler
from chainsaws.aws.lambda_client.event_handler.handler_models import LambdaEvent

@aws_lambda_handler()
def handler(event, context):
    # Parse event
    event_data = LambdaEvent(**event)

    # Get JSON body
    body = event_data.get_json_body()

    # Return response
    return {
        "data": {
            "message": "Hello, World!"
        }
    }
```

### API Gateway Event Handling

```python
from chainsaws.aws.lambda_client.event_handler import aws_lambda_handler
from chainsaws.aws.lambda_client.event_handler.handler_models import LambdaEvent

@aws_lambda_handler()
def handler(event, context):
    # Check if event is from API Gateway
    if LambdaEvent.is_api_gateway_event(event):
        event_data = LambdaEvent(**event)
        source_ip = event_data.request_context.get_source_ip()
        return {
            "data": {
                "source_ip": source_ip,
                "message": "Request from API Gateway"
            }
        }

    return {
        "data": {
            "message": "Direct Lambda invocation"
        }
    }
```

### Error Handling

```python
from chainsaws.aws.lambda_client.event_handler import HTTPException, AppError, NotFoundError
from chainsaws.aws.lambda_client.event_handler import aws_lambda_handler

def notify_error(error_message: str):
    # Error notification logic
    print(f"Error occurred: {error_message}")

@aws_lambda_handler(
    error_receiver=notify_error,
    use_traceback=True
)
def handler(event, context):
    try:
        # Business logic
        user = get_user(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        result = process_data(user)
        return {"data": result}
        
    except ValueError as e:
        # Convert to AppError with custom code
        raise AppError("E001", str(e))
        
    except HTTPException as e:
        # HTTPException and its subclasses are automatically handled
        raise

### Error Response Format

#### HTTP Exception Response
```json
{
    "detail": "User not found",
    "duration": 0.123,
    "error": {
        "type": "NotFoundError",
        "status_code": 404,
        "headers": null
    }
}
```

#### Application Error Response
```json
{
    "detail": "Invalid input data",
    "duration": 0.123,
    "error": {
        "type": "AppError",
        "status_code": 400,
        "headers": null,
        "code": "E001"
    }
}
```

#### AWS Service Error Response
```json
{
    "detail": "Error accessing DynamoDB",
    "duration": 0.234,
    "service_error": {
        "code": "ResourceNotFoundException",
        "message": "Requested resource not found",
        "request_id": "ABCDEF123456",
        "http_status": 404
    },
    "traceback": "..."
}
```

## Handler Configuration Options

```python
@aws_lambda_handler(
    error_receiver=notify_error,        # Function to call when error occurs
    content_type="application/json",    # Response Content-Type
    use_traceback=True,                # Include stack trace in error responses
    ignore_app_errors=["E001", "E002"] # List of error codes to ignore for notifications
)
def handler(event, context):
    pass
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
       event_data = LambdaEvent.from_dict(event)
       body = event_data.get_json_body()
       user = UserRequest(**body)
       return {"data": user.to_dict()}
   ```

2. **Structured Error Handling**

   ```python
   from chainsaws import AppError

   @aws_lambda_handler()
   def handler(event, context):
       try:
           user = get_user(user_id)
           if not user:
               raise AppErro("E000", "User not found")
               
           if not validate_user(user):
               raise AppError("E001", "Invalid user data")
               
           return process_request(user)
           
       except TimeoutError:
           raise AppError("E002", "Processing timeout")
   ```

3. **Event Source Differentiation**

   ```python
   @aws_lambda_handler()
   def handler(event, context):
       event_data = LambdaEvent(**event)

       if event_data.is_api_gateway_event(event):
           return handle_api_request(event_data)
       else:
           return handle_direct_invocation(event_data)
   ```

4. **CORS Configuration**
   - By default, allows all origins
   - Headers can be customized for enhanced security when needed
