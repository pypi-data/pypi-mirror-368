# Error Utilities

Structured error handling utilities for AWS Lambda functions, providing standardized error responses and error tracking capabilities.

## Features

- Structured error handling with dataclasses
- Type-safe error creation
- Standardized error format
- JSON serialization support

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.utils.error_utils import AppError

# Create an error instance
error = AppError(
    code='S00001',
    message='Invalid request parameter',
    details={'param': 'user_id', 'value': 'invalid'}
)

# Convert to string
print(str(error))  # AppError[S00001]: Invalid request parameter

# Convert to dictionary
error_dict = error.to_dict()
print(error_dict)
# {
#     'code': 'S00001',
#     'message': 'Invalid request parameter',
#     'timestamp': '2024-01-01T00:00:00',
#     'details': {'param': 'user_id', 'value': 'invalid'}
# }
```

## AppError Model

### Fields

- `code`: Error code (string)
- `message`: Error message (string)
- `timestamp`: Error occurrence time (datetime, auto-generated)
- `details`: Additional error details (optional dictionary)

### Methods

- `to_dict()`: Convert error to dictionary
- `__str__()`: Format error as string

### Example Usage in Lambda Handler

```python
from chainsaws.utils.error_utils import AppError
from chainsaws.utils.handler_utils import lambda_handler_decorator

@lambda_handler_decorator()
def handler(event, context):
    try:
        # Your handler logic
        user_id = event.get('user_id')
        if not user_id:
            raise AppError(
                code='B00001',
                message='Missing user ID',
                details={'event': event}
            )

        # Process request
        result = process_user(user_id)
        return {'data': result}

    except ValueError as e:
        raise AppError(
            code='B00002',
            message=str(e),
            details={'user_id': user_id}
        )
```

### Error Response Format

When an `AppError` is raised, it will be caught by the handler decorator and formatted as:

```json
{
    "rslt_cd": "B00001",
    "rslt_msg": "Missing user ID",
    "timestamp": "2024-01-01T00:00:00",
    "details": {
        "event": {...}
    }
}
```

## Best Practices

1. **Use Consistent Error Codes**

   ```python
   # Define error codes as constants
   USER_NOT_FOUND = 'B00404'
   INVALID_REQUEST = 'B00400'

   # Use in handlers
   raise AppError(USER_NOT_FOUND, "User not found")
   ```

2. **Include Relevant Details**

   ```python
   raise AppError(
       code='B00001',
       message='Invalid parameter',
       details={
           'param_name': 'user_id',
           'received_value': user_id,
           'expected_type': 'string'
       }
   )
   ```

3. **Error Handling with Type Safety**

   ```python
   from typing import Dict, Any

   def process_user(data: Dict[str, Any]) -> Dict[str, Any]:
       try:
           # Process user data
           return {'success': True}
       except KeyError as e:
           raise AppError(
               code='B00001',
               message=f'Missing required field: {str(e)}',
               details={'data': data}
           )
   ```
