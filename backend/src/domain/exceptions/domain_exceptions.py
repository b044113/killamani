"""
Domain Exceptions

Custom exceptions for domain-level business rule violations and errors.
"""


class DomainException(Exception):
    """Base exception for all domain errors"""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


# ============================================================================
# Entity Errors
# ============================================================================

class EntityNotFoundError(DomainException):
    """Raised when an entity is not found"""
    def __init__(self, entity_type: str, entity_id: str):
        message = f"{entity_type} with ID {entity_id} not found"
        super().__init__(message, code="ENTITY_NOT_FOUND")
        self.entity_type = entity_type
        self.entity_id = entity_id


class InvalidEntityStateError(DomainException):
    """Raised when an entity is in an invalid state"""
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_ENTITY_STATE")


class DuplicateEntityError(DomainException):
    """Raised when attempting to create a duplicate entity"""
    def __init__(self, entity_type: str, field: str, value: str):
        message = f"{entity_type} with {field}='{value}' already exists"
        super().__init__(message, code="DUPLICATE_ENTITY")
        self.entity_type = entity_type
        self.field = field
        self.value = value


# ============================================================================
# Validation Errors
# ============================================================================

class ValidationError(DomainException):
    """Raised when validation fails"""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class InvalidBirthDataError(ValidationError):
    """Raised when birth data is invalid"""
    def __init__(self, message: str):
        super().__init__(message, field="birth_data")


# ============================================================================
# Authorization Errors
# ============================================================================

class UnauthorizedAccessError(DomainException):
    """Raised when user attempts unauthorized access"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, code="UNAUTHORIZED_ACCESS")


class InsufficientPermissionsError(DomainException):
    """Raised when user lacks required permissions"""
    def __init__(self, required_permission: str):
        message = f"Insufficient permissions. Required: {required_permission}"
        super().__init__(message, code="INSUFFICIENT_PERMISSIONS")
        self.required_permission = required_permission


class InvalidCredentialsError(DomainException):
    """Raised when login credentials are invalid"""
    def __init__(self):
        super().__init__("Invalid email or password", code="INVALID_CREDENTIALS")


# ============================================================================
# Specific Entity Errors
# ============================================================================

class UserNotFoundError(EntityNotFoundError):
    """Raised when a user is not found"""
    def __init__(self, user_id: str):
        super().__init__("User", user_id)


class ClientNotFoundError(EntityNotFoundError):
    """Raised when a client is not found"""
    def __init__(self, client_id: str):
        super().__init__("Client", client_id)


class ChartNotFoundError(EntityNotFoundError):
    """Raised when a chart is not found"""
    def __init__(self, chart_id: str):
        super().__init__("Chart", chart_id)


# ============================================================================
# Calculation Errors
# ============================================================================

class CalculationError(DomainException):
    """Raised when astrological calculation fails"""
    def __init__(self, message: str, calculation_type: str = None):
        super().__init__(message, code="CALCULATION_ERROR")
        self.calculation_type = calculation_type


class InvalidChartDataError(CalculationError):
    """Raised when chart data is invalid or incomplete"""
    def __init__(self, message: str):
        super().__init__(message, calculation_type="chart")


class InvalidTransitDataError(CalculationError):
    """Raised when transit data is invalid"""
    def __init__(self, message: str):
        super().__init__(message, calculation_type="transit")


class InvalidSolarReturnDataError(CalculationError):
    """Raised when solar return data is invalid"""
    def __init__(self, message: str):
        super().__init__(message, calculation_type="solar_return")


# ============================================================================
# Storage Errors
# ============================================================================

class StorageError(DomainException):
    """Raised when file storage operation fails"""
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, code="STORAGE_ERROR")
        self.operation = operation


class FileNotFoundError(StorageError):
    """Raised when a file is not found in storage"""
    def __init__(self, file_path: str):
        message = f"File not found: {file_path}"
        super().__init__(message, operation="read")
        self.file_path = file_path


# ============================================================================
# Interpreter Errors
# ============================================================================

class InterpretationError(DomainException):
    """Raised when chart interpretation fails"""
    def __init__(self, message: str, language: str = None):
        super().__init__(message, code="INTERPRETATION_ERROR")
        self.language = language


class UnsupportedLanguageError(InterpretationError):
    """Raised when requested language is not supported"""
    def __init__(self, language: str):
        message = f"Unsupported language: {language}"
        super().__init__(message, language=language)


# ============================================================================
# Business Rule Violations
# ============================================================================

class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated"""
    def __init__(self, message: str, rule: str = None):
        super().__init__(message, code="BUSINESS_RULE_VIOLATION")
        self.rule = rule


class MaxClientsExceededError(BusinessRuleViolationError):
    """Raised when consultant exceeds maximum client limit"""
    def __init__(self, max_clients: int):
        message = f"Maximum number of clients ({max_clients}) exceeded"
        super().__init__(message, rule="max_clients_per_consultant")
        self.max_clients = max_clients


class MaxChartsExceededError(BusinessRuleViolationError):
    """Raised when client exceeds maximum chart limit"""
    def __init__(self, max_charts: int):
        message = f"Maximum number of charts ({max_charts}) exceeded"
        super().__init__(message, rule="max_charts_per_client")
        self.max_charts = max_charts
