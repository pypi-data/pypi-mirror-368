"""
PyIDVerify Driver's License Validator

Validates US driver's license numbers with state-specific patterns and rules.
Supports all 50 US states plus DC with comprehensive format validation.

Author: PyIDVerify Team
License: MIT
"""

import re
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from datetime import datetime
from ..core.base_validator import BaseValidator
from ..core.types import IDType, ValidationResult, ValidationLevel
from ..core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class DriversLicenseInfo:
    """Information about a driver's license."""
    license_number: str
    state: str
    is_valid: bool = True
    state_name: Optional[str] = None
    format_type: Optional[str] = None
    check_digit_valid: bool = True


class DriversLicenseValidator(BaseValidator):
    """
    US Driver's License validator for all 50 states plus DC.
    
    Features:
    - State-specific format validation
    - Check digit validation where applicable
    - Format normalization
    - Expiration date validation (when provided)
    - Comprehensive state pattern library
    - Support for legacy and current formats
    """
    
    SUPPORTED_TYPE = IDType.DRIVERS_LICENSE
    
    # State-specific driver's license patterns and rules
    STATE_PATTERNS = {
        'AL': {  # Alabama
            'name': 'Alabama',
            'patterns': [r'^\d{7,8}$'],
            'format': 'Numeric',
            'length': [7, 8],
            'check_digit': False,
            'notes': '7-8 digits'
        },
        'AK': {  # Alaska
            'name': 'Alaska',
            'patterns': [r'^\d{1,7}$'],
            'format': 'Numeric',
            'length': [1, 7],
            'check_digit': False,
            'notes': '1-7 digits'
        },
        'AZ': {  # Arizona
            'name': 'Arizona',
            'patterns': [
                r'^[A-Z]{1}\d{8}$',  # 1 letter + 8 digits
                r'^\d{9}$',          # 9 digits (alternative format)
                r'^[A-Z]{2}\d{2,5}$' # 2 letters + 2-5 digits
            ],
            'format': 'Mixed',
            'length': [9, 10],
            'check_digit': False,
            'notes': 'Letter+8digits or 9digits or 2letters+2-5digits'
        },
        'AR': {  # Arkansas
            'name': 'Arkansas',
            'patterns': [r'^\d{4,9}$'],
            'format': 'Numeric',
            'length': [4, 9],
            'check_digit': False,
            'notes': '4-9 digits'
        },
        'CA': {  # California
            'name': 'California',
            'patterns': [r'^[A-Z]{1}\d{7}$'],
            'format': 'Alphanumeric',
            'length': [8],
            'check_digit': True,
            'notes': '1 letter followed by 7 digits'
        },
        'CO': {  # Colorado
            'name': 'Colorado',
            'patterns': [
                r'^\d{9}$',           # 9 digits
                r'^[A-Z]{1}\d{3,6}$', # 1 letter + 3-6 digits
                r'^[A-Z]{2}\d{2,5}$'  # 2 letters + 2-5 digits
            ],
            'format': 'Mixed',
            'length': [4, 9],
            'check_digit': False,
            'notes': '9digits or letter+3-6digits or 2letters+2-5digits'
        },
        'CT': {  # Connecticut
            'name': 'Connecticut',
            'patterns': [r'^\d{9}$'],
            'format': 'Numeric',
            'length': [9],
            'check_digit': False,
            'notes': '9 digits'
        },
        'DC': {  # District of Columbia
            'name': 'District of Columbia',
            'patterns': [
                r'^\d{7}$',          # 7 digits
                r'^\d{9}$'           # 9 digits (newer format)
            ],
            'format': 'Numeric',
            'length': [7, 9],
            'check_digit': False,
            'notes': '7 or 9 digits'
        },
        'DE': {  # Delaware
            'name': 'Delaware',
            'patterns': [r'^\d{1,7}$'],
            'format': 'Numeric',
            'length': [1, 7],
            'check_digit': False,
            'notes': '1-7 digits'
        },
        'FL': {  # Florida
            'name': 'Florida',
            'patterns': [
                r'^[A-Z]{1}\d{12}$',  # 1 letter + 12 digits
                r'^\d{13}$'           # 13 digits
            ],
            'format': 'Mixed',
            'length': [13],
            'check_digit': False,
            'notes': 'Letter+12digits or 13digits'
        },
        'GA': {  # Georgia
            'name': 'Georgia',
            'patterns': [r'^\d{7,9}$'],
            'format': 'Numeric',
            'length': [7, 9],
            'check_digit': False,
            'notes': '7-9 digits'
        },
        'HI': {  # Hawaii
            'name': 'Hawaii',
            'patterns': [
                r'^[A-Z]{1}\d{8}$',  # 1 letter + 8 digits
                r'^\d{9}$'           # 9 digits
            ],
            'format': 'Mixed',
            'length': [9],
            'check_digit': False,
            'notes': 'Letter+8digits or 9digits'
        },
        'ID': {  # Idaho
            'name': 'Idaho',
            'patterns': [
                r'^[A-Z]{2}\d{6}[A-Z]{1}$',  # 2 letters + 6 digits + 1 letter
                r'^\d{9}$'                    # 9 digits
            ],
            'format': 'Mixed',
            'length': [9],
            'check_digit': False,
            'notes': '2letters+6digits+1letter or 9digits'
        },
        'IL': {  # Illinois
            'name': 'Illinois',
            'patterns': [
                r'^[A-Z]{1}\d{11,12}$',  # 1 letter + 11-12 digits
                r'^\d{12}$'               # 12 digits
            ],
            'format': 'Mixed',
            'length': [12, 13],
            'check_digit': False,
            'notes': 'Letter+11-12digits or 12digits'
        },
        'IN': {  # Indiana
            'name': 'Indiana',
            'patterns': [
                r'^\d{10}$',          # 10 digits
                r'^\d{4}-\d{2}-\d{4}$' # ####-##-#### format
            ],
            'format': 'Numeric',
            'length': [10],
            'check_digit': False,
            'notes': '10 digits (####-##-#### format)'
        },
        'IA': {  # Iowa
            'name': 'Iowa',
            'patterns': [
                r'^\d{9}$',           # 9 digits
                r'^\d{3}[A-Z]{2}\d{4}$' # 3digits+2letters+4digits
            ],
            'format': 'Mixed',
            'length': [9],
            'check_digit': False,
            'notes': '9digits or 3digits+2letters+4digits'
        },
        'KS': {  # Kansas
            'name': 'Kansas',
            'patterns': [
                r'^[A-Z]{1}\d{8}$',   # 1 letter + 8 digits
                r'^\d{9}$'            # 9 digits
            ],
            'format': 'Mixed',
            'length': [9],
            'check_digit': False,
            'notes': 'Letter+8digits or 9digits'
        },
        'KY': {  # Kentucky
            'name': 'Kentucky',
            'patterns': [
                r'^[A-Z]{1}\d{8,9}$', # 1 letter + 8-9 digits
                r'^\d{9}$'            # 9 digits
            ],
            'format': 'Mixed',
            'length': [9, 10],
            'check_digit': False,
            'notes': 'Letter+8-9digits or 9digits'
        },
        'LA': {  # Louisiana
            'name': 'Louisiana',
            'patterns': [r'^\d{1,9}$'],
            'format': 'Numeric',
            'length': [1, 9],
            'check_digit': False,
            'notes': '1-9 digits'
        },
        'ME': {  # Maine
            'name': 'Maine',
            'patterns': [
                r'^\d{7,8}$',         # 7-8 digits
                r'^\d{7}[A-Z]{1}$'    # 7 digits + 1 letter
            ],
            'format': 'Mixed',
            'length': [7, 8],
            'check_digit': False,
            'notes': '7-8digits or 7digits+1letter'
        },
        'MD': {  # Maryland
            'name': 'Maryland',
            'patterns': [r'^[A-Z]{1}\d{12}$'],
            'format': 'Alphanumeric',
            'length': [13],
            'check_digit': False,
            'notes': '1 letter + 12 digits'
        },
        'MA': {  # Massachusetts
            'name': 'Massachusetts',
            'patterns': [
                r'^[A-Z]{1}\d{8}$',   # 1 letter + 8 digits
                r'^\d{9}$'            # 9 digits
            ],
            'format': 'Mixed',
            'length': [9],
            'check_digit': False,
            'notes': 'Letter+8digits or 9digits'
        },
        'MI': {  # Michigan
            'name': 'Michigan',
            'patterns': [
                r'^[A-Z]{1}\d{10}$',  # 1 letter + 10 digits
                r'^[A-Z]{1}\d{12}$'   # 1 letter + 12 digits
            ],
            'format': 'Alphanumeric',
            'length': [11, 13],
            'check_digit': False,
            'notes': 'Letter+10digits or letter+12digits'
        },
        'MN': {  # Minnesota
            'name': 'Minnesota',
            'patterns': [r'^[A-Z]{1}\d{12}$'],
            'format': 'Alphanumeric',
            'length': [13],
            'check_digit': False,
            'notes': '1 letter + 12 digits'
        },
        'MS': {  # Mississippi
            'name': 'Mississippi',
            'patterns': [r'^\d{9}$'],
            'format': 'Numeric',
            'length': [9],
            'check_digit': False,
            'notes': '9 digits'
        },
        'MO': {  # Missouri
            'name': 'Missouri',
            'patterns': [
                r'^[A-Z]{1}\d{5,9}$', # 1 letter + 5-9 digits
                r'^\d{8,9}$',         # 8-9 digits
                r'^\d{3}[A-Z]{1}\d{6}$' # 3digits+1letter+6digits
            ],
            'format': 'Mixed',
            'length': [6, 10],
            'check_digit': False,
            'notes': 'Various formats including letter+5-9digits'
        },
        'MT': {  # Montana
            'name': 'Montana',
            'patterns': [
                r'^\d{13,14}$',       # 13-14 digits
                r'^\d{9}$'            # 9 digits (alternative)
            ],
            'format': 'Numeric',
            'length': [9, 14],
            'check_digit': False,
            'notes': '13-14digits or 9digits'
        },
        'NE': {  # Nebraska
            'name': 'Nebraska',
            'patterns': [
                r'^[A-Z]{1}\d{6,8}$', # 1 letter + 6-8 digits
                r'^\d{8}$'            # 8 digits
            ],
            'format': 'Mixed',
            'length': [7, 9],
            'check_digit': False,
            'notes': 'Letter+6-8digits or 8digits'
        },
        'NV': {  # Nevada
            'name': 'Nevada',
            'patterns': [
                r'^\d{10}$',          # 10 digits
                r'^\d{12}$',          # 12 digits
                r'^X\d{8}$'           # X + 8 digits
            ],
            'format': 'Mixed',
            'length': [9, 12],
            'check_digit': False,
            'notes': '10digits, 12digits, or X+8digits'
        },
        'NH': {  # New Hampshire
            'name': 'New Hampshire',
            'patterns': [
                r'^\d{2}[A-Z]{3}\d{5}$', # ##ABC##### format
                r'^\d{10}$'               # 10 digits
            ],
            'format': 'Mixed',
            'length': [10],
            'check_digit': False,
            'notes': '##ABC##### or 10digits'
        },
        'NJ': {  # New Jersey
            'name': 'New Jersey',
            'patterns': [
                r'^[A-Z]{1}\d{14}$',  # 1 letter + 14 digits
                r'^\d{15}$'           # 15 digits
            ],
            'format': 'Mixed',
            'length': [15],
            'check_digit': False,
            'notes': 'Letter+14digits or 15digits'
        },
        'NM': {  # New Mexico
            'name': 'New Mexico',
            'patterns': [r'^\d{8,9}$'],
            'format': 'Numeric',
            'length': [8, 9],
            'check_digit': False,
            'notes': '8-9 digits'
        },
        'NY': {  # New York
            'name': 'New York',
            'patterns': [
                r'^\d{8,9}$',         # 8-9 digits
                r'^\d{16}$',          # 16 digits (enhanced)
                r'^\d{3}[A-Z]{3}\d{8}$' # Enhanced format
            ],
            'format': 'Mixed',
            'length': [8, 16],
            'check_digit': False,
            'notes': '8-9digits, 16digits, or enhanced format'
        },
        'NC': {  # North Carolina
            'name': 'North Carolina',
            'patterns': [
                r'^\d{1,12}$',        # 1-12 digits
                r'^\d{13}$'           # 13 digits
            ],
            'format': 'Numeric',
            'length': [1, 13],
            'check_digit': False,
            'notes': '1-12digits or 13digits'
        },
        'ND': {  # North Dakota
            'name': 'North Dakota',
            'patterns': [
                r'^[A-Z]{3}\d{6}$',   # 3 letters + 6 digits
                r'^\d{9}$'            # 9 digits
            ],
            'format': 'Mixed',
            'length': [9],
            'check_digit': False,
            'notes': '3letters+6digits or 9digits'
        },
        'OH': {  # Ohio
            'name': 'Ohio',
            'patterns': [
                r'^[A-Z]{1}\d{4,8}$', # 1 letter + 4-8 digits
                r'^\d{8}$'            # 8 digits
            ],
            'format': 'Mixed',
            'length': [5, 9],
            'check_digit': False,
            'notes': 'Letter+4-8digits or 8digits'
        },
        'OK': {  # Oklahoma
            'name': 'Oklahoma',
            'patterns': [
                r'^[A-Z]{1}\d{9}$',   # 1 letter + 9 digits
                r'^\d{10}$'           # 10 digits
            ],
            'format': 'Mixed',
            'length': [10],
            'check_digit': False,
            'notes': 'Letter+9digits or 10digits'
        },
        'OR': {  # Oregon
            'name': 'Oregon',
            'patterns': [r'^\d{1,9}$'],
            'format': 'Numeric',
            'length': [1, 9],
            'check_digit': False,
            'notes': '1-9 digits'
        },
        'PA': {  # Pennsylvania
            'name': 'Pennsylvania',
            'patterns': [r'^\d{8}$'],
            'format': 'Numeric',
            'length': [8],
            'check_digit': False,
            'notes': '8 digits'
        },
        'RI': {  # Rhode Island
            'name': 'Rhode Island',
            'patterns': [
                r'^[A-Z]{1}\d{6}$',   # 1 letter + 6 digits
                r'^\d{7}$'            # 7 digits
            ],
            'format': 'Mixed',
            'length': [7],
            'check_digit': False,
            'notes': 'Letter+6digits or 7digits'
        },
        'SC': {  # South Carolina
            'name': 'South Carolina',
            'patterns': [
                r'^\d{5,11}$',        # 5-11 digits
                r'^\d{2}[A-Z]{1}\d{8}$' # Enhanced format
            ],
            'format': 'Mixed',
            'length': [5, 11],
            'check_digit': False,
            'notes': '5-11digits or enhanced format'
        },
        'SD': {  # South Dakota
            'name': 'South Dakota',
            'patterns': [
                r'^\d{6,10}$',        # 6-10 digits
                r'^\d{12}$'           # 12 digits
            ],
            'format': 'Numeric',
            'length': [6, 12],
            'check_digit': False,
            'notes': '6-10digits or 12digits'
        },
        'TN': {  # Tennessee
            'name': 'Tennessee',
            'patterns': [r'^\d{7,9}$'],
            'format': 'Numeric',
            'length': [7, 9],
            'check_digit': False,
            'notes': '7-9 digits'
        },
        'TX': {  # Texas
            'name': 'Texas',
            'patterns': [r'^\d{7,8}$'],
            'format': 'Numeric',
            'length': [7, 8],
            'check_digit': False,
            'notes': '7-8 digits'
        },
        'UT': {  # Utah
            'name': 'Utah',
            'patterns': [r'^\d{4,10}$'],
            'format': 'Numeric',
            'length': [4, 10],
            'check_digit': False,
            'notes': '4-10 digits'
        },
        'VT': {  # Vermont
            'name': 'Vermont',
            'patterns': [
                r'^\d{8}$',           # 8 digits
                r'^\d{7}[A-Z]{1}$'    # 7 digits + 1 letter
            ],
            'format': 'Mixed',
            'length': [8],
            'check_digit': False,
            'notes': '8digits or 7digits+1letter'
        },
        'VA': {  # Virginia
            'name': 'Virginia',
            'patterns': [
                r'^[A-Z]{1}\d{8}$',   # 1 letter + 8 digits
                r'^\d{9}$'            # 9 digits
            ],
            'format': 'Mixed',
            'length': [9],
            'check_digit': False,
            'notes': 'Letter+8digits or 9digits'
        },
        'WA': {  # Washington
            'name': 'Washington',
            'patterns': [r'^[A-Z]{1,7}[A-Z0-9\*]{5}[A-Z]{2}$'],
            'format': 'Alphanumeric',
            'length': [12],
            'check_digit': False,
            'notes': 'Complex alphanumeric format'
        },
        'WV': {  # West Virginia
            'name': 'West Virginia',
            'patterns': [
                r'^[A-Z]{1}\d{6}$',   # 1 letter + 6 digits
                r'^\d{7}$'            # 7 digits
            ],
            'format': 'Mixed',
            'length': [7],
            'check_digit': False,
            'notes': 'Letter+6digits or 7digits'
        },
        'WI': {  # Wisconsin
            'name': 'Wisconsin',
            'patterns': [
                r'^[A-Z]{1}\d{13}$',  # 1 letter + 13 digits
                r'^\d{14}$'           # 14 digits
            ],
            'format': 'Mixed',
            'length': [14],
            'check_digit': False,
            'notes': 'Letter+13digits or 14digits'
        },
        'WY': {  # Wyoming
            'name': 'Wyoming',
            'patterns': [r'^\d{9,10}$'],
            'format': 'Numeric',
            'length': [9, 10],
            'check_digit': False,
            'notes': '9-10 digits'
        }
    }
    
    def __init__(self, config=None):
        """Initialize driver's license validator."""
        super().__init__(config)
        logger.debug("DriversLicenseValidator initialized")
        
    def validate(self, 
                license_number: str, 
                state: Optional[str] = None,
                level: ValidationLevel = ValidationLevel.STANDARD,
                metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate driver's license number.
        
        Args:
            license_number: License number to validate
            state: US state code (if known)
            level: Validation level
            metadata: Additional validation metadata
            
        Returns:
            ValidationResult with detailed license information
        """
        try:
            # Clean input
            clean_license = self._clean_license_number(license_number)
            
            if not clean_license:
                return ValidationResult(
                    is_valid=False,
                    id_type=IDType.DRIVERS_LICENSE,
                    confidence=0.0,
                    errors=['Empty license number'],
                    metadata={}
                )
                
            errors = []
            confidence = 0.8
            validation_metadata = {
                'normalized_license': clean_license,
                'input_state': state,
            }
            
            # If state is provided, validate against state-specific rules
            if state:
                state = state.upper()
                if state in self.STATE_PATTERNS:
                    license_info = self._validate_for_state(clean_license, state)
                    validation_metadata.update({
                        'state': state,
                        'state_name': license_info.state_name,
                        'format_type': license_info.format_type,
                        'check_digit_valid': license_info.check_digit_valid,
                    })
                    
                    if not license_info.is_valid:
                        errors.append(f'Invalid format for {state}')
                        confidence = 0.3
                        
                    if not license_info.check_digit_valid:
                        errors.append('Check digit validation failed')
                        confidence = min(confidence, 0.5)
                        
                else:
                    errors.append(f'Unsupported state: {state}')
                    confidence = 0.2
                    
            else:
                # Try to detect state if not provided
                detected_states = self._detect_possible_states(clean_license)
                validation_metadata['possible_states'] = detected_states
                
                if not detected_states:
                    errors.append('Unable to determine state or invalid format')
                    confidence = 0.2
                elif len(detected_states) > 3:
                    errors.append('License format matches too many states')
                    confidence = 0.6
                else:
                    confidence = 0.7
                    
            # Additional validation for higher levels
            if level in [ValidationLevel.STANDARD, ValidationLevel.STRICT]:
                # Check for suspicious patterns
                suspicious_checks = self._check_suspicious_patterns(clean_license)
                if suspicious_checks['has_suspicious']:
                    if level == ValidationLevel.STRICT:
                        errors.extend(suspicious_checks['warnings'])
                        confidence = min(confidence, 0.6)
                    else:
                        validation_metadata['warnings'] = suspicious_checks['warnings']
                        
                validation_metadata['suspicious_checks'] = suspicious_checks
                
            if level == ValidationLevel.STRICT:
                # Enhanced validation
                if state and state in self.STATE_PATTERNS:
                    enhanced_checks = self._perform_enhanced_validation(clean_license, state)
                    validation_metadata.update(enhanced_checks)
                    
                    if not enhanced_checks.get('passes_all_checks', True):
                        confidence = min(confidence, 0.7)
                        
            return ValidationResult(
                is_valid=len(errors) == 0,
                id_type=IDType.DRIVERS_LICENSE,
                confidence=confidence,
                errors=errors,
                metadata=validation_metadata
            )
            
        except Exception as e:
            logger.error(f"Driver's license validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                id_type=IDType.DRIVERS_LICENSE,
                confidence=0.0,
                errors=[f'Validation error: {str(e)}'],
                metadata={}
            )
            
    def can_validate(self, value: str) -> bool:
        """Check if value could be a driver's license."""
        try:
            clean_value = self._clean_license_number(value)
            # Basic check: alphanumeric, 4-16 characters
            return bool(re.match(r'^[A-Z0-9]{4,16}$', clean_value))
        except:
            return False
            
    def get_supported_states(self) -> List[str]:
        """Get list of supported state codes."""
        return list(self.STATE_PATTERNS.keys())
        
    def get_state_info(self, state: str) -> Optional[Dict[str, Any]]:
        """Get information about state license format."""
        return self.STATE_PATTERNS.get(state.upper())
        
    def _clean_license_number(self, license_number: str) -> str:
        """Clean and normalize license number."""
        # Remove spaces, hyphens, periods and convert to uppercase
        return re.sub(r'[\s\-\.]', '', license_number.upper())
        
    def _validate_for_state(self, license_number: str, state: str) -> DriversLicenseInfo:
        """Validate license number for specific state."""
        state_info = self.STATE_PATTERNS[state]
        
        license_info = DriversLicenseInfo(
            license_number=license_number,
            state=state,
            state_name=state_info['name'],
            format_type=state_info['format'],
            is_valid=False,
            check_digit_valid=True
        )
        
        # Check against all patterns for the state
        for pattern in state_info['patterns']:
            if re.match(pattern, license_number):
                license_info.is_valid = True
                break
                
        # Check length constraints
        if license_info.is_valid and 'length' in state_info:
            length_range = state_info['length']
            if isinstance(length_range, list) and len(length_range) == 2:
                min_len, max_len = length_range
                if not (min_len <= len(license_number) <= max_len):
                    license_info.is_valid = False
                    
        # Check digit validation (if applicable)
        if license_info.is_valid and state_info.get('check_digit', False):
            license_info.check_digit_valid = self._validate_check_digit(license_number, state)
            
        return license_info
        
    def _detect_possible_states(self, license_number: str) -> List[str]:
        """Detect possible states for license number."""
        possible_states = []
        
        for state, state_info in self.STATE_PATTERNS.items():
            for pattern in state_info['patterns']:
                if re.match(pattern, license_number):
                    possible_states.append(state)
                    break
                    
        return possible_states
        
    def _validate_check_digit(self, license_number: str, state: str) -> bool:
        """Validate check digit for states that use them."""
        # Currently only California (CA) has documented check digit algorithm
        if state == 'CA':
            return self._validate_california_check_digit(license_number)
        return True  # Assume valid for other states
        
    def _validate_california_check_digit(self, license_number: str) -> bool:
        """Validate California driver's license check digit."""
        if len(license_number) != 8 or not license_number[0].isalpha():
            return False
            
        try:
            # California uses a specific algorithm for check digit
            # This is a simplified version - actual algorithm is more complex
            letter = license_number[0]
            digits = license_number[1:]
            
            # Convert letter to number (A=1, B=2, etc.)
            letter_value = ord(letter) - ord('A') + 1
            
            # Simple check digit calculation (placeholder)
            total = letter_value
            for i, digit in enumerate(digits[:-1]):
                total += int(digit) * (i + 1)
                
            check_digit = total % 10
            return check_digit == int(digits[-1])
            
        except (ValueError, IndexError):
            return False
            
    def _check_suspicious_patterns(self, license_number: str) -> Dict[str, Any]:
        """Check for suspicious patterns in license number."""
        warnings = []
        has_suspicious = False
        
        # All same digit/character
        if len(set(license_number)) == 1:
            warnings.append('All characters are identical')
            has_suspicious = True
            
        # Sequential patterns
        if len(license_number) >= 4:
            # Check for ascending sequence
            ascending = all(
                ord(license_number[i]) == ord(license_number[i-1]) + 1
                for i in range(1, min(5, len(license_number)))
            )
            if ascending:
                warnings.append('Contains ascending sequence')
                has_suspicious = True
                
        # Common test patterns
        test_patterns = ['TEST', '1234', 'ABCD', '0000', '1111']
        for pattern in test_patterns:
            if pattern in license_number:
                warnings.append(f'Contains test pattern: {pattern}')
                has_suspicious = True
                
        return {
            'has_suspicious': has_suspicious,
            'warnings': warnings,
            'pattern_checks': {
                'all_same': len(set(license_number)) == 1,
                'contains_test_pattern': any(p in license_number for p in test_patterns),
                'sequential': 'ascending' in ' '.join(warnings).lower(),
            }
        }
        
    def _perform_enhanced_validation(self, license_number: str, state: str) -> Dict[str, Any]:
        """Perform enhanced validation checks."""
        checks = {
            'length_check': True,
            'format_check': True,
            'character_check': True,
            'passes_all_checks': True,
        }
        
        state_info = self.STATE_PATTERNS[state]
        
        # Enhanced length validation
        if 'length' in state_info:
            length_range = state_info['length']
            if isinstance(length_range, list):
                min_len, max_len = length_range
                checks['length_check'] = min_len <= len(license_number) <= max_len
                
        # Enhanced format validation
        format_type = state_info['format']
        if format_type == 'Numeric':
            checks['format_check'] = license_number.isdigit()
        elif format_type == 'Alphanumeric':
            checks['format_check'] = license_number.isalnum()
            
        # Character composition check
        if format_type == 'Numeric':
            checks['character_check'] = all(c.isdigit() for c in license_number)
        elif format_type == 'Alphanumeric':
            # Check for reasonable mix of letters and numbers
            letters = sum(1 for c in license_number if c.isalpha())
            digits = sum(1 for c in license_number if c.isdigit())
            checks['character_check'] = letters > 0 and digits > 0
            
        checks['passes_all_checks'] = all(checks.values())
        
        return checks
        
    def get_supported_types(self) -> List[IDType]:
        """Get supported ID types."""
        return [IDType.DRIVERS_LICENSE]
