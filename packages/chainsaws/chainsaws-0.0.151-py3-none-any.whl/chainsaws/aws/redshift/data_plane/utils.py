"""Utility functions for Redshift operations."""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

from psycopg2.extensions import quote_ident

from .models import QueryState


def format_identifier(identifier: str) -> str:
    """Format an identifier for safe use in SQL queries."""
    return quote_ident(identifier, None)


def format_literal(value: Any) -> str:
    """Format a value as a SQL literal."""
    if value is None:
        return 'NULL'
    elif isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, datetime):
        return f"'{value.isoformat()}'"
    elif isinstance(value, (list, tuple)):
        return f"({', '.join(format_literal(v) for v in value)})"
    else:
        return f"'{str(value)}'"


def validate_identifier(identifier: str) -> bool:
    """Validate that a string is a valid SQL identifier."""
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, identifier))


def validate_table_name(table_name: str) -> bool:
    """Validate that a string is a valid table name."""
    parts = table_name.split('.')
    return all(validate_identifier(part) for part in parts)


def parse_table_name(table_name: str) -> Tuple[Optional[str], Optional[str], str]:
    """Parse a table name into (database, schema, table) parts."""
    parts = table_name.split('.')
    if len(parts) == 3:
        return tuple(parts)
    elif len(parts) == 2:
        return None, parts[0], parts[1]
    else:
        return None, None, parts[0]


def format_table_name(
    table: str,
    schema: Optional[str] = None,
    database: Optional[str] = None,
) -> str:
    """Format a fully qualified table name."""
    parts = []
    if database:
        parts.append(format_identifier(database))
    if schema:
        parts.append(format_identifier(schema))
    parts.append(format_identifier(table))
    return '.'.join(parts)


def format_column_definition(
    name: str,
    data_type: str,
    nullable: bool = True,
    default: Optional[Any] = None,
    encode: Optional[str] = None,
    distkey: bool = False,
    sortkey: bool = False,
) -> str:
    """Format a column definition for CREATE TABLE."""
    parts = [format_identifier(name), data_type.upper()]
    if not nullable:
        parts.append('NOT NULL')
    if default is not None:
        parts.append(f'DEFAULT {format_literal(default)}')
    if encode:
        parts.append(f'ENCODE {encode.upper()}')
    if distkey:
        parts.append('DISTKEY')
    if sortkey:
        parts.append('SORTKEY')
    return ' '.join(parts)


def format_where_clause(conditions: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Format a WHERE clause from a dictionary of conditions."""
    if not conditions:
        return '', {}

    parts = []
    params = {}
    param_counter = 0

    for column, value in conditions.items():
        param_counter += 1
        param_name = f'p{param_counter}'

        if value is None:
            parts.append(f'{format_identifier(column)} IS NULL')
        elif isinstance(value, (list, tuple)):
            params[param_name] = tuple(value)
            parts.append(
                f'{format_identifier(column)} IN %({param_name})s')
        else:
            params[param_name] = value
            parts.append(
                f'{format_identifier(column)} = %({param_name})s')

    return ' AND '.join(parts), params


def format_order_by(
    columns: List[Union[str, Tuple[str, str]]],
) -> str:
    """Format an ORDER BY clause."""
    parts = []
    for col in columns:
        if isinstance(col, tuple):
            column, direction = col
            parts.append(
                f'{format_identifier(column)} {direction.upper()}')
        else:
            parts.append(format_identifier(col))
    return ', '.join(parts)


def format_limit_offset(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> str:
    """Format LIMIT and OFFSET clauses."""
    parts = []
    if limit is not None:
        parts.append(f'LIMIT {limit}')
    if offset is not None:
        parts.append(f'OFFSET {offset}')
    return ' '.join(parts)


def infer_redshift_type(value: Any) -> str:
    """Infer Redshift data type from a Python value."""
    if value is None:
        return 'VARCHAR(256)'
    elif isinstance(value, bool):
        return 'BOOLEAN'
    elif isinstance(value, int):
        if -32768 <= value <= 32767:
            return 'SMALLINT'
        elif -2147483648 <= value <= 2147483647:
            return 'INTEGER'
        else:
            return 'BIGINT'
    elif isinstance(value, float):
        return 'DOUBLE PRECISION'
    elif isinstance(value, datetime):
        return 'TIMESTAMP'
    elif isinstance(value, (list, tuple)):
        return 'SUPER'
    elif isinstance(value, dict):
        return 'SUPER'
    else:
        return 'VARCHAR(256)'


def format_create_table(
    table_name: str,
    columns: List[Tuple[str, str]],
    schema: Optional[str] = None,
    database: Optional[str] = None,
    diststyle: str = 'AUTO',
    distkey: Optional[str] = None,
    sortstyle: str = 'AUTO',
    sortkeys: Optional[List[str]] = None,
) -> str:
    """Format a CREATE TABLE statement."""
    full_table = format_table_name(table_name, schema, database)
    column_defs = [
        format_column_definition(name, data_type)
        for name, data_type in columns
    ]

    parts = [
        f'CREATE TABLE {full_table}',
        f'({", ".join(column_defs)})',
        f'DISTSTYLE {diststyle.upper()}'
    ]

    if distkey:
        parts.append(f'DISTKEY ({format_identifier(distkey)})')

    if sortkeys:
        parts.append(
            f'COMPOUND SORTKEY ({", ".join(map(format_identifier, sortkeys))})')
    else:
        parts.append(f'SORTSTYLE {sortstyle.upper()}')

    return ' '.join(parts)


def format_copy_options(options: Dict[str, Any]) -> str:
    """Format COPY command options."""
    parts = []
    for key, value in options.items():
        if isinstance(value, bool):
            if value:
                parts.append(key.upper())
        else:
            parts.append(f"{key.upper()} {value}")
    return ' '.join(parts)


def get_query_state_message(state: QueryState) -> str:
    """Get a human-readable message for a query state."""
    messages = {
        QueryState.SUBMITTED: "Query has been submitted",
        QueryState.PICKED: "Query is being processed",
        QueryState.STARTED: "Query execution has started",
        QueryState.COMPLETED: "Query has completed successfully",
        QueryState.FAILED: "Query execution failed",
        QueryState.CANCELLED: "Query was cancelled",
    }
    return messages.get(state, "Unknown query state")


def format_duration(duration_ms: float) -> str:
    """Format a duration in milliseconds as a human-readable string."""
    if duration_ms < 1000:
        return f"{duration_ms:.0f}ms"
    elif duration_ms < 60000:
        return f"{duration_ms/1000:.1f}s"
    else:
        minutes = int(duration_ms / 60000)
        seconds = (duration_ms % 60000) / 1000
        return f"{minutes}m {seconds:.1f}s"


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)
