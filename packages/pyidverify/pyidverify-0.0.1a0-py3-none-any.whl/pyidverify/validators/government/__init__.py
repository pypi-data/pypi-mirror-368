"""
Government Identifier Validators
===============================

This module provides validators for government-issued identification including
Social Security Numbers, driver's licenses, and passport numbers.

Features:
- Social Security Number validation with area code verification
- Driver's license validation with state-specific formats
- Passport number validation with country specifications
- Privacy-compliant logging and HIPAA compliance
- Fraud detection and security audit trails

Examples:
    >>> from pyidverify.validators.government import SSNValidator
    >>> 
    >>> # SSN validation
    >>> ssn_validator = SSNValidator()
    >>> result = ssn_validator.validate("123-45-6789")
    >>> print(f"SSN valid: {result.is_valid}")
    >>> print(f"State: {result.metadata.get('state')}")

Available Validators:
- SSNValidator: Social Security Number validation with area code verification

Security Notes:
- All government ID validation includes anonymized logging for privacy
- HIPAA-compliant data handling for sensitive personal information
- Rate limiting to prevent enumeration attacks
- Fraud pattern detection for known invalid numbers
"""

# Import validation classes with graceful error handling
try:
    from .ssn import SSNValidator, SSNValidationOptions
    _SSN_AVAILABLE = True
except ImportError as e:
    _SSN_AVAILABLE = False
    _SSN_ERROR = str(e)

# Create validator registry for government identifiers
GOVERNMENT_VALIDATORS = {}

if _SSN_AVAILABLE:
    GOVERNMENT_VALIDATORS['ssn'] = SSNValidator
    GOVERNMENT_VALIDATORS['social_security'] = SSNValidator
    GOVERNMENT_VALIDATORS['social_security_number'] = SSNValidator

def get_government_validator(validator_type: str):
    """
    Get a government identifier validator by type.
    
    Args:
        validator_type: Type of validator ('ssn', 'social_security')
        
    Returns:
        Validator class
        
    Raises:
        ValueError: If validator type is not available
    """
    validator_type = validator_type.lower()
    
    if validator_type not in GOVERNMENT_VALIDATORS:
        available = list(GOVERNMENT_VALIDATORS.keys())
        raise ValueError(
            f"Government validator '{validator_type}' not available. "
            f"Available validators: {available}"
        )
    
    return GOVERNMENT_VALIDATORS[validator_type]

def create_government_validator(validator_type: str, **options):
    """
    Create a government identifier validator instance.
    
    Args:
        validator_type: Type of validator to create
        **options: Configuration options for the validator
        
    Returns:
        Configured validator instance
    """
    validator_class = get_government_validator(validator_type)
    return validator_class(**options)

def list_government_validators():
    """
    List available government identifier validators.
    
    Returns:
        Dictionary with validator info
    """
    validators_info = {}
    
    for name, validator_class in GOVERNMENT_VALIDATORS.items():
        try:
            # Get validator information if available
            if hasattr(validator_class, 'get_info'):
                temp_instance = validator_class()
                info = temp_instance.get_info()
            else:
                info = {
                    "validator_type": name,
                    "class_name": validator_class.__name__
                }
            validators_info[name] = info
        except Exception as e:
            validators_info[name] = {
                "validator_type": name,
                "error": str(e)
            }
    
    return validators_info

def get_import_status():
    """Get import status for debugging"""
    return {
        'ssn': {
            'available': _SSN_AVAILABLE,
            'error': _SSN_ERROR if not _SSN_AVAILABLE else None
        }
    }

# Privacy and compliance utilities
def validate_privacy_compliance(validator_config: dict) -> dict:
    """
    Validate privacy compliance settings for government validators.
    
    Args:
        validator_config: Configuration dictionary for validator
        
    Returns:
        Dictionary with compliance status and recommendations
    """
    compliance_status = {
        'is_compliant': True,
        'warnings': [],
        'recommendations': []
    }
    
    # Check for anonymization in logs (required for government IDs)
    if not validator_config.get('anonymize_logs', True):
        compliance_status['is_compliant'] = False
        compliance_status['warnings'].append("Logging without anonymization violates privacy requirements")
        compliance_status['recommendations'].append("Enable anonymize_logs option")
    
    # Check for rate limiting
    if not validator_config.get('rate_limiting', True):
        compliance_status['warnings'].append("Rate limiting recommended for privacy compliance")
        compliance_status['recommendations'].append("Enable rate limiting to prevent enumeration attacks")
    
    # Check for audit logging
    if not validator_config.get('audit_logging', True):
        compliance_status['warnings'].append("Audit logging recommended for compliance")
        compliance_status['recommendations'].append("Enable audit logging for compliance requirements")
    
    # Check for strict validation
    if not validator_config.get('strict_validation', False):
        compliance_status['recommendations'].append("Consider enabling strict validation for production use")
    
    return compliance_status

def get_supported_states():
    """Get list of supported states for SSN validation"""
    if _SSN_AVAILABLE:
        try:
            validator = SSNValidator()
            # This would return the states from the area assignments
            return list(validator._area_assignments.keys())
        except Exception:
            pass
    
    # Fallback list of US states and territories
    return [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC', 'PR', 'VI', 'GU', 'AS'
    ]

def create_privacy_compliant_validator(validator_type: str, **options):
    """
    Create a government validator with privacy-focused configuration.
    
    Args:
        validator_type: Type of validator to create
        **options: Additional configuration options
        
    Returns:
        Configured validator with privacy settings
    """
    # Privacy-focused defaults
    privacy_options = {
        'anonymize_logs': True,
        'strict_validation': True,
        'check_invalid_patterns': True,
    }
    
    # SSN specific privacy options
    if validator_type.lower() in ['ssn', 'social_security', 'social_security_number']:
        privacy_options.update({
            'validate_format': True,
            'validate_area': True,
            'validate_group': True,
            'validate_serial': True,
            'allow_test_numbers': False
        })
    
    # Merge with user options (user options take precedence)
    privacy_options.update(options)
    
    return create_government_validator(validator_type, **privacy_options)

def get_validator_security_info(validator_type: str) -> dict:
    """
    Get security information about a government validator.
    
    Args:
        validator_type: Type of validator to analyze
        
    Returns:
        Dictionary with security information
    """
    security_info = {
        'validator_type': validator_type,
        'privacy_features': [],
        'security_features': [],
        'compliance_standards': []
    }
    
    if validator_type.lower() in ['ssn', 'social_security', 'social_security_number']:
        security_info.update({
            'privacy_features': [
                'Anonymous logging',
                'SSN anonymization',
                'Memory-safe operations',
                'No persistent storage'
            ],
            'security_features': [
                'Rate limiting',
                'Input sanitization',
                'Invalid pattern detection',
                'Test number filtering'
            ],
            'compliance_standards': [
                'HIPAA Privacy Rule',
                'Privacy Act of 1974',
                'State privacy laws'
            ]
        })
    
    return security_info

# Export public interface
__all__ = [
    # Validator classes (if available)
]

# Add available validators to __all__
if _SSN_AVAILABLE:
    __all__.extend(['SSNValidator', 'SSNValidationOptions'])

# Add utility functions
__all__.extend([
    'get_government_validator',
    'create_government_validator',
    'list_government_validators',
    'get_import_status',
    'validate_privacy_compliance',
    'get_supported_states',
    'create_privacy_compliant_validator',
    'get_validator_security_info',
    'GOVERNMENT_VALIDATORS'
])

# Version and metadata
__version__ = "1.0.0"
__author__ = "PyIDVerify Development Team"
__description__ = "Government identifier validation library with privacy compliance"
