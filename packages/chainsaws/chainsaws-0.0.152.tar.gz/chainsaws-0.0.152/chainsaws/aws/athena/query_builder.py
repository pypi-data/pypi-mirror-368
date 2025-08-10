"""SQL query builder for Athena."""
from typing import Any, List, Optional, Union, Dict
from datetime import datetime, date


class QueryBuilder:
    """SQL query builder for Athena queries."""

    def __init__(self) -> None:
        """Initialize QueryBuilder."""
        self._select: List[str] = []
        self._from: Optional[str] = None
        self._where: List[str] = []
        self._group_by: List[str] = []
        self._having: List[str] = []
        self._order_by: List[str] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None

    def select(self, *columns: str) -> "QueryBuilder":
        """Add columns to SELECT clause.

        Args:
            *columns: Column names or expressions

        Returns:
            QueryBuilder: Self for chaining
        """
        self._select.extend(columns)
        return self

    def from_(self, table: str) -> "QueryBuilder":
        """Set FROM clause.

        Args:
            table: Table name or subquery

        Returns:
            QueryBuilder: Self for chaining
        """
        self._from = table
        return self

    def where(self, condition: Union[str, Dict[str, Any]]) -> "QueryBuilder":
        """Add WHERE conditions.

        Args:
            condition: SQL condition string or dict of column-value pairs

        Returns:
            QueryBuilder: Self for chaining
        """
        if isinstance(condition, str):
            self._where.append(condition)
        else:
            for column, value in condition.items():
                self._where.append(self._format_condition(column, value))
        return self

    def group_by(self, *columns: str) -> "QueryBuilder":
        """Add GROUP BY columns.

        Args:
            *columns: Column names

        Returns:
            QueryBuilder: Self for chaining
        """
        self._group_by.extend(columns)
        return self

    def having(self, condition: str) -> "QueryBuilder":
        """Add HAVING conditions.

        Args:
            condition: SQL condition string

        Returns:
            QueryBuilder: Self for chaining
        """
        self._having.append(condition)
        return self

    def order_by(self, *columns: str) -> "QueryBuilder":
        """Add ORDER BY columns.

        Args:
            *columns: Column names with optional ASC/DESC

        Returns:
            QueryBuilder: Self for chaining
        """
        self._order_by.extend(columns)
        return self

    def limit(self, count: int) -> "QueryBuilder":
        """Set LIMIT clause.

        Args:
            count: Maximum number of rows

        Returns:
            QueryBuilder: Self for chaining
        """
        self._limit = count
        return self

    def offset(self, count: int) -> "QueryBuilder":
        """Set OFFSET clause.

        Args:
            count: Number of rows to skip

        Returns:
            QueryBuilder: Self for chaining
        """
        self._offset = count
        return self

    def _format_condition(self, column: str, value: Any) -> str:
        """Format a WHERE condition based on value type.

        Args:
            column: Column name
            value: Value to compare against

        Returns:
            str: Formatted condition
        """
        if value is None:
            return f"{column} IS NULL"
        elif isinstance(value, (int, float)):
            return f"{column} = {value}"
        elif isinstance(value, (datetime, date)):
            return f"{column} = DATE '{value}'"
        elif isinstance(value, (list, tuple)):
            values = ", ".join(self._format_value(v) for v in value)
            return f"{column} IN ({values})"
        else:
            return f"{column} = {self._format_value(value)}"

    def _format_value(self, value: Any) -> str:
        """Format a value for SQL query.

        Args:
            value: Value to format

        Returns:
            str: Formatted value
        """
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, (datetime, date)):
            return f"DATE '{value}'"
        return str(value)

    def build(self) -> str:
        """Build the SQL query string.

        Returns:
            str: Complete SQL query

        Raises:
            ValueError: If required clauses are missing
        """
        if not self._select:
            raise ValueError("SELECT clause is required")
        if not self._from:
            raise ValueError("FROM clause is required")

        query_parts = []

        # SELECT
        select_clause = "SELECT " + ", ".join(self._select)
        query_parts.append(select_clause)

        # FROM
        query_parts.append(f"FROM {self._from}")

        # WHERE
        if self._where:
            query_parts.append("WHERE " + " AND ".join(self._where))

        # GROUP BY
        if self._group_by:
            query_parts.append("GROUP BY " + ", ".join(self._group_by))

        # HAVING
        if self._having:
            query_parts.append("HAVING " + " AND ".join(self._having))

        # ORDER BY
        if self._order_by:
            query_parts.append("ORDER BY " + ", ".join(self._order_by))

        # LIMIT
        if self._limit is not None:
            query_parts.append(f"LIMIT {self._limit}")

        # OFFSET
        if self._offset is not None:
            query_parts.append(f"OFFSET {self._offset}")

        return "\n".join(query_parts)
