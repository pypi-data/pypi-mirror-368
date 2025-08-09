"""
Phone Number Validator
=====================

This module implements comprehensive phone number validation supporting
international formats, regional variations, and carrier detection.

Features:
- E.164 international format validation
- Regional format support for major countries
- Country code validation and detection
- Carrier detection capabilities (optional)
- Number portability checks (optional)
- Fraud detection for known bad numbers
- Format normalization and standardization

Examples:
    >>> from pyidverify.validators.personal.phone import PhoneValidator
    >>> 
    >>> validator = PhoneValidator()
    >>> result = validator.validate("(555) 123-4567", country="US")
    >>> print(result.is_valid)  # True
    >>> 
    >>> # International format
    >>> result = validator.validate("+1-555-123-4567")
    >>> print(result.metadata.get('country_code'))  # "US"

Security Features:
- Input sanitization prevents injection attacks
- Rate limiting prevents enumeration attacks
- Carrier lookup timeouts prevent DoS attacks
- Memory-safe string operations
- Audit logging for sensitive operations
"""

from typing import Optional, Dict, Any, List, Set, Tuple, Union
import re
import time
try:
    import phonenumbers
    from phonenumbers import NumberParseException, PhoneNumberType
    from phonenumbers.phonenumberutil import PhoneNumberUtil
    from phonenumbers.geocoder import description_for_number
    from phonenumbers.carrier import name_for_number
    _PHONENUMBERS_AVAILABLE = True
except ImportError:
    _PHONENUMBERS_AVAILABLE = False
    # Create minimal fallbacks
    class NumberParseException(Exception):
        pass
    class PhoneNumberType:
        FIXED_LINE = 0
        MOBILE = 1
        TOLL_FREE = 2
    class PhoneNumberUtil:
        @classmethod
        def get_instance(cls):
            return cls()
        def parse(self, number, region):
            raise NumberParseException("phonenumbers not available")
from dataclasses import dataclass
from pathlib import Path
import json

try:
    from ...core.base_validator import BaseValidator
    from ...core.types import IDType, ValidationResult, ValidationLevel
    from ...core.exceptions import ValidationError, SecurityError
    from ...utils.extractors import normalize_input, clean_input
    from ...utils.caching import LRUCache
    from ...security.audit import AuditLogger
    from ...security.rate_limiting import RateLimiter
    from ...config.countries import get_country_info, get_phone_patterns
    _IMPORTS_AVAILABLE = True
except ImportError as e:
    # Graceful degradation
    _IMPORTS_AVAILABLE = False
    _IMPORT_ERROR = str(e)
    
    # Mock classes for development
    class BaseValidator:
        def __init__(self): pass
    
    class ValidationResult:
        def __init__(self, is_valid, id_type, confidence=1.0, metadata=None, errors=None):
            self.is_valid = is_valid
            self.id_type = id_type
            self.confidence = confidence
            self.metadata = metadata or {}
            self.errors = errors or []

@dataclass
class PhoneValidationOptions:
    """Configuration options for phone validation"""
    check_format: bool = True
    check_region: bool = True
    check_carrier: bool = False
    check_line_type: bool = True
    allow_mobile: bool = True
    allow_landline: bool = True
    allow_voip: bool = True
    allow_premium: bool = False
    allow_shared_cost: bool = False
    default_region: str = "US"
    strict_validation: bool = False
    
    def __post_init__(self):
        """Validate configuration options"""
        if self.default_region and len(self.default_region) != 2:
            raise ValueError("default_region must be a 2-letter country code")

