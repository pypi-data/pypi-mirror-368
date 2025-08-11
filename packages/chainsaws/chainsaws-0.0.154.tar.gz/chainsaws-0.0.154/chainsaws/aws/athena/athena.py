"""High-level API for AWS Athena."""

from contextlib import contextmanager, asynccontextmanager
import logging
import time
from typing import Any, Dict, Optional, Generator, List, Callable, BinaryIO, Union, TypeVar, AsyncGenerator, Type
import asyncio
from pathlib import Path

from chainsaws.aws.athena._athena_internal import Athena
from chainsaws.aws.athena.athena_models import (
    AthenaAPIConfig,
    QueryExecution,
    QueryExecutionState,
    QueryResult,
    Database,
    ListDatabasesResponse,
    Table,
    ListTablesResponse,
    WorkGroup,
    ListWorkGroupsResponse,
    WorkGroupConfiguration,
    WorkGroupState,
    PartitionResponse,
    QueryAnalysis,
    TypedQueryResult,
    QueryPerformanceReport,
    DetailedError,
)
from chainsaws.aws.athena.athena_exception import (
    QueryExecutionError,
    QueryTimeoutError,
    QueryCancellationError,
    InvalidQueryError,
    ResultError,
)
from chainsaws.aws.athena.template import QueryTemplate
from chainsaws.aws.shared import session
from chainsaws.aws.s3 import S3API
from chainsaws.aws.athena.query_builder import QueryBuilder
from chainsaws.aws.athena.session import QuerySession
from chainsaws.aws.athena.async_session import AsyncSession

logger = logging.getLogger(__name__)

T = TypeVar('T')


