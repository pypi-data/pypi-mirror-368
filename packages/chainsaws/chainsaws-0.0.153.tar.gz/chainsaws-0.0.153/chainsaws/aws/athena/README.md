# AWS Athena Client

A high-level Python client for AWS Athena. Easily use Athena's core features including query execution, database management, table management, and more.

## Key Features

- Query Execution and Results

  - Synchronous/Asynchronous query execution
  - Download results to CSV files
  - Handle large results with pagination
  - Asynchronous query monitoring

- Database Management

  - Create/Delete/Get databases
  - List available databases

- Table Management

  - Create/Delete/Get tables
  - List available tables
  - Partition management

- Workgroup Management

  - Create/Delete/Modify/Get workgroups
  - Manage workgroup settings

- Query Analysis and Optimization
  - Query performance analysis
  - Cost estimation
  - Optimization recommendations

## Installation

```bash
pip install chainsaws
```

## Quick Start

### Basic Configuration

```python
from chainsaws.aws.athena import AthenaAPI, AthenaAPIConfig

config = AthenaAPIConfig(
    region="ap-northeast-2",
    result_store_bucket="your-athena-results",  # S3 bucket for storing Athena query results
    output_location="s3://your-athena-results/query-results/",  # Optional
    database="your_database",
    workgroup="primary"  # Optional, defaults to "primary"
)

athena = AthenaAPI(config)
```

### Query Execution

```python
# Execute raw SQL query
result = athena.execute_query(
    query="SELECT * FROM your_table LIMIT 10",
    database="your_database"
)

# Use query builder
query = athena.create_query()
result = (query
    .select("id", "name", "COUNT(*) as count")
    .from_("your_table")
    .where({
        "year": "2023",
        "status": ["active", "pending"]
    })
    .group_by("id", "name")
    .having("COUNT(*) > 10")
    .order_by("count DESC")
    .limit(100)
    .build())

# Execute query using builder
result = athena.execute_builder(query)

# Handle complex conditions easily
query = athena.create_query()
result = (query
    .select("*")
    .from_("sales")
    .where({
        "date": datetime.date(2023, 12, 1),  # Automatically converted to DATE '2023-12-01'
        "category": ["electronics", "books"],  # Automatically converted to IN clause
        "price": 100.50,  # Numbers used as is
        "status": None,   # Automatically converted to IS NULL
    })
    .build())
```

### Download Results

```python
# Execute query and download results directly to file
athena.execute_query_to_file(
    query="SELECT * FROM your_table",
    output_path="query_results.csv"
)

# Download results of an existing query
athena.download_query_results(
    query_execution_id="query_id",
    output_path="query_results.csv"
)

# Download results to a stream
with open("query_results.csv", "wb") as f:
    athena.download_query_results(
        query_execution_id="query_id",
        output_path=f
    )

# Get S3 location of query results
s3_location = athena.get_query_output_location("query_id")
print(f"Results stored at: {s3_location}")
```

### Handle Large Data

```python
# Process large results with pagination
for row in athena.get_query_results_iterator(
    query_execution_id="query_id",
    page_size=1000
):
    process_row(row)
```

## Advanced Features

### Pagination Handling

```python
# Process large results
for row in athena.get_query_results_iterator(
    query_execution_id="query_id",
    page_size=1000
):
    process_row(row)
```

### Workgroup Management

```python
# Create workgroup
athena.create_work_group(
    work_group_name="dev_group",
    description="Development team workgroup",
    configuration={
        "ResultConfiguration": {
            "OutputLocation": "s3://your-bucket/dev-results/"
        },
        "EnforceWorkGroupConfiguration": True,
        "PublishCloudWatchMetricsEnabled": True
    }
)
```

### Query Session Management

Use context manager to manage query sessions:

```python
# Execute queries in a session
with athena.session("my_database") as session:
    # Execute multiple queries in session
    result1 = session.execute("SELECT * FROM table1")
    result2 = session.execute("SELECT * FROM table2")

    # Use query builder in session
    query = athena.create_query()
    result3 = session.execute_builder(
        query.select("*")
            .from_("table3")
            .where({"status": "active"})
    )

    # Check status of active queries
    active_queries = session.get_active_queries()
    for query in active_queries:
        print(f"Query {query['QueryExecutionId']}: {query['Status']['State']}")

# When session ends, running queries are stopped and resources are cleaned up

# Manual session management
session = athena.create_session("my_database")
try:
    result = session.execute("SELECT * FROM my_table")
finally:
    session.cleanup()  # Manual resource cleanup
```

