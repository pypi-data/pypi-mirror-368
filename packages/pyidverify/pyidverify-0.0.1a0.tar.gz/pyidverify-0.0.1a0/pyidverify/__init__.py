"""
PyIDVerify - Enterprise-Grade ID Verification Library

A comprehensive, security-first Python library for validating and verifying
identification numbers, personal identifiers, and sensitive data with
military-grade encryption and enterprise compliance features.

Features:
    - Military-grade security with AES-256-GCM encryption
    - GDPR, HIPAA, PCI DSS compliance built-in
    - Comprehensive ID validation (SSN, Credit Cards, Phone, Email, etc.)
    - Real-time fraud detection and risk scoring
    - Audit trails with tamper-evident logging
    - High-performance async validation
    - Enterprise-ready monitoring and analytics

Example:
    >>> import pyidverify
    >>> validator = pyidverify.get_validator('ssn')
    >>> result = validator.validate('123-45-6789')
    >>> print(f"Valid: {result.is_valid}, Confidence: {result.confidence}")

Security Note:
    This library handles sensitive personal information. Ensure proper
    security configurations and compliance with applicable regulations.
"""

__version__ = "2.0.0"
__author__ = "HWDigi"
__email__ = "HWDigi"
__license__ = "MIT"
__copyright__ = "Copyright 2025 HWDigi"

# Security and compliance information
__security_contact__ = "HWDigi"
__compliance_standards__ = ["GDPR", "HIPAA", "PCI DSS", "SOX"]
__encryption_standards__ = ["FIPS 140-2", "NIST", "AES-256-GCM", "Argon2id"]

from typing import Dict, Type, Optional, Any
import warnings
import sys

# Version compatibility check
if sys.version_info < (3, 8):
    raise RuntimeError(
        "PyIDVerify requires Python 3.8 or later for security and performance reasons. "
        "Please upgrade your Python version."
    )

# Import core components with lazy loading for performance
from .core.validator_registry import ValidatorRegistry
from .core.config import PyIDVerifyConfig
from .core.exceptions import (
    PyIDVerifyError,
    ValidationError,
    SecurityError,
    ConfigurationError
)

# Enhanced Email Verification System
from .email_verification import (
    EnhancedEmailValidator,
    EmailVerificationMode,
    create_enhanced_email_validator,
    verify_email_hybrid,
    verify_email_behavioral
)
from .core.types import IDType, ValidationResult, ValidationLevel
from .core.exceptions import (
    PyIDVerifyError,
    ValidationError, 
    ConfigurationError
)
from .security.exceptions import (
    SecurityError,
    ComplianceError
)

# Lazy imports to improve startup performance
_validator_cache: Dict[str, Any] = {}
_engine_instance: Optional[Any] = None

def get_validator(id_type: str, **kwargs) -> Any:
    """
    Get a validator instance for the specified ID type.
    
    Args:
        id_type: Type of ID to validate ('ssn', 'credit_card', 'email', etc.)
        **kwargs: Additional configuration options
        
    Returns:
        Validator instance for the specified ID type
        
    Raises:
        ValidationError: If the ID type is not supported
        ConfigurationError: If validator configuration is invalid
        
    Example:
        >>> validator = get_validator('ssn', security_level='high')
        >>> result = validator.validate('123-45-6789')
    """
    if id_type not in _validator_cache:
        # Lazy import to avoid circular dependencies
        from .validators import get_validator_class
        
        validator_class = get_validator_class(id_type)
        if validator_class is None:
            raise ValidationError(f"Unsupported ID type: {id_type}")
        
        _validator_cache[id_type] = validator_class(**kwargs)
    
    return _validator_cache[id_type]

def get_validation_engine(**kwargs) -> Any:
    """
    Get the main validation engine instance (singleton).
    
    Args:
        **kwargs: Configuration options for the engine
        
    Returns:
        ValidationEngine instance
        
    Example:
        >>> engine = get_validation_engine(enable_analytics=True)
        >>> results = engine.validate_batch([
        ...     ('ssn', '123-45-6789'),
        ...     ('email', 'user@example.com')
        ... ])
    """
    global _engine_instance
    
    if _engine_instance is None:
        # Lazy import
        from .core.validation_engine import ValidationEngine
        _engine_instance = ValidationEngine(**kwargs)
    
    return _engine_instance

def validate(value: str, id_type: Optional[str] = None, **kwargs) -> ValidationResult:
    """
    Quick validation function for single values.
    
    Args:
        value: The value to validate
        id_type: Type of ID (auto-detected if None)
        **kwargs: Additional validation options
        
    Returns:
        ValidationResult object with validation details
        
    Example:
        >>> result = pyidverify.validate('user@example.com', 'email')
        >>> if result.is_valid:
        ...     print("Email is valid!")
    """
    engine = get_validation_engine()
    return engine.validate(value, id_type=id_type, **kwargs)

