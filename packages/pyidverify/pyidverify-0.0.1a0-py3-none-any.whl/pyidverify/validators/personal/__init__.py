"""
Personal Identifier Validators
=============================

This module provides validators for personal identification information including
email addresses, phone numbers, and IP addresses.

Features:
- Email validation with RFC compliance and reputation checking
- Phone number validation with international format support
- IP address validation with IPv4/IPv6 and network analysis

Examples:
    >>> from pyidverify.validators.personal import EmailValidator, PhoneValidator, IPAddressValidator
    >>> 
    >>> # Email validation
    >>> email_validator = EmailValidator()
    >>> result = email_validator.validate("user@example.com")
    >>> print(f"Email valid: {result.is_valid}")
    >>> 
    >>> # Phone validation
    >>> phone_validator = PhoneValidator()
    >>> result = phone_validator.validate("+1-555-123-4567")
    >>> print(f"Phone valid: {result.is_valid}")
    >>> 
    >>> # IP validation
    >>> ip_validator = IPAddressValidator()
    >>> result = ip_validator.validate("192.168.1.1")
    >>> print(f"IP valid: {result.is_valid}")

Available Validators:
- EmailValidator: Comprehensive email address validation
- PhoneValidator: International phone number validation  
- IPAddressValidator: IPv4/IPv6 address validation
"""

# Import validation classes with graceful error handling
try:
    from .email import EmailValidator, EmailValidationOptions
    _EMAIL_AVAILABLE = True
except ImportError as e:
    _EMAIL_AVAILABLE = False
    _EMAIL_ERROR = str(e)

try:
    from .phone import PhoneValidator, PhoneValidationOptions
    _PHONE_AVAILABLE = True
except ImportError as e:
    _PHONE_AVAILABLE = False
    _PHONE_ERROR = str(e)

try:
    from .ip import IPAddressValidator, IPValidationOptions
    _IP_AVAILABLE = True
except ImportError as e:
    _IP_AVAILABLE = False
    _IP_ERROR = str(e)

# Create validator registry for personal identifiers
PERSONAL_VALIDATORS = {}

if _EMAIL_AVAILABLE:
    PERSONAL_VALIDATORS['email'] = EmailValidator

if _PHONE_AVAILABLE:
    PERSONAL_VALIDATORS['phone'] = PhoneValidator

if _IP_AVAILABLE:
    PERSONAL_VALIDATORS['ip'] = IPAddressValidator
    PERSONAL_VALIDATORS['ip_address'] = IPAddressValidator

def get_personal_validator(validator_type: str):
    """
    Get a personal identifier validator by type.
    
    Args:
        validator_type: Type of validator ('email', 'phone', 'ip')
        
    Returns:
        Validator class
        
    Raises:
        ValueError: If validator type is not available
    """
    validator_type = validator_type.lower()
    
    if validator_type not in PERSONAL_VALIDATORS:
        available = list(PERSONAL_VALIDATORS.keys())
        raise ValueError(
            f"Personal validator '{validator_type}' not available. "
            f"Available validators: {available}"
        )
    
    return PERSONAL_VALIDATORS[validator_type]

def create_personal_validator(validator_type: str, **options):
    """
    Create a personal identifier validator instance.
    
    Args:
        validator_type: Type of validator to create
        **options: Configuration options for the validator
        
    Returns:
        Configured validator instance
    """
    validator_class = get_personal_validator(validator_type)
    return validator_class(**options)

def list_personal_validators():
    """
    List available personal identifier validators.
    
    Returns:
        Dictionary with validator info
    """
    validators_info = {}
    
    for name, validator_class in PERSONAL_VALIDATORS.items():
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
        'email': {
            'available': _EMAIL_AVAILABLE,
            'error': _EMAIL_ERROR if not _EMAIL_AVAILABLE else None
        },
        'phone': {
            'available': _PHONE_AVAILABLE,
            'error': _PHONE_ERROR if not _PHONE_AVAILABLE else None
        },
        'ip': {
            'available': _IP_AVAILABLE,
            'error': _IP_ERROR if not _IP_AVAILABLE else None
        }
    }

# Export public interface
__all__ = [
    # Validator classes (if available)
]

# Add available validators to __all__
if _EMAIL_AVAILABLE:
    __all__.extend(['EmailValidator', 'EmailValidationOptions'])

if _PHONE_AVAILABLE:
    __all__.extend(['PhoneValidator', 'PhoneValidationOptions'])

if _IP_AVAILABLE:
    __all__.extend(['IPAddressValidator', 'IPValidationOptions'])

# Add utility functions
__all__.extend([
    'get_personal_validator',
    'create_personal_validator', 
    'list_personal_validators',
    'get_import_status',
    'PERSONAL_VALIDATORS'
])

# Version and metadata
__version__ = "1.0.0"
__author__ = "PyIDVerify Development Team"
__description__ = "Personal identifier validation library"
