

class DynamoDBError(Exception):
    """Base exception for all DynamoDB related errors."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        super().__init__(message)
        self.original_error = original_error


class DynamoDBPartitionError(DynamoDBError):
    """Base class for partition related errors."""


class PartitionNotFoundError(DynamoDBPartitionError):
    """Error of partition not found."""


class BatchOperationError(DynamoDBError):
    """Error during batch operation."""

    def __init__(
        self,
        message: str,
        succeeded_items: list | None = None,
        failed_items: list | None = None,
    ) -> None:
        super().__init__(message)
        self.succeeded_items = succeeded_items or []
        self.failed_items = failed_items or []
