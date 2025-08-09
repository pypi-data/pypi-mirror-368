"""
Core Exception Classes

Defines the exception hierarchy for the PyIDVerify library core framework.
These exceptions provide clear error handling with detailed context and
integration with the security audit system.

Features:
- Hierarchical exception structure
- Detailed error context and metadata
- Security-aware error handling
- Integration with audit logging
- Developer-friendly error messages

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
import uuid

from ..security.exceptions import SecurityError, AuditError
from .types import IDType, ValidationLevel, ValidationStatus


class PyIDVerifyError(Exception):
    """
    Base exception class for all PyIDVerify errors.
    
    Provides common functionality for error tracking, context preservation,
    and integration with the audit system.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        user_message: Optional[str] = None
    ):
        """
        Initialize base exception.
        
        Args:
            message: Technical error message for developers
            error_code: Structured error code for programmatic handling
            context: Additional context information
            cause: Underlying exception that caused this error
            user_message: User-friendly error message
        """
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code or self._default_error_code()
        self.context = context or {}
        self.cause = cause
        self.user_message = user_message or self._default_user_message()
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc)
        
        # Add exception chain information
        if cause:
            self.__cause__ = cause
    
    def _default_error_code(self) -> str:
        """Generate default error code based on exception class."""
        class_name = self.__class__.__name__
        # Convert CamelCase to SNAKE_CASE
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).upper()
    
    def _default_user_message(self) -> str:
        """Generate default user-friendly message."""
        return "An error occurred during ID validation. Please check your input and try again."
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary representation.
        
        Returns:
            Dictionary containing exception details
        """
        return {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
            "exception_type": self.__class__.__name__
        }
    
    def add_context(self, key: str, value: Any) -> None:
        """Add additional context information."""
        self.context[key] = value
    
    def __str__(self) -> str:
        """String representation with error ID for tracking."""
        return f"[{self.error_id}] {self.message}"


class ValidationError(PyIDVerifyError):
    """
    Exception raised when ID validation fails due to invalid input.
    
    This is raised for expected validation failures, not system errors.
    """
    
    def __init__(
        self,
        message: str,
        id_type: Optional[IDType] = None,
        original_value: Optional[str] = None,
        validation_level: Optional[ValidationLevel] = None,
        errors: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            id_type: Type of ID being validated
            original_value: Original input value (will be sanitized)
            validation_level: Validation level that was attempted
            errors: List of specific validation errors
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        self.id_type = id_type
        self.original_value = self._sanitize_value(original_value)
        self.validation_level = validation_level
        self.errors = errors or []
        
        # Add context information
        if id_type:
            self.add_context("id_type", id_type.value)
        if validation_level:
            self.add_context("validation_level", validation_level.name)
        if self.errors:
            self.add_context("validation_errors", self.errors)
    
    def _sanitize_value(self, value: Optional[str]) -> Optional[str]:
        """Sanitize sensitive value for logging."""
        if not value:
            return value
        
        # For security, only show first few and last few characters
        if len(value) <= 4:
            return "*" * len(value)
        elif len(value) <= 10:
            return value[:2] + "*" * (len(value) - 4) + value[-2:]
        else:
            return value[:3] + "*" * (len(value) - 6) + value[-3:]
    
    def _default_user_message(self) -> str:
        """Generate user-friendly message for validation errors."""
        if hasattr(self, 'id_type') and self.id_type:
            return f"The {self.id_type.display_name} format is invalid. Please check your input."
        return "The ID format is invalid. Please check your input and try again."


class ConfigurationError(PyIDVerifyError):
    """
    Exception raised when there's an issue with system configuration.
    """
    
    def __init__(
        self,
        message: str,
        config_section: Optional[str] = None,
        config_key: Optional[str] = None,
        expected_type: Optional[type] = None,
        actual_value: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_section: Configuration section with the issue
            config_key: Specific configuration key
            expected_type: Expected type for the configuration value
            actual_value: Actual value that caused the error
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        self.config_section = config_section
        self.config_key = config_key
        self.expected_type = expected_type
        self.actual_value = actual_value
        
        # Add context information
        if config_section:
            self.add_context("config_section", config_section)
        if config_key:
            self.add_context("config_key", config_key)
        if expected_type:
            self.add_context("expected_type", expected_type.__name__)
        if actual_value is not None:
            self.add_context("actual_value", str(actual_value))
    
    def _default_user_message(self) -> str:
        return "System configuration error. Please contact support."


class ValidatorError(PyIDVerifyError):
    """
    Exception raised when there's an issue with validator operation.
    """
    
    def __init__(
        self,
        message: str,
        validator_name: Optional[str] = None,
        validator_version: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize validator error.
        
        Args:
            message: Error message
            validator_name: Name of the validator that failed
            validator_version: Version of the validator
            operation: Operation that was being performed
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        self.validator_name = validator_name
        self.validator_version = validator_version
        self.operation = operation
        
        # Add context information
        if validator_name:
            self.add_context("validator_name", validator_name)
        if validator_version:
            self.add_context("validator_version", validator_version)
        if operation:
            self.add_context("operation", operation)
    
    def _default_user_message(self) -> str:
        return "Validation service temporarily unavailable. Please try again later."


class EngineError(PyIDVerifyError):
    """
    Exception raised when there's an issue with the validation engine.
    """
    
    def __init__(
        self,
        message: str,
        engine_operation: Optional[str] = None,
        request_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize engine error.
        
        Args:
            message: Error message
            engine_operation: Engine operation that failed
            request_id: Request ID for tracking
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        self.engine_operation = engine_operation
        self.request_id = request_id
        
        # Add context information
        if engine_operation:
            self.add_context("engine_operation", engine_operation)
        if request_id:
            self.add_context("request_id", request_id)
    
    def _default_user_message(self) -> str:
        return "Service temporarily unavailable. Please try again later."


class TimeoutError(PyIDVerifyError):
    """
    Exception raised when a validation operation times out.
    """
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            timeout_seconds: Timeout value that was exceeded
            operation: Operation that timed out
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        
        # Add context information
        if timeout_seconds:
            self.add_context("timeout_seconds", timeout_seconds)
        if operation:
            self.add_context("operation", operation)
    
    def _default_user_message(self) -> str:
        return "Request took too long to process. Please try again."


class RateLimitError(PyIDVerifyError):
    """
    Exception raised when rate limits are exceeded.
    """
    
    def __init__(
        self,
        message: str,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
        retry_after_seconds: Optional[int] = None,
        identifier: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            limit: Rate limit that was exceeded
            window_seconds: Time window for the limit
            retry_after_seconds: Seconds to wait before retrying
            identifier: Identifier that hit the limit (IP, user, etc.)
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        self.limit = limit
        self.window_seconds = window_seconds
        self.retry_after_seconds = retry_after_seconds
        self.identifier = self._sanitize_identifier(identifier)
        
        # Add context information
        if limit:
            self.add_context("limit", limit)
        if window_seconds:
            self.add_context("window_seconds", window_seconds)
        if retry_after_seconds:
            self.add_context("retry_after_seconds", retry_after_seconds)
        if self.identifier:
            self.add_context("identifier", self.identifier)
    
    def _sanitize_identifier(self, identifier: Optional[str]) -> Optional[str]:
        """Sanitize identifier for logging."""
        if not identifier:
            return identifier
        
        # For IP addresses, mask last octet
        if "." in identifier and identifier.count(".") == 3:
            parts = identifier.split(".")
            return f"{parts[0]}.{parts[1]}.{parts[2]}.***"
        
        # For other identifiers, mask partially
        if len(identifier) > 6:
            return identifier[:3] + "*" * (len(identifier) - 6) + identifier[-3:]
        else:
            return "*" * len(identifier)
    
    def _default_user_message(self) -> str:
        retry_msg = ""
        if self.retry_after_seconds:
            retry_msg = f" Please try again in {self.retry_after_seconds} seconds."
        return f"Too many requests. Please slow down.{retry_msg}"


class ExternalServiceError(PyIDVerifyError):
    """
    Exception raised when external service integration fails.
    """
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        service_endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize external service error.
        
        Args:
            message: Error message
            service_name: Name of the external service
            service_endpoint: Service endpoint that failed
            status_code: HTTP status code (if applicable)
            response_body: Response body (will be truncated)
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        self.service_name = service_name
        self.service_endpoint = service_endpoint
        self.status_code = status_code
        self.response_body = self._truncate_response(response_body)
        
        # Add context information
        if service_name:
            self.add_context("service_name", service_name)
        if service_endpoint:
            self.add_context("service_endpoint", service_endpoint)
        if status_code:
            self.add_context("status_code", status_code)
        if self.response_body:
            self.add_context("response_body", self.response_body)
    
    def _truncate_response(self, response: Optional[str]) -> Optional[str]:
        """Truncate response body for logging."""
        if not response:
            return response
        
        max_length = 500
        if len(response) > max_length:
            return response[:max_length] + "... (truncated)"
        return response
    
    def _default_user_message(self) -> str:
        return "External service temporarily unavailable. Please try again later."


class DataIntegrityError(PyIDVerifyError):
    """
    Exception raised when data integrity issues are detected.
    """
    
    def __init__(
        self,
        message: str,
        data_source: Optional[str] = None,
        integrity_check: Optional[str] = None,
        expected_value: Optional[str] = None,
        actual_value: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize data integrity error.
        
        Args:
            message: Error message
            data_source: Source of the corrupted data
            integrity_check: Type of integrity check that failed
            expected_value: Expected value (sanitized)
            actual_value: Actual value (sanitized)
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        
        self.data_source = data_source
        self.integrity_check = integrity_check
        self.expected_value = expected_value
        self.actual_value = actual_value
        
        # Add context information
        if data_source:
            self.add_context("data_source", data_source)
        if integrity_check:
            self.add_context("integrity_check", integrity_check)
        if expected_value:
            self.add_context("expected_value", expected_value)
        if actual_value:
            self.add_context("actual_value", actual_value)
    
    def _default_user_message(self) -> str:
        return "Data integrity issue detected. Please contact support."


class PermissionError(SecurityError):
    """
    Exception raised when access is denied due to insufficient permissions.
    
    Inherits from SecurityError to integrate with security audit system.
    """
    
    def __init__(
        self,
        message: str,
        required_permission: Optional[str] = None,
        user_permissions: Optional[List[str]] = None,
        resource: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize permission error.
        
        Args:
            message: Error message
            required_permission: Permission that was required
            user_permissions: Permissions the user has
            resource: Resource being accessed
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, operation="permission_check", **kwargs)
        
        self.required_permission = required_permission
        self.user_permissions = user_permissions or []
        self.resource = resource
        
        # Add context information (via SecurityError)
        if required_permission:
            self.add_context("required_permission", required_permission)
        if user_permissions:
            self.add_context("user_permissions", user_permissions)
        if resource:
            self.add_context("resource", resource)
    
    def _default_user_message(self) -> str:
        return "Access denied. You don't have permission to perform this operation."


# Exception factory functions for common scenarios
def create_validation_error(
    message: str,
    id_type: IDType,
    value: str,
    errors: Optional[List[str]] = None
) -> ValidationError:
    """
    Factory function for creating validation errors.
    
    Args:
        message: Error message
        id_type: Type of ID being validated
        value: Value that failed validation
        errors: List of specific errors
        
    Returns:
        Configured ValidationError instance
    """
    return ValidationError(
        message=message,
        id_type=id_type,
        original_value=value,
        errors=errors,
        error_code=f"VALIDATION_FAILED_{id_type.name}"
    )


def create_timeout_error(operation: str, timeout_seconds: float) -> TimeoutError:
    """
    Factory function for creating timeout errors.
    
    Args:
        operation: Operation that timed out
        timeout_seconds: Timeout value
        
    Returns:
        Configured TimeoutError instance
    """
    return TimeoutError(
        message=f"Operation '{operation}' timed out after {timeout_seconds} seconds",
        operation=operation,
        timeout_seconds=timeout_seconds,
        error_code="OPERATION_TIMEOUT"
    )


class BiometricError(ValidationError):
    """
    Exception raised for biometric-specific validation errors.
    
    Handles errors related to biometric processing including template generation,
    liveness detection, quality assessment, and matching operations.
    """
    
    def __init__(
        self,
        message: str,
        id_type: Optional[IDType] = None,
        biometric_type: Optional[str] = None,
        quality_score: Optional[float] = None,
        liveness_score: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize biometric error.
        
        Args:
            message: Error description
            id_type: Type of ID being validated
            biometric_type: Type of biometric that caused the error
            quality_score: Quality score of the biometric sample (if available)
            liveness_score: Liveness detection score (if available)
            **kwargs: Additional arguments passed to ValidationError
        """
        context = kwargs.get('context', {})
        context.update({
            'biometric_type': biometric_type,
            'quality_score': quality_score,
            'liveness_score': liveness_score,
            'error_category': 'biometric'
        })
        kwargs['context'] = context
        
        super().__init__(message, id_type=id_type, **kwargs)
        self.biometric_type = biometric_type
        self.quality_score = quality_score
        self.liveness_score = liveness_score


def create_rate_limit_error(
    limit: int,
    window_seconds: int,
    retry_after_seconds: int,
    identifier: Optional[str] = None
) -> RateLimitError:
    """
    Factory function for creating rate limit errors.
    
    Args:
        limit: Rate limit that was exceeded
        window_seconds: Time window for the limit
        retry_after_seconds: Seconds to wait before retrying
        identifier: Identifier that hit the limit
        
    Returns:
        Configured RateLimitError instance
    """
    return RateLimitError(
        message=f"Rate limit exceeded: {limit} requests per {window_seconds} seconds",
        limit=limit,
        window_seconds=window_seconds,
        retry_after_seconds=retry_after_seconds,
        identifier=identifier,
        error_code="RATE_LIMIT_EXCEEDED"
    )
