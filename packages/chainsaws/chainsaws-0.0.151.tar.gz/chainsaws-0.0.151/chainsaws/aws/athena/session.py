"""Query session management for Athena."""
from typing import Optional, List, Dict
import logging

from chainsaws.aws.athena.athena import AthenaAPI
from chainsaws.aws.athena.athena_models import QueryResult, QueryExecution
from chainsaws.aws.athena.query_builder import QueryBuilder

logger = logging.getLogger(__name__)


class QuerySession:
    """A session for executing Athena queries with automatic cleanup."""

    def __init__(self, athena_api: "AthenaAPI", database: Optional[str] = None) -> None:
        """Initialize QuerySession.

        Args:
            athena_api: AthenaAPI instance
            database: Optional default database for this session
        """
        self.athena = athena_api
        self.database = database
        self._active_queries: List[str] = []
        self._results_cache: Dict[str, QueryResult] = {}

    def __enter__(self) -> "QuerySession":
        """Enter the context manager.

        Returns:
            QuerySession: Self for use in with statement
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager and cleanup resources.

        This will stop any running queries and clear the results cache.
        """
        self.cleanup()

    def execute(
        self,
        query: str,
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        timeout: int = 300,
    ) -> QueryResult:
        """Execute a query in this session.

        Args:
            query: SQL query to execute
            database: Database name (defaults to session's database)
            output_location: Result storage location
            timeout: Maximum time to wait for results in seconds

        Returns:
            QueryResult: Query execution result

        Raises:
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            InvalidQueryError: Invalid query syntax
        """
        try:
            result = self.athena.execute_query(
                query=query,
                database=database or self.database,
                output_location=output_location,
                timeout=timeout,
            )
            self._active_queries.append(result["QueryExecutionId"])
            self._results_cache[result["QueryExecutionId"]] = result
            return result
        except:
            # 예외가 발생하면 현재 쿼리를 중지하고 다시 발생시킴
            if self._active_queries:
                self.athena.stop_query(self._active_queries[-1])
            raise

    def execute_builder(
        self,
        builder: QueryBuilder,
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        timeout: int = 300,
    ) -> QueryResult:
        """Execute a query from QueryBuilder in this session.

        Args:
            builder: QueryBuilder instance
            database: Database name (defaults to session's database)
            output_location: Result storage location
            timeout: Maximum time to wait for results in seconds

        Returns:
            QueryResult: Query execution result

        Raises:
            ValueError: If query builder is missing required clauses
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            InvalidQueryError: Invalid query syntax
        """
        query = builder.build()
        return self.execute(
            query=query,
            database=database,
            output_location=output_location,
            timeout=timeout,
        )

    def get_active_queries(self) -> List[QueryExecution]:
        """Get status of all active queries in this session.

        Returns:
            List[QueryExecution]: List of query execution information
        """
        return [
            self.athena.get_query_status(query_id)
            for query_id in self._active_queries
        ]

    def get_cached_result(self, query_execution_id: str) -> Optional[QueryResult]:
        """Get cached result for a query.

        Args:
            query_execution_id: Query execution ID

        Returns:
            Optional[QueryResult]: Cached result if available
        """
        return self._results_cache.get(query_execution_id)

    def cleanup(self) -> None:
        """Stop all running queries and clear the cache."""
        for query_id in self._active_queries:
            try:
                self.athena.stop_query(query_id)
            except Exception as e:
                logger.warning(f"Failed to stop query {query_id}: {e!s}")

        self._active_queries.clear()
        self._results_cache.clear()
        logger.info("Query session cleaned up")
