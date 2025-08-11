from datetime import datetime
from typing import Any, Optional

from chainsaws.aws.cloudwatch.cloudwatch import CloudWatchAPI
from chainsaws.aws.cloudwatch.cloudwatch_models import QueryResult, QuerySortBy


class QueryBuilder:
    """Builder for CloudWatch Logs Insights queries."""

    def __init__(self, api: CloudWatchAPI) -> None:
        self.api = api
        self._query_parts = []
        self._log_groups: list[str] = []
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        self._limit: Optional[int] = None
        self._sort_by: QuerySortBy = QuerySortBy.TIME_DESC

    def log_groups(self, *groups: str) -> "QueryBuilder":
        """Specify log groups to query."""
        self._log_groups.extend(groups)
        return self

    def filter(self, **conditions: Any) -> "QueryBuilder":
        """Add filter conditions."""
        conditions_str = " and ".join(
            f"{k} = {str(v)!r}" for k, v in conditions.items()
        )
        self._query_parts.append(f"filter {conditions_str}")
        return self

    def filter_pattern(self, pattern: str) -> "QueryBuilder":
        """Add raw filter pattern."""
        self._query_parts.append(f"filter {pattern}")
        return self

    def parse_message(
        self,
        pattern: str,
        as_field: str,
    ) -> "QueryBuilder":
        """Parse message field."""
        self._query_parts.append(f"parse @message {pattern} as {as_field}")
        return self

    def stats(self, *expressions: str) -> "QueryBuilder":
        """Add statistics expressions."""
        self._query_parts.append(f"stats {', '.join(expressions)}")
        return self

    def group_by(self, *fields: str) -> "QueryBuilder":
        """Group results by fields."""
        if fields:
            self._query_parts.append(f"by {', '.join(fields)}")
        return self

    def sort(
        self,
        field: str,
        desc: bool = True,
    ) -> "QueryBuilder":
        """Sort results."""
        self._query_parts.append(
            f"sort {field} {'desc' if desc else 'asc'}")
        return self

    def limit(self, n: int) -> "QueryBuilder":
        """Limit number of results."""
        self._limit = n
        return self

    def time_range(
        self,
        start: datetime,
        end: Optional[datetime] = None,
    ) -> "QueryBuilder":
        """Set time range."""
        self._start_time = start
        self._end_time = end or datetime.now()
        return self

    def build(self) -> str:
        """Build query string."""
        return " | ".join(self._query_parts)

    def execute(self) -> QueryResult:
        """Execute query and get results."""
        if not self._log_groups:
            msg = "No log groups specified"
            raise ValueError(msg)
        if not self._start_time:
            msg = "Time range not specified"
            raise ValueError(msg)

        query_id = self.api.start_query(
            query_string=self.build(),
            log_group_names=self._log_groups,
            start_time=self._start_time,
            end_time=self._end_time,
            limit=self._limit,
            sort_by=self._sort_by,
        )
        return self.api.get_query_results(query_id, wait=True)
