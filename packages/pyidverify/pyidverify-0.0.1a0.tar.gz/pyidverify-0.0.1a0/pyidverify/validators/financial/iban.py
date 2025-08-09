"""
PyIDVerify IBAN Validator

Validates International Bank Account Numbers (IBAN) with MOD-97 algorithm
and country-specific formatting rules.

Author: PyIDVerify Team
License: MIT
"""

import re
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from ..core.base_validator import BaseValidator
from ..core.types import IDType, ValidationResult, ValidationLevel
from ..core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class IBANInfo:
    """Information about an IBAN."""
    iban: str
    country_code: str
    check_digits: str
    bank_code: str
    account_number: str
    is_valid: bool = True
    country_name: Optional[str] = None
    bank_name: Optional[str] = None


class IBANValidator(BaseValidator):
    """
    IBAN (International Bank Account Number) validator.
    
    Features:
    - MOD-97 check digit validation
    - Country-specific format validation
    - Length validation for 70+ countries
    - Bank code validation
    - Format normalization and display formatting
    - Comprehensive error reporting
    """
    
    SUPPORTED_TYPE = IDType.IBAN
    
    # IBAN country specifications: (country_code, length, format_regex, country_name)
    IBAN_SPECS = {
        'AD': (24, r'AD\d{2}\d{4}\d{4}\d{12}', 'Andorra'),
        'AE': (23, r'AE\d{2}\d{3}\d{16}', 'United Arab Emirates'),
        'AL': (28, r'AL\d{2}\d{8}[A-Z0-9]{16}', 'Albania'),
        'AT': (20, r'AT\d{2}\d{5}\d{11}', 'Austria'),
        'AZ': (28, r'AZ\d{2}[A-Z]{4}[A-Z0-9]{20}', 'Azerbaijan'),
        'BA': (20, r'BA\d{2}\d{3}\d{3}\d{8}\d{2}', 'Bosnia and Herzegovina'),
        'BE': (16, r'BE\d{2}\d{3}\d{7}\d{2}', 'Belgium'),
        'BG': (22, r'BG\d{2}[A-Z]{4}\d{6}\d{8}', 'Bulgaria'),
        'BH': (22, r'BH\d{2}[A-Z]{4}[A-Z0-9]{14}', 'Bahrain'),
        'BR': (29, r'BR\d{2}\d{8}\d{5}\d{10}[A-Z]{1}[A-Z0-9]{1}', 'Brazil'),
        'BY': (28, r'BY\d{2}[A-Z0-9]{4}\d{4}[A-Z0-9]{16}', 'Belarus'),
        'CH': (21, r'CH\d{2}\d{5}[A-Z0-9]{12}', 'Switzerland'),
        'CR': (22, r'CR\d{2}\d{4}\d{14}', 'Costa Rica'),
        'CY': (28, r'CY\d{2}\d{3}\d{5}[A-Z0-9]{16}', 'Cyprus'),
        'CZ': (24, r'CZ\d{2}\d{4}\d{6}\d{10}', 'Czech Republic'),
        'DE': (22, r'DE\d{2}\d{8}\d{10}', 'Germany'),
        'DK': (18, r'DK\d{2}\d{4}\d{9}\d{1}', 'Denmark'),
        'DO': (28, r'DO\d{2}[A-Z0-9]{4}\d{20}', 'Dominican Republic'),
        'EE': (20, r'EE\d{2}\d{2}\d{2}\d{11}\d{1}', 'Estonia'),
        'EG': (29, r'EG\d{2}\d{4}\d{4}\d{17}', 'Egypt'),
        'ES': (24, r'ES\d{2}\d{4}\d{4}\d{1}\d{1}\d{10}', 'Spain'),
        'FI': (18, r'FI\d{2}\d{6}\d{7}\d{1}', 'Finland'),
        'FO': (18, r'FO\d{2}\d{4}\d{9}\d{1}', 'Faroe Islands'),
        'FR': (27, r'FR\d{2}\d{5}\d{5}[A-Z0-9]{11}\d{2}', 'France'),
        'GB': (22, r'GB\d{2}[A-Z]{4}\d{6}\d{8}', 'United Kingdom'),
        'GE': (22, r'GE\d{2}[A-Z]{2}\d{16}', 'Georgia'),
        'GI': (23, r'GI\d{2}[A-Z]{4}[A-Z0-9]{15}', 'Gibraltar'),
        'GL': (18, r'GL\d{2}\d{4}\d{9}\d{1}', 'Greenland'),
        'GR': (27, r'GR\d{2}\d{3}\d{4}[A-Z0-9]{16}', 'Greece'),
        'GT': (28, r'GT\d{2}[A-Z0-9]{4}[A-Z0-9]{20}', 'Guatemala'),
        'HR': (21, r'HR\d{2}\d{7}\d{10}', 'Croatia'),
        'HU': (28, r'HU\d{2}\d{3}\d{4}\d{1}\d{15}\d{1}', 'Hungary'),
        'IE': (22, r'IE\d{2}[A-Z]{4}\d{6}\d{8}', 'Ireland'),
        'IL': (23, r'IL\d{2}\d{3}\d{3}\d{13}', 'Israel'),
        'IS': (26, r'IS\d{2}\d{4}\d{2}\d{6}\d{10}', 'Iceland'),
        'IT': (27, r'IT\d{2}[A-Z]{1}\d{5}\d{5}[A-Z0-9]{12}', 'Italy'),
        'JO': (30, r'JO\d{2}[A-Z]{4}\d{4}[A-Z0-9]{18}', 'Jordan'),
        'KW': (30, r'KW\d{2}[A-Z]{4}[A-Z0-9]{22}', 'Kuwait'),
        'KZ': (20, r'KZ\d{2}\d{3}[A-Z0-9]{13}', 'Kazakhstan'),
        'LB': (28, r'LB\d{2}\d{4}[A-Z0-9]{20}', 'Lebanon'),
        'LC': (32, r'LC\d{2}[A-Z]{4}[A-Z0-9]{24}', 'Saint Lucia'),
        'LI': (21, r'LI\d{2}\d{5}[A-Z0-9]{12}', 'Liechtenstein'),
        'LT': (20, r'LT\d{2}\d{5}\d{11}', 'Lithuania'),
        'LU': (20, r'LU\d{2}\d{3}[A-Z0-9]{13}', 'Luxembourg'),
        'LV': (21, r'LV\d{2}[A-Z]{4}[A-Z0-9]{13}', 'Latvia'),
        'MC': (27, r'MC\d{2}\d{5}\d{5}[A-Z0-9]{11}\d{2}', 'Monaco'),
        'MD': (24, r'MD\d{2}[A-Z0-9]{2}[A-Z0-9]{18}', 'Moldova'),
        'ME': (22, r'ME\d{2}\d{3}\d{13}\d{2}', 'Montenegro'),
        'MK': (19, r'MK\d{2}\d{3}[A-Z0-9]{10}\d{2}', 'North Macedonia'),
        'MR': (27, r'MR13\d{5}\d{5}\d{11}\d{2}', 'Mauritania'),
        'MT': (31, r'MT\d{2}[A-Z]{4}\d{5}[A-Z0-9]{18}', 'Malta'),
        'MU': (30, r'MU\d{2}[A-Z]{4}\d{2}\d{2}\d{12}\d{3}[A-Z]{3}', 'Mauritius'),
        'NL': (18, r'NL\d{2}[A-Z]{4}\d{10}', 'Netherlands'),
        'NO': (15, r'NO\d{2}\d{4}\d{6}\d{1}', 'Norway'),
        'PK': (24, r'PK\d{2}[A-Z]{4}[A-Z0-9]{16}', 'Pakistan'),
        'PL': (28, r'PL\d{2}\d{8}[A-Z0-9]{16}', 'Poland'),
        'PS': (29, r'PS\d{2}[A-Z]{4}[A-Z0-9]{21}', 'Palestine'),
        'PT': (25, r'PT\d{2}\d{4}\d{4}\d{11}\d{2}', 'Portugal'),
        'QA': (29, r'QA\d{2}[A-Z]{4}[A-Z0-9]{21}', 'Qatar'),
        'RO': (24, r'RO\d{2}[A-Z]{4}[A-Z0-9]{16}', 'Romania'),
        'RS': (22, r'RS\d{2}\d{3}\d{13}\d{2}', 'Serbia'),
        'SA': (24, r'SA\d{2}\d{2}[A-Z0-9]{18}', 'Saudi Arabia'),
        'SE': (24, r'SE\d{2}\d{3}\d{16}\d{1}', 'Sweden'),
        'SI': (19, r'SI\d{2}\d{5}\d{8}\d{2}', 'Slovenia'),
        'SK': (24, r'SK\d{2}\d{4}\d{6}\d{10}', 'Slovakia'),
        'SM': (27, r'SM\d{2}[A-Z]{1}\d{5}\d{5}[A-Z0-9]{12}', 'San Marino'),
        'TN': (24, r'TN59\d{2}\d{3}\d{13}\d{2}', 'Tunisia'),
        'TR': (26, r'TR\d{2}\d{5}[A-Z0-9]{1}[A-Z0-9]{16}', 'Turkey'),
        'UA': (29, r'UA\d{2}\d{6}[A-Z0-9]{19}', 'Ukraine'),
        'VG': (24, r'VG\d{2}[A-Z]{4}\d{16}', 'Virgin Islands'),
        'XK': (20, r'XK\d{2}\d{4}\d{10}\d{2}', 'Kosovo'),
    }
    
    def __init__(self, config=None):
        """Initialize IBAN validator."""
        super().__init__(config)
        logger.debug("IBANValidator initialized")
        
    def validate(self, 
                iban: str, 
                level: ValidationLevel = ValidationLevel.STANDARD,
                metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate IBAN with comprehensive checks.
        
        Args:
            iban: IBAN to validate
            level: Validation level (BASIC, STANDARD, STRICT)
            metadata: Additional validation metadata
            
        Returns:
            ValidationResult with detailed IBAN information
        """
        try:
            # Parse and normalize IBAN
            iban_info = self._parse_iban(iban)
            if not iban_info.is_valid:
                return ValidationResult(
                    is_valid=False,
                    id_type=IDType.IBAN,
                    confidence=0.0,
                    errors=['Invalid IBAN format'],
                    metadata={}
                )
                
            # Basic validation - format and length
            errors = []
            confidence = 0.8
            
            # Country validation
            if not self._validate_country(iban_info):
                errors.append(f'Invalid country code: {iban_info.country_code}')
                confidence = 0.2
                
            # Length validation
            if not self._validate_length(iban_info):
                errors.append(f'Invalid length for {iban_info.country_code} IBAN')
                confidence = 0.3
                
            # Format validation
            if not self._validate_format(iban_info):
                errors.append('Invalid format for country')
                confidence = 0.4
                
            # MOD-97 check digit validation
            if not self._validate_mod97(iban_info):
                errors.append('Invalid check digits (MOD-97 failed)')
                confidence = 0.1
                
            # Enhanced validation for higher levels
            validation_metadata = {
                'country_code': iban_info.country_code,
                'country_name': iban_info.country_name,
                'check_digits': iban_info.check_digits,
                'bank_code': iban_info.bank_code,
                'account_number': iban_info.account_number,
                'formatted_iban': self._format_iban(iban_info.iban),
            }
            
            if level in [ValidationLevel.STANDARD, ValidationLevel.STRICT]:
                # Bank code validation
                bank_validation = self._validate_bank_code(iban_info)
                if not bank_validation['is_valid']:
                    if level == ValidationLevel.STRICT:
                        errors.extend(bank_validation['errors'])
                        confidence = min(confidence, 0.6)
                    else:
                        # Warning for standard level
                        validation_metadata['bank_warnings'] = bank_validation['errors']
                        
                validation_metadata.update({
                    'bank_validation': bank_validation,
                    'iban_length': len(iban_info.iban),
                    'expected_length': self.IBAN_SPECS.get(iban_info.country_code, (0,))[0],
                })
                
            if level == ValidationLevel.STRICT:
                # Additional strict validation
                strict_checks = self._perform_strict_checks(iban_info)
                validation_metadata.update(strict_checks)
                
                if strict_checks.get('suspicious_patterns'):
                    confidence = min(confidence, 0.7)
                    errors.append('Suspicious patterns detected')
                    
            return ValidationResult(
                is_valid=len(errors) == 0,
                id_type=IDType.IBAN,
                confidence=confidence,
                errors=errors,
                metadata=validation_metadata
            )
            
        except Exception as e:
            logger.error(f"IBAN validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                id_type=IDType.IBAN,
                confidence=0.0,
                errors=[f'Validation error: {str(e)}'],
                metadata={}
            )
            
    def can_validate(self, value: str) -> bool:
        """Check if value looks like an IBAN."""
        try:
            clean_value = self._clean_iban(value)
            # Basic pattern: 2 letters + 2 digits + up to 30 alphanumeric
            pattern = r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$'
            return bool(re.match(pattern, clean_value))
        except:
            return False
            
    def normalize_iban(self, iban: str) -> str:
        """Normalize IBAN to standard format."""
        return self._clean_iban(iban)
        
    def format_iban(self, iban: str, grouped: bool = True) -> str:
        """Format IBAN for display."""
        clean_iban = self._clean_iban(iban)
        if grouped:
            return self._format_iban(clean_iban)
        return clean_iban
        
    def _parse_iban(self, iban: str) -> IBANInfo:
        """Parse IBAN into components."""
        try:
            clean_iban = self._clean_iban(iban)
            
            if len(clean_iban) < 4:
                return IBANInfo('', '', '', '', '', False)
                
            country_code = clean_iban[:2]
            check_digits = clean_iban[2:4]
            bank_account = clean_iban[4:]
            
            # Extract bank code (varies by country)
            bank_code, account_number = self._extract_bank_account(country_code, bank_account)
            
            country_name = None
            if country_code in self.IBAN_SPECS:
                country_name = self.IBAN_SPECS[country_code][2]
                
            return IBANInfo(
                iban=clean_iban,
                country_code=country_code,
                check_digits=check_digits,
                bank_code=bank_code,
                account_number=account_number,
                country_name=country_name,
                is_valid=True
            )
            
        except Exception:
            return IBANInfo('', '', '', '', '', False)
            
    def _clean_iban(self, iban: str) -> str:
        """Clean and normalize IBAN."""
        # Remove spaces, hyphens, and convert to uppercase
        return re.sub(r'[\s\-]', '', iban.upper())
        
    def _validate_country(self, iban_info: IBANInfo) -> bool:
        """Validate country code."""
        return iban_info.country_code in self.IBAN_SPECS
        
    def _validate_length(self, iban_info: IBANInfo) -> bool:
        """Validate IBAN length for country."""
        if iban_info.country_code not in self.IBAN_SPECS:
            return False
        expected_length = self.IBAN_SPECS[iban_info.country_code][0]
        return len(iban_info.iban) == expected_length
        
    def _validate_format(self, iban_info: IBANInfo) -> bool:
        """Validate IBAN format for country."""
        if iban_info.country_code not in self.IBAN_SPECS:
            return False
        format_regex = self.IBAN_SPECS[iban_info.country_code][1]
        return bool(re.match(format_regex, iban_info.iban))
        
    def _validate_mod97(self, iban_info: IBANInfo) -> bool:
        """Validate IBAN using MOD-97 algorithm."""
        try:
            # Rearrange: move first 4 characters to end
            rearranged = iban_info.iban[4:] + iban_info.iban[:4]
            
            # Replace letters with numbers (A=10, B=11, ..., Z=35)
            numeric_string = ''
            for char in rearranged:
                if char.isalpha():
                    numeric_string += str(ord(char) - ord('A') + 10)
                else:
                    numeric_string += char
                    
            # Calculate MOD 97
            remainder = int(numeric_string) % 97
            return remainder == 1
            
        except (ValueError, OverflowError):
            # For very long IBANs, use iterative MOD calculation
            try:
                return self._mod97_iterative(iban_info.iban)
            except:
                return False
                
    def _mod97_iterative(self, iban: str) -> bool:
        """MOD-97 calculation for long IBANs."""
        # Rearrange: move first 4 characters to end
        rearranged = iban[4:] + iban[:4]
        
        # Replace letters with numbers and calculate MOD iteratively
        remainder = 0
        for char in rearranged:
            if char.isalpha():
                remainder = (remainder * 100 + (ord(char) - ord('A') + 10)) % 97
            else:
                remainder = (remainder * 10 + int(char)) % 97
                
        return remainder == 1
        
    def _extract_bank_account(self, country_code: str, bank_account: str) -> tuple:
        """Extract bank code and account number based on country."""
        # Simplified extraction - in production, use detailed country specifications
        bank_code_lengths = {
            'DE': 8,  # Germany: 8-digit bank code
            'FR': 10, # France: 5-digit bank + 5-digit branch
            'GB': 10, # UK: 4-letter bank + 6-digit sort code
            'IT': 11, # Italy: 1 check + 5-digit ABI + 5-digit CAB
            'ES': 8,  # Spain: 4-digit bank + 4-digit branch
            'NL': 4,  # Netherlands: 4-letter bank code
            'CH': 5,  # Switzerland: 5-digit bank code
            'AT': 5,  # Austria: 5-digit bank code
        }
        
        bank_length = bank_code_lengths.get(country_code, 4)
        bank_code = bank_account[:bank_length] if len(bank_account) >= bank_length else bank_account
        account_number = bank_account[bank_length:] if len(bank_account) > bank_length else ''
        
        return bank_code, account_number
        
    def _validate_bank_code(self, iban_info: IBANInfo) -> Dict[str, Any]:
        """Validate bank code (placeholder - would integrate with bank directories)."""
        return {
            'is_valid': True,
            'errors': [],
            'bank_name': None,
            'bank_address': None
        }
        
    def _perform_strict_checks(self, iban_info: IBANInfo) -> Dict[str, Any]:
        """Perform additional strict validation checks."""
        checks = {
            'suspicious_patterns': False,
            'bank_exists': True,
            'country_restrictions': [],
        }
        
        # Check for suspicious patterns
        if iban_info.account_number == '0' * len(iban_info.account_number):
            checks['suspicious_patterns'] = True
            
        # Check for sequential patterns
        if len(iban_info.account_number) > 5:
            digits = ''.join(c for c in iban_info.account_number if c.isdigit())
            if len(digits) > 5:
                is_sequential = all(
                    int(digits[i]) == int(digits[i-1]) + 1 
                    for i in range(1, min(6, len(digits)))
                )
                if is_sequential:
                    checks['suspicious_patterns'] = True
                    
        return checks
        
    def _format_iban(self, iban: str) -> str:
        """Format IBAN with spaces for readability."""
        # Group in blocks of 4 characters
        formatted = ' '.join(iban[i:i+4] for i in range(0, len(iban), 4))
        return formatted
        
    def get_supported_types(self) -> List[IDType]:
        """Get supported ID types."""
        return [IDType.IBAN]
        
    def get_supported_countries(self) -> List[str]:
        """Get list of supported country codes."""
        return list(self.IBAN_SPECS.keys())
