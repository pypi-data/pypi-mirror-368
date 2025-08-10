"""Asynchronous query session for Athena."""

import asyncio
from typing import Optional, AsyncGenerator, Callable, Any, Dict, TYPE_CHECKING
import logging
from datetime import datetime

from chainsaws.aws.athena.athena_models import (
    QueryResult,
    QueryExecution,
    QueryExecutionState,
)
from chainsaws.aws.athena.athena_exception import (
    QueryExecutionError,
    QueryTimeoutError,
    QueryCancellationError,
)

if TYPE_CHECKING:
    from chainsaws.aws.athena.athena import AthenaAPI

logger = logging.getLogger(__name__)


class AsyncQueryExecution:
    """Asynchronous query execution handler."""

    def __init__(
        self,
        athena_api: "AthenaAPI",
        query_execution_id: str,
        on_progress: Optional[Callable[[float], None]] = None,
        on_partial_result: Optional[Callable[[QueryResult], None]] = None,
    ) -> None:
        """Initialize AsyncQueryExecution.

        Args:
            athena_api: AthenaAPI instance
            query_execution_id: Query execution ID
            on_progress: Optional callback for progress updates
            on_partial_result: Optional callback for partial results
        """
        self.athena = athena_api
        self.query_execution_id = query_execution_id
        self.on_progress = on_progress
        self.on_partial_result = on_partial_result
        self._start_time = datetime.now()

    async def wait_for_completion(self, timeout: float = 300.0) -> QueryExecution:
        """Wait for query completion asynchronously.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            QueryExecution: Final query execution state

        Raises:
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            QueryCancellationError: Query was cancelled
        """
        while True:
            execution = self.athena.get_query_status(self.query_execution_id)
            state = execution["Status"]["State"]

            # Calculate and report progress
            if self.on_progress:
                elapsed = (datetime.now() - self._start_time).total_seconds()
                progress = min(elapsed / timeout * 100,
                               99.0) if timeout > 0 else 0
                self.on_progress(progress)

            if state == QueryExecutionState.SUCCEEDED:
                if self.on_progress:
                    self.on_progress(100.0)
                return execution

            if state == QueryExecutionState.FAILED:
                reason = execution["Status"].get(
                    "StateChangeReason", "Unknown error")
                raise QueryExecutionError(f"Query execution failed: {reason}")

            if state == QueryExecutionState.CANCELLED:
                raise QueryCancellationError("Query was cancelled")

            if (datetime.now() - self._start_time).total_seconds() > timeout:
                raise QueryTimeoutError(
                    f"Query execution exceeded timeout of {timeout} seconds")

            await asyncio.sleep(1.0)

    async def stream_results(
        self,
        page_size: int = 1000,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream query results asynchronously.

        Args:
            page_size: Number of results per page

        Yields:
            Dict[str, Any]: Each row of the result set

        Raises:
            QueryExecutionError: Query execution failed or invalid state
        """
        next_token = None
        while True:
            result_set = self.athena.athena.get_query_results(
                query_execution_id=self.query_execution_id,
                next_token=next_token,
                max_results=page_size,
            )

            if self.on_partial_result:
                self.on_partial_result(result_set)

            for row in result_set["Rows"]:
                yield row

            next_token = result_set.get("NextToken")
            if not next_token:
                break

            await asyncio.sleep(0.1)  # Prevent too rapid requests


class AsyncSession:
    """Asynchronous session for executing Athena queries."""

    def __init__(self, athena_api: "AthenaAPI", database: Optional[str] = None) -> None:
        """Initialize AsyncSession.

        Args:
            athena_api: AthenaAPI instance
            database: Optional default database for this session
        """
        self.athena = athena_api
        self.database = database
        self._active_queries: set[str] = set()

    async def __aenter__(self) -> "AsyncSession":
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager and cleanup resources."""
        await self.cleanup()

    def execute_async(
        self,
        query: str,
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        on_progress: Optional[Callable[[float], None]] = None,
        on_partial_result: Optional[Callable[[QueryResult], None]] = None,
    ) -> AsyncQueryExecution:
        """Execute a query asynchronously.

        Args:
            query: SQL query to execute
            database: Database name (defaults to session's database)
            output_location: Result storage location
            on_progress: Optional callback for progress updates
            on_partial_result: Optional callback for partial results

        Returns:
            AsyncQueryExecution: Query execution handler

        Raises:
            QueryExecutionError: Failed to start query execution
        """
        execution_id = self.athena.execute_query_async(
            query=query,
            database=database or self.database,
            output_location=output_location,
        )
        self._active_queries.add(execution_id)
        return AsyncQueryExecution(
            self.athena,
            execution_id,
            on_progress=on_progress,
            on_partial_result=on_partial_result,
        )

    async def cleanup(self) -> None:
        """Stop all running queries and clear the session."""
        for query_id in self._active_queries:
            try:
                self.athena.stop_query(query_id)
            except Exception as e:
                logger.warning(f"Failed to stop query {query_id}: {e!s}")

        self._active_queries.clear()
        logger.info("Async query session cleaned up")
