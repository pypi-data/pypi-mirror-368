"""
PyIDVerify Core Framework

The core framework provides the fundamental building blocks for ID validation,
including type definitions, interfaces, base classes, and the validation engine.
This module establishes the architecture and contracts that all validators follow.

Features:
- Comprehensive type system with security integration
- Protocol-based interfaces for extensibility  
- Abstract base classes for common functionality
- Validation engine for orchestrating operations
- Plugin architecture for custom extensions

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

from typing import List, Dict, Any, Optional, Set

# Import core types and enumerations
from .types import (
    IDType,
    ValidationLevel,
    ValidationStatus,
    SecurityFlags,
    ValidationResult,
    ValidationMetadata,
    ValidationRequest,
    create_validation_result,
    create_error_result,
    create_validation_metadata
)

# Import exception hierarchy
from .exceptions import (
    PyIDVerifyError,
    ValidationError,
    ConfigurationError,
    ValidatorError,
    EngineError,
    TimeoutError,
    RateLimitError,
    ExternalServiceError,
    DataIntegrityError,
    PermissionError,
    create_validation_error,
    create_timeout_error,
    create_rate_limit_error
)

# Import interface protocols
from .interfaces import (
    ConfigProvider,
    CacheProvider,
    SecurityProvider,
    MetricsProvider,
    BaseValidator as BaseValidatorInterface,
    ValidatorInfo,
    ValidatorCapability,
    create_validator_info,
    validation_context
)

# Import base validator framework
from .base_validator import BaseValidator

# Import validation engine
from .engine import (
    ValidationEngine,
    ValidatorRegistry,
    ValidationStrategy,
    FirstSuccessStrategy,
    ConsensusStrategy
)

# Import interfaces and protocols
from .interfaces import (
    ValidatorCapability,
    ValidatorInfo,
    BaseValidator,
    ConfigProvider,
    CacheProvider,
    SecurityProvider,
    MetricsProvider,
    ValidatorRegistry,
    ValidationEngine,
    Plugin,
    PluginManager,
    validation_context,
    create_validator_info
)

# Version information
__version__ = "1.0.0"
__api_version__ = "1.0"

# Export all public components
__all__ = [
    # Version info
    "__version__",
    "__api_version__",
    
    # Core types
    "IDType",
    "ValidationLevel", 
    "ValidationStatus",
    "SecurityFlags",
    "ValidationResult",
    "ValidationMetadata",
    "ValidationRequest",
    "BatchValidationRequest",
    
    # Exception classes
    "PyIDVerifyError",
    "ValidationError",
    "ConfigurationError",
    "ValidatorError", 
    "EngineError",
    "TimeoutError",
    "RateLimitError",
    "ExternalServiceError",
    "DataIntegrityError",
    "PermissionError",
    
    # Interfaces and protocols
    "ValidatorCapability",
    "ValidatorInfo",
    "BaseValidator",
    "ConfigProvider",
    "CacheProvider", 
    "SecurityProvider",
    "MetricsProvider",
    "ValidatorRegistry",
    "ValidationEngine",
    "Plugin",
    "PluginManager",
    
    # Utility functions
    "create_validation_result",
    "create_error_result",
    "create_validation_error",
    "create_timeout_error",
    "create_rate_limit_error",
    "create_validator_info",
    "validation_context",
    
    # Helper functions
    "get_supported_id_types",
    "get_validation_levels",
    "get_security_flags",
    "validate_id_type",
    "validate_validation_level"
]


def get_supported_id_types() -> List[IDType]:
    """
    Get list of all supported ID types.
    
    Returns:
        List of all IDType enum values
    """
    return list(IDType)


def get_validation_levels() -> List[ValidationLevel]:
    """
    Get list of all validation levels.
    
    Returns:
        List of all ValidationLevel enum values
    """
    return list(ValidationLevel)


def get_security_flags() -> List[SecurityFlags]:
    """
    Get list of all security flags.
    
    Returns:
        List of all SecurityFlags enum values
    """
    return list(SecurityFlags)


def validate_id_type(id_type: Any) -> IDType:
    """
    Validate and convert ID type parameter.
    
    Args:
        id_type: ID type to validate (string, IDType, or None)
        
    Returns:
        Validated IDType enum value
        
    Raises:
        ValidationError: If ID type is invalid
    """
    if isinstance(id_type, IDType):
        return id_type
    
    if isinstance(id_type, str):
        try:
            # Try direct enum lookup first
            return IDType(id_type.lower())
        except ValueError:
            # Try name-based lookup
            for enum_type in IDType:
                if enum_type.name.lower() == id_type.upper():
                    return enum_type
            
            raise ValidationError(
                f"Invalid ID type: '{id_type}'. "
                f"Supported types: {[t.value for t in IDType]}"
            )
    
    raise ValidationError(
        f"Invalid ID type parameter: expected string or IDType, got {type(id_type).__name__}"
    )


def validate_validation_level(level: Any) -> ValidationLevel:
    """
    Validate and convert validation level parameter.
    
    Args:
        level: Validation level to validate (string, int, ValidationLevel)
        
    Returns:
        Validated ValidationLevel enum value
        
    Raises:
        ValidationError: If validation level is invalid
    """
    if isinstance(level, ValidationLevel):
        return level
    
    if isinstance(level, int):
        try:
            return ValidationLevel(level)
        except ValueError:
            valid_values = [l.value for l in ValidationLevel]
            raise ValidationError(
                f"Invalid validation level: {level}. Valid values: {valid_values}"
            )
    
    if isinstance(level, str):
        try:
            # Try name-based lookup
            return ValidationLevel[level.upper()]
        except KeyError:
            valid_names = [l.name for l in ValidationLevel]
            raise ValidationError(
                f"Invalid validation level: '{level}'. Valid names: {valid_names}"
            )
    
    raise ValidationError(
        f"Invalid validation level parameter: expected int, string or ValidationLevel, "
        f"got {type(level).__name__}"
    )


def get_id_type_info(id_type: IDType) -> Dict[str, Any]:
    """
    Get comprehensive information about an ID type.
    
    Args:
        id_type: ID type to get information for
        
    Returns:
        Dictionary containing ID type metadata
    """
    return {
        "name": id_type.name,
        "value": id_type.value,
        "display_name": id_type.display_name,
        "security_level": id_type.security_level,
        "compliance_frameworks": list(id_type.compliance_frameworks),
        "typical_length_range": id_type.typical_length_range,
        "description": f"Validation for {id_type.display_name}"
    }


def get_validation_level_info(level: ValidationLevel) -> Dict[str, Any]:
    """
    Get comprehensive information about a validation level.
    
    Args:
        level: Validation level to get information for
        
    Returns:
        Dictionary containing validation level metadata
    """
    return {
        "name": level.name,
        "value": level.value,
        "description": level.description,
        "typical_latency_ms": level.typical_latency_ms,
        "numeric_value": level.value
    }


def create_default_validation_context(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    validation_level: ValidationLevel = ValidationLevel.STANDARD,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Create default validation context with common parameters.
    
    Args:
        user_id: User identifier
        session_id: Session identifier  
        request_id: Request identifier
        validation_level: Validation level to use
        **kwargs: Additional context parameters
        
    Returns:
        Validation context dictionary
    """
    context = {
        "validation_level": validation_level,
        "timestamp": ValidationMetadata(
            validator_name="context_creator",
            validator_version=__version__,
            validation_timestamp=None,
            processing_time_ms=0.0,
            validation_level=validation_level
        ).validation_timestamp
    }
    
    if user_id:
        context["user_id"] = user_id
    if session_id:
        context["session_id"] = session_id
    if request_id:
        context["request_id"] = request_id
    
    # Add any additional parameters
    context.update(kwargs)
    
    return context


