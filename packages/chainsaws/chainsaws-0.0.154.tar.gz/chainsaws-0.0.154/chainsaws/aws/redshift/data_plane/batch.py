"""Batch operations for efficient data loading and manipulation in Redshift."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .models import BatchOperationResult
from .query_builder import InsertBuilder


@dataclass
class BatchConfig:
    """Configuration for batch operations."""
    batch_size: int = 1000
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    parallel_workers: int = 5
    timeout: float = 300.0  # seconds


class BatchProcessor:
    """Process batch operations efficiently."""

    def __init__(self, config: BatchConfig):
        self.config = config
        self._semaphore = asyncio.Semaphore(config.parallel_workers)

    async def _execute_batch(
        self,
        connection,
        query: str,
        params: Dict[str, Any],
    ) -> Tuple[int, Optional[str]]:
        """Execute a single batch with retry logic."""
        for attempt in range(self.config.max_retries):
            try:
                async with self._semaphore:
                    async with connection.cursor() as cursor:
                        await cursor.execute(query, params)
                        return cursor.rowcount, None
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    return 0, str(e)
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        return 0, "Max retries exceeded"

    async def batch_insert(
        self,
        connection,
        table_name: str,
        columns: List[str],
        values: List[List[Any]],
    ) -> BatchOperationResult:
        """Insert multiple rows in batches."""
        start_time = datetime.now()
        total_rows = len(values)
        processed_rows = 0
        failed_rows = 0
        error_messages = []

        # Process in batches
        for i in range(0, total_rows, self.config.batch_size):
            batch_values = values[i:i + self.config.batch_size]
            builder = InsertBuilder(table_name)
            builder.columns(*columns)
            builder.values(*batch_values)
            query, params = builder.build()

            rows_affected, error = await self._execute_batch(connection, query, params)
            processed_rows += rows_affected
            if error:
                failed_rows += len(batch_values) - rows_affected
                error_messages.append(
                    f"Batch {i // self.config.batch_size}: {error}")

        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        return BatchOperationResult(
            total_records=total_rows,
            processed_records=processed_rows,
            failed_records=failed_rows,
            execution_time_ms=duration_ms,
            error_messages=error_messages,
        )

    async def batch_update(
        self,
        connection,
        table_name: str,
        updates: List[Dict[str, Any]],
        key_columns: List[str],
    ) -> BatchOperationResult:
        """Update multiple rows in batches."""
        start_time = datetime.now()
        total_rows = len(updates)
        processed_rows = 0
        failed_rows = 0
        error_messages = []

        # Process in batches
        for i in range(0, total_rows, self.config.batch_size):
            batch_updates = updates[i:i + self.config.batch_size]

            # Build case statements for each column
            case_statements = {}
            for column in set().union(*(update.keys() for update in batch_updates)):
                if column not in key_columns:
                    cases = []
                    for j, update in enumerate(batch_updates):
                        if column in update:
                            conditions = [
                                f"{key} = {self._format_value(update[key])}"
                                for key in key_columns
                            ]
                            cases.append(
                                f"WHEN {' AND '.join(conditions)} "
                                f"THEN {self._format_value(update[column])}"
                            )
                    case_statements[column] = f"CASE {' '.join(cases)} ELSE {
                        column} END"

            # Build the update query
            if case_statements:
                set_clause = ", ".join(
                    f"{column} = {case_stmt}"
                    for column, case_stmt in case_statements.items()
                )
                where_conditions = []
                for update in batch_updates:
                    conditions = [
                        f"{key} = {self._format_value(update[key])}"
                        for key in key_columns
                    ]
                    where_conditions.append(f"({' AND '.join(conditions)})")
                query = f"UPDATE {table_name} SET {
                    set_clause} WHERE {' OR '.join(where_conditions)}"

                rows_affected, error = await self._execute_batch(connection, query, {})
                processed_rows += rows_affected
                if error:
                    failed_rows += len(batch_updates) - rows_affected
                    error_messages.append(
                        f"Batch {i // self.config.batch_size}: {error}")

        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        return BatchOperationResult(
            total_records=total_rows,
            processed_records=processed_rows,
            failed_records=failed_rows,
            execution_time_ms=duration_ms,
            error_messages=error_messages,
        )

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for SQL query."""
        if value is None:
            return "NULL"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, datetime):
            return f"'{value.isoformat()}'"
        else:
            return f"'{str(value)}'"


class BulkLoader:
    """Load data in bulk using COPY command."""

    def __init__(self, config: BatchConfig):
        self.config = config

    async def copy_from_s3(
        self,
        connection,
        table_name: str,
        s3_path: str,
        iam_role: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> BatchOperationResult:
        """Load data from S3 using COPY command."""
        start_time = datetime.now()
        error_message = None

        try:
            # Build COPY command
            copy_options = {
                'DELIMITER': ',',
                'IGNOREHEADER': 1,
                'DATEFORMAT': 'auto',
                'TIMEFORMAT': 'auto',
                'BLANKSASNULL': True,
                'EMPTYASNULL': True,
                'MAXERROR': 0,
                'STATUPDATE': True,
                'COMPUPDATE': True,
            }
            if options:
                copy_options.update(options)

            option_str = ' '.join(
                f"{key} {value if isinstance(value, bool) else str(value)}"
                for key, value in copy_options.items()
            )

            copy_command = f"""
                COPY {table_name}
                FROM '{s3_path}'
                IAM_ROLE '{iam_role}'
                {option_str}
            """

            # Execute COPY command
            async with connection.cursor() as cursor:
                await cursor.execute(copy_command)
                result = await cursor.fetchone()
                processed_rows = result[0] if result else 0

            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            return BatchOperationResult(
                total_records=processed_rows,
                processed_records=processed_rows,
                failed_records=0,
                execution_time_ms=duration_ms,
                error_messages=[],
            )

        except Exception as e:
            error_message = str(e)
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            return BatchOperationResult(
                total_records=0,
                processed_records=0,
                failed_records=0,
                execution_time_ms=duration_ms,
                error_messages=[error_message],
            )

    async def unload_to_s3(
        self,
        connection,
        query: str,
        s3_path: str,
        iam_role: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> BatchOperationResult:
        """Unload query results to S3 using UNLOAD command."""
        start_time = datetime.now()
        error_message = None

        try:
            # Build UNLOAD command
            unload_options = {
                'DELIMITER': ',',
                'HEADER': True,
                'GZIP': True,
                'ALLOWOVERWRITE': True,
                'PARALLEL': True,
                'MAXFILESIZE': 6.25 * 1024 ** 3,  # 6.25GB
            }
            if options:
                unload_options.update(options)

            option_str = ' '.join(
                f"{key} {value if isinstance(value, bool) else str(value)}"
                for key, value in unload_options.items()
            )

            unload_command = f"""
                UNLOAD ('{query}')
                TO '{s3_path}'
                IAM_ROLE '{iam_role}'
                {option_str}
            """

            # Execute UNLOAD command
            async with connection.cursor() as cursor:
                await cursor.execute(unload_command)
                result = await cursor.fetchone()
                processed_rows = result[0] if result else 0

            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            return BatchOperationResult(
                total_records=processed_rows,
                processed_records=processed_rows,
                failed_records=0,
                execution_time_ms=duration_ms,
                error_messages=[],
            )

        except Exception as e:
            error_message = str(e)
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            return BatchOperationResult(
                total_records=0,
                processed_records=0,
                failed_records=0,
                execution_time_ms=duration_ms,
                error_messages=[error_message],
            )
