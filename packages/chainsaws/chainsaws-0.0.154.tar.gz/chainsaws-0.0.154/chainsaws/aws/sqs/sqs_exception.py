class SQSException(Exception):
    """Base class for all SQS exceptions."""

    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)