# Framework information
FRAMEWORK_INFO = {
    "name": "PyIDVerify Core Framework",
    "version": __version__,
    "api_version": __api_version__,
    "description": "Enterprise-grade ID validation framework with security-first design",
    "supported_id_types": len(IDType),
    "validation_levels": len(ValidationLevel),
    "security_flags": len(SecurityFlags),
    "features": [
        "Military-grade encryption and hashing",
        "Tamper-evident audit logging", 
        "Multi-framework compliance (GDPR, HIPAA, PCI DSS, SOX)",
        "Advanced data sanitization and PII protection",
        "High-performance batch processing",
        "Async validation support",
        "Extensible plugin architecture",
        "Comprehensive error handling",
        "Real-time metrics and monitoring",
        "Enterprise security controls"
    ]
}


def get_framework_info() -> Dict[str, Any]:
    """
    Get comprehensive framework information.
    
    Returns:
        Dictionary containing framework metadata
    """
    return FRAMEWORK_INFO.copy()


def validate_framework_compatibility(required_version: str) -> bool:
    """
    Check if current framework version is compatible with required version.
    
    Args:
        required_version: Required framework version (semantic version)
        
    Returns:
        True if compatible, False otherwise
    """
    try:
        from packaging import version
        current = version.parse(__version__)
        required = version.parse(required_version)
        
        # Compatible if major version matches and current >= required
        return (current.major == required.major and current >= required)
    except ImportError:
        # Fallback to simple string comparison if packaging not available
        return __version__ >= required_version


# Export all public components
__all__ = [
    # Core Types
    'IDType',
    'ValidationLevel',
    'ValidationStatus',
    'SecurityFlags',
    'ValidationResult',
    'ValidationMetadata',
    'ValidationRequest',
    'create_validation_result',
    'create_error_result',
    'create_validation_metadata',
    
    # Exceptions
    'CoreError',
    'ValidationError',
    'ConfigurationError',
    'ValidatorError',
    'EngineError',
    'TimeoutError',
    'DependencyError',
    'create_validation_error',
    'create_validator_error',
    'create_configuration_error',
    
    # Interface Protocols
    'ConfigProvider',
    'CacheProvider',
    'SecurityProvider',
    'MetricsProvider',
    'BaseValidatorInterface',
    'ValidatorInfo',
    'ValidatorCapability',
    'create_validator_info',
    'create_validator_capability',
    
    # Base Framework
    'BaseValidator',
    
    # Validation Engine
    'ValidationEngine',
    'ValidatorRegistry',
    'ValidationStrategy',
    'FirstSuccessStrategy',
    'ConsensusStrategy',
    
    # Utilities and Info
    'get_framework_info',
    'get_supported_id_types',
    'get_validation_levels',
    'create_validation_context',
    'sanitize_input_value',
    'validate_configuration',
    'validate_framework_compatibility'
]


# Initialize core framework
def _initialize_core_framework() -> None:
    """Initialize core framework components."""
    import logging
    
    # Set up core logging
    logger = logging.getLogger('pyidverify.core')
    logger.info(f"PyIDVerify Core Framework v{__version__} initialized")
    logger.info(f"API Version: {__api_version__}")
    logger.info(f"Supported ID Types: {len(IDType)}")
    logger.info(f"Validation Levels: {len(ValidationLevel)}")


# Initialize on import
_initialize_core_framework()
