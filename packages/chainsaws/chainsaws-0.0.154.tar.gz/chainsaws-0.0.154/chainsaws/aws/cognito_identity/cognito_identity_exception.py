class CognitoIdentityException(Exception):
    """Base exception for Cognito Identity errors."""
    pass


class CognitoIdentityInvalidParameterException(CognitoIdentityException):
    """InvalidParameterException"""
    pass


class CognitoIdentityResourceNotFoundException(CognitoIdentityException):
    """ResourceNotFoundException"""
    pass


class CognitoIdentityNotAuthorizedException(CognitoIdentityException):
    """NotAuthorizedException"""
    pass


class CognitoIdentityTooManyRequestsException(CognitoIdentityException):
    """TooManyRequestsException"""
    pass


class CognitoIdentityInternalErrorException(CognitoIdentityException):
    """InternalErrorException"""
    pass


class CognitoIdentityLimitExceededException(CognitoIdentityException):
    """LimitExceededException"""
    pass


class CognitoIdentityExternalServiceException(CognitoIdentityException):
    """ExternalServiceException"""
    pass


class CognitoIdentityDeveloperUserAlreadyRegisteredException(CognitoIdentityException):
    """DeveloperUserAlreadyRegisteredException"""
    pass


class CognitoIdentityResourceConflictException(CognitoIdentityException):
    """ResourceConflictException"""
    pass


class CognitoIdentityInvalidIdentityPoolConfigurationException(CognitoIdentityException):
    """InvalidIdentityPoolConfigurationException"""
    pass


