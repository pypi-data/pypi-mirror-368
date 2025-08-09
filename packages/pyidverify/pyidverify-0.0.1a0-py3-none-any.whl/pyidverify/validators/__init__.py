"""
PyIDVerify Validators Package
============================

This package contains all the ID validation implementations for the PyIDVerify library.
The validators are organized by category and provide comprehensive validation for various
types of identification data.
"""

from typing import Dict, Any, List, Optional, Type, Union

# Version information
__version__ = "1.0.0-dev"
__author__ = "PyIDVerify Development Team"
__license__ = "MIT"

# Import core validator types and base classes
_CORE_AVAILABLE = True
_CORE_ERROR = None

try:
    from ..core.base_validator import BaseValidator
    from ..core.types import IDType, ValidationResult, ValidationLevel
    from ..core.exceptions import ValidationError, SecurityError
except ImportError as e:
    _CORE_AVAILABLE = False
    _CORE_ERROR = str(e)


def get_validator_class(validator_name: str) -> Optional[Type]:
    """Get a validator class by name with direct import."""
    try:
        if validator_name == 'email':
            from .personal.email import EmailValidator
            return EmailValidator
        elif validator_name == 'phone':
            from .personal.phone import PhoneValidator
            return PhoneValidator
        elif validator_name == 'ip_address':
            from .personal.ip_address import IPAddressValidator
            return IPAddressValidator
        elif validator_name == 'credit_card':
            from .financial.credit_card import CreditCardValidator
            return CreditCardValidator
        elif validator_name == 'bank_account':
            from .financial.bank_account import BankAccountValidator
            return BankAccountValidator
        elif validator_name == 'iban':
            from .financial.iban import IBANValidator
            return IBANValidator
        elif validator_name == 'ssn':
            from .government.ssn import SSNValidator
            return SSNValidator
        elif validator_name == 'drivers_license':
            from .government.drivers_license import DriversLicenseValidator
            return DriversLicenseValidator
        elif validator_name == 'passport':
            from .government.passport import PassportValidator
            return PassportValidator
        else:
            return None
    except ImportError:
        return None


def get_supported_validators() -> Dict[str, Dict[str, Any]]:
    """Get information about all supported validators."""
    validators_info = {}
    
    validator_list = [
        'email', 'phone', 'ip_address', 
        'credit_card', 'bank_account', 'iban',
        'ssn', 'drivers_license', 'passport'
    ]
    
    for name in validator_list:
        validator_class = get_validator_class(name)
        if validator_class:
            validators_info[name] = {
                'class': validator_class.__name__,
                'module': validator_class.__module__,
                'id_type': name,
                'available': True
            }
        else:
            validators_info[name] = {
                'class': f'{name.title()}Validator',
                'module': f'pyidverify.validators.{name}',
                'id_type': name,
                'available': False,
                'error': 'Import failed'
            }
            
    return validators_info


def list_available_validators() -> List[str]:
    """Get list of available validator names."""
    available = []
    validator_list = [
        'email', 'phone', 'ip_address', 
        'credit_card', 'bank_account', 'iban',
        'ssn', 'drivers_license', 'passport'
    ]
    
    for name in validator_list:
        if get_validator_class(name):
            available.append(name)
    
    return available


def create_validator(validator_name: str, **kwargs):
    """Create a validator instance by name."""
    validator_class = get_validator_class(validator_name)
    if validator_class:
        return validator_class(**kwargs)
    return None


def get_module_status() -> Dict[str, Dict[str, Any]]:
    """Get status of validator modules."""
    status = {
        'core': {
            'available': _CORE_AVAILABLE,
            'error': _CORE_ERROR if not _CORE_AVAILABLE else None
        }
    }
    
    # Check each validator category
    for category in ['personal', 'financial', 'government', 'custom']:
        try:
            __import__(f'pyidverify.pyidverify.validators.{category}')
            status[category] = {'available': True, 'error': None}
        except ImportError as e:
            status[category] = {'available': False, 'error': str(e)}
    
    return status


# Export main functions
__all__ = [
    'get_validator_class',
    'get_supported_validators', 
    'list_available_validators',
    'create_validator',
    'get_module_status',
]

if _CORE_AVAILABLE:
    __all__.extend(['BaseValidator', 'ValidationResult', 'ValidationLevel', 'IDType'])
