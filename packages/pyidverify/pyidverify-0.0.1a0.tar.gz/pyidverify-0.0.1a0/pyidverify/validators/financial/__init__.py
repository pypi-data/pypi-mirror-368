"""
Financial Identifier Validators
==============================

This module provides validators for financial identification information including
credit cards, bank accounts, and other financial instruments.

Features:
- Credit card validation with Luhn algorithm and network detection
- US bank account validation with ABA routing numbers
- International Bank Account Number (IBAN) validation
- Fraud detection and security compliance
- PCI DSS compliant logging and data handling

Examples:
    >>> from pyidverify.validators.financial import CreditCardValidator, BankAccountValidator
    >>> 
    >>> # Credit card validation
    >>> cc_validator = CreditCardValidator()
    >>> result = cc_validator.validate("4111111111111111")
    >>> print(f"Card valid: {result.is_valid}")
    >>> 
    >>> # Bank account validation
    >>> bank_validator = BankAccountValidator()
    >>> result = bank_validator.validate_us_account("021000021", "1234567890")
    >>> print(f"Account valid: {result.is_valid}")
    >>> 
    >>> # IBAN validation
    >>> result = bank_validator.validate_iban("GB29NWBK60161331926819")
    >>> print(f"IBAN valid: {result.is_valid}")

Available Validators:
- CreditCardValidator: Comprehensive credit card validation with network detection
- BankAccountValidator: US and international bank account validation
"""

# Import validation classes with graceful error handling
try:
    from .credit_card import CreditCardValidator, CreditCardValidationOptions
    _CREDIT_CARD_AVAILABLE = True
except ImportError as e:
    _CREDIT_CARD_AVAILABLE = False
    _CREDIT_CARD_ERROR = str(e)

try:
    from .bank_account import BankAccountValidator, BankAccountValidationOptions
    _BANK_ACCOUNT_AVAILABLE = True
except ImportError as e:
    _BANK_ACCOUNT_AVAILABLE = False
    _BANK_ACCOUNT_ERROR = str(e)

# Create validator registry for financial identifiers
FINANCIAL_VALIDATORS = {}

if _CREDIT_CARD_AVAILABLE:
    FINANCIAL_VALIDATORS['credit_card'] = CreditCardValidator
    FINANCIAL_VALIDATORS['card'] = CreditCardValidator

if _BANK_ACCOUNT_AVAILABLE:
    FINANCIAL_VALIDATORS['bank_account'] = BankAccountValidator
    FINANCIAL_VALIDATORS['account'] = BankAccountValidator
    FINANCIAL_VALIDATORS['iban'] = BankAccountValidator

def get_financial_validator(validator_type: str):
    """
    Get a financial identifier validator by type.
    
    Args:
        validator_type: Type of validator ('credit_card', 'bank_account', 'iban')
        
    Returns:
        Validator class
        
    Raises:
        ValueError: If validator type is not available
    """
    validator_type = validator_type.lower()
    
    if validator_type not in FINANCIAL_VALIDATORS:
        available = list(FINANCIAL_VALIDATORS.keys())
        raise ValueError(
            f"Financial validator '{validator_type}' not available. "
            f"Available validators: {available}"
        )
    
    return FINANCIAL_VALIDATORS[validator_type]

def create_financial_validator(validator_type: str, **options):
    """
    Create a financial identifier validator instance.
    
    Args:
        validator_type: Type of validator to create
        **options: Configuration options for the validator
        
    Returns:
        Configured validator instance
    """
    validator_class = get_financial_validator(validator_type)
    return validator_class(**options)

def list_financial_validators():
    """
    List available financial identifier validators.
    
    Returns:
        Dictionary with validator info
    """
    validators_info = {}
    
    for name, validator_class in FINANCIAL_VALIDATORS.items():
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
        'credit_card': {
            'available': _CREDIT_CARD_AVAILABLE,
            'error': _CREDIT_CARD_ERROR if not _CREDIT_CARD_AVAILABLE else None
        },
        'bank_account': {
            'available': _BANK_ACCOUNT_AVAILABLE,
            'error': _BANK_ACCOUNT_ERROR if not _BANK_ACCOUNT_AVAILABLE else None
        }
    }

# Security and compliance utilities
def validate_pci_compliance(validator_config: dict) -> dict:
    """
    Validate PCI DSS compliance settings for financial validators.
    
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
    
    # Check for anonymization in logs
    if not validator_config.get('anonymize_logs', True):
        compliance_status['is_compliant'] = False
        compliance_status['warnings'].append("Logging without anonymization violates PCI DSS requirements")
        compliance_status['recommendations'].append("Enable anonymize_logs option")
    
    # Check for rate limiting
    if not validator_config.get('rate_limiting', True):
        compliance_status['warnings'].append("Rate limiting recommended for PCI compliance")
        compliance_status['recommendations'].append("Enable rate limiting to prevent enumeration attacks")
    
    # Check for audit logging
    if not validator_config.get('audit_logging', True):
        compliance_status['warnings'].append("Audit logging recommended for PCI compliance")
        compliance_status['recommendations'].append("Enable audit logging for compliance requirements")
    
    return compliance_status

def get_supported_card_networks():
    """Get list of supported credit card networks"""
    if _CREDIT_CARD_AVAILABLE:
        try:
            validator = CreditCardValidator()
            info = validator.get_info()
            return info.get('supported_networks', [])
        except Exception:
            pass
    
    # Fallback list
    return ['visa', 'mastercard', 'amex', 'discover', 'jcb', 'diners']

def get_supported_iban_countries():
    """Get list of supported IBAN countries"""
    if _BANK_ACCOUNT_AVAILABLE:
        try:
            validator = BankAccountValidator()
            info = validator.get_info()
            return info.get('iban_countries_supported', 0)
        except Exception:
            pass
    
    return 0

def create_secure_validator(validator_type: str, **options):
    """
    Create a financial validator with security-focused configuration.
    
    Args:
        validator_type: Type of validator to create
        **options: Additional configuration options
        
    Returns:
        Configured validator with security settings
    """
    # Security-focused defaults
    secure_options = {
        'anonymize_logs': True,
        'strict_validation': True,
        'check_fraud_patterns': True,
        'validate_checksum': True,
    }
    
    # Credit card specific security options
    if validator_type.lower() in ['credit_card', 'card']:
        secure_options.update({
            'validate_luhn': True,
            'validate_network': True,
            'check_test_cards': True
        })
    
    # Bank account specific security options
    elif validator_type.lower() in ['bank_account', 'account', 'iban']:
        secure_options.update({
            'validate_routing': True,
            'validate_institution': True,
            'validate_account_format': True
        })
    
    # Merge with user options (user options take precedence)
    secure_options.update(options)
    
    return create_financial_validator(validator_type, **secure_options)

# Export public interface
__all__ = [
    # Validator classes (if available)
]

# Add available validators to __all__
if _CREDIT_CARD_AVAILABLE:
    __all__.extend(['CreditCardValidator', 'CreditCardValidationOptions'])

if _BANK_ACCOUNT_AVAILABLE:
    __all__.extend(['BankAccountValidator', 'BankAccountValidationOptions'])

# Add utility functions
__all__.extend([
    'get_financial_validator',
    'create_financial_validator',
    'list_financial_validators',
    'get_import_status',
    'validate_pci_compliance',
    'get_supported_card_networks',
    'get_supported_iban_countries',
    'create_secure_validator',
    'FINANCIAL_VALIDATORS'
])

# Version and metadata
__version__ = "1.0.0"
__author__ = "PyIDVerify Development Team"
__description__ = "Financial identifier validation library with PCI DSS compliance"
