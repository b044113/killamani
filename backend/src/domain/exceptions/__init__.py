"""
Domain Exceptions

Custom exceptions for domain-level errors.
"""
from .domain_exceptions import (
    DomainException,
    EntityNotFoundError,
    InvalidEntityStateError,
    DuplicateEntityError,
    UnauthorizedAccessError,
    ValidationError,
    CalculationError,
    ChartNotFoundError,
    ClientNotFoundError,
    UserNotFoundError,
    InvalidCredentialsError,
    InvalidBirthDataError,
    InsufficientPermissionsError,
    StorageError,
    FileNotFoundError,
    InterpretationError,
    UnsupportedLanguageError,
)

__all__ = [
    "DomainException",
    "EntityNotFoundError",
    "InvalidEntityStateError",
    "DuplicateEntityError",
    "UnauthorizedAccessError",
    "ValidationError",
    "CalculationError",
    "ChartNotFoundError",
    "ClientNotFoundError",
    "UserNotFoundError",
    "InvalidCredentialsError",
    "InvalidBirthDataError",
    "InsufficientPermissionsError",
    "StorageError",
    "FileNotFoundError",
    "InterpretationError",
    "UnsupportedLanguageError",
]
