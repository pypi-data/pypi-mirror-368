"""Main API implementation for Redshift."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, TypeVar, cast, Pattern, Union

import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection as Connection

from .models import (
    RedshiftRecordList,
    QueryParams,
    QueryResult,
    QueryState,
    QueryStatistics,
    TypedQueryResult,
    BatchOperationResult,
    Column,
    RedshiftValue,
    RedshiftRecord,
    Table,
    QueryPerformanceReport,
)
from .exception import (
    QueryExecutionError,
    ResourceNotFoundError,
    TransactionError,
)

T = TypeVar('T')


class RedshiftAPI:
    """High-level API for interacting with AWS Redshift."""

    async def execute_query(
        self,
        query: str,
        parameters: Optional[QueryParams] = None,
    ) -> QueryResult:
        """Execute a query and return results.

        Args:
            query: SQL query to execute
            parameters: Query parameters
            timeout: Query timeout in seconds

        Returns:
            QueryResult containing execution results and statistics

        Raises:
            QueryExecutionError: If query execution fails
        """
        async with self.connection() as conn:
            try:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    start_time = datetime.now()
                    cur.execute(query, parameters or {})
                    rows = cur.fetchall() if cur.description else None
                    end_time = datetime.now()

                    execution_time = (end_time - start_time).total_seconds()
                    statistics = QueryStatistics(
                        elapsed_time=execution_time,
                        cpu_time=execution_time,  # Approximation
                        queued_time=0.0,
                        bytes_scanned=0,  # Would need EXPLAIN ANALYZE
                        rows_produced=len(rows) if rows else 0,
                        rows_affected=cur.rowcount,
                    )

                    return QueryResult(
                        query_id=str(id(cur)),
                        query=query,
                        state=QueryState.FINISHED,
                        statistics=statistics,
                        result_rows=[dict(row) for row in (rows or [])],
                        error_message=None,
                    )

            except psycopg2.Error as e:
                raise QueryExecutionError(str(e), query)

    async def execute_typed_query(
        self,
        query: str,
        parameters: Optional[QueryParams] = None,
        timeout: Optional[int] = None,
    ) -> TypedQueryResult[T]:
        """Execute a query and return typed results.

        Args:
            query: SQL query to execute
            parameters: Query parameters
            timeout: Query timeout in seconds

        Returns:
            TypedQueryResult containing execution results with typed rows

        Raises:
            QueryExecutionError: If query execution fails
        """
        result = await self.execute_query(query, parameters, timeout)
        return TypedQueryResult.from_query_result(result)

    async def batch_insert(
        self,
        table_name: str,
        data: RedshiftRecordList,
        chunk_size: int = 1000,
    ) -> BatchOperationResult:
        """Insert multiple rows in batch.

        Args:
            table_name: Target table name
            data: List of records to insert
            chunk_size: Number of records per batch

        Returns:
            BatchOperationResult containing operation statistics

        Raises:
            QueryExecutionError: If batch insert fails
        """
        if not data:
            return BatchOperationResult(
                total_records=0,
                processed_records=0,
                failed_records=0,
                execution_time=0.0,
            )

        start_time = datetime.now()
        processed = 0
        failed = 0

        async with self.transaction() as conn:
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                try:
                    columns = chunk[0].keys()
                    values = [tuple(record[col] for col in columns)
                              for record in chunk]

                    with conn.cursor() as cur:
                        args_str = ','.join(
                            cur.mogrify(
                                "(%s)" + ",".join(["%s"] * (len(columns)-1)), x).decode()
                            for x in values
                        )
                        cur.execute(f"""
                            INSERT INTO {table_name} ({','.join(columns)})
                            VALUES {args_str}
                        """)
                    processed += len(chunk)
                except Exception as e:
                    logging.error(f"Failed to insert batch: {e}")
                    failed += len(chunk)

        execution_time = (datetime.now() - start_time).total_seconds()
        return BatchOperationResult(
            total_records=len(data),
            processed_records=processed,
            failed_records=failed,
            execution_time=execution_time,
        )

    async def batch_update(
        self,
        table_name: str,
        updates: RedshiftRecordList,
        key_fields: List[str],
        chunk_size: int = 1000,
    ) -> BatchOperationResult:
        """Update multiple rows in batch.

        Args:
            table_name: Target table name
            updates: List of records to update
            key_fields: Fields to use as update keys
            chunk_size: Number of records per batch

        Returns:
            BatchOperationResult containing operation statistics

        Raises:
            QueryExecutionError: If batch update fails
        """
        if not updates or not key_fields:
            return BatchOperationResult(
                total_records=0,
                processed_records=0,
                failed_records=0,
                execution_time=0.0,
            )

        start_time = datetime.now()
        processed = 0
        failed = 0

        async with self.transaction() as conn:
            for i in range(0, len(updates), chunk_size):
                chunk = updates[i:i + chunk_size]
                try:
                    for record in chunk:
                        update_fields = {
                            k: v for k, v in record.items() if k not in key_fields}
                        where_clause = " AND ".join(
                            f"{k} = %s" for k in key_fields)
                        set_clause = ", ".join(
                            f"{k} = %s" for k in update_fields.keys())

                        with conn.cursor() as cur:
                            cur.execute(f"""
                                UPDATE {table_name}
                                SET {set_clause}
                                WHERE {where_clause}
                            """, [*update_fields.values(), *[record[k] for k in key_fields]])

                    processed += len(chunk)
                except Exception as e:
                    logging.error(f"Failed to update batch: {e}")
                    failed += len(chunk)

        execution_time = (datetime.now() - start_time).total_seconds()
        return BatchOperationResult(
            total_records=len(updates),
            processed_records=processed,
            failed_records=failed,
            execution_time=execution_time,
        )

    async def get_table_schema(
        self,
        table_name: str,
        schema: Optional[str] = None,
    ) -> List[Column]:
        """Get schema information for a table.

        Args:
            table_name: Name of the table
            schema: Optional schema name

        Returns:
            List of Column objects describing table schema

        Raises:
            ResourceNotFoundError: If table does not exist
        """
        sql = """
        SELECT
            column_name as name,
            data_type as type,
            is_nullable = 'YES' as nullable,
            column_default as default,
            encoding as encoding,
            distkey as distkey,
            sortkey > 0 as sortkey
        FROM pg_table_def
        WHERE tablename = %(table)s
        """
        if schema:
            sql += " AND schemaname = %(schema)s"

        result = await self.execute_query(sql, {"table": table_name, "schema": schema})
        if not result.result_rows:
            raise ResourceNotFoundError("Table", table_name)

        return cast(List[Column], result.result_rows)

    @asynccontextmanager
    async def transaction(
        self,
        isolation_level: Optional[str] = None,
        readonly: bool = False,
        deferrable: bool = False,
    ) -> AsyncGenerator[Connection, None]:
        """Start a transaction with the specified isolation level.

        Args:
            isolation_level: Transaction isolation level
            readonly: Whether transaction is read-only
            deferrable: Whether transaction is deferrable

        Yields:
            Database connection for transaction

        Raises:
            TransactionError: If transaction operations fail
        """
        async with self.connection() as conn:
            try:
                if isolation_level:
                    await self.execute_query(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
                if readonly:
                    await self.execute_query("SET TRANSACTION READ ONLY")
                if deferrable:
                    await self.execute_query("SET TRANSACTION DEFERRABLE")

                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise TransactionError(str(e)) from e

    async def insert(
        self,
        table_name: str,
        data: Union[RedshiftRecord, RedshiftRecordList],
    ) -> int:
        """Insert data into a table.

        Args:
            table_name: Target table name
            data: Single record or list of records to insert

        Returns:
            Number of rows affected

        Raises:
            QueryExecutionError: If insert operation fails
        """
        if not isinstance(data, list):
            data = [data]

        if not data:
            return 0

        columns = list(data[0].keys())
        placeholders = ", ".join(["%s"] * len(columns))
        values = [tuple(record[col] for col in columns) for record in data]

        sql = f"""
            INSERT INTO {table_name} ({", ".join(columns)})
            VALUES ({placeholders})
        """

        result = await self.execute_query(sql, values)
        return result.affected_rows

    async def update(
        self,
        table_name: str,
        updates: RedshiftRecord,
        conditions: RedshiftRecord,
    ) -> int:
        """Update records in a table.

        Args:
            table_name: Target table name
            updates: Fields and values to update
            conditions: WHERE conditions for update

        Returns:
            Number of rows affected

        Raises:
            QueryExecutionError: If update operation fails
        """
        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        where_clause = " AND ".join(f"{k} = %s" for k in conditions.keys())

        sql = f"""
            UPDATE {table_name}
            SET {set_clause}
            WHERE {where_clause}
        """

        parameters = [*updates.values(), *conditions.values()]
        result = await self.execute_query(sql, parameters)
        return result.affected_rows

    async def delete(
        self,
        table_name: str,
        conditions: RedshiftRecord,
    ) -> int:
        """Delete records from a table.

        Args:
            table_name: Target table name
            conditions: WHERE conditions for delete

        Returns:
            Number of rows affected

        Raises:
            QueryExecutionError: If delete operation fails
        """
        where_clause = " AND ".join(f"{k} = %s" for k in conditions.keys())

        sql = f"""
            DELETE FROM {table_name}
            WHERE {where_clause}
        """

        result = await self.execute_query(sql, list(conditions.values()))
        return result.affected_rows

    async def explain_query(
        self,
        query: str,
        analyze: bool = False,
    ) -> QueryPerformanceReport:
        """Get query execution plan with performance analysis.

        Args:
            query: SQL query to explain
            analyze: Whether to execute the query for actual timing

        Returns:
            QueryPerformanceReport containing execution plan and statistics

        Raises:
            QueryExecutionError: If explain operation fails
        """
        explain_query = f"EXPLAIN {'ANALYZE ' if analyze else ''}JSON {query}"
        result = await self.execute_query(explain_query)

        if not result.result_rows:
            raise QueryExecutionError("Failed to get query plan", query)

        plan_data = result.result_rows[0]
        statistics = QueryStatistics(
            execution_time=plan_data.get("Execution Time", 0.0),
            cpu_time=plan_data.get("Planning Time", 0.0),
            queued_time=0.0,
            processed_rows=plan_data.get("Plan", {}).get("Actual Rows", 0),
            processed_bytes=plan_data.get(
                "Plan", {}).get("Actual Total Bytes", 0),
            peak_memory_usage=plan_data.get(
                "Plan", {}).get("Peak Memory Usage", 0),
        )

        bottlenecks = []
        if statistics.execution_time > 1000:  # 1 second
            bottlenecks.append("High execution time")
        if statistics.processed_bytes > 1_000_000_000:  # 1GB
            bottlenecks.append("Large data scan")

        return QueryPerformanceReport(
            query_id=str(id(result)),
            execution_plan=str(plan_data),
            statistics=statistics,
            bottlenecks=bottlenecks,
            recommendations=self._generate_recommendations(plan_data),
        )

    def _generate_recommendations(self, plan_data: Dict[str, RedshiftValue]) -> List[str]:
        """Generate query optimization recommendations based on execution plan.

        Args:
            plan_data: Query plan data from EXPLAIN command

        Returns:
            List of optimization recommendations
        """
        recommendations = []
        plan = plan_data.get("Plan", {})

        if plan.get("Node Type") == "Seq Scan":
            recommendations.append(
                "Consider adding an index to avoid sequential scan")

        if plan.get("Sort Key"):
            recommendations.append("Review sort key distribution")

        if plan.get("Rows Removed by Filter") > plan.get("Actual Rows", 0):
            recommendations.append(
                "Add more selective filters to reduce data scanning")

        return recommendations

    async def list_tables(
        self,
        schema: Optional[str] = None,
        pattern: Optional[Pattern[str]] = None,
    ) -> List[Table]:
        """List tables in the database.

        Args:
            schema: Schema name to filter tables
            pattern: Regex pattern to filter table names

        Returns:
            List of Table objects with basic information

        Raises:
            QueryExecutionError: If listing tables fails
        """
        sql = """
            SELECT 
                schemaname as schema,
                tablename as name,
                'table' as type
            FROM pg_tables
            WHERE schemaname = %(schema)s
        """

        result = await self.execute_query(sql, {"schema": schema or "public"})
        tables = cast(List[Table], result.result_rows)

        if pattern:
            tables = [t for t in tables if pattern.match(t["name"])]

        return tables