Session benefits:

- Automatic resource cleanup
- Track running queries
- Result caching
- Maintain database context

## Exception Handling

```python
from chainsaws.aws.athena import (
    QueryExecutionError,
    QueryTimeoutError,
    InvalidQueryError
)

try:
    result = athena.execute_query(query="SELECT * FROM table")
except QueryTimeoutError:
    print("Query execution timed out")
except InvalidQueryError as e:
    print(f"Invalid query: {e}")
except QueryExecutionError as e:
    print(f"Query execution error: {e}")
```

### Using Query Templates

Use query templates for safe parameterized query execution:

```python
# Create template
template = athena.create_template("""
    SELECT *
    FROM {table}
    WHERE year = {year}
    AND category IN {categories}
    AND status = {status}
""")

# Execute template
result = template.execute(
    table="sales",
    year=2023,
    categories=["electronics", "books"],  # Automatically converted to IN clause
    status="active"
)

# Save results to file
template.execute_to_file(
    output_path="sales_report.csv",
    table="sales",
    year=2023,
    categories=["electronics", "books"],
    status="active"
)

# Render template string only
query = template.render(
    table="sales",
    year=2023,
    categories=["electronics", "books"],
    status="active"
)
print(f"Generated query: {query}")
```

Template benefits:

- SQL injection prevention
- Automatic parameter type conversion
- Reusable queries
- Missing parameter validation

### Typed Query Results

Execute queries with strongly typed results:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserStats:
    user_id: str
    visit_count: int
    last_visit: datetime

# Execute query with typed results
result = athena.execute_typed(
    query="SELECT user_id, COUNT(*) as visit_count, MAX(visit_time) as last_visit FROM visits GROUP BY user_id",
    output_type=UserStats
)

# Access strongly typed data
for user in result.data:
    print(f"User {user.user_id} visited {user.visit_count} times")

# Access execution metadata
print(f"Query took {result.execution_time:.2f} seconds")
print(f"Scanned {result.scanned_bytes / 1024**3:.2f} GB")
```

### Asynchronous Query Execution

Use async sessions for better performance with long-running queries:

```python
async with athena.async_session() as session:
    # Execute query with progress monitoring
    query = session.execute_async(
        "SELECT * FROM huge_table",
        on_progress=lambda progress: print(f"Progress: {progress:.1f}%"),
        on_partial_result=lambda batch: process_batch(batch)
    )

    # Wait for completion
    execution = await query.wait_for_completion()

    # Stream results
    async for row in query.stream_results():
        process_row(row)
```

### Query Performance Analysis

Analyze query performance and get optimization suggestions:

```python
report = athena.analyze_query_performance(
    "SELECT * FROM large_table WHERE date BETWEEN '2023-01-01' AND '2023-12-31'"
)

print(f"Estimated cost: ${report.cost_estimate:.2f}")
print(f"Execution time: {report.execution_time:.1f} seconds")
print(f"Data scanned: {report.data_scanned / 1024**3:.1f} GB")
print(f"Risk level: {report.risk_level}")

print("\nOptimization suggestions:")
for suggestion in report.suggestions:
    print(f"- {suggestion}")

print("\nBottlenecks:")
for bottleneck in report.bottlenecks:
    print(f"- {bottleneck}")

print("\nOptimization tips:")
for tip in report.optimization_tips:
    print(f"- {tip}")
```

### Enhanced Error Handling

Get detailed error information with suggestions:

```python
try:
    result = athena.execute_query("SELECT * FROM non_existent_table")
except Exception as e:
    error = athena.handle_error(e)

    print(f"Error code: {error.error_code}")
    print(f"Stage: {error.query_stage}")
    print(f"Message: {error.message}")

    print("\nSuggestions:")
    for suggestion in error.suggestions:
        print(f"- {suggestion}")

    if error.is_recoverable:
        print("\nThis error is recoverable")

    if error.has_quick_fix:
        print("\nQuick fixes available")
```
