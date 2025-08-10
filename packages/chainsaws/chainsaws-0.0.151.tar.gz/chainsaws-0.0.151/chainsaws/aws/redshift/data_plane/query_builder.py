"""Query builder for Redshift SQL statements."""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Literal


class QueryType(str, Enum):
    """Types of SQL queries."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class ComparisonOperator(str, Enum):
    """Comparison operators for query conditions."""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_EQUALS = ">="
    LESS_THAN = "<"
    LESS_EQUALS = "<="
    LIKE = "LIKE"
    ILIKE = "ILIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    BETWEEN = "BETWEEN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    CONTAINS = "@>"  # JSON/Array contains
    CONTAINED_BY = "<@"  # JSON/Array is contained by
    OVERLAPS = "&&"  # JSON/Array overlaps
    HAS_KEY = "?"  # JSON has key
    ANY = "ANY"
    ALL = "ALL"
    EXISTS = "EXISTS"


class JoinType(str, Enum):
    """Types of SQL JOIN operations."""
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL JOIN"
    CROSS = "CROSS JOIN"
    LATERAL = "LATERAL"


class AggregateFunction(str, Enum):
    """Common aggregate functions in PostgreSQL/Redshift."""
    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    STRING_AGG = "STRING_AGG"
    ARRAY_AGG = "ARRAY_AGG"
    JSONB_AGG = "JSONB_AGG"
    JSONB_OBJECT_AGG = "JSONB_OBJECT_AGG"


class WindowFunction(str, Enum):
    """Common window functions in PostgreSQL/Redshift."""
    ROW_NUMBER = "ROW_NUMBER"
    RANK = "RANK"
    DENSE_RANK = "DENSE_RANK"
    FIRST_VALUE = "FIRST_VALUE"
    LAST_VALUE = "LAST_VALUE"
    LAG = "LAG"
    LEAD = "LEAD"
    NTH_VALUE = "NTH_VALUE"
    NTILE = "NTILE"
    PERCENT_RANK = "PERCENT_RANK"
    CUME_DIST = "CUME_DIST"


class OrderDirection(str, Enum):
    """Order direction for ORDER BY clauses."""
    ASC = "ASC"
    DESC = "DESC"
    NULLS_FIRST = "NULLS FIRST"
    NULLS_LAST = "NULLS LAST"


class SetOperation(str, Enum):
    """Set operations for combining queries."""
    UNION = "UNION"
    UNION_ALL = "UNION ALL"
    INTERSECT = "INTERSECT"
    EXCEPT = "EXCEPT"


class QueryBuilder:
    """Enhanced query builder with support for all query types."""

    def __init__(self, table_name: str, query_type: QueryType = QueryType.SELECT):
        """Initialize query builder.

        Args:
            table_name: Name of the target table
            query_type: Type of SQL query to build
        """
        self.table_name = table_name
        self.query_type = query_type
        self._params: Dict[str, Any] = {}
        self._param_counter: int = 0

        # SELECT specific
        self.columns: List[str] = []
        self.joins: List[Dict[str, Any]] = []
        self.conditions: List[Dict[str, Any]] = []
        self.group_by: List[str] = []
        self.having: List[str] = []
        self.order_by: List[Tuple[str, OrderDirection]] = []
        self.limit_value: Optional[int] = None
        self.offset_value: Optional[int] = None
        self.window_functions: List[Dict[str, Any]] = []
        self.with_queries: List[Dict[str, Any]] = []
        self.distinct_on: Optional[List[str]] = None
        self.set_operations: List[Dict[str, Any]] = []
        self.for_update: bool = False
        self.for_update_options: Dict[str, Any] = {}

        # INSERT specific
        self.insert_columns: List[str] = []
        self.insert_values: List[List[Any]] = []
        self.insert_select: Optional[Tuple[str, Dict[str, Any]]] = None
        self.on_conflict_action: Optional[Dict[str, Any]] = None

        # UPDATE specific
        self.update_values: Dict[str, Any] = {}

        # Common
        self.returning: List[str] = []

    def _add_param(self, value: Any) -> str:
        """Add a parameter and return its placeholder."""
        self._param_counter += 1
        key = f"p{self._param_counter}"
        self._params[key] = value
        return f"%({key})s"

    # SELECT operations
    def select(self, *columns: str) -> "QueryBuilder":
        """Add columns to select."""
        self.columns.extend(columns)
        return self

    def distinct(self, *columns: str) -> "QueryBuilder":
        """Add DISTINCT ON clause."""
        self.distinct_on = list(columns)
        return self

    def join(
        self,
        table: str,
        condition: str,
        join_type: JoinType = JoinType.INNER,
        lateral: bool = False,
    ) -> "QueryBuilder":
        """Add a JOIN clause with optional LATERAL support."""
        self.joins.append({
            "table": table,
            "condition": condition,
            "type": join_type,
            "lateral": lateral,
        })
        return self

    def where(
        self,
        condition: str,
        *values: Any,
        operator: Literal["AND", "OR"] = "AND"
    ) -> "QueryBuilder":
        """Add a WHERE condition with AND/OR operator."""
        placeholders = [self._add_param(v) for v in values]
        self.conditions.append({
            "condition": condition.format(*placeholders),
            "operator": operator
        })
        return self

    def aggregate(
        self,
        function: AggregateFunction,
        column: str,
        alias: Optional[str] = None,
        filter_condition: Optional[str] = None,
        *filter_values: Any,
    ) -> "QueryBuilder":
        """Add an aggregate function."""
        agg = f"{function}({column})"
        if filter_condition:
            placeholders = [self._add_param(v) for v in filter_values]
            agg += f" FILTER (WHERE {filter_condition.format(*placeholders)})"
        if alias:
            agg += f" AS {alias}"
        self.columns.append(agg)
        return self

    def json_build(
        self,
        alias: str,
        **kwargs: Any,
    ) -> "QueryBuilder":
        """Build a JSON object from columns/expressions."""
        pairs = []
        for key, value in kwargs.items():
            pairs.append(f"'{key}', {value}")
        json_obj = f"JSON_BUILD_OBJECT({', '.join(pairs)}) AS {alias}"
        self.columns.append(json_obj)
        return self

    def array_operation(
        self,
        column: str,
        operator: ComparisonOperator,
        value: Any,
    ) -> "QueryBuilder":
        """Add array operation condition."""
        placeholder = self._add_param(value)
        self.conditions.append({
            "condition": f"{column} {operator} {placeholder}",
            "operator": "AND"
        })
        return self

    def full_text_search(
        self,
        columns: List[str],
        query: str,
        language: str = "english",
    ) -> "QueryBuilder":
        """Add full text search condition."""
        to_tsvector = f"to_tsvector('{language}', {' || ' .join(columns)})"
        to_tsquery = f"to_tsquery('{language}', {self._add_param(query)})"
        self.conditions.append({
            "condition": f"{to_tsvector} @@ {to_tsquery}",
            "operator": "AND"
        })
        return self

    def set_operation(
        self,
        operation: SetOperation,
        other: Union[str, "QueryBuilder"],
    ) -> "QueryBuilder":
        """Add a set operation (UNION, INTERSECT, EXCEPT)."""
        if isinstance(other, QueryBuilder):
            sql, params = other.build()
            self._params.update(params)
            query_str = sql
        else:
            query_str = other

        self.set_operations.append({
            "operation": operation,
            "query": query_str,
        })
        return self

    def for_update_of(
        self,
        *tables: str,
        no_wait: bool = False,
        skip_locked: bool = False,
    ) -> "QueryBuilder":
        """Add FOR UPDATE clause."""
        self.for_update = True
        self.for_update_options = {
            "tables": tables,
            "no_wait": no_wait,
            "skip_locked": skip_locked,
        }
        return self

    # INSERT operations
    def insert_into(self, *columns: str) -> "QueryBuilder":
        """Specify columns for INSERT."""
        self.insert_columns.extend(columns)
        return self

    def values(self, *rows: Union[Dict[str, Any], List[Any]]) -> "QueryBuilder":
        """Add values for INSERT."""
        if isinstance(rows[0], dict):
            # Handle dict input
            if not self.insert_columns:
                self.insert_columns = list(rows[0].keys())
            self.insert_values.extend([
                [row[col] for col in self.insert_columns]
                for row in rows
            ])
        else:
            # Handle list input
            self.insert_values.extend(rows)
        return self

    def on_conflict(
        self,
        columns: Union[str, List[str]],
        action: Literal["nothing", "update"] = "nothing",
        update_columns: Optional[List[str]] = None,
    ) -> "QueryBuilder":
        """Add ON CONFLICT clause for INSERT."""
        self.on_conflict_action = {
            "columns": columns if isinstance(columns, list) else [columns],
            "action": action,
            "update_columns": update_columns,
        }
        return self

    # UPDATE operations
    def set(self, values: Dict[str, Any]) -> "QueryBuilder":
        """Set values for UPDATE."""
        self.update_values.update(values)
        return self

    # Common operations
    def returning(self, *columns: str) -> "QueryBuilder":
        """Add RETURNING clause."""
        self.returning.extend(columns)
        return self

    def build(self) -> Tuple[str, Dict[str, Any]]:
        """Build the complete SQL query."""
        if self.query_type == QueryType.SELECT:
            return self._build_select()
        elif self.query_type == QueryType.INSERT:
            return self._build_insert()
        elif self.query_type == QueryType.UPDATE:
            return self._build_update()
        else:  # DELETE
            return self._build_delete()

    def _build_select(self) -> Tuple[str, Dict[str, Any]]:
        """Build SELECT query."""
        parts = []

        # WITH clause
        if self.with_queries:
            with_parts = []
            for cte in self.with_queries:
                cte_def = f"{cte['name']}"
                if cte["columns"]:
                    cte_def += f"({', '.join(cte['columns'])})"
                cte_def += f" AS ({cte['query']})"
                with_parts.append(cte_def)
            parts.append("WITH " + ",\n".join(with_parts))

        # SELECT clause
        select_clause = "SELECT "
        if self.distinct_on:
            select_clause += f"DISTINCT ON ({', '.join(self.distinct_on)}) "
        if not self.columns:
            select_clause += "*"
        else:
            all_columns = list(self.columns)
            for wf in self.window_functions:
                window_def = f"{wf['function']}() OVER ("
                if wf["partition_by"]:
                    window_def += f"PARTITION BY {
                        ', '.join(wf['partition_by'])} "
                if wf["order_by"]:
                    order_parts = [f"{col} {direction.value}"
                                   for col, direction in wf["order_by"]]
                    window_def += f"ORDER BY {', '.join(order_parts)}"
                window_def += f") AS {wf['alias']}"
                all_columns.append(window_def)
            select_clause += ", ".join(all_columns)
        parts.append(select_clause)

        # FROM clause
        parts.append(f"FROM {self.table_name}")

        # JOIN clauses
        for join in self.joins:
            join_clause = ""
            if join["lateral"]:
                join_clause += "LATERAL "
            join_clause += f"{join['type'].value} {join['table']}"
            if join["condition"]:
                join_clause += f" ON {join['condition']}"
            parts.append(join_clause)

        # WHERE clause
        if self.conditions:
            where_parts = []
            for i, cond in enumerate(self.conditions):
                if i == 0:
                    where_parts.append(f"({cond['condition']})")
                else:
                    where_parts.append(
                        f"{cond['operator']} ({cond['condition']})")
            parts.append("WHERE " + " ".join(where_parts))

        # GROUP BY clause
        if self.group_by:
            parts.append("GROUP BY " + ", ".join(self.group_by))

        # HAVING clause
        if self.having:
            parts.append(
                "HAVING " + " AND ".join(f"({h})" for h in self.having))

        # Set operations
        for set_op in self.set_operations:
            parts.append(f"{set_op['operation'].value}")
            parts.append(set_op['query'])

        # ORDER BY clause
        if self.order_by:
            order_parts = [f"{col} {direction.value}"
                           for col, direction in self.order_by]
            parts.append("ORDER BY " + ", ".join(order_parts))

        # LIMIT and OFFSET
        if self.limit_value is not None:
            parts.append(f"LIMIT {self.limit_value}")
        if self.offset_value is not None:
            parts.append(f"OFFSET {self.offset_value}")

        # FOR UPDATE clause
        if self.for_update:
            for_update = "FOR UPDATE"
            if self.for_update_options["tables"]:
                for_update += f" OF {
                    ', '.join(self.for_update_options['tables'])}"
            if self.for_update_options["no_wait"]:
                for_update += " NOWAIT"
            elif self.for_update_options["skip_locked"]:
                for_update += " SKIP LOCKED"
            parts.append(for_update)

        return " ".join(parts), self._params

    def _build_insert(self) -> Tuple[str, Dict[str, Any]]:
        """Build INSERT query."""
        parts = [f"INSERT INTO {self.table_name}"]

        if self.insert_columns:
            parts.append(f"({', '.join(self.insert_columns)})")

        if self.insert_select:
            select_sql, select_params = self.insert_select
            self._params.update(select_params)
            parts.append(select_sql)
        else:
            value_groups = []
            for row in self.insert_values:
                placeholders = [self._add_param(v) for v in row]
                value_groups.append(f"({', '.join(placeholders)})")
            parts.append("VALUES " + ",\n".join(value_groups))

        if self.on_conflict_action:
            parts.append(
                f"ON CONFLICT ({', '.join(self.on_conflict_action['columns'])})")
            if self.on_conflict_action["action"] == "nothing":
                parts.append("DO NOTHING")
            else:
                update_cols = self.on_conflict_action["update_columns"]
                if update_cols:
                    set_parts = [
                        f"{col} = EXCLUDED.{col}" for col in update_cols]
                    parts.append("DO UPDATE SET " + ", ".join(set_parts))

        if self.returning:
            parts.append("RETURNING " + ", ".join(self.returning))

        return " ".join(parts), self._params

    def _build_update(self) -> Tuple[str, Dict[str, Any]]:
        """Build UPDATE query."""
        parts = [f"UPDATE {self.table_name}"]

        # SET clause
        set_parts = []
        for col, value in self.update_values.items():
            placeholder = self._add_param(value)
            set_parts.append(f"{col} = {placeholder}")
        parts.append("SET " + ", ".join(set_parts))

        # WHERE clause
        if self.conditions:
            where_parts = []
            for i, cond in enumerate(self.conditions):
                if i == 0:
                    where_parts.append(f"({cond['condition']})")
                else:
                    where_parts.append(
                        f"{cond['operator']} ({cond['condition']})")
            parts.append("WHERE " + " ".join(where_parts))

        if self.returning:
            parts.append("RETURNING " + ", ".join(self.returning))

        return " ".join(parts), self._params

    def _build_delete(self) -> Tuple[str, Dict[str, Any]]:
        """Build DELETE query."""
        parts = [f"DELETE FROM {self.table_name}"]

        # WHERE clause
        if self.conditions:
            where_parts = []
            for i, cond in enumerate(self.conditions):
                if i == 0:
                    where_parts.append(f"({cond['condition']})")
                else:
                    where_parts.append(
                        f"{cond['operator']} ({cond['condition']})")
            parts.append("WHERE " + " ".join(where_parts))

        if self.returning:
            parts.append("RETURNING " + ", ".join(self.returning))

        return " ".join(parts), self._params
