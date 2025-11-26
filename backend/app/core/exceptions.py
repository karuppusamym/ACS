"""Custom exceptions and error handlers"""
from fastapi import HTTPException, status
from typing import Optional, Any, Dict


class BaseAPIException(HTTPException):
    """Base exception for all API errors"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra = extra or {}


class ValidationException(BaseAPIException):
    """Raised when input validation fails"""

    def __init__(self, detail: str, field: Optional[str] = None):
        extra = {"field": field} if field else {}
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            extra=extra
        )


class AuthenticationException(BaseAPIException):
    """Raised when authentication fails"""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(BaseAPIException):
    """Raised when user lacks permissions"""

    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundException(BaseAPIException):
    """Raised when resource is not found"""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
            error_code="NOT_FOUND",
            extra={"resource": resource, "identifier": str(identifier)}
        )


class ConflictException(BaseAPIException):
    """Raised when there's a conflict (e.g., duplicate resource)"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT"
        )


class DatabaseException(BaseAPIException):
    """Raised when database operation fails"""

    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )


class ExternalServiceException(BaseAPIException):
    """Raised when external service (LLM, etc.) fails"""

    def __init__(self, service: str, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service} service error: {detail}",
            error_code="EXTERNAL_SERVICE_ERROR",
            extra={"service": service}
        )


class RateLimitException(BaseAPIException):
    """Raised when rate limit is exceeded"""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED"
        )


def format_error_response(
    status_code: int,
    detail: str,
    error_code: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format error response consistently"""
    response = {
        "error": True,
        "status_code": status_code,
        "detail": detail
    }

    if error_code:
        response["error_code"] = error_code

    if extra:
        response["extra"] = extra

    return response
