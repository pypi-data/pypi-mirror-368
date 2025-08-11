class APIGatewayManagementException(Exception):
    """Base exception for APIGatewayManagement."""

    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)


class APIGatewayManagementEndpointURLRequiredException(APIGatewayManagementException):
    """Exception raised when endpoint_url is required."""

    def __init__(self, message: str, *args: object) -> None:
        message = f"endpoint_url is required: {message}"
        super().__init__(message, *args)


class APIGatewayManagementPostToConnectionError(APIGatewayManagementException):
    """Exception raised when post_to_connection fails."""

    def __init__(self, message: str, *args: object) -> None:
        message = f"Failed to post to connection: {message}"
        super().__init__(message, *args)


class APIGatewayManagementGetConnectionError(APIGatewayManagementException):
    """Exception raised when get_connection fails."""

    def __init__(self, message: str, *args: object) -> None:
        message = f"Failed to get connection: {message}"
        super().__init__(message, *args)


class APIGatewayManagementDeleteConnectionError(APIGatewayManagementException):
    """Exception raised when delete_connection fails."""

    def __init__(self, message: str, *args: object) -> None:
        message = f"Failed to delete connection: {message}"
        super().__init__(message, *args) 