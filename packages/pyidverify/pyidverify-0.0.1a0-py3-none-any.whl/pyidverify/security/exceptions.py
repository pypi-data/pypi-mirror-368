"""
Security Exception Classes

Custom exceptions for PyIDVerify security operations, providing detailed error
information for debugging and security incident response.

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

from typing import Optional, Dict, Any, List
import logging

# Configure exception logging
exception_logger = logging.getLogger('pyidverify.security.exceptions')


class SecurityError(Exception):
    """
    Base exception for all security-related errors.
    
    This exception indicates a security violation, configuration error,
    or other security-related issue that requires immediate attention.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        security_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize SecurityError.
        
        Args:
            message: Human-readable error description
            error_code: Machine-readable error code for automated handling
            details: Additional error details (will be sanitized)
            security_context: Security context information for audit logs
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "SEC_GENERAL"
        self.details = self._sanitize_details(details or {})
        self.security_context = security_context or {}
        
        # Log security error for monitoring
        exception_logger.warning(
            f"SecurityError: {self.error_code} - {message}",
            extra={'error_code': self.error_code, 'details': self.details}
        )
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize error details to prevent sensitive data leakage.
        
        Args:
            details: Original error details
            
        Returns:
            Sanitized details dictionary
        """
        sanitized = {}
        sensitive_keys = {'password', 'key', 'token', 'secret', 'hash', 'ssn', 'card'}
        
        for key, value in details.items():
            # Check if key contains sensitive terms
            if any(sensitive_term in key.lower() for sensitive_term in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 100:
                # Truncate very long strings that might contain sensitive data
                sanitized[key] = value[:50] + "... [TRUNCATED]"
            else:
                sanitized[key] = value
                
        return sanitized
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for serialization.
        
        Returns:
            Dictionary representation of the exception
        """
        return {
            'error_type': 'SecurityError',
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'security_context': self.security_context
        }


class CryptographicError(SecurityError):
    """
    Exception raised for cryptographic operation failures.
    
    This includes encryption/decryption failures, key generation issues,
    hash verification failures, and other cryptographic problems.
    """
    
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None,
        algorithm: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize CryptographicError.
        
        Args:
            message: Error description
            operation: Cryptographic operation that failed (encrypt, decrypt, hash, etc.)
            algorithm: Algorithm being used when error occurred
            **kwargs: Additional arguments passed to SecurityError
        """
        self.operation = operation
        self.algorithm = algorithm
        
        # Add cryptographic context to details
        details = kwargs.get('details', {})
        if operation:
            details['operation'] = operation
        if algorithm:
            details['algorithm'] = algorithm
            
        kwargs['details'] = details
        kwargs['error_code'] = kwargs.get('error_code', 'CRYPTO_ERROR')
        
        super().__init__(message, **kwargs)
        
        # Enhanced logging for crypto errors
        exception_logger.error(
            f"CryptographicError in {operation or 'unknown'} operation "
            f"using {algorithm or 'unknown'} algorithm: {message}"
        )


class AuditError(SecurityError):
    """
    Exception raised for audit system failures.
    
    This includes audit log corruption, integrity verification failures,
    and audit system configuration errors.
    """
    
    def __init__(
        self, 
        message: str, 
        audit_operation: Optional[str] = None,
        log_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize AuditError.
        
        Args:
            message: Error description
            audit_operation: Audit operation that failed
            log_id: Identifier of the affected audit log
            **kwargs: Additional arguments passed to SecurityError
        """
        self.audit_operation = audit_operation
        self.log_id = log_id
        
        # Add audit context to details
        details = kwargs.get('details', {})
        if audit_operation:
            details['audit_operation'] = audit_operation
        if log_id:
            details['log_id'] = log_id
            
        kwargs['details'] = details
        kwargs['error_code'] = kwargs.get('error_code', 'AUDIT_ERROR')
        
        super().__init__(message, **kwargs)


