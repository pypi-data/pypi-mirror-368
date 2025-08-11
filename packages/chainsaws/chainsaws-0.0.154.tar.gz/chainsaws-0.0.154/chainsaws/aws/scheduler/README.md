# AWS EventBridge Scheduler

The `scheduler` module provides a high-level interface for working with AWS EventBridge Scheduler. It allows you to easily create, manage, and schedule Lambda function invocations with various scheduling patterns.

## Features

- Type-safe schedule expressions with validation
- Builder pattern for creating schedule expressions
- Support for at, rate, and cron expressions
- Convenient helper methods for common scheduling patterns
- Automatic validation of Lambda function existence
- Task scheduling utilities for Lambda functions

## Usage

### Basic Setup

```python
from chainsaws.aws.scheduler import SchedulerAPI, ScheduleExpressionBuilder

# Initialize the scheduler
scheduler = SchedulerAPI(schedule_group="my-group")
```

### Creating Schedules

The module provides multiple ways to create schedules:

#### Using Schedule Expression Builder

```python
# Daily schedule at 9:00 AM UTC
schedule_name = scheduler.init_scheduler(
    lambda_function_arn="arn:aws:lambda:region:account:function:name",
    schedule_expression=ScheduleExpressionBuilder.daily_at(hour=9),
    description="Daily morning job"
)

# Weekly schedule on Monday at 10:30 AM UTC
schedule_name = scheduler.init_scheduler(
    lambda_function_arn="arn:aws:lambda:region:account:function:name",
    schedule_expression=ScheduleExpressionBuilder.weekly_on(
        day="MON",
        hour=10,
        minute=30
    ),
    description="Weekly report generation"
)

# Run every 5 minutes
schedule_name = scheduler.init_scheduler(
    lambda_function_arn="arn:aws:lambda:region:account:function:name",
    schedule_expression=ScheduleExpressionBuilder.every_n_minutes(5),
    description="Frequent monitoring task"
)

# One-time execution
from datetime import datetime
schedule_name = scheduler.init_scheduler(
    lambda_function_arn="arn:aws:lambda:region:account:function:name",
    schedule_expression=ScheduleExpressionBuilder.at(
        datetime(2024, 3, 15, 14, 30)
    ),
    description="One-time data migration"
)
```

#### Using Raw Schedule Expressions

You can also use raw schedule expressions, which will be validated:

```python
from chainsaws.aws.scheduler import ScheduleExpression

# Using cron expression
schedule_name = scheduler.init_scheduler(
    lambda_function_arn="arn:aws:lambda:region:account:function:name",
    schedule_expression=ScheduleExpression("cron(0 8 * * ? *)"),
    description="Daily at 8 AM UTC"
)

# Using rate expression
schedule_name = scheduler.init_scheduler(
    lambda_function_arn="arn:aws:lambda:region:account:function:name",
    schedule_expression=ScheduleExpression("rate(5 minutes)"),
    description="Every 5 minutes"
)
```

### Managing Schedules

```python
# List all schedules
response = scheduler.list_schedules()
for schedule in response["schedules"]:
    print(f"Schedule: {schedule['name']}, Next invocation: {schedule['next_invocation']}")

# Enable/Disable schedules
scheduler.disable_schedule("my-schedule")
scheduler.enable_schedule("my-schedule")

# Delete a schedule
scheduler.delete_schedule("my-schedule")

# Update a schedule
scheduler.update_schedule(
    name="my-schedule",
    schedule_expression=ScheduleExpressionBuilder.every_n_minutes(10),
    description="Updated description"
)
```

### Task Scheduling in Lambda Functions

The module also provides utilities for scheduling tasks within Lambda functions:

```python
from chainsaws.aws.scheduler import ScheduledTask, join

def handler(event, context):
    """Lambda handler for scheduled tasks."""

    # Tasks to run daily at midnight
    with ScheduledTask('0 0 * * *') as do:
        def daily_cleanup():
            print("Running daily cleanup")

        def generate_report():
            print("Generating daily report")

        do(daily_cleanup)
        do(generate_report)

    # Tasks to run every 15 minutes
    with ScheduledTask('*/15 * * * *') as do:
        def check_metrics():
            print("Checking metrics")

        do(check_metrics)

    # Wait for all tasks to complete
    join()
```

## Schedule Expression Types

### At Expression

- Format: `at(yyyy-mm-ddThh:mm:ss)`
- Example: `at(2024-03-15T14:30:00)`
- Use for one-time executions

### Rate Expression

- Format: `rate(value unit)`
- Units: minute(s), hour(s), day(s)
- Example: `rate(5 minutes)`, `rate(1 hour)`
- Use for fixed-interval recurring schedules

### Cron Expression

- Format: `cron(minutes hours day_of_month month day_of_week year)`
- Example: `cron(0 8 * * ? *)`
- Use for complex recurring schedules

## Error Handling

The module includes comprehensive error handling:

```python
try:
    scheduler.init_scheduler(...)
except ValueError as e:
    print(f"Invalid schedule expression: {e}")
except LambdaException as e:
    print(f"Lambda function error: {e}")
except Exception as e:
    print(f"Other error: {e}")
```

## Best Practices

1. Use the `ScheduleExpressionBuilder` for type-safe schedule creation
2. Always provide descriptive names and descriptions for schedules
3. Use schedule groups to organize related schedules
4. Handle errors appropriately to ensure robust scheduling
5. Clean up unused schedules to avoid resource waste
6. Use `ScheduledTask` for organizing multiple tasks in Lambda functions
7. Always call `join()` after defining scheduled tasks to ensure completion
