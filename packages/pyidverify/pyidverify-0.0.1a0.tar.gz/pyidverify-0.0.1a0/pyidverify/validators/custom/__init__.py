"""
Custom Validators Package
========================

This package provides custom validation capabilities including:

1. **Custom Regex Validator**: Secure regex-based validation with ReDoS protection
2. **Composite Validator**: Multi-field and business rule validation
3. **Validator Templates**: Pre-built validation patterns for common use cases

Features:
- ReDoS (Regular Expression DoS) protection
- Pattern complexity analysis and security scoring
- Multi-field validation with cross-field dependencies
- Business rule validation with conditional logic
- Validator chaining and composition
- Performance monitoring and caching
- Comprehensive security analysis

Examples:
    >>> from pyidverify.validators.custom import CustomRegexValidator, CompositeValidator
    >>> 
    >>> # Custom regex validator
    >>> validator = CustomRegexValidator(r'^\d{3}-\d{2}-\d{4}$', name="SSN Format")
    >>> result = validator.validate("123-45-6789")
    >>> 
    >>> # Composite validation
    >>> composite = CompositeValidator()
    >>> composite.add_field_rule(FieldValidationRule("email", EmailValidator()))
    >>> composite.add_business_rule("age_check", lambda data: (data.get('age', 0) >= 18, None))

Security Features:
- ReDoS vulnerability detection and prevention
- Pattern security analysis with risk assessment
- Input length limits and timeout protection
- Rate limiting and abuse prevention
- Comprehensive audit logging
- Memory usage monitoring
"""

from typing import Dict, Any, List, Optional

# Import main classes with graceful degradation
try:
    from .regex_validator import (
        CustomRegexValidator,
        CustomRegexValidationOptions,
        PatternSecurityAnalysis,
        PatternSecurityAnalyzer,
        TimeoutError
    )
    from .composite_validator import (
        CompositeValidator,
        CompositeValidationResult,
        FieldValidationRule,
        BusinessRule,
        ValidationStrategy,
        create_user_registration_validator,
        create_financial_profile_validator
    )
    _VALIDATORS_AVAILABLE = True
except ImportError:
    _VALIDATORS_AVAILABLE = False
    
    # Provide basic interface for development
    CustomRegexValidator = None
    CompositeValidator = None

def get_available_validators() -> Dict[str, Any]:
    """Get list of available custom validators"""
    validators = {}
    
    if _VALIDATORS_AVAILABLE:
        validators.update({
            'custom_regex': {
                'class': CustomRegexValidator,
                'description': 'Secure custom regex validator with ReDoS protection',
                'features': [
                    'redos_protection',
                    'pattern_security_analysis',
                    'timeout_protection',
                    'complexity_analysis',
                    'performance_monitoring'
                ]
            },
            'composite': {
                'class': CompositeValidator,
                'description': 'Multi-field and business rule validator',
                'features': [
                    'multi_field_validation',
                    'business_rules',
                    'validation_strategies',
                    'field_dependencies',
                    'conditional_logic'
                ]
            }
        })
    
    return validators

def create_custom_regex_validator(pattern: str, **options) -> Optional[Any]:
    """
    Factory function to create a custom regex validator.
    
    Args:
        pattern: Regular expression pattern
        **options: Validation options
        
    Returns:
        CustomRegexValidator instance or None if not available
    """
    if _VALIDATORS_AVAILABLE and CustomRegexValidator:
        return CustomRegexValidator(pattern, **options)
    return None

def create_composite_validator(name: str = "Custom") -> Optional[Any]:
    """
    Factory function to create a composite validator.
    
    Args:
        name: Name for the validator
        
    Returns:
        CompositeValidator instance or None if not available
    """
    if _VALIDATORS_AVAILABLE and CompositeValidator:
        return CompositeValidator(name=name)
    return None

def analyze_pattern_security(pattern: str) -> Optional[Dict[str, Any]]:
    """
    Analyze a regex pattern for security vulnerabilities.
    
    Args:
        pattern: Regular expression pattern to analyze
        
    Returns:
        Security analysis results or None if not available
    """
    if _VALIDATORS_AVAILABLE and PatternSecurityAnalyzer:
        analyzer = PatternSecurityAnalyzer()
        analysis = analyzer.analyze_pattern(pattern)
        return {
            'complexity_score': analysis.complexity_score,
            'has_redos_risk': analysis.has_redos_risk,
            'risk_patterns': analysis.risk_patterns,
            'recommendations': analysis.recommendations,
            'is_safe': analysis.is_safe
        }
    return None

# Common validation patterns
COMMON_PATTERNS = {
    'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
    'ipv4': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
    'ipv6': r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$',
    'mac_address': r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
    'hex_color': r'^#[0-9A-Fa-f]{6}$',
    'base64': r'^[A-Za-z0-9+/]*={0,2}$',
    'jwt_token': r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$',
    'semver': r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$',
}

def get_common_pattern(pattern_name: str) -> Optional[str]:
    """
    Get a common validation pattern by name.
    
    Args:
        pattern_name: Name of the pattern
        
    Returns:
        Regex pattern string or None if not found
    """
    return COMMON_PATTERNS.get(pattern_name.lower())

def list_common_patterns() -> List[str]:
    """Get list of available common patterns"""
    return list(COMMON_PATTERNS.keys())

def create_pattern_validator(pattern_name: str, **options) -> Optional[Any]:
    """
    Create a validator using a common pattern.
    
    Args:
        pattern_name: Name of the common pattern
        **options: Validation options
        
    Returns:
        CustomRegexValidator instance or None if not available
    """
    pattern = get_common_pattern(pattern_name)
    if pattern and _VALIDATORS_AVAILABLE:
        return create_custom_regex_validator(
            pattern, 
            name=f"Common_{pattern_name.title()}", 
            **options
        )
    return None

# Package information
__version__ = "1.0.0"
__author__ = "PyIDVerify Development Team"
__description__ = "Custom validation capabilities with security-first design"

# Export public interface
__all__ = [
    # Main classes
    "CustomRegexValidator",
    "CustomRegexValidationOptions", 
    "PatternSecurityAnalysis",
    "PatternSecurityAnalyzer",
    "CompositeValidator",
    "CompositeValidationResult",
    "FieldValidationRule",
    "BusinessRule",
    "ValidationStrategy",
    
    # Factory functions
    "create_custom_regex_validator",
    "create_composite_validator",
    "create_user_registration_validator",
    "create_financial_profile_validator",
    "create_pattern_validator",
    
    # Utility functions
    "get_available_validators",
    "analyze_pattern_security",
    "get_common_pattern",
    "list_common_patterns",
    
    # Constants
    "COMMON_PATTERNS",
    
    # Exceptions
    "TimeoutError",
]

# Module-level configuration
def configure_defaults(**options) -> None:
    """Configure default options for custom validators"""
    global _default_options
    _default_options = options

def get_package_info() -> Dict[str, Any]:
    """Get package information and status"""
    return {
        'name': 'pyidverify.validators.custom',
        'version': __version__,
        'description': __description__,
        'author': __author__,
        'validators_available': _VALIDATORS_AVAILABLE,
        'available_validators': list(get_available_validators().keys()),
        'common_patterns': list_common_patterns(),
        'features': [
            'regex_validation',
            'composite_validation',
            'security_analysis',
            'redos_protection',
            'business_rules',
            'pattern_templates'
        ]
    }