class ValidationSecurityError(SecurityError):
    """
    Exception raised when validation operations encounter security issues.
    
    This includes detection of malicious input, injection attempts,
    and security policy violations during validation.
    """
    
    def __init__(
        self, 
        message: str, 
        validation_type: Optional[str] = None,
        threat_type: Optional[str] = None,
        input_hash: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize ValidationSecurityError.
        
        Args:
            message: Error description
            validation_type: Type of validation being performed
            threat_type: Type of security threat detected
            input_hash: Hash of the input that caused the error (for tracking)
            **kwargs: Additional arguments passed to SecurityError
        """
        self.validation_type = validation_type
        self.threat_type = threat_type
        self.input_hash = input_hash
        
        # Add validation context to details
        details = kwargs.get('details', {})
        if validation_type:
            details['validation_type'] = validation_type
        if threat_type:
            details['threat_type'] = threat_type
        if input_hash:
            details['input_hash'] = input_hash
            
        kwargs['details'] = details
        kwargs['error_code'] = kwargs.get('error_code', 'VALIDATION_SECURITY_ERROR')
        
        super().__init__(message, **kwargs)


class ConfigurationError(SecurityError):
    """
    Exception raised for security configuration errors.
    
    This includes invalid security settings, missing required configuration,
    and conflicting security policies.
    """
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        config_value: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize ConfigurationError.
        
        Args:
            message: Error description
            config_key: Configuration key that caused the error
            config_value: Configuration value (will be sanitized if sensitive)
            **kwargs: Additional arguments passed to SecurityError
        """
        self.config_key = config_key
        self.config_value = config_value
        
        # Add configuration context to details
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        if config_value:
            # Sanitize potentially sensitive configuration values
            if any(sensitive in config_key.lower() for sensitive in ['key', 'secret', 'password', 'token']):
                details['config_value'] = "[REDACTED]"
            else:
                details['config_value'] = str(config_value)
                
        kwargs['details'] = details
        kwargs['error_code'] = kwargs.get('error_code', 'CONFIG_ERROR')
        
        super().__init__(message, **kwargs)


class ComplianceError(SecurityError):
    """
    Exception raised for regulatory compliance violations.
    
    This includes GDPR, HIPAA, PCI DSS, and other compliance framework
    violations detected during operation.
    """
    
    def __init__(
        self, 
        message: str, 
        regulation: Optional[str] = None,
        article: Optional[str] = None,
        severity: str = "high",
        **kwargs
    ):
        """
        Initialize ComplianceError.
        
        Args:
            message: Error description
            regulation: Regulation that was violated (GDPR, HIPAA, etc.)
            article: Specific article or section violated
            severity: Severity level (low, medium, high, critical)
            **kwargs: Additional arguments passed to SecurityError
        """
        self.regulation = regulation
        self.article = article
        self.severity = severity
        
        # Add compliance context to details
        details = kwargs.get('details', {})
        if regulation:
            details['regulation'] = regulation
        if article:
            details['article'] = article
        details['severity'] = severity
        
        kwargs['details'] = details
        kwargs['error_code'] = kwargs.get('error_code', 'COMPLIANCE_ERROR')
        
        super().__init__(message, **kwargs)
        
        # Enhanced logging for compliance errors
        exception_logger.critical(
            f"ComplianceError: {regulation or 'Unknown'} violation - {message}",
            extra={'regulation': regulation, 'article': article, 'severity': severity}
        )


class AccessDeniedError(SecurityError):
    """
    Exception raised for access control violations.
    
    This includes authentication failures, insufficient permissions,
    and authorization policy violations.
    """
    
    def __init__(
        self, 
        message: str, 
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize AccessDeniedError.
        
        Args:
            message: Error description
            user_id: ID of the user attempting access
            resource: Resource being accessed
            required_permission: Permission required for access
            **kwargs: Additional arguments passed to SecurityError
        """
        self.user_id = user_id
        self.resource = resource
        self.required_permission = required_permission
        
        # Add access control context to details
        details = kwargs.get('details', {})
        if user_id:
            details['user_id'] = user_id
        if resource:
            details['resource'] = resource
        if required_permission:
            details['required_permission'] = required_permission
            
        kwargs['details'] = details
        kwargs['error_code'] = kwargs.get('error_code', 'ACCESS_DENIED')
        
        super().__init__(message, **kwargs)


class RateLimitExceededError(SecurityError):
    """
    Exception raised when rate limits are exceeded.
    
    This includes API rate limiting, request throttling, and abuse prevention
    mechanisms being triggered.
    """
    
    def __init__(
        self, 
        message: str, 
        rate_limit: Optional[int] = None,
        current_rate: Optional[int] = None,
        reset_time: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize RateLimitExceededError.
        
        Args:
            message: Error description
            rate_limit: Maximum allowed rate
            current_rate: Current request rate
            reset_time: Time when rate limit resets (Unix timestamp)
            **kwargs: Additional arguments passed to SecurityError
        """
        self.rate_limit = rate_limit
        self.current_rate = current_rate
        self.reset_time = reset_time
        
        # Add rate limiting context to details
        details = kwargs.get('details', {})
        if rate_limit is not None:
            details['rate_limit'] = rate_limit
        if current_rate is not None:
            details['current_rate'] = current_rate
        if reset_time is not None:
            details['reset_time'] = reset_time
            
        kwargs['details'] = details
        kwargs['error_code'] = kwargs.get('error_code', 'RATE_LIMIT_EXCEEDED')
        
        super().__init__(message, **kwargs)


# Exception hierarchy for easy catching
SECURITY_EXCEPTIONS = [
    SecurityError,
    CryptographicError,
    AuditError,
    ValidationSecurityError,
    ConfigurationError,
    ComplianceError,
    AccessDeniedError,
    RateLimitExceededError,
]

def is_security_exception(exception: Exception) -> bool:
    """
    Check if an exception is a security-related exception.
    
    Args:
        exception: Exception to check
        
    Returns:
        True if the exception is security-related, False otherwise
    """
    return isinstance(exception, tuple(SECURITY_EXCEPTIONS))

def get_exception_context(exception: Exception) -> Dict[str, Any]:
    """
    Extract security context from an exception for logging/monitoring.
    
    Args:
        exception: Exception to extract context from
        
    Returns:
        Dictionary containing exception context
    """
    if isinstance(exception, SecurityError):
        return exception.to_dict()
    
    return {
        'error_type': type(exception).__name__,
        'message': str(exception),
        'is_security_related': is_security_exception(exception)
    }
