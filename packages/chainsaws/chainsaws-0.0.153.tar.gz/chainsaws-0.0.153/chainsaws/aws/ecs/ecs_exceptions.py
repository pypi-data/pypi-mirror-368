class ECSException(Exception):
    """Base exception for ECS errors."""
    pass


class ECSClusterException(ECSException):
    """Exception for ECS cluster errors."""
    pass


class ECSServiceException(ECSException):
    """Exception for ECS service errors."""
    pass


class ECSTaskException(ECSException):
    """Exception for ECS task errors."""
    pass


class ECSTaskDefinitionException(ECSException):
    """Exception for ECS task definition errors."""
    pass


class ECSContainerInstanceException(ECSException):
    """Exception for ECS container instance errors."""
    pass