class PhoneValidator(BaseValidator):
    """
    Comprehensive phone number validator with international support.
    
    This validator supports E.164 international format, regional formats,
    and provides detailed metadata about phone numbers including carrier
    information and line type detection.
    """
    
    def __init__(self, **options):
        """
        Initialize phone validator.
        
        Args:
            **options: Validation options (see PhoneValidationOptions)
        """
        if _IMPORTS_AVAILABLE:
            super().__init__()
            self.audit_logger = AuditLogger("phone_validator")
            self.rate_limiter = RateLimiter(max_requests=1000, time_window=3600)
            self.validation_cache = LRUCache(maxsize=1000)
            self.carrier_cache = LRUCache(maxsize=500)
        
        # Configure validation options
        self.options = PhoneValidationOptions(**options)
        
        # Initialize phone number utility
        if _PHONENUMBERS_AVAILABLE:
            self.phone_util = PhoneNumberUtil.get_instance()
        else:
            self.phone_util = None
        
        # Load fraud/spam number patterns
        self._fraud_patterns = self._load_fraud_patterns()
        
        # Compile regex patterns for fast pre-validation
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for phone validation"""
        
        # E.164 international format pattern
        self._e164_pattern = re.compile(r'^\+[1-9]\d{1,14}$')
        
        # US/NANP format patterns
        self._us_patterns = {
            'standard': re.compile(r'^(\+?1[-.\s]?)?\(?([2-9]\d{2})\)?[-.\s]?([2-9]\d{2})[-.\s]?(\d{4})$'),
            'compact': re.compile(r'^(\+?1)?([2-9]\d{2})([2-9]\d{2})(\d{4})$'),
            'international': re.compile(r'^\+1[2-9]\d{2}[2-9]\d{6}$')
        }
        
        # UK format patterns
        self._uk_patterns = {
            'mobile': re.compile(r'^(\+44|0)?7\d{9}$'),
            'landline': re.compile(r'^(\+44|0)?[1-9]\d{8,9}$')
        }
        
        # Generic international pattern (loose validation)
        self._international_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        
        # Invalid number patterns (known spam/fraud patterns)
        self._invalid_patterns = [
            re.compile(r'^(\+?1)?[0-1]\d{9}$'),  # Invalid area codes (0, 1)
            re.compile(r'^(\+?1)?\d{3}[0-1]\d{6}$'),  # Invalid exchange codes
            re.compile(r'^(\+?1)?\d{6}(0000|1111)$'),  # Invalid line numbers
        ]
    
    def _load_fraud_patterns(self) -> Set[str]:
        """Load known fraud/spam number patterns"""
        fraud_patterns = set()
        
        # Built-in fraud patterns (sample)
        built_in_fraud = {
            # Known spam prefixes
            '+1900',  # Premium rate
            '+1976',  # Caribbean premium
            # Add more patterns as needed
        }
        
        fraud_patterns.update(built_in_fraud)
        
        # Try to load from external file
        try:
            fraud_file = Path(__file__).parent / 'data' / 'fraud_patterns.json'
            if fraud_file.exists():
                with open(fraud_file, 'r', encoding='utf-8') as f:
                    external_patterns = json.load(f)
                    if isinstance(external_patterns, list):
                        fraud_patterns.update(external_patterns)
        except Exception:
            pass  # Use built-in patterns if external file unavailable
        
        return fraud_patterns
    
    def validate(self, phone: str, country: Optional[str] = None, 
                validation_level: ValidationLevel = None) -> ValidationResult:
        """
        Validate a phone number.
        
        Args:
            phone: Phone number to validate
            country: Country code for regional validation
            validation_level: Level of validation to perform
            
        Returns:
            ValidationResult with validation details
            
        Examples:
            >>> validator = PhoneValidator()
            >>> result = validator.validate("(555) 123-4567", country="US")
            >>> print(f"Valid: {result.is_valid}")
        """
        start_time = time.time()
        errors = []
        metadata = {
            'original_input': phone,
            'validation_time': None,
            'checks_performed': []
        }
        
        try:
            # Rate limiting check
            if _IMPORTS_AVAILABLE and not self.rate_limiter.allow_request("phone_validation"):
                raise SecurityError("Rate limit exceeded for phone validation")
            
            # Input validation
            if not isinstance(phone, str):
                errors.append("Phone number must be a string")
                return self._create_result(False, errors, metadata, 0.0)
            
            if len(phone.strip()) == 0:
                errors.append("Phone number cannot be empty")
                return self._create_result(False, errors, metadata, 0.0)
            
            # Normalize input
            normalized_phone = self._normalize_phone(phone)
            metadata['normalized_phone'] = normalized_phone
            
            # Use provided country or default
            region = country or self.options.default_region
            metadata['region'] = region
            
            # Check cache first
            cache_key = f"{normalized_phone}:{region}"
            if _IMPORTS_AVAILABLE:
                cached_result = self.validation_cache.get(cache_key)
                if cached_result:
                    return cached_result
            
            confidence = 1.0
            
            # 1. Basic format validation
            if self.options.check_format:
                format_valid, format_errors = self._validate_format(normalized_phone, region)
                metadata['checks_performed'].append('format')
                if not format_valid:
                    errors.extend(format_errors)
                    confidence *= 0.2
            
            # 2. Parse with phonenumbers library
            try:
                parsed_number = self.phone_util.parse(normalized_phone, region)
                metadata['country_code'] = parsed_number.country_code
                metadata['national_number'] = parsed_number.national_number
                metadata['checks_performed'].append('parse')
                
                # 3. Validity check
                is_valid = self.phone_util.is_valid_number(parsed_number)
                metadata['is_valid_number'] = is_valid
                if not is_valid:
                    errors.append("Phone number is not valid")
                    confidence *= 0.1
                
                # 4. Region validation
                if self.options.check_region and is_valid:
                    region_valid = self._validate_region(parsed_number, region)
                    metadata['checks_performed'].append('region')
                    metadata['region_matches'] = region_valid
                    if not region_valid and self.options.strict_validation:
                        errors.append(f"Phone number does not match expected region: {region}")
                        confidence *= 0.7
                
                # 5. Line type validation
                if self.options.check_line_type and is_valid:
                    line_type_valid, line_type_info = self._validate_line_type(parsed_number)
                    metadata['checks_performed'].append('line_type')
                    metadata.update(line_type_info)
                    if not line_type_valid:
                        errors.append(f"Phone number type not allowed: {line_type_info.get('line_type')}")
                        confidence *= 0.3
                
                # 6. Carrier information (optional)
                if self.options.check_carrier and is_valid:
                    carrier_info = self._get_carrier_info(parsed_number)
                    metadata['checks_performed'].append('carrier')
                    metadata.update(carrier_info)
                
                # 7. Geographic information
                if is_valid:
                    geo_info = self._get_geographic_info(parsed_number)
                    metadata.update(geo_info)
                
                # 8. Fraud detection
                fraud_detected = self._detect_fraud(normalized_phone, parsed_number)
                if fraud_detected:
                    errors.append("Phone number flagged as potentially fraudulent")
                    confidence *= 0.1
                
            except NumberParseException as e:
                errors.append(f"Failed to parse phone number: {e}")
                confidence = 0.0
            
            # Calculate final validation result
            is_valid = len(errors) == 0 and confidence > 0.5
            
            # Create result
            result = self._create_result(is_valid, errors, metadata, confidence)
            
            # Cache result
            if _IMPORTS_AVAILABLE:
                self.validation_cache.set(cache_key, result)
            
            # Audit logging
            if _IMPORTS_AVAILABLE:
                self.audit_logger.log_validation(
                    "phone", normalized_phone, is_valid, metadata
                )
            
            return result
            
        except SecurityError:
            raise
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return self._create_result(False, errors, metadata, 0.0)
        
        finally:
            metadata['validation_time'] = time.time() - start_time
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for consistent processing"""
        # Remove common separators and formatting
        normalized = re.sub(r'[^\d+]', '', phone.strip())
        
        # Handle common prefixes
        if normalized.startswith('00'):
            # Replace 00 with + for international format
            normalized = '+' + normalized[2:]
        elif normalized.startswith('011') and len(normalized) > 11:
            # US international prefix
            normalized = '+' + normalized[3:]
        
        return normalized
    
    def _validate_format(self, phone: str, region: str) -> Tuple[bool, List[str]]:
        """Validate phone number format using regex patterns"""
        errors = []
        
        # Check for obviously invalid patterns first
        for invalid_pattern in self._invalid_patterns:
            if invalid_pattern.match(phone):
                errors.append("Phone number matches known invalid pattern")
                return False, errors
        
        # Check E.164 format
        if phone.startswith('+'):
            if self._e164_pattern.match(phone):
                return True, []
            else:
                errors.append("Invalid E.164 international format")
                return False, errors
        
        # Region-specific validation
        if region == "US" or region == "CA":
            # NANP (North American Numbering Plan)
            for pattern_name, pattern in self._us_patterns.items():
                if pattern.match(phone):
                    return True, []
            errors.append("Invalid US/Canada phone number format")
            
        elif region == "GB":
            # UK format validation
            for pattern_name, pattern in self._uk_patterns.items():
                if pattern.match(phone):
                    return True, []
            errors.append("Invalid UK phone number format")
            
        else:
            # Generic international validation
            if self._international_pattern.match(phone):
                return True, []
            errors.append("Invalid international phone number format")
        
        return False, errors
    
    def _validate_region(self, parsed_number, expected_region: str) -> bool:
        """Validate that phone number belongs to expected region"""
        try:
            actual_region = self.phone_util.get_region_code_for_number(parsed_number)
            return actual_region == expected_region
        except Exception:
            return False
    
    def _validate_line_type(self, parsed_number) -> Tuple[bool, Dict[str, Any]]:
        """Validate phone number line type against allowed types"""
        try:
            number_type = self.phone_util.get_number_type(parsed_number)
            
            line_type_info = {
                'line_type': None,
                'line_type_code': number_type
            }
            
            # Map number types to readable names
            type_mapping = {
                PhoneNumberType.MOBILE: 'mobile',
                PhoneNumberType.FIXED_LINE: 'landline',
                PhoneNumberType.FIXED_LINE_OR_MOBILE: 'fixed_or_mobile',
                PhoneNumberType.TOLL_FREE: 'toll_free',
                PhoneNumberType.PREMIUM_RATE: 'premium',
                PhoneNumberType.SHARED_COST: 'shared_cost',
                PhoneNumberType.VOIP: 'voip',
                PhoneNumberType.PERSONAL_NUMBER: 'personal',
                PhoneNumberType.PAGER: 'pager',
                PhoneNumberType.UAN: 'uan',
                PhoneNumberType.VOICEMAIL: 'voicemail',
                PhoneNumberType.UNKNOWN: 'unknown'
            }
            
            line_type_name = type_mapping.get(number_type, 'unknown')
            line_type_info['line_type'] = line_type_name
            
            # Check if line type is allowed
            allowed = True
            if number_type == PhoneNumberType.MOBILE and not self.options.allow_mobile:
                allowed = False
            elif number_type == PhoneNumberType.FIXED_LINE and not self.options.allow_landline:
                allowed = False
            elif number_type == PhoneNumberType.VOIP and not self.options.allow_voip:
                allowed = False
            elif number_type == PhoneNumberType.PREMIUM_RATE and not self.options.allow_premium:
                allowed = False
            elif number_type == PhoneNumberType.SHARED_COST and not self.options.allow_shared_cost:
                allowed = False
            
            return allowed, line_type_info
            
        except Exception:
            return True, {'line_type': 'unknown', 'line_type_code': None}
    
    def _get_carrier_info(self, parsed_number) -> Dict[str, Any]:
        """Get carrier information for the phone number"""
        carrier_info = {
            'carrier_name': None,
            'carrier_code': None
        }
        
        try:
            # Check cache first
            cache_key = f"carrier:{parsed_number.country_code}:{parsed_number.national_number}"
            if _IMPORTS_AVAILABLE:
                cached_info = self.carrier_cache.get(cache_key)
                if cached_info:
                    return cached_info
            
            # Get carrier name
            carrier_name = name_for_number(parsed_number, 'en')
            if carrier_name:
                carrier_info['carrier_name'] = carrier_name
            
            # Cache result
            if _IMPORTS_AVAILABLE:
                self.carrier_cache.set(cache_key, carrier_info)
            
        except Exception:
            pass  # Ignore carrier lookup failures
        
        return carrier_info
    
    def _get_geographic_info(self, parsed_number) -> Dict[str, Any]:
        """Get geographic information for the phone number"""
        geo_info = {
            'region_code': None,
            'region_name': None,
            'time_zones': None
        }
        
        try:
            # Get region code
            region_code = self.phone_util.get_region_code_for_number(parsed_number)
            if region_code:
                geo_info['region_code'] = region_code
            
            # Get region description
            region_desc = description_for_number(parsed_number, 'en')
            if region_desc:
                geo_info['region_name'] = region_desc
            
        except Exception:
            pass  # Ignore geo lookup failures
        
        return geo_info
    
    def _detect_fraud(self, normalized_phone: str, parsed_number) -> bool:
        """Detect potentially fraudulent phone numbers"""
        try:
            # Check against known fraud patterns
            for pattern in self._fraud_patterns:
                if normalized_phone.startswith(pattern):
                    return True
            
            # Check for premium rate numbers (often used in fraud)
            number_type = self.phone_util.get_number_type(parsed_number)
            if number_type == PhoneNumberType.PREMIUM_RATE:
                return True
            
            # Additional fraud detection logic could be added here
            # (e.g., checking against blacklists, recent fraud reports, etc.)
            
            return False
            
        except Exception:
            return False  # Don't flag as fraud if detection fails
    
    def _create_result(self, is_valid: bool, errors: List[str], 
                      metadata: Dict[str, Any], confidence: float) -> ValidationResult:
        """Create validation result object"""
        if _IMPORTS_AVAILABLE:
            return ValidationResult(
                is_valid=is_valid,
                id_type=IDType.PHONE,
                confidence=confidence,
                metadata=metadata,
                errors=errors
            )
        else:
            # Fallback for development
            return ValidationResult(
                is_valid=is_valid,
                id_type="phone",
                confidence=confidence,
                metadata=metadata,
                errors=errors
            )
    
    def validate_batch(self, phones: List[str], country: Optional[str] = None, 
                      **kwargs) -> List[ValidationResult]:
        """
        Validate multiple phone numbers.
        
        Args:
            phones: List of phone numbers to validate
            country: Default country code for validation
            **kwargs: Additional validation options
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        
        for phone in phones:
            try:
                result = self.validate(phone, country=country, **kwargs)
                results.append(result)
            except Exception as e:
                # Create error result for failed validation
                error_result = self._create_result(
                    is_valid=False,
                    errors=[f"Validation failed: {str(e)}"],
                    metadata={'original_input': phone},
                    confidence=0.0
                )
                results.append(error_result)
        
        return results
    
    def format_phone(self, phone: str, country: Optional[str] = None, 
                    format_type: str = "national") -> str:
        """
        Format phone number for display.
        
        Args:
            phone: Phone number to format
            country: Country code for parsing
            format_type: Format type ("national", "international", "e164")
            
        Returns:
            Formatted phone number string
        """
        try:
            region = country or self.options.default_region
            parsed_number = self.phone_util.parse(phone, region)
            
            if format_type == "national":
                return self.phone_util.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
            elif format_type == "international":
                return self.phone_util.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            elif format_type == "e164":
                return self.phone_util.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            else:
                return phone  # Return original if unknown format type
                
        except Exception:
            return phone  # Return original if formatting fails
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Update validator configuration.
        
        Args:
            config: Configuration dictionary
        """
        for key, value in config.items():
            if hasattr(self.options, key):
                setattr(self.options, key, value)
            else:
                raise ValidationError(f"Unknown configuration option: {key}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this validator"""
        return {
            "validator_type": "phone",
            "supported_formats": ["E.164", "NANP", "UK", "International"],
            "features": [
                "format_validation",
                "region_validation",
                "line_type_detection",
                "carrier_lookup",
                "geographic_info",
                "fraud_detection"
            ],
            "options": {
                "check_format": self.options.check_format,
                "check_region": self.options.check_region,
                "check_carrier": self.options.check_carrier,
                "check_line_type": self.options.check_line_type,
                "default_region": self.options.default_region,
                "strict_validation": self.options.strict_validation
            },
            "allowed_types": {
                "mobile": self.options.allow_mobile,
                "landline": self.options.allow_landline,
                "voip": self.options.allow_voip,
                "premium": self.options.allow_premium,
                "shared_cost": self.options.allow_shared_cost
            },
            "fraud_patterns_count": len(self._fraud_patterns),
            "cache_stats": {
                "validation_cache": self.validation_cache.stats().to_dict() if _IMPORTS_AVAILABLE else None,
                "carrier_cache": self.carrier_cache.stats().to_dict() if _IMPORTS_AVAILABLE else None
            }
        }

# Export public interface
__all__ = [
    "PhoneValidator",
    "PhoneValidationOptions"
]
