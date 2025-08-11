"""Exceptions for Lambda handlers."""

from typing import Any, Dict, Optional
from http import HTTPStatus

class HTTPException(Exception):
    """FastAPI-compatible HTTP exception."""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize HTTP exception.
        
        Args:
            status_code: HTTP status code
            detail: Error detail (can be any JSON-serializable object)
            headers: Additional headers to include in the response
        """
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(str(detail) if detail else HTTPStatus(status_code).phrase)

class AppError(HTTPException):
    """Application-specific error with error code."""
    
    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        super().__init__(
            status_code=status_code,
            detail=message
        )
