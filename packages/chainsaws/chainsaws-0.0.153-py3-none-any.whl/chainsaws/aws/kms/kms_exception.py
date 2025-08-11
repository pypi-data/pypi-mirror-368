class KMSException(Exception):
    """Base exception for KMS errors."""
    pass


class KMSValidationError(KMSException):
    """Raised when input validation fails."""
    pass


class KMSKeyNotFoundError(KMSException):
    """Raised when a requested key is not found."""
    pass


class KMSInvalidKeyStateError(KMSException):
    """Raised when a key is in an invalid state for the requested operation."""
    pass


class KMSInvalidGrantTokenError(KMSException):
    """Raised when a grant token is invalid."""
    pass


class KMSInvalidMarkerError(KMSException):
    """Raised when a pagination marker is invalid."""
    pass


class KMSLimitExceededError(KMSException):
    """Raised when a limit is exceeded."""
    pass


class KMSMalformedPolicyDocumentError(KMSException):
    """Raised when a policy document is malformed."""
    pass


class KMSUnsupportedOperationError(KMSException):
    """Raised when an operation is not supported."""
    pass


class KMSDisabledError(KMSException):
    """Raised when a key is disabled."""
    pass


class KMSExpiredImportTokenError(KMSException):
    """Raised when an import token has expired."""
    pass


class KMSIncorrectKeyMaterialError(KMSException):
    """Raised when key material is incorrect."""
    pass


class KMSInvalidImportTokenError(KMSException):
    """Raised when an import token is invalid."""
    pass


class KMSInvalidKeyUsageError(KMSException):
    """Raised when key usage is invalid."""
    pass


class KMSKeyUnavailableError(KMSException):
    """Raised when a key is unavailable."""
    pass


class KMSNotFoundException(KMSException):
    """Raised when a requested resource is not found."""
    pass


class KMSPendingImportError(KMSException):
    """Raised when a key is pending import."""
    pass


class KMSUnsupportedKeySpecError(KMSException):
    """Raised when a key specification is not supported."""
    pass
