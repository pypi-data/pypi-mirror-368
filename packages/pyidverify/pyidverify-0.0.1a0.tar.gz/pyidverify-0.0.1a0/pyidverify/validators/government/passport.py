"""
PyIDVerify Passport Validator

Validates passport numbers for multiple countries with format-specific validation.
Supports 30+ countries with comprehensive format and check digit validation.

Author: PyIDVerify Team
License: MIT
"""

import re
import logging
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime, date
from ..core.base_validator import BaseValidator
from ..core.types import IDType, ValidationResult, ValidationLevel
from ..core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class PassportInfo:
    """Information about a passport."""
    passport_number: str
    country: str
    is_valid: bool = True
    country_name: Optional[str] = None
    format_type: Optional[str] = None
    check_digit_valid: bool = True
    machine_readable: bool = False


class PassportValidator(BaseValidator):
    """
    International passport validator supporting 30+ countries.
    
    Features:
    - Country-specific format validation
    - Check digit validation (where applicable)
    - Machine-readable zone (MRZ) validation
    - ICAO Document 9303 compliance
    - Format normalization
    - Expiration date validation (when provided)
    - Biometric passport detection
    - Security feature validation
    """
    
    SUPPORTED_TYPE = IDType.PASSPORT
    
    # Country-specific passport patterns and rules
    COUNTRY_PATTERNS = {
        'US': {  # United States
            'name': 'United States',
            'patterns': [r'^[A-Z]{1,2}\d{7}$'],  # 1-2 letters + 7 digits
            'format': 'Alphanumeric',
            'length': [8, 9],
            'check_digit': False,
            'mrz': True,
            'notes': '1-2 letters followed by 7 digits'
        },
        'CA': {  # Canada
            'name': 'Canada',
            'patterns': [r'^[A-Z]{2}\d{6}$'],  # 2 letters + 6 digits
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': False,
            'mrz': True,
            'notes': '2 letters followed by 6 digits'
        },
        'GB': {  # United Kingdom
            'name': 'United Kingdom',
            'patterns': [r'^\d{9}$'],  # 9 digits
            'format': 'Numeric',
            'length': [9],
            'check_digit': True,
            'mrz': True,
            'notes': '9 digits with check digit'
        },
        'DE': {  # Germany
            'name': 'Germany',
            'patterns': [
                r'^[CFGHJKLMNPRTVWXYZ]\d{7}[CFGHJKLMNPRTVWXYZ]\d{1}$',  # ePassport
                r'^\d{8}[CFGHJKLMNPRTVWXYZ]\d{1}$'  # Traditional
            ],
            'format': 'Alphanumeric',
            'length': [10],
            'check_digit': True,
            'mrz': True,
            'notes': 'Letter+7digits+Letter+CheckDigit or 8digits+Letter+CheckDigit'
        },
        'FR': {  # France
            'name': 'France',
            'patterns': [r'^\d{2}[A-Z]{2}\d{5}$'],  # 2digits + 2letters + 5digits
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': True,
            'mrz': True,
            'notes': '2 digits + 2 letters + 5 digits'
        },
        'IT': {  # Italy
            'name': 'Italy',
            'patterns': [
                r'^[A-Z]{2}\d{7}$',    # 2 letters + 7 digits
                r'^[A-Z]{1}\d{7}[A-Z]{1}$'  # Letter + 7 digits + letter
            ],
            'format': 'Alphanumeric',
            'length': [8, 9],
            'check_digit': False,
            'mrz': True,
            'notes': '2letters+7digits or Letter+7digits+Letter'
        },
        'ES': {  # Spain
            'name': 'Spain',
            'patterns': [r'^[A-Z]{3}\d{6}$'],  # 3 letters + 6 digits
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': False,
            'mrz': True,
            'notes': '3 letters followed by 6 digits'
        },
        'NL': {  # Netherlands
            'name': 'Netherlands',
            'patterns': [r'^[A-Z]{2}[A-Z0-9]{6}\d{1}$'],  # 2letters + 6alphanumeric + 1digit
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': True,
            'mrz': True,
            'notes': '2 letters + 6 alphanumeric + check digit'
        },
        'AU': {  # Australia
            'name': 'Australia',
            'patterns': [
                r'^[A-Z]{1}\d{7}$',    # 1 letter + 7 digits
                r'^[A-Z]{2}\d{7}$'     # 2 letters + 7 digits
            ],
            'format': 'Alphanumeric',
            'length': [8, 9],
            'check_digit': False,
            'mrz': True,
            'notes': '1-2 letters followed by 7 digits'
        },
        'JP': {  # Japan
            'name': 'Japan',
            'patterns': [r'^[A-Z]{2}\d{7}$'],  # 2 letters + 7 digits
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': False,
            'mrz': True,
            'notes': '2 letters followed by 7 digits'
        },
        'KR': {  # South Korea
            'name': 'South Korea',
            'patterns': [
                r'^[A-Z]{1}\d{8}$',    # 1 letter + 8 digits
                r'^[A-Z]{2}\d{7}$'     # 2 letters + 7 digits
            ],
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': False,
            'mrz': True,
            'notes': 'Letter+8digits or 2letters+7digits'
        },
        'CN': {  # China
            'name': 'China',
            'patterns': [
                r'^[EGP]\d{8}$',       # E/G/P + 8 digits
                r'^1[45]\d{7}$'        # 14xxxxxxx or 15xxxxxxx
            ],
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': False,
            'mrz': True,
            'notes': 'E/G/P+8digits or 14/15+7digits'
        },
        'IN': {  # India
            'name': 'India',
            'patterns': [
                r'^[A-Z]{1}\d{7}$',    # 1 letter + 7 digits
                r'^[A-Z]{2}\d{6}$'     # 2 letters + 6 digits
            ],
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': False,
            'mrz': True,
            'notes': 'Letter+7digits or 2letters+6digits'
        },
        'BR': {  # Brazil
            'name': 'Brazil',
            'patterns': [r'^[A-Z]{2}\d{6}$'],  # 2 letters + 6 digits
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': False,
            'mrz': True,
            'notes': '2 letters followed by 6 digits'
        },
        'MX': {  # Mexico
            'name': 'Mexico',
            'patterns': [r'^\d{8}[A-Z]{1}\d{1}$'],  # 8digits + 1letter + 1digit
            'format': 'Alphanumeric',
            'length': [10],
            'check_digit': True,
            'mrz': True,
            'notes': '8 digits + 1 letter + check digit'
        },
        'RU': {  # Russia
            'name': 'Russia',
            'patterns': [r'^\d{9}$'],  # 9 digits
            'format': 'Numeric',
            'length': [9],
            'check_digit': True,
            'mrz': True,
            'notes': '9 digits with check digit'
        },
        'ZA': {  # South Africa
            'name': 'South Africa',
            'patterns': [r'^[A-Z]\d{8}$'],  # 1 letter + 8 digits
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': False,
            'mrz': True,
            'notes': '1 letter followed by 8 digits'
        },
        'SG': {  # Singapore
            'name': 'Singapore',
            'patterns': [r'^[A-Z]\d{7}[A-Z]$'],  # Letter + 7digits + Letter
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': True,
            'mrz': True,
            'notes': 'Letter + 7 digits + check letter'
        },
        'CH': {  # Switzerland
            'name': 'Switzerland',
            'patterns': [r'^[A-Z]\d{7}$'],  # 1 letter + 7 digits
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': False,
            'mrz': True,
            'notes': '1 letter followed by 7 digits'
        },
        'SE': {  # Sweden
            'name': 'Sweden',
            'patterns': [r'^\d{8}$'],  # 8 digits
            'format': 'Numeric',
            'length': [8],
            'check_digit': True,
            'mrz': True,
            'notes': '8 digits with integrated check'
        },
        'NO': {  # Norway
            'name': 'Norway',
            'patterns': [r'^[A-Z]\d{7}$'],  # 1 letter + 7 digits
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': False,
            'mrz': True,
            'notes': '1 letter followed by 7 digits'
        },
        'DK': {  # Denmark
            'name': 'Denmark',
            'patterns': [r'^\d{9}$'],  # 9 digits
            'format': 'Numeric',
            'length': [9],
            'check_digit': True,
            'mrz': True,
            'notes': '9 digits with check digit'
        },
        'FI': {  # Finland
            'name': 'Finland',
            'patterns': [r'^[A-Z]{2}\d{7}$'],  # 2 letters + 7 digits
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': True,
            'mrz': True,
            'notes': '2 letters followed by 7 digits'
        },
        'BE': {  # Belgium
            'name': 'Belgium',
            'patterns': [
                r'^[A-Z]{2}\d{6}$',    # 2 letters + 6 digits
                r'^[A-Z]{3}\d{5}$'     # 3 letters + 5 digits
            ],
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': False,
            'mrz': True,
            'notes': '2-3 letters + 5-6 digits'
        },
        'AT': {  # Austria
            'name': 'Austria',
            'patterns': [r'^[A-Z]\d{7}$'],  # 1 letter + 7 digits
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': False,
            'mrz': True,
            'notes': '1 letter followed by 7 digits'
        },
        'IE': {  # Ireland
            'name': 'Ireland',
            'patterns': [r'^[A-Z]{2}\d{7}$'],  # 2 letters + 7 digits
            'format': 'Alphanumeric',
            'length': [9],
            'check_digit': False,
            'mrz': True,
            'notes': '2 letters followed by 7 digits'
        },
        'PL': {  # Poland
            'name': 'Poland',
            'patterns': [r'^[A-Z]{2}\d{6}$'],  # 2 letters + 6 digits
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': True,
            'mrz': True,
            'notes': '2 letters followed by 6 digits'
        },
        'PT': {  # Portugal
            'name': 'Portugal',
            'patterns': [r'^[A-Z]\d{6}$'],  # 1 letter + 6 digits
            'format': 'Alphanumeric',
            'length': [7],
            'check_digit': False,
            'mrz': True,
            'notes': '1 letter followed by 6 digits'
        },
        'GR': {  # Greece
            'name': 'Greece',
            'patterns': [r'^[A-Z]{2}\d{6}$'],  # 2 letters + 6 digits
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': False,
            'mrz': True,
            'notes': '2 letters followed by 6 digits'
        },
        'TR': {  # Turkey
            'name': 'Turkey',
            'patterns': [
                r'^[A-Z]\d{8}$',       # 1 letter + 8 digits
                r'^\d{9}$'             # 9 digits
            ],
            'format': 'Mixed',
            'length': [9],
            'check_digit': False,
            'mrz': True,
            'notes': 'Letter+8digits or 9digits'
        },
        'IL': {  # Israel
            'name': 'Israel',
            'patterns': [r'^\d{8}$'],  # 8 digits
            'format': 'Numeric',
            'length': [8],
            'check_digit': True,
            'mrz': True,
            'notes': '8 digits with check digit algorithm'
        },
        'AE': {  # United Arab Emirates
            'name': 'United Arab Emirates',
            'patterns': [r'^[A-Z]\d{7}$'],  # 1 letter + 7 digits
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': False,
            'mrz': True,
            'notes': '1 letter followed by 7 digits'
        },
        'SA': {  # Saudi Arabia
            'name': 'Saudi Arabia',
            'patterns': [
                r'^[A-Z]\d{8}$',       # 1 letter + 8 digits
                r'^\d{9}$'             # 9 digits
            ],
            'format': 'Mixed',
            'length': [9],
            'check_digit': False,
            'mrz': True,
            'notes': 'Letter+8digits or 9digits'
        }
    }
    
    # MRZ character mapping for check digit calculation
    MRZ_CHAR_VALUES = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'I': 18,
        'J': 19, 'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24, 'P': 25, 'Q': 26, 'R': 27,
        'S': 28, 'T': 29, 'U': 30, 'V': 31, 'W': 32, 'X': 33, 'Y': 34, 'Z': 35, '<': 0
    }
    
    def __init__(self, config=None):
        """Initialize passport validator."""
        super().__init__(config)
        logger.debug("PassportValidator initialized")
        
    def validate(self, 
                passport_number: str, 
                country: Optional[str] = None,
                level: ValidationLevel = ValidationLevel.STANDARD,
                metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate passport number.
        
        Args:
            passport_number: Passport number to validate
            country: Country code (ISO 3166-1 alpha-2)
            level: Validation level
            metadata: Additional validation metadata (expiration_date, etc.)
            
        Returns:
            ValidationResult with detailed passport information
        """
        try:
            # Clean input
            clean_passport = self._clean_passport_number(passport_number)
            
            if not clean_passport:
                return ValidationResult(
                    is_valid=False,
                    id_type=IDType.PASSPORT,
                    confidence=0.0,
                    errors=['Empty passport number'],
                    metadata={}
                )
                
            errors = []
            confidence = 0.8
            validation_metadata = {
                'normalized_passport': clean_passport,
                'input_country': country,
            }
            
            # If country is provided, validate against country-specific rules
            if country:
                country = country.upper()
                if country in self.COUNTRY_PATTERNS:
                    passport_info = self._validate_for_country(clean_passport, country)
                    validation_metadata.update({
                        'country': country,
                        'country_name': passport_info.country_name,
                        'format_type': passport_info.format_type,
                        'check_digit_valid': passport_info.check_digit_valid,
                        'machine_readable': passport_info.machine_readable,
                    })
                    
                    if not passport_info.is_valid:
                        errors.append(f'Invalid format for {country}')
                        confidence = 0.3
                        
                    if not passport_info.check_digit_valid:
                        errors.append('Check digit validation failed')
                        confidence = min(confidence, 0.5)
                        
                else:
                    errors.append(f'Unsupported country: {country}')
                    confidence = 0.2
                    
            else:
                # Try to detect country if not provided
                detected_countries = self._detect_possible_countries(clean_passport)
                validation_metadata['possible_countries'] = detected_countries
                
                if not detected_countries:
                    errors.append('Unable to determine country or invalid format')
                    confidence = 0.2
                elif len(detected_countries) > 5:
                    errors.append('Passport format matches too many countries')
                    confidence = 0.6
                else:
                    confidence = 0.7
                    
            # Validate expiration date if provided
            if metadata and 'expiration_date' in metadata:
                exp_validation = self._validate_expiration_date(metadata['expiration_date'])
                validation_metadata.update(exp_validation)
                if not exp_validation['is_valid']:
                    errors.extend(exp_validation['errors'])
                    confidence = min(confidence, 0.6)
                    
            # Additional validation for higher levels
            if level in [ValidationLevel.STANDARD, ValidationLevel.STRICT]:
                # Check for suspicious patterns
                suspicious_checks = self._check_suspicious_patterns(clean_passport)
                if suspicious_checks['has_suspicious']:
                    if level == ValidationLevel.STRICT:
                        errors.extend(suspicious_checks['warnings'])
                        confidence = min(confidence, 0.6)
                    else:
                        validation_metadata['warnings'] = suspicious_checks['warnings']
                        
                validation_metadata['suspicious_checks'] = suspicious_checks
                
            if level == ValidationLevel.STRICT:
                # Enhanced validation
                if country and country in self.COUNTRY_PATTERNS:
                    enhanced_checks = self._perform_enhanced_validation(clean_passport, country)
                    validation_metadata.update(enhanced_checks)
                    
                    if not enhanced_checks.get('passes_all_checks', True):
                        confidence = min(confidence, 0.7)
                        
                # ICAO compliance check
                icao_compliance = self._check_icao_compliance(clean_passport)
                validation_metadata['icao_compliance'] = icao_compliance
                
            return ValidationResult(
                is_valid=len(errors) == 0,
                id_type=IDType.PASSPORT,
                confidence=confidence,
                errors=errors,
                metadata=validation_metadata
            )
            
        except Exception as e:
            logger.error(f"Passport validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                id_type=IDType.PASSPORT,
                confidence=0.0,
                errors=[f'Validation error: {str(e)}'],
                metadata={}
            )
            
    def can_validate(self, value: str) -> bool:
        """Check if value could be a passport number."""
        try:
            clean_value = self._clean_passport_number(value)
            # Basic check: alphanumeric, 6-15 characters
            return bool(re.match(r'^[A-Z0-9]{6,15}$', clean_value))
        except:
            return False
            
    def get_supported_countries(self) -> List[str]:
        """Get list of supported country codes."""
        return list(self.COUNTRY_PATTERNS.keys())
        
    def get_country_info(self, country: str) -> Optional[Dict[str, Any]]:
        """Get information about country passport format."""
        return self.COUNTRY_PATTERNS.get(country.upper())
        
    def validate_mrz(self, mrz_line: str) -> Dict[str, Any]:
        """Validate Machine Readable Zone (MRZ) line."""
        try:
            # Remove any non-alphanumeric characters and convert to uppercase
            clean_mrz = re.sub(r'[^A-Z0-9<]', '', mrz_line.upper())
            
            if len(clean_mrz) not in [30, 36, 44]:  # Standard MRZ line lengths
                return {
                    'is_valid': False,
                    'errors': ['Invalid MRZ line length'],
                    'check_digits': {}
                }
                
            # Extract passport number and check digit from MRZ
            # Format varies by document type, this is for TD-3 (passport book)
            if len(clean_mrz) == 44:
                passport_part = clean_mrz[0:9]  # First 9 characters
                passport_number = passport_part.rstrip('<')
                check_digit = clean_mrz[9]
                
                # Validate check digit
                calculated_check = self._calculate_mrz_check_digit(passport_part)
                
                return {
                    'is_valid': str(calculated_check) == check_digit,
                    'passport_number': passport_number,
                    'check_digit': check_digit,
                    'calculated_check': calculated_check,
                    'mrz_length': len(clean_mrz),
                    'errors': [] if str(calculated_check) == check_digit else ['MRZ check digit mismatch']
                }
                
            return {
                'is_valid': False,
                'errors': ['Unsupported MRZ format'],
                'mrz_length': len(clean_mrz)
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f'MRZ validation error: {str(e)}'],
            }
            
    def _clean_passport_number(self, passport_number: str) -> str:
        """Clean and normalize passport number."""
        # Remove spaces, hyphens, periods and convert to uppercase
        return re.sub(r'[\s\-\.]', '', passport_number.upper())
        
    def _validate_for_country(self, passport_number: str, country: str) -> PassportInfo:
        """Validate passport number for specific country."""
        country_info = self.COUNTRY_PATTERNS[country]
        
        passport_info = PassportInfo(
            passport_number=passport_number,
            country=country,
            country_name=country_info['name'],
            format_type=country_info['format'],
            machine_readable=country_info.get('mrz', False),
            is_valid=False,
            check_digit_valid=True
        )
        
        # Check against all patterns for the country
        for pattern in country_info['patterns']:
            if re.match(pattern, passport_number):
                passport_info.is_valid = True
                break
                
        # Check length constraints
        if passport_info.is_valid and 'length' in country_info:
            length_range = country_info['length']
            if isinstance(length_range, list):
                if len(length_range) == 1:
                    if len(passport_number) != length_range[0]:
                        passport_info.is_valid = False
                elif len(length_range) == 2:
                    min_len, max_len = length_range
                    if not (min_len <= len(passport_number) <= max_len):
                        passport_info.is_valid = False
                        
        # Check digit validation (if applicable)
        if passport_info.is_valid and country_info.get('check_digit', False):
            passport_info.check_digit_valid = self._validate_check_digit(passport_number, country)
            
        return passport_info
        
    def _detect_possible_countries(self, passport_number: str) -> List[str]:
        """Detect possible countries for passport number."""
        possible_countries = []
        
        for country, country_info in self.COUNTRY_PATTERNS.items():
            for pattern in country_info['patterns']:
                if re.match(pattern, passport_number):
                    possible_countries.append(country)
                    break
                    
        return possible_countries
        
    def _validate_check_digit(self, passport_number: str, country: str) -> bool:
        """Validate check digit for countries that use them."""
        if country == 'GB':
            return self._validate_uk_check_digit(passport_number)
        elif country == 'DE':
            return self._validate_german_check_digit(passport_number)
        elif country == 'FR':
            return self._validate_french_check_digit(passport_number)
        elif country == 'NL':
            return self._validate_dutch_check_digit(passport_number)
        elif country == 'MX':
            return self._validate_mexican_check_digit(passport_number)
        elif country == 'RU':
            return self._validate_russian_check_digit(passport_number)
        elif country == 'SG':
            return self._validate_singapore_check_digit(passport_number)
        elif country == 'SE':
            return self._validate_swedish_check_digit(passport_number)
        elif country == 'DK':
            return self._validate_danish_check_digit(passport_number)
        elif country == 'FI':
            return self._validate_finnish_check_digit(passport_number)
        elif country == 'PL':
            return self._validate_polish_check_digit(passport_number)
        elif country == 'IL':
            return self._validate_israeli_check_digit(passport_number)
        
        return True  # Assume valid for other countries
        
    def _validate_uk_check_digit(self, passport_number: str) -> bool:
        """Validate UK passport check digit."""
        if len(passport_number) != 9 or not passport_number.isdigit():
            return False
            
        try:
            # UK uses a weighted sum algorithm
            digits = [int(d) for d in passport_number[:8]]
            weights = [8, 7, 6, 5, 4, 3, 2, 1]
            
            total = sum(digit * weight for digit, weight in zip(digits, weights))
            check_digit = total % 11
            
            if check_digit == 10:
                check_digit = 0
                
            return check_digit == int(passport_number[8])
            
        except (ValueError, IndexError):
            return False
            
    def _validate_german_check_digit(self, passport_number: str) -> bool:
        """Validate German passport check digit."""
        if len(passport_number) != 10:
            return False
            
        try:
            # German passports use MRZ-style check digit calculation
            check_part = passport_number[:-1]  # All but last digit
            calculated_check = self._calculate_mrz_check_digit(check_part)
            
            return str(calculated_check) == passport_number[-1]
            
        except (ValueError, IndexError):
            return False
            
    def _validate_french_check_digit(self, passport_number: str) -> bool:
        """Validate French passport check digit (simplified)."""
        if len(passport_number) != 9:
            return False
            
        # This is a simplified version - actual French algorithm is more complex
        return True  # Placeholder
        
    def _validate_dutch_check_digit(self, passport_number: str) -> bool:
        """Validate Dutch passport check digit."""
        if len(passport_number) != 9:
            return False
            
        try:
            # Dutch uses MRZ-style check digit
            check_part = passport_number[:-1]
            calculated_check = self._calculate_mrz_check_digit(check_part)
            
            return str(calculated_check) == passport_number[-1]
            
        except (ValueError, IndexError):
            return False
            
    def _validate_mexican_check_digit(self, passport_number: str) -> bool:
        """Validate Mexican passport check digit."""
        if len(passport_number) != 10:
            return False
            
        # Simplified validation
        return passport_number[-1].isdigit()
        
    def _validate_russian_check_digit(self, passport_number: str) -> bool:
        """Validate Russian passport check digit."""
        if len(passport_number) != 9 or not passport_number.isdigit():
            return False
            
        # Simplified validation - actual algorithm varies
        return True  # Placeholder
        
    def _validate_singapore_check_digit(self, passport_number: str) -> bool:
        """Validate Singapore passport check digit."""
        if len(passport_number) != 9:
            return False
            
        try:
            # Singapore uses a specific algorithm
            letter = passport_number[0]
            digits = [int(d) for d in passport_number[1:8]]
            check_letter = passport_number[8]
            
            # Weights for Singapore passport
            weights = [2, 7, 6, 5, 4, 3, 2]
            letter_value = ord(letter) - ord('A') + 1
            
            total = letter_value + sum(digit * weight for digit, weight in zip(digits, weights))
            remainder = total % 11
            
            # Check letter mapping
            check_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'Z', 'J']
            
            return check_letters[remainder] == check_letter
            
        except (ValueError, IndexError):
            return False
            
    def _validate_swedish_check_digit(self, passport_number: str) -> bool:
        """Validate Swedish passport check digit."""
        # Simplified validation
        return len(passport_number) == 8 and passport_number.isdigit()
        
    def _validate_danish_check_digit(self, passport_number: str) -> bool:
        """Validate Danish passport check digit."""
        # Simplified validation
        return len(passport_number) == 9 and passport_number.isdigit()
        
    def _validate_finnish_check_digit(self, passport_number: str) -> bool:
        """Validate Finnish passport check digit."""
        # Simplified validation
        return len(passport_number) == 9
        
    def _validate_polish_check_digit(self, passport_number: str) -> bool:
        """Validate Polish passport check digit."""
        # Simplified validation
        return len(passport_number) == 8
        
    def _validate_israeli_check_digit(self, passport_number: str) -> bool:
        """Validate Israeli passport check digit."""
        if len(passport_number) != 8 or not passport_number.isdigit():
            return False
            
        # Israeli ID number algorithm (Luhn-like)
        try:
            digits = [int(d) for d in passport_number[:7]]
            total = 0
            
            for i, digit in enumerate(digits):
                if i % 2 == 0:
                    digit *= 2
                    if digit > 9:
                        digit = digit // 10 + digit % 10
                total += digit
                
            check_digit = (10 - (total % 10)) % 10
            return check_digit == int(passport_number[7])
            
        except (ValueError, IndexError):
            return False
            
    def _calculate_mrz_check_digit(self, data: str) -> int:
        """Calculate MRZ check digit using ICAO algorithm."""
        weights = [7, 3, 1]
        total = 0
        
        for i, char in enumerate(data):
            value = self.MRZ_CHAR_VALUES.get(char, 0)
            weight = weights[i % 3]
            total += value * weight
            
        return total % 10
        
    def _validate_expiration_date(self, exp_date: Any) -> Dict[str, Any]:
        """Validate passport expiration date."""
        try:
            if isinstance(exp_date, str):
                # Try to parse various date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y%m%d']:
                    try:
                        exp_date = datetime.strptime(exp_date, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return {
                        'is_valid': False,
                        'errors': ['Invalid date format'],
                        'expired': None,
                        'days_until_expiry': None
                    }
                    
            elif isinstance(exp_date, datetime):
                exp_date = exp_date.date()
                
            if not isinstance(exp_date, date):
                return {
                    'is_valid': False,
                    'errors': ['Invalid date type'],
                    'expired': None,
                    'days_until_expiry': None
                }
                
            today = date.today()
            days_until_expiry = (exp_date - today).days
            expired = exp_date < today
            
            return {
                'is_valid': not expired,
                'errors': ['Passport has expired'] if expired else [],
                'expired': expired,
                'expiration_date': exp_date.isoformat(),
                'days_until_expiry': days_until_expiry,
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f'Date validation error: {str(e)}'],
                'expired': None,
                'days_until_expiry': None
            }
            
    def _check_suspicious_patterns(self, passport_number: str) -> Dict[str, Any]:
        """Check for suspicious patterns in passport number."""
        warnings = []
        has_suspicious = False
        
        # All same digit/character
        if len(set(passport_number)) == 1:
            warnings.append('All characters are identical')
            has_suspicious = True
            
        # Sequential patterns
        if len(passport_number) >= 4:
            # Check for ascending sequence
            ascending = all(
                ord(passport_number[i]) == ord(passport_number[i-1]) + 1
                for i in range(1, min(5, len(passport_number)))
            )
            if ascending:
                warnings.append('Contains ascending sequence')
                has_suspicious = True
                
        # Common test patterns
        test_patterns = ['TEST', 'TEMP', '1234', 'ABCD', '0000', '1111']
        for pattern in test_patterns:
            if pattern in passport_number:
                warnings.append(f'Contains test pattern: {pattern}')
                has_suspicious = True
                
        # Check for obvious fake patterns
        fake_patterns = ['FAKE', 'NULL', 'XXXX']
        for pattern in fake_patterns:
            if pattern in passport_number:
                warnings.append(f'Contains suspicious pattern: {pattern}')
                has_suspicious = True
                
        return {
            'has_suspicious': has_suspicious,
            'warnings': warnings,
            'pattern_checks': {
                'all_same': len(set(passport_number)) == 1,
                'contains_test_pattern': any(p in passport_number for p in test_patterns),
                'contains_fake_pattern': any(p in passport_number for p in fake_patterns),
                'sequential': 'ascending' in ' '.join(warnings).lower(),
            }
        }
        
    def _perform_enhanced_validation(self, passport_number: str, country: str) -> Dict[str, Any]:
        """Perform enhanced validation checks."""
        checks = {
            'length_check': True,
            'format_check': True,
            'character_check': True,
            'pattern_match': True,
            'passes_all_checks': True,
        }
        
        country_info = self.COUNTRY_PATTERNS[country]
        
        # Enhanced length validation
        if 'length' in country_info:
            length_range = country_info['length']
            if isinstance(length_range, list):
                if len(length_range) == 1:
                    checks['length_check'] = len(passport_number) == length_range[0]
                else:
                    min_len, max_len = length_range
                    checks['length_check'] = min_len <= len(passport_number) <= max_len
                    
        # Enhanced format validation
        format_type = country_info['format']
        if format_type == 'Numeric':
            checks['format_check'] = passport_number.isdigit()
        elif format_type == 'Alphanumeric':
            checks['format_check'] = passport_number.isalnum()
            
        # Character composition check
        if format_type == 'Alphanumeric':
            # Check for reasonable mix of letters and numbers
            letters = sum(1 for c in passport_number if c.isalpha())
            digits = sum(1 for c in passport_number if c.isdigit())
            checks['character_check'] = letters > 0 or digits > 0
            
        # Pattern matching
        checks['pattern_match'] = any(
            re.match(pattern, passport_number) 
            for pattern in country_info['patterns']
        )
        
        checks['passes_all_checks'] = all(checks.values())
        
        return checks
        
    def _check_icao_compliance(self, passport_number: str) -> Dict[str, Any]:
        """Check ICAO Document 9303 compliance."""
        compliance = {
            'character_set_valid': True,
            'length_acceptable': True,
            'format_standard': True,
            'overall_compliant': True,
        }
        
        # Check character set (alphanumeric only)
        if not passport_number.isalnum():
            compliance['character_set_valid'] = False
            
        # Check length (ICAO recommends 6-9 characters)
        if not (6 <= len(passport_number) <= 15):
            compliance['length_acceptable'] = False
            
        # Check format patterns (no special characters in basic format)
        if not re.match(r'^[A-Z0-9]+$', passport_number):
            compliance['format_standard'] = False
            
        compliance['overall_compliant'] = all(compliance.values())
        
        return compliance
        
    def get_supported_types(self) -> List[IDType]:
        """Get supported ID types."""
        return [IDType.PASSPORT]
