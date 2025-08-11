"""Internal implementation of Athena API."""
import logging
from typing import Any, Dict, Optional, List

import boto3

from chainsaws.aws.athena.athena_models import (
    AthenaAPIConfig,
    QueryExecution,
    ResultSet,
    ListDatabasesResponse,
    Database,
    Table,
    ListTablesResponse,
    WorkGroup,
    ListWorkGroupsResponse,
    WorkGroupConfiguration,
    WorkGroupState,
)
from chainsaws.aws.athena.athena_exception import (
    QueryExecutionError,
    QueryCancellationError,
    InvalidQueryError,
)

logger = logging.getLogger(__name__)


class Athena:
    """Internal implementation of Athena service."""

    def __init__(
        self,
        boto3_session: boto3.Session,
        config: AthenaAPIConfig,
    ) -> None:
        """Initialize Athena client.

        Args:
            boto3_session: AWS session
            config: Athena API configuration
        """
        self.config = config
        self.client = boto3_session.client(
            service_name="athena",
            region_name=config.region,
        )

    def start_query_execution(
        self,
        query: str,
        database: Optional[str] = None,
        output_location: Optional[str] = None,
    ) -> str:
        """Start query execution.

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
        try:
            response = self.client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    "Database": database or self.config.database,
                },
                ResultConfiguration={
                    "OutputLocation": output_location or self.config.output_location,
                },
                WorkGroup=self.config.workgroup,
            )
            return response["QueryExecutionId"]
        except self.client.exceptions.InvalidRequestException as e:
            logger.exception(f"Invalid query: {e!s}")
            raise InvalidQueryError(str(e)) from e
        except Exception as e:
            logger.exception(f"Failed to start query execution: {e!s}")
            raise QueryExecutionError(str(e)) from e

    def get_query_execution(self, query_execution_id: str) -> QueryExecution:
        """Get query execution status.

        Args:
            query_execution_id: Query execution ID

        Returns:
            QueryExecution: Query execution information

        Raises:
            QueryExecutionError: Failed to get query status
        """
        try:
            response = self.client.get_query_execution(
                QueryExecutionId=query_execution_id)
            return response["QueryExecution"]
        except Exception as e:
            logger.exception(f"Failed to get query execution: {e!s}")
            raise QueryExecutionError(str(e)) from e

    def get_query_results(
        self,
        query_execution_id: str,
        next_token: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> ResultSet:
        """Get query results.

        Args:
            query_execution_id: Query execution ID
            next_token: Token for next page
            max_results: Maximum number of results

        Returns:
            ResultSet: Query results

        Raises:
            QueryExecutionError: Failed to get query results
        """
        try:
            params: Dict[str, Any] = {
                "QueryExecutionId": query_execution_id,
            }
            if next_token:
                params["NextToken"] = next_token
            if max_results:
                params["MaxResults"] = max_results

            response = self.client.get_query_results(**params)
            return response["ResultSet"]
        except Exception as e:
            logger.exception(f"Failed to get query results: {e!s}")
            raise QueryExecutionError(str(e)) from e

    def stop_query_execution(self, query_execution_id: str) -> None:
        """Stop query execution.

        Args:
            query_execution_id: Query execution ID

        Raises:
            QueryCancellationError: Failed to stop query execution
        """
        try:
            self.client.stop_query_execution(
                QueryExecutionId=query_execution_id)
        except Exception as e:
            logger.exception(f"Failed to stop query execution: {e!s}")
            raise QueryCancellationError(str(e)) from e

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
        """
        params = {}
        if next_token:
            params["NextToken"] = next_token
        if max_results:
            params["MaxResults"] = max_results

        response = self.client.list_databases(
            CatalogName=self.config.catalog_name,
            **params,
        )
        return ListDatabasesResponse(
            DatabaseList=response["DatabaseList"],
            NextToken=response.get("NextToken"),
        )

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
        """
        database_input: Database = {"Name": database_name}
        if description:
            database_input["Description"] = description

        properties = {}
        if location_uri:
            properties["LocationUri"] = location_uri
        if parameters:
            properties["Parameters"] = parameters

        if properties:
            database_input["Properties"] = properties

        self.client.create_database(
            CatalogName=self.config.catalog_name,
            DatabaseInput=database_input,
        )

    def delete_database(self, database_name: str) -> None:
        """Delete a database.

        Args:
            database_name: Name of the database to delete
        """
        self.client.delete_database(
            CatalogName=self.config.catalog_name,
            DatabaseName=database_name,
        )

    def get_database(self, database_name: str) -> Database:
        """Get database details.

        Args:
            database_name: Name of the database to get

        Returns:
            Database details
        """
        response = self.client.get_database(
            CatalogName=self.config.catalog_name,
            DatabaseName=database_name,
        )
        return response["Database"]

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
        """
        params = {}
        if next_token:
            params["NextToken"] = next_token
        if max_results:
            params["MaxResults"] = max_results

        response = self.client.list_tables(
            CatalogName=self.config.catalog_name,
            DatabaseName=database_name,
            **params,
        )
        return ListTablesResponse(
            TableList=response["TableList"],
            NextToken=response.get("NextToken"),
        )

    def get_table(self, database_name: str, table_name: str) -> Table:
        """Get table details.

        Args:
            database_name: Database containing the table
            table_name: Name of the table to get

        Returns:
            Table details
        """
        response = self.client.get_table(
            CatalogName=self.config.catalog_name,
            DatabaseName=database_name,
            TableName=table_name,
        )
        return response["Table"]

    def delete_table(self, database_name: str, table_name: str) -> None:
        """Delete a table.

        Args:
            database_name: Database containing the table
            table_name: Name of the table to delete
        """
        self.client.delete_table(
            CatalogName=self.config.catalog_name,
            DatabaseName=database_name,
            TableName=table_name,
        )

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
        """
        table_input: Dict[str, Any] = {
            "Name": table_name,
            "TableType": table_type or "EXTERNAL_TABLE",
            "StorageDescriptor": {
                "Location": location,
                "Columns": columns,
            },
        }

        if description:
            table_input["Description"] = description

        if parameters:
            table_input["Parameters"] = parameters

        self.client.create_table(
            CatalogName=self.config.catalog_name,
            DatabaseName=database_name,
            TableInput=table_input,
        )

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
        """
        params = {}
        if next_token:
            params["NextToken"] = next_token
        if max_results:
            params["MaxResults"] = max_results

        response = self.client.list_work_groups(**params)
        return ListWorkGroupsResponse(
            WorkGroups=response["WorkGroups"],
            NextToken=response.get("NextToken"),
        )

    def get_work_group(self, work_group_name: str) -> WorkGroup:
        """Get workgroup details.

        Args:
            work_group_name: Name of the workgroup to get

        Returns:
            WorkGroup details
        """
        response = self.client.get_work_group(WorkGroup=work_group_name)
        return response["WorkGroup"]

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
        """
        params: Dict[str, Any] = {
            "Name": work_group_name,
            "State": state,
        }

        if description:
            params["Description"] = description

        if configuration:
            params["Configuration"] = configuration

        self.client.create_work_group(**params)

    def delete_work_group(self, work_group_name: str) -> None:
        """Delete a workgroup.

        Args:
            work_group_name: Name of the workgroup to delete
        """
        self.client.delete_work_group(WorkGroup=work_group_name)

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
        """
        params: Dict[str, Any] = {
            "WorkGroup": work_group_name,
        }

        if description:
            params["Description"] = description

        if configuration:
            params["ConfigurationUpdates"] = configuration

        if state:
            params["State"] = state

        self.client.update_work_group(**params)
