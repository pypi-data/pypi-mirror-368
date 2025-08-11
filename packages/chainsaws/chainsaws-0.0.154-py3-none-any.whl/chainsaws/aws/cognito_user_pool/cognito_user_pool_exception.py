class CognitoUserPoolException(Exception):
    """Base exception for Cognito User Pool API."""
    pass


class UserPoolNotFoundException(CognitoUserPoolException):
    """Raised when the specified user pool was not found."""
    pass


class UserPoolAlreadyExistsException(CognitoUserPoolException):
    """Raised when attempting to create a resource that already exists."""
    pass


class InvalidParameterException(CognitoUserPoolException):
    """Raised when parameters are invalid."""
    pass


class NotAuthorizedException(CognitoUserPoolException):
    """Raised when the caller is not authorized."""
    pass


class LimitExceededException(CognitoUserPoolException):
    """Raised when service limits are exceeded."""
    pass


class TooManyRequestsException(CognitoUserPoolException):
    """Raised when throttled due to too many requests."""
    pass


class ResourceInUseException(CognitoUserPoolException):
    """Raised when the resource is in use and cannot be modified."""
    pass


class AliasExistsException(CognitoUserPoolException):
    """Raised when alias already exists."""
    pass


class UsernameExistsException(CognitoUserPoolException):
    """Raised when username already exists."""
    pass