class AthenaAPI:
    """High-level API for AWS Athena operations."""

    def __init__(self, config: AthenaAPIConfig) -> None:
        """Initialize Athena API.

        Args:
            config: Athena API configuration
        """
        self.config = config
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.athena = Athena(
            boto3_session=self.boto3_session,
            config=config,
        )
        # S3 클라이언트 초기화
        self.s3 = S3API(
            bucket_name=config.result_store_bucket,
            region=config.region,
            credentials=config.credentials if config.credentials else None,
        )

    def execute_query(
        self,
        query: str,
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        timeout: int = 300,
        poll_interval: int = 1,
    ) -> QueryResult:
        """Execute a query and wait for results.

        Args:
            query: SQL query to execute
            database: Database name (defaults to config's database)
            output_location: Result storage location (defaults to config's output_location)
            timeout: Maximum time to wait for results in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            QueryResult: Query execution result including results if successful

        Raises:
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            InvalidQueryError: Invalid query syntax
        """
        try:
            # Start query execution
            execution_id = self.athena.start_query_execution(
                query=query,
                database=database,
                output_location=output_location or self.config.get_output_location(),
            )

            # Wait for completion
            start_time = time.time()
            while True:
                if time.time() - start_time > timeout:
                    self.athena.stop_query_execution(execution_id)
                    msg = f"Query execution exceeded timeout of {
                        timeout} seconds"
                    raise QueryTimeoutError(msg)

                execution = self.athena.get_query_execution(execution_id)
                state = execution["Status"]["State"]

                if state == QueryExecutionState.SUCCEEDED:
                    # Get results for successful query
                    result_set = self.athena.get_query_results(execution_id)
                    return QueryResult(
                        QueryExecutionId=execution_id,
                        Query=query,
                        State=state,
                        Statistics=execution.get("Statistics"),
                        ResultSet=result_set,
                    )

                if state == QueryExecutionState.FAILED:
                    reason = execution["Status"].get(
                        "StateChangeReason", "Unknown error")
                    raise QueryExecutionError(
                        f"Query execution failed: {reason}")

                if state == QueryExecutionState.CANCELLED:
                    raise QueryCancellationError("Query was cancelled")

                time.sleep(poll_interval)

        except (QueryTimeoutError, QueryExecutionError, QueryCancellationError, InvalidQueryError):
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during query execution: {e!s}")
            raise QueryExecutionError(str(e)) from e

    def execute_query_async(
        self,
        query: str,
        database: Optional[str] = None,
        output_location: Optional[str] = None,
    ) -> str:
        """Execute a query asynchronously.

        Args:
            query: SQL query to execute
            database: Database name (defaults to config's database)
            output_location: Result storage location (defaults to config's output_location)

        Returns:
            str: Query execution ID

        Raises:
            InvalidQueryError: Invalid query syntax
            QueryExecutionError: Failed to start query execution
        """
        return self.athena.start_query_execution(
            query=query,
            database=database,
            output_location=output_location,
        )

    def get_query_results(
        self,
        query_execution_id: str,
        wait: bool = True,
        timeout: int = 300,
        poll_interval: int = 1,
    ) -> QueryResult:
        """Get results of a query execution.

        Args:
            query_execution_id: Query execution ID
            wait: Whether to wait for query completion
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            QueryResult: Query execution result including results if successful

        Raises:
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            ResultError: Failed to get query results
        """
        try:
            start_time = time.time()
            while True:
                execution = self.athena.get_query_execution(query_execution_id)
                state = execution["Status"]["State"]

                if state == QueryExecutionState.SUCCEEDED:
                    result_set = self.athena.get_query_results(
                        query_execution_id)
                    return QueryResult(
                        QueryExecutionId=query_execution_id,
                        Query=execution["Query"],
                        State=state,
                        Statistics=execution.get("Statistics"),
                        ResultSet=result_set,
                    )

                if state == QueryExecutionState.FAILED:
                    reason = execution["Status"].get(
                        "StateChangeReason", "Unknown error")
                    raise QueryExecutionError(
                        f"Query execution failed: {reason}")

                if state == QueryExecutionState.CANCELLED:
                    raise QueryCancellationError("Query was cancelled")

                if not wait:
                    return QueryResult(
                        QueryExecutionId=query_execution_id,
                        Query=execution["Query"],
                        State=state,
                        Statistics=execution.get("Statistics"),
                    )

                if time.time() - start_time > timeout:
                    msg = f"Query execution exceeded timeout of {
                        timeout} seconds"
                    raise QueryTimeoutError(msg)

                time.sleep(poll_interval)

        except (QueryTimeoutError, QueryExecutionError, QueryCancellationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to get query results: {e!s}")
            raise ResultError(str(e)) from e

    def get_query_results_iterator(
        self,
        query_execution_id: str,
        page_size: int = 1000,
    ) -> Generator[Dict[str, Any], None, None]:
        """Get query results with pagination.

        Args:
            query_execution_id: Query execution ID
            page_size: Number of results per page

        Yields:
            Dict[str, Any]: Each row of the result set

        Raises:
            QueryExecutionError: Query execution failed or invalid state
            ResultError: Failed to get query results
        """
        try:
            next_token = None
            while True:
                result_set = self.athena.get_query_results(
                    query_execution_id=query_execution_id,
                    next_token=next_token,
                    max_results=page_size,
                )

                for row in result_set["Rows"]:
                    yield row

                next_token = result_set.get("NextToken")
                if not next_token:
                    break

        except Exception as e:
            logger.exception(f"Failed to get query results: {e!s}")
            raise ResultError(str(e)) from e

    def stop_query(self, query_execution_id: str) -> None:
        """Stop a running query.

        Args:
            query_execution_id: Query execution ID

        Raises:
            QueryCancellationError: Failed to stop query
        """
        self.athena.stop_query_execution(query_execution_id)

    def get_query_status(self, query_execution_id: str) -> QueryExecution:
        """Get current status of a query execution.

        Args:
            query_execution_id: Query execution ID

        Returns:
            QueryExecution: Current query execution information

        Raises:
            QueryExecutionError: Failed to get query status
        """
        return self.athena.get_query_execution(query_execution_id)

    def list_databases(
        self,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> ListDatabasesResponse:
        """List available databases.

        Args:
            next_token: Token for the next page of results
            max_results: Maximum number of results to return

        Returns:
            ListDatabasesResponse containing the list of databases

        Raises:
            Exception: If the operation fails
        """
        try:
            return self.athena.list_databases(
                next_token=next_token,
                max_results=max_results,
            )
        except Exception as e:
            logger.exception(f"Failed to list databases: {e!s}")
            raise

    def create_database(
        self,
        database_name: str,
        description: Optional[str] = None,
        location_uri: Optional[str] = None,
        parameters: Optional[Dict[str, str]] = None,
    ) -> None:
        """Create a new database.

        Args:
            database_name: Name of the database to create
            description: Optional description of the database
            location_uri: Optional S3 location for the database
            parameters: Optional parameters for the database

        Raises:
            Exception: If the operation fails
        """
        try:
            self.athena.create_database(
                database_name=database_name,
                description=description,
                location_uri=location_uri,
                parameters=parameters,
            )
        except Exception as e:
            logger.exception(f"Failed to create database: {e!s}")
            raise

    def delete_database(self, database_name: str) -> None:
        """Delete a database.

        Args:
            database_name: Name of the database to delete

        Raises:
            Exception: If the operation fails
        """
        try:
            self.athena.delete_database(database_name=database_name)
        except Exception as e:
            logger.exception(f"Failed to delete database: {e!s}")
            raise

    def get_database(self, database_name: str) -> Database:
        """Get database details.

        Args:
            database_name: Name of the database to get

        Returns:
            Database details

        Raises:
            Exception: If the operation fails
        """
        try:
            return self.athena.get_database(database_name=database_name)
        except Exception as e:
            logger.exception(f"Failed to get database: {e!s}")
            raise

    def list_tables(
        self,
        database_name: str,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> ListTablesResponse:
        """List tables in a database.

        Args:
            database_name: Database to list tables from
            next_token: Token for the next page of results
            max_results: Maximum number of results to return

        Returns:
            ListTablesResponse containing the list of tables

        Raises:
            Exception: If the operation fails
        """
        try:
            return self.athena.list_tables(
                database_name=database_name,
                next_token=next_token,
                max_results=max_results,
            )
        except Exception as e:
            logger.exception(f"Failed to list tables: {e!s}")
            raise

    def get_table(self, database_name: str, table_name: str) -> Table:
        """Get table details.

        Args:
            database_name: Database containing the table
            table_name: Name of the table to get

        Returns:
            Table details

        Raises:
            Exception: If the operation fails
        """
        try:
            return self.athena.get_table(
                database_name=database_name,
                table_name=table_name,
            )
        except Exception as e:
            logger.exception(f"Failed to get table: {e!s}")
            raise

    def delete_table(self, database_name: str, table_name: str) -> None:
        """Delete a table.

        Args:
            database_name: Database containing the table
            table_name: Name of the table to delete

        Raises:
            Exception: If the operation fails
        """
        try:
            self.athena.delete_table(
                database_name=database_name,
                table_name=table_name,
            )
        except Exception as e:
            logger.exception(f"Failed to delete table: {e!s}")
            raise

    def create_table(
        self,
        database_name: str,
        table_name: str,
        columns: List[Dict[str, str]],
        location: str,
        description: Optional[str] = None,
        table_type: Optional[str] = None,
        parameters: Optional[Dict[str, str]] = None,
    ) -> None:
        """Create a new table.

        Args:
            database_name: Database to create table in
            table_name: Name of the table to create
            columns: List of column definitions
            location: S3 location of the table data
            description: Optional table description
            table_type: Optional table type
            parameters: Optional table parameters

        Raises:
            Exception: If the operation fails
        """
        try:
            self.athena.create_table(
                database_name=database_name,
                table_name=table_name,
                columns=columns,
                location=location,
                description=description,
                table_type=table_type,
                parameters=parameters,
            )
        except Exception as e:
            logger.exception(f"Failed to create table: {e!s}")
            raise

    def list_work_groups(
        self,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> ListWorkGroupsResponse:
        """List workgroups.

        Args:
            next_token: Token for the next page of results
            max_results: Maximum number of results to return

        Returns:
            ListWorkGroupsResponse containing the list of workgroups

        Raises:
            Exception: If the operation fails
        """
        try:
            return self.athena.list_work_groups(
                next_token=next_token,
                max_results=max_results,
            )
        except Exception as e:
            logger.exception(f"Failed to list workgroups: {e!s}")
            raise

    def get_work_group(self, work_group_name: str) -> WorkGroup:
        """Get workgroup details.

        Args:
            work_group_name: Name of the workgroup to get

        Returns:
            WorkGroup details

        Raises:
            Exception: If the operation fails
        """
        try:
            return self.athena.get_work_group(work_group_name=work_group_name)
        except Exception as e:
            logger.exception(f"Failed to get workgroup: {e!s}")
            raise

    def create_work_group(
        self,
        work_group_name: str,
        description: Optional[str] = None,
        configuration: Optional[WorkGroupConfiguration] = None,
        state: WorkGroupState = WorkGroupState.ENABLED,
    ) -> None:
        """Create a new workgroup.

        Args:
            work_group_name: Name of the workgroup to create
            description: Optional workgroup description
            configuration: Optional workgroup configuration
            state: Initial state of the workgroup

        Raises:
            Exception: If the operation fails
        """
        try:
            self.athena.create_work_group(
                work_group_name=work_group_name,
                description=description,
                configuration=configuration,
                state=state,
            )
        except Exception as e:
            logger.exception(f"Failed to create workgroup: {e!s}")
            raise

    def delete_work_group(self, work_group_name: str) -> None:
        """Delete a workgroup.

        Args:
            work_group_name: Name of the workgroup to delete

        Raises:
            Exception: If the operation fails
        """
        try:
            self.athena.delete_work_group(work_group_name=work_group_name)
        except Exception as e:
            logger.exception(f"Failed to delete workgroup: {e!s}")
            raise

    def update_work_group(
        self,
        work_group_name: str,
        description: Optional[str] = None,
        configuration: Optional[WorkGroupConfiguration] = None,
        state: Optional[WorkGroupState] = None,
    ) -> None:
        """Update a workgroup.

        Args:
            work_group_name: Name of the workgroup to update
            description: Optional new description
            configuration: Optional new configuration
            state: Optional new state

        Raises:
            Exception: If the operation fails
        """
        try:
            self.athena.update_work_group(
                work_group_name=work_group_name,
                description=description,
                configuration=configuration,
                state=state,
            )
        except Exception as e:
            logger.exception(f"Failed to update workgroup: {e!s}")
            raise

    async def monitor_query_execution(
        self,
        query_execution_id: str,
        poll_interval: float = 1.0,
        callback: Optional[Callable[[QueryExecution], None]] = None,
    ) -> QueryExecution:
        """Monitor a query execution asynchronously.

        Args:
            query_execution_id: Query execution ID
            poll_interval: Time between status checks in seconds
            callback: Optional callback function to handle status updates

        Returns:
            QueryExecution: Final query execution state

        Raises:
            QueryExecutionError: Query execution failed
        """
        while True:
            execution = self.get_query_status(query_execution_id)

            if callback:
                callback(execution)

            state = execution["Status"]["State"]
            if state in [QueryExecutionState.SUCCEEDED, QueryExecutionState.FAILED, QueryExecutionState.CANCELLED]:
                if state == QueryExecutionState.FAILED:
                    reason = execution["Status"].get(
                        "StateChangeReason", "Unknown error")
                    raise QueryExecutionError(
                        f"Query execution failed: {reason}")
                if state == QueryExecutionState.CANCELLED:
                    raise QueryCancellationError("Query was cancelled")
                return execution

            await asyncio.sleep(poll_interval)

    def add_partition(
        self,
        database_name: str,
        table_name: str,
        partition_values: Dict[str, str],
        location: str,
    ) -> None:
        """Add a partition to a table.

        Args:
            database_name: Database containing the table
            table_name: Name of the table
            partition_values: Dictionary of partition keys and values
            location: S3 location of the partition data

        Raises:
            Exception: If the operation fails
        """
        try:
            partition_input = {
                "Values": list(partition_values.values()),
                "StorageDescriptor": {
                    "Location": location,
                },
            }

            self.athena.client.create_partition(
                CatalogName=self.athena.config.catalog_name,
                DatabaseName=database_name,
                TableName=table_name,
                PartitionInput=partition_input,
            )
        except Exception as e:
            logger.exception(f"Failed to add partition: {e!s}")
            raise

    def list_partitions(
        self,
        database_name: str,
        table_name: str,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> PartitionResponse:
        """List partitions of a table.

        Args:
            database_name: Database containing the table
            table_name: Name of the table
            next_token: Token for the next page of results
            max_results: Maximum number of results to return

        Returns:
            PartitionResponse containing the list of partitions

        Raises:
            Exception: If the operation fails
        """
        try:
            params = {}
            if next_token:
                params["NextToken"] = next_token
            if max_results:
                params["MaxResults"] = max_results

            response = self.athena.client.list_partitions(
                CatalogName=self.athena.config.catalog_name,
                DatabaseName=database_name,
                TableName=table_name,
                **params,
            )

            return PartitionResponse(
                Partitions=response["Partitions"],
                NextToken=response.get("NextToken"),
            )
        except Exception as e:
            logger.exception(f"Failed to list partitions: {e!s}")
            raise

    def analyze_query(
        self,
        query: str,
        database: Optional[str] = None,
    ) -> QueryAnalysis:
        """Analyze a query for performance and cost estimation.

        Args:
            query: SQL query to analyze
            database: Optional database name for context

        Returns:
            QueryAnalysis containing performance metrics and recommendations

        Raises:
            Exception: If the operation fails
        """
        try:
            # Start query execution with EXPLAIN
            explain_query = f"EXPLAIN {query}"
            execution_id = self.execute_query_async(
                query=explain_query,
                database=database,
            )

            # Wait for execution to complete
            while True:
                execution = self.get_query_status(execution_id)
                state = execution["Status"]["State"]

                if state == QueryExecutionState.SUCCEEDED:
                    break
                if state in [QueryExecutionState.FAILED, QueryExecutionState.CANCELLED]:
                    raise QueryExecutionError(
                        f"Query analysis failed with state: {state}")

                time.sleep(1)

            # Get execution statistics
            stats = execution.get("Statistics", {})
            engine_version = execution.get("EngineVersion", {}).get(
                "EffectiveEngineVersion", "Unknown")

            # Calculate cost estimate (assuming $5 per TB scanned)
            data_scanned_tb = float(
                stats.get("DataScannedInBytes", 0)) / (1024 ** 4)
            cost_estimate = data_scanned_tb * 5

            # Generate optimization recommendations
            recommendations = []
            if data_scanned_tb > 1:
                recommendations.append(
                    "Consider adding partition pruning to reduce data scan")
            if stats.get("TotalExecutionTimeInMillis", 0) > 30000:
                recommendations.append("Consider optimizing JOIN conditions")

            return QueryAnalysis(
                ExecutionTime=float(
                    stats.get("TotalExecutionTimeInMillis", 0)) / 1000,
                DataScanned=float(stats.get("DataScannedInBytes", 0)),
                CostEstimate=cost_estimate,
                EngineVersion=engine_version,
                Statistics=stats,
                RecommendedOptimizations=recommendations,
            )

        except Exception as e:
            logger.exception(f"Failed to analyze query: {e!s}")
            raise

    def download_query_results(
        self,
        query_execution_id: str,
        output_path: Union[str, Path, BinaryIO],
        wait_for_completion: bool = True,
        timeout: int = 300,
    ) -> None:
        """Download query results directly from S3.

        Args:
            query_execution_id: Query execution ID
            output_path: Local path or file object to save results
            wait_for_completion: Whether to wait for query completion
            timeout: Maximum time to wait for query completion in seconds

        Raises:
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            ResultError: Failed to download results
        """
        try:
            if wait_for_completion:
                # Wait for query completion
                start_time = time.time()
                while True:
                    if time.time() - start_time > timeout:
                        raise QueryTimeoutError(
                            f"Query execution exceeded timeout of {timeout} seconds")

                    execution = self.get_query_status(query_execution_id)
                    state = execution["Status"]["State"]

                    if state == QueryExecutionState.SUCCEEDED:
                        break
                    if state == QueryExecutionState.FAILED:
                        reason = execution["Status"].get(
                            "StateChangeReason", "Unknown error")
                        raise QueryExecutionError(
                            f"Query execution failed: {reason}")
                    if state == QueryExecutionState.CANCELLED:
                        raise QueryCancellationError("Query was cancelled")

                    time.sleep(1)

            # Get S3 path
            output_config = self.athena.client.get_query_execution(
                QueryExecutionId=query_execution_id
            )["QueryExecution"]["ResultConfiguration"]

            s3_output_location = output_config["OutputLocation"]

            # Download file from S3
            self.s3.download_file(
                s3_uri=s3_output_location,
                output_path=output_path,
            )

        except (QueryTimeoutError, QueryExecutionError, QueryCancellationError):
            raise
        except Exception as e:
            logger.exception(f"Failed to download query results: {e!s}")
            raise ResultError(str(e)) from e

    def execute_query_to_file(
        self,
        query: str,
        output_path: Union[str, Path, BinaryIO],
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        timeout: int = 300,
    ) -> None:
        """Execute a query and download results directly to a file.

        Args:
            query: SQL query
            output_path: Local path or file object to save results
            database: Database name (defaults to config's database)
            output_location: Result storage location (defaults to config's output_location)
            timeout: Maximum time to wait in seconds

        Raises:
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            InvalidQueryError: Invalid query syntax
            ResultError: Failed to download results
        """
        result = self.execute_query(
            query=query,
            database=database,
            output_location=output_location,
            timeout=timeout,
        )
        self.download_query_results(
            query_execution_id=result["QueryExecutionId"],
            output_path=output_path,
            wait_for_completion=False,  # Already confirmed completion in execute_query
        )

    def get_query_output_location(self, query_execution_id: str) -> str:
        """Get the S3 location of query results.

        Args:
            query_execution_id: Query execution ID

        Returns:
            str: S3 URI of query results

        Raises:
            QueryExecutionError: Failed to get query information
        """
        try:
            output_config = self.athena.client.get_query_execution(
                QueryExecutionId=query_execution_id
            )["QueryExecution"]["ResultConfiguration"]
            return output_config["OutputLocation"]
        except Exception as e:
            logger.exception(f"Failed to get query output location: {e!s}")
            raise QueryExecutionError(str(e)) from e

    def create_query(self) -> QueryBuilder:
        """Create a new query builder instance.

        Returns:
            QueryBuilder: New query builder instance
        """
        return QueryBuilder()

    def execute_builder(
        self,
        builder: QueryBuilder,
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        timeout: int = 300,
        poll_interval: int = 1,
    ) -> QueryResult:
        """Execute a query from QueryBuilder.

        Args:
            builder: QueryBuilder instance
            database: Database name (defaults to config's database)
            output_location: Result storage location (defaults to config's output_location)
            timeout: Maximum time to wait for results in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            QueryResult: Query execution result including results if successful

        Raises:
            ValueError: If query builder is missing required clauses
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            InvalidQueryError: Invalid query syntax
        """
        query = builder.build()
        return self.execute_query(
            query=query,
            database=database,
            output_location=output_location,
            timeout=timeout,
            poll_interval=poll_interval,
        )

    def create_session(self, database: Optional[str] = None) -> QuerySession:
        """Create a new query session.

        Args:
            database: Optional default database for the session

        Returns:
            QuerySession: New query session instance
        """
        return QuerySession(self, database)

    @contextmanager
    def session(self, database: Optional[str] = None) -> Generator[QuerySession, None, None]:
        """Create a query session as a context manager.

        Args:
            database: Optional default database for the session

        Returns:
            Generator[QuerySession, None, None]: Query session for use in with statement

        Example:
            with athena.session("my_database") as session:
                result = session.execute("SELECT * FROM my_table")
        """
        session = self.create_session(database)
        try:
            yield session
        finally:
            session.cleanup()

    def create_template(self, template: str) -> "QueryTemplate":
        """Create a new query template.

        Args:
            template: SQL query template with named parameters

        Returns:
            QueryTemplate: New query template instance

        Example:
            template = athena.create_template(
                "SELECT * FROM {table} WHERE year = {year}"
            )
            result = template.execute(table="sales", year=2023)
        """
        from chainsaws.aws.athena.template import QueryTemplate
        return QueryTemplate(self, template)

    def analyze_query_performance(
        self,
        query: str,
        database: Optional[str] = None,
    ) -> QueryPerformanceReport:
        """Analyze query performance and provide optimization suggestions.

        Args:
            query: SQL query to analyze
            database: Optional database name for context

        Returns:
            QueryPerformanceReport: Performance analysis report

        Raises:
            QueryExecutionError: Failed to analyze query
        """
        try:
            # Execute EXPLAIN query
            explain_result = self.execute_query(
                query=f"EXPLAIN {query}",
                database=database,
            )

            # Parse EXPLAIN output
            explain_output = explain_result["ResultSet"]["Rows"]

            # Extract query plan information
            plan_info = self._parse_explain_output(explain_output)

            # Execute EXPLAIN ANALYZE for more detailed statistics
            analyze_result = self.execute_query(
                query=f"EXPLAIN ANALYZE {query}",
                database=database,
            )

            # Calculate metrics
            stats = analyze_result.get("Statistics", {})
            execution_time = float(
                stats.get("TotalExecutionTimeInMillis", 0)) / 1000
            data_scanned = int(stats.get("DataScannedInBytes", 0))
            cost_estimate = data_scanned / (1024 ** 4) * 5  # $5 per TB

            # Generate optimization suggestions
            suggestions = []
            bottlenecks = []
            optimization_tips = []

            # Check data scan size
            if data_scanned > 1024 ** 4:  # 1 TB
                suggestions.append(
                    "Consider adding partition pruning to reduce data scan")
                optimization_tips.append(
                    "Add WHERE clause on partitioned columns")

            # Check execution time
            if execution_time > 60:  # 1 minute
                suggestions.append("Query execution time is high")
                optimization_tips.append("Consider optimizing JOIN conditions")
                bottlenecks.append("Slow query execution")

            # Check for full table scans
            if "FullScan" in str(plan_info):
                suggestions.append("Full table scan detected")
                optimization_tips.append("Add appropriate WHERE clauses")
                bottlenecks.append("Full table scan")

            # Determine risk level
            risk_level = "LOW"
            # 5 TB or 5 minutes
            if data_scanned > 5 * (1024 ** 4) or execution_time > 300:
                risk_level = "HIGH"
            elif data_scanned > 1024 ** 4 or execution_time > 60:  # 1 TB or 1 minute
                risk_level = "MEDIUM"

            return QueryPerformanceReport(
                execution_time=execution_time,
                data_scanned=data_scanned,
                cost_estimate=cost_estimate,
                engine_version=analyze_result.get("EngineVersion", {}).get(
                    "EffectiveEngineVersion", "Unknown"),
                suggestions=suggestions,
                risk_level=risk_level,
                bottlenecks=bottlenecks,
                optimization_tips=optimization_tips,
                partition_info=plan_info.get("partitions"),
                join_info=plan_info.get("joins"),
            )

        except Exception as e:
            logger.exception(f"Failed to analyze query performance: {e!s}")
            raise QueryExecutionError(str(e)) from e

    def _parse_explain_output(self, explain_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse EXPLAIN output to extract query plan information.

        Args:
            explain_rows: Raw EXPLAIN output rows

        Returns:
            Dict[str, Any]: Parsed query plan information
        """
        plan_info = {
            "partitions": {},
            "joins": {},
            "scans": [],
        }

        for row in explain_rows:
            row_str = str(row)

            # Extract partition information
            if "Partition pruning:" in row_str:
                plan_info["partitions"]["pruned"] = "enabled" in row_str.lower()

            # Extract join information
            if "Join Operator:" in row_str:
                join_type = "BROADCAST" if "broadcast" in row_str.lower() else "SHUFFLE"
                plan_info["joins"][f"join_{len(plan_info['joins'])}"] = {
                    "type": join_type,
                    "description": row_str,
                }

            # Extract scan information
            if "Table Scan:" in row_str:
                plan_info["scans"].append(row_str)

        return plan_info

    def execute_typed(
        self,
        query: str,
        output_type: Type[T],
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        timeout: int = 300,
    ) -> TypedQueryResult[T]:
        """Execute a query and return strongly typed results.

        Args:
            query: SQL query to execute
            output_type: Type for the result rows
            database: Database name (defaults to config's database)
            output_location: Result storage location
            timeout: Maximum time to wait in seconds

        Returns:
            TypedQueryResult[T]: Query results with strongly typed data

        Raises:
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            InvalidQueryError: Invalid query syntax
        """
        result = self.execute_query(
            query=query,
            database=database,
            output_location=output_location,
            timeout=timeout,
        )
        return TypedQueryResult.from_query_result(result, output_type)

    def create_async_session(self, database: Optional[str] = None) -> AsyncSession:
        """Create a new async query session.

        Args:
            database: Optional default database for the session

        Returns:
            AsyncSession: New async session instance
        """
        from chainsaws.aws.athena.async_session import AsyncSession
        return AsyncSession(self, database)

    @asynccontextmanager
    async def async_session(self, database: Optional[str] = None) -> AsyncGenerator[AsyncSession, None]:
        """Create an async query session as a context manager.

        Args:
            database: Optional default database for the session

        Returns:
            AsyncGenerator[AsyncSession, None]: Async session for use in async with statement

        Example:
            async with athena.async_session("my_database") as session:
                query = await session.execute_async("SELECT * FROM my_table")
                async for row in query.stream_results():
                    process_row(row)
        """
        session = self.create_async_session(database)
        try:
            yield session
        finally:
            await session.cleanup()

    def handle_error(self, error: Exception) -> DetailedError:
        """Create detailed error information from an exception.

        Args:
            error: Exception to analyze

        Returns:
            DetailedError: Detailed error information with suggestions
        """
        if isinstance(error, QueryTimeoutError):
            return DetailedError(
                error_code="TIMEOUT",
                message=str(error),
                details={"timeout_seconds": 300},  # Default timeout
                suggestions=[
                    "Consider using async execution for long-running queries",
                    "Optimize query to reduce execution time",
                    "Increase timeout value if needed",
                ],
                query_stage="EXECUTION",
                error_type="TIMEOUT",
            )

        if isinstance(error, InvalidQueryError):
            return DetailedError(
                error_code="INVALID_QUERY",
                message=str(error),
                details={},
                suggestions=[
                    "Check query syntax",
                    "Verify table and column names",
                    "Ensure all referenced tables exist",
                ],
                query_stage="VALIDATION",
                error_type="SYNTAX",
            )

        if isinstance(error, QueryExecutionError):
            error_str = str(error).lower()

            if "permission" in error_str:
                return DetailedError(
                    error_code="PERMISSION_DENIED",
                    message=str(error),
                    details={},
                    suggestions=[
                        "Check IAM permissions",
                        "Verify access to S3 bucket",
                        "Ensure workgroup permissions are correct",
                    ],
                    query_stage="EXECUTION",
                    error_type="PERMISSION",
                )

            if "resource not found" in error_str:
                return DetailedError(
                    error_code="RESOURCE_NOT_FOUND",
                    message=str(error),
                    details={},
                    suggestions=[
                        "Verify database exists",
                        "Check table existence",
                        "Ensure S3 location is accessible",
                    ],
                    query_stage="EXECUTION",
                    error_type="RESOURCE",
                )

            return DetailedError(
                error_code="EXECUTION_ERROR",
                message=str(error),
                details={},
                suggestions=[
                    "Check query logic",
                    "Verify data types match",
                    "Ensure sufficient resources",
                ],
                query_stage="EXECUTION",
                error_type="EXECUTION",
            )

        return DetailedError(
            error_code="UNKNOWN",
            message=str(error),
            details={},
            suggestions=[
                "Check AWS service status",
                "Verify network connectivity",
                "Review CloudWatch logs",
            ],
            query_stage="UNKNOWN",
            error_type="UNKNOWN",
        )