async def validate_async(value: str, id_type: Optional[str] = None, **kwargs) -> ValidationResult:
    """
    Async validation function for single values.
    
    Args:
        value: The value to validate
        id_type: Type of ID (auto-detected if None)
        **kwargs: Additional validation options
        
    Returns:
        ValidationResult object with validation details
        
    Example:
        >>> result = await pyidverify.validate_async('user@example.com', 'email')
        >>> if result.is_valid:
        ...     print("Email is valid!")
    """
    engine = get_validation_engine()
    return await engine.validate_async(value, id_type=id_type, **kwargs)

# Configuration management
def configure(**kwargs) -> None:
    """
    Configure global PyIDVerify settings.
    
    Args:
        **kwargs: Configuration options
            - security_level: 'low', 'medium', 'high', 'maximum'
            - enable_audit: bool
            - enable_analytics: bool
            - cache_size: int
            - rate_limit_enabled: bool
            
    Example:
        >>> pyidverify.configure(
        ...     security_level='high',
        ...     enable_audit=True,
        ...     enable_analytics=True
        ... )
    """
    from .config import settings
    settings.update(**kwargs)

def get_supported_types() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all supported ID types.
    
    Returns:
        Dictionary mapping ID types to their capabilities and metadata
        
    Example:
        >>> types = pyidverify.get_supported_types()
        >>> print("Supported types:", list(types.keys()))
    """
    from .validators import get_supported_validators
    return get_supported_validators()

# Security utilities
def generate_test_data(id_type: str, count: int = 10, **kwargs) -> list:
    """
    Generate realistic but invalid test data for development and testing.
    
    SECURITY NOTE: Generated data is cryptographically guaranteed to be invalid
    in real systems to prevent accidental use of valid personal information.
    
    Args:
        id_type: Type of ID to generate
        count: Number of test values to generate
        **kwargs: Generation options
        
    Returns:
        List of test values
        
    Example:
        >>> test_ssns = pyidverify.generate_test_data('ssn', count=5)
        >>> for ssn in test_ssns:
        ...     print(f"Test SSN: {ssn}")
    """
    from ..utils.generators import generate_test_data as _generate
    return _generate(id_type, count=count, **kwargs)

# Health and monitoring
def health_check() -> Dict[str, Any]:
    """
    Perform a comprehensive health check of the PyIDVerify system.
    
    Returns:
        Dictionary with health status information
        
    Example:
        >>> status = pyidverify.health_check()
        >>> if status['overall'] == 'healthy':
        ...     print("System is operational")
    """
    from .monitoring.health import perform_health_check
    return perform_health_check()

# Version and build information
def get_version_info() -> Dict[str, str]:
    """
    Get detailed version and build information.
    
    Returns:
        Dictionary with version details
    """
    try:
        from ._version import version_info
        return version_info
    except ImportError:
        return {
            "version": __version__,
            "build": "development",
            "security_level": "standard",
            "compliance": ", ".join(__compliance_standards__),
        }

# Security warning for development builds
if __version__.endswith("-dev"):
    warnings.warn(
        "You are using a development version of PyIDVerify. "
        "This version may contain experimental features and should not be used in production. "
        "For production use, install a stable release version.",
        UserWarning,
        stacklevel=2
    )

# Export public API
__all__ = [
    # Core functions
    "validate",
    "validate_async", 
    "get_validator",
    "get_validation_engine",
    "configure",
    
    # Information functions
    "get_supported_types",
    "get_version_info",
    "health_check",
    
    # Utility functions
    "generate_test_data",
    
    # Types and exceptions
    "IDType",
    "ValidationResult", 
    "ValidationLevel",
    "PyIDVerifyError",
    "ValidationError",
    "SecurityError",
    "ConfigurationError",
    "ComplianceError",
    
    # Metadata
    "__version__",
    "__author__",
    "__license__",
    "__security_contact__",
    "__compliance_standards__",
    "__encryption_standards__",
]

# Performance optimization: Pre-warm critical imports in background
import threading

def _background_import():
    """Pre-load critical modules in background for better performance."""
    try:
        # Import heavy dependencies in background
        from .security import encryption  # noqa: F401
        from .security import hashing    # noqa: F401
        from .validators.government import ssn  # noqa: F401
        from .validators.personal import email  # noqa: F401
    except ImportError:
        # Modules not yet implemented, ignore
        pass

# Start background import thread (non-blocking)
_import_thread = threading.Thread(target=_background_import, daemon=True)
_import_thread.start()
