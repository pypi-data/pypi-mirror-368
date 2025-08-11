"""Query template management for Athena."""
from typing import Any, Optional, Union, BinaryIO
from pathlib import Path
import re
from string import Formatter

from chainsaws.aws.athena.athena_models import QueryResult
from chainsaws.aws.athena.athena import AthenaAPI


class QueryTemplate:
    """Template for parameterized Athena queries."""

    def __init__(self, athena_api: "AthenaAPI", template: str) -> None:
        """Initialize QueryTemplate.

        Args:
            athena_api: AthenaAPI instance
            template: SQL query template with named parameters

        Raises:
            ValueError: If template format is invalid
        """
        self.athena = athena_api
        self.template = template
        self._validate_template()

    def _validate_template(self) -> None:
        """Validate the template format.

        Raises:
            ValueError: If template format is invalid
        """
        # Validate Python string formatting
        try:
            field_names = [
                fname for _, fname, _, _ in Formatter().parse(self.template)
                if fname is not None
            ]
            if len(set(field_names)) != len(field_names):
                raise ValueError("Duplicate parameter names in template")
        except Exception as e:
            raise ValueError(f"Invalid template format: {e}")

        # Basic validation for SQL injection prevention
        dangerous_patterns = [
            r';\s*$',  # Query terminator
            r'--',     # Comment
            r'/\*',    # Block comment start
            r'\*/',    # Block comment end
            r'xp_',    # SQL Server stored procedure
            r'sp_',    # SQL Server stored procedure
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, self.template, re.IGNORECASE):
                raise ValueError(
                    f"Template contains potentially dangerous pattern: {pattern}")

    def _format_value(self, value: Any) -> str:
        """Format a value for SQL query.

        Args:
            value: Value to format

        Returns:
            str: SQL-safe formatted value
        """
        if value is None:
            return "NULL"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            return "(" + ", ".join(self._format_value(v) for v in value) + ")"
        else:
            # Escape string
            return f"'{str(value).replace("'", "''")}'"

    def render(self, **params: Any) -> str:
        """Render the template with parameters.

        Args:
            **params: Parameter values for the template

        Returns:
            str: Rendered SQL query

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        # 파라미터 검증
        required_params = [
            fname for _, fname, _, _ in Formatter().parse(self.template)
            if fname is not None
        ]
        missing_params = set(required_params) - set(params.keys())
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")

        # 파라미터 값 포맷팅
        formatted_params = {
            key: self._format_value(value)
            for key, value in params.items()
        }

        # 템플릿 렌더링
        return self.template.format(**formatted_params)

    def execute(
        self,
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        timeout: int = 300,
        **params: Any,
    ) -> QueryResult:
        """Execute the template with parameters.

        Args:
            database: Database name
            output_location: Result storage location
            timeout: Maximum time to wait for results in seconds
            **params: Parameter values for the template

        Returns:
            QueryResult: Query execution result

        Raises:
            ValueError: If required parameters are missing or invalid
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            InvalidQueryError: Invalid query syntax
        """
        query = self.render(**params)
        return self.athena.execute_query(
            query=query,
            database=database,
            output_location=output_location,
            timeout=timeout,
        )

    def execute_to_file(
        self,
        output_path: Union[str, "Path", "BinaryIO"],
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        timeout: int = 300,
        **params: Any,
    ) -> None:
        """Execute the template and save results to a file.

        Args:
            output_path: Path to save results
            database: Database name
            output_location: Result storage location
            timeout: Maximum time to wait for results in seconds
            **params: Parameter values for the template

        Raises:
            ValueError: If required parameters are missing or invalid
            QueryTimeoutError: Query execution exceeded timeout
            QueryExecutionError: Query execution failed
            InvalidQueryError: Invalid query syntax
            ResultError: Failed to save results
        """
        query = self.render(**params)
        self.athena.execute_query_to_file(
            query=query,
            output_path=output_path,
            database=database,
            output_location=output_location,
            timeout=timeout,
        )
