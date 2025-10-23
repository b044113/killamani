"""
Error Handler Middleware

Converts domain exceptions to HTTP responses.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ....domain.exceptions import (
    DomainException,
    EntityNotFoundError,
    DuplicateEntityError,
    UnauthorizedAccessError,
    ValidationError,
    InvalidCredentialsError,
    CalculationError,
    InterpretationError,
    StorageError,
)


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """
    Handle domain exceptions and convert to appropriate HTTP responses.

    Args:
        request: FastAPI request
        exc: Domain exception

    Returns:
        JSON response with error details
    """
    # Map domain exceptions to HTTP status codes
    status_map = {
        EntityNotFoundError: status.HTTP_404_NOT_FOUND,
        DuplicateEntityError: status.HTTP_409_CONFLICT,
        UnauthorizedAccessError: status.HTTP_403_FORBIDDEN,
        ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
        CalculationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        InterpretationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        StorageError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    # Get status code for exception type
    status_code = status_map.get(type(exc), status.HTTP_400_BAD_REQUEST)

    # Build error response
    error_response = {
        "error": {
            "code": exc.code if hasattr(exc, 'code') else "UNKNOWN_ERROR",
            "message": exc.message if hasattr(exc, 'message') else str(exc),
            "type": exc.__class__.__name__,
        }
    }

    # Add additional details if available
    if hasattr(exc, 'field') and exc.field:
        error_response["error"]["field"] = exc.field

    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle FastAPI validation errors.

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSON response with validation errors
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle any unhandled exceptions.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON response with generic error
    """
    # Log the exception for debugging (in production, use proper logging)
    print(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )
