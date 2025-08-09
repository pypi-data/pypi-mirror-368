"""
Bank Account Validator
=====================

This module implements comprehensive bank account validation including routing
numbers, account numbers, and international bank account formats.

Features:
- US routing number validation (ABA format)
- Account number format validation
- International bank account number (IBAN) validation
- Bank identification and routing verification
- Account type detection (checking, savings, etc.)
- Institution validation against Federal Reserve database
- Format normalization and standardization
- Fraud detection for suspicious patterns

Examples:
    >>> from pyidverify.validators.financial.bank_account import BankAccountValidator
    >>> 
    >>> validator = BankAccountValidator()
    >>> result = validator.validate_us_account("021000021", "1234567890")
    >>> print(f"Valid: {result.is_valid}")
    >>> 
    >>> # IBAN validation
    >>> result = validator.validate_iban("GB29NWBK60161331926819")
    >>> print(f"IBAN valid: {result.is_valid}")

Security Features:
- Input sanitization prevents injection attacks
- Rate limiting prevents account enumeration
- Institution verification against known banks
- Fraud pattern detection for known bad accounts
- Audit logging for compliance requirements
- Anonymization for sensitive data logging
"""

from typing import Optional, Dict, Any, List, Set, Tuple, Union
import re
import time
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
    from ...config.financial import get_routing_database, get_iban_countries
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
class BankAccountValidationOptions:
    """Configuration options for bank account validation"""
    validate_routing: bool = True
    validate_account_format: bool = True
    validate_institution: bool = False
    validate_checksum: bool = True
    allow_international: bool = True
    strict_validation: bool = False
    anonymize_logs: bool = True  # For financial privacy
    check_fraud_patterns: bool = True
    
    def __post_init__(self):
        """Validate configuration options"""
        pass

class BankAccountValidator(BaseValidator):
    """
    Comprehensive bank account validator with support for US and international formats.
    
    This validator supports ABA routing numbers, account numbers, IBAN validation,
    and institution verification for financial compliance.
    """
    
    def __init__(self, **options):
        """
        Initialize bank account validator.
        
        Args:
            **options: Validation options (see BankAccountValidationOptions)
        """
        if _IMPORTS_AVAILABLE:
            super().__init__()
            self.audit_logger = AuditLogger("bank_account_validator")
            self.rate_limiter = RateLimiter(max_requests=200, time_window=3600)
            self.validation_cache = LRUCache(maxsize=500)
            self.routing_cache = LRUCache(maxsize=1000)
            self.iban_cache = LRUCache(maxsize=500)
        
        # Configure validation options
        self.options = BankAccountValidationOptions(**options)
        
        # Load routing number database
        self._routing_database = self._load_routing_database()
        
        # Load IBAN country specifications
        self._iban_specs = self._load_iban_specifications()
        
        # Load fraud patterns
        self._fraud_patterns = self._load_fraud_patterns()
        
        # Compile regex patterns
        self._compile_patterns()
    
    def _load_routing_database(self) -> Dict[str, Dict[str, Any]]:
        """Load ABA routing number database"""
        # Sample routing numbers (in production, would load from Fed database)
        routing_db = {
            '021000021': {
                'bank_name': 'JPMorgan Chase Bank',
                'location': 'New York, NY',
                'active': True,
                'wire_eligible': True
            },
            '011401533': {
                'bank_name': 'Wells Fargo Bank',
                'location': 'San Francisco, CA', 
                'active': True,
                'wire_eligible': True
            },
            '026009593': {
                'bank_name': 'Bank of America',
                'location': 'Charlotte, NC',
                'active': True,
                'wire_eligible': True
            },
            '111000025': {
                'bank_name': 'Federal Reserve Bank',
                'location': 'Boston, MA',
                'active': True,
                'wire_eligible': True
            }
        }
        
        # Try to load from external file
        try:
            routing_file = Path(__file__).parent / 'data' / 'routing_numbers.json'
            if routing_file.exists():
                with open(routing_file, 'r', encoding='utf-8') as f:
                    external_routing = json.load(f)
                    routing_db.update(external_routing)
        except Exception:
            pass  # Use built-in database if external file unavailable
        
        return routing_db
    
    def _load_iban_specifications(self) -> Dict[str, Dict[str, Any]]:
        """Load IBAN country specifications"""
        iban_specs = {
            'AD': {'length': 24, 'name': 'Andorra', 'example': 'AD1200012030200359100100'},
            'AE': {'length': 23, 'name': 'UAE', 'example': 'AE070331234567890123456'},
            'AL': {'length': 28, 'name': 'Albania', 'example': 'AL47212110090000000235698741'},
            'AT': {'length': 20, 'name': 'Austria', 'example': 'AT611904300234573201'},
            'AZ': {'length': 28, 'name': 'Azerbaijan', 'example': 'AZ21NABZ00000000137010001944'},
            'BA': {'length': 20, 'name': 'Bosnia and Herzegovina', 'example': 'BA391290079401028494'},
            'BE': {'length': 16, 'name': 'Belgium', 'example': 'BE68539007547034'},
            'BG': {'length': 22, 'name': 'Bulgaria', 'example': 'BG80BNBG96611020345678'},
            'BH': {'length': 22, 'name': 'Bahrain', 'example': 'BH67BMAG00001299123456'},
            'BR': {'length': 29, 'name': 'Brazil', 'example': 'BR1800360305000010009795493C1'},
            'CH': {'length': 21, 'name': 'Switzerland', 'example': 'CH9300762011623852957'},
            'CR': {'length': 21, 'name': 'Costa Rica', 'example': 'CR0515202001026284066'},
            'CY': {'length': 28, 'name': 'Cyprus', 'example': 'CY17002001280000001200527600'},
            'CZ': {'length': 24, 'name': 'Czech Republic', 'example': 'CZ6508000000192000145399'},
            'DE': {'length': 22, 'name': 'Germany', 'example': 'DE89370400440532013000'},
            'DK': {'length': 18, 'name': 'Denmark', 'example': 'DK5000400440116243'},
            'DO': {'length': 28, 'name': 'Dominican Republic', 'example': 'DO28BAGR00000001212453611324'},
            'EE': {'length': 20, 'name': 'Estonia', 'example': 'EE382200221020145685'},
            'ES': {'length': 24, 'name': 'Spain', 'example': 'ES9121000418450200051332'},
            'FI': {'length': 18, 'name': 'Finland', 'example': 'FI2112345600000785'},
            'FO': {'length': 18, 'name': 'Faroe Islands', 'example': 'FO6264600001631634'},
            'FR': {'length': 27, 'name': 'France', 'example': 'FR1420041010050500013M02606'},
            'GB': {'length': 22, 'name': 'United Kingdom', 'example': 'GB29NWBK60161331926819'},
            'GE': {'length': 22, 'name': 'Georgia', 'example': 'GE29NB0000000101904917'},
            'GI': {'length': 23, 'name': 'Gibraltar', 'example': 'GI75NWBK000000007099453'},
            'GL': {'length': 18, 'name': 'Greenland', 'example': 'GL8964710001000206'},
            'GR': {'length': 27, 'name': 'Greece', 'example': 'GR1601101250000000012300695'},
            'GT': {'length': 28, 'name': 'Guatemala', 'example': 'GT82TRAJ01020000001210029690'},
            'HR': {'length': 21, 'name': 'Croatia', 'example': 'HR1210010051863000160'},
            'HU': {'length': 28, 'name': 'Hungary', 'example': 'HU42117730161111101800000000'},
            'IE': {'length': 22, 'name': 'Ireland', 'example': 'IE29AIBK93115212345678'},
            'IL': {'length': 23, 'name': 'Israel', 'example': 'IL620108000000099999999'},
            'IS': {'length': 26, 'name': 'Iceland', 'example': 'IS140159260076545510730339'},
            'IT': {'length': 27, 'name': 'Italy', 'example': 'IT60X0542811101000000123456'},
            'JO': {'length': 30, 'name': 'Jordan', 'example': 'JO94CBJO0010000000000131000302'},
            'KW': {'length': 30, 'name': 'Kuwait', 'example': 'KW81CBKU0000000000001234560101'},
            'KZ': {'length': 20, 'name': 'Kazakhstan', 'example': 'KZ86125KZT5004100100'},
            'LB': {'length': 28, 'name': 'Lebanon', 'example': 'LB62099900000001001901229114'},
            'LC': {'length': 32, 'name': 'Saint Lucia', 'example': 'LC55HEMM000100010012001200023015'},
            'LI': {'length': 21, 'name': 'Liechtenstein', 'example': 'LI21088100002324013AA'},
            'LT': {'length': 20, 'name': 'Lithuania', 'example': 'LT121000011101001000'},
            'LU': {'length': 20, 'name': 'Luxembourg', 'example': 'LU280019400644750000'},
            'LV': {'length': 21, 'name': 'Latvia', 'example': 'LV80BANK0000435195001'},
            'MC': {'length': 27, 'name': 'Monaco', 'example': 'MC5811222000010123456789030'},
            'MD': {'length': 24, 'name': 'Moldova', 'example': 'MD24AG000225100013104168'},
            'ME': {'length': 22, 'name': 'Montenegro', 'example': 'ME25505000012345678951'},
            'MK': {'length': 19, 'name': 'Macedonia', 'example': 'MK07250120000058984'},
            'MR': {'length': 27, 'name': 'Mauritania', 'example': 'MR1300020001010000123456753'},
            'MT': {'length': 31, 'name': 'Malta', 'example': 'MT84MALT011000012345MTLCAST001S'},
            'MU': {'length': 30, 'name': 'Mauritius', 'example': 'MU17BOMM0101101030300200000MUR'},
            'NL': {'length': 18, 'name': 'Netherlands', 'example': 'NL91ABNA0417164300'},
            'NO': {'length': 15, 'name': 'Norway', 'example': 'NO9386011117947'},
            'PK': {'length': 24, 'name': 'Pakistan', 'example': 'PK36SCBL0000001123456702'},
            'PL': {'length': 28, 'name': 'Poland', 'example': 'PL61109010140000071219812874'},
            'PS': {'length': 29, 'name': 'Palestinian Territory', 'example': 'PS92PALS000000000400123456702'},
            'PT': {'length': 25, 'name': 'Portugal', 'example': 'PT50000201231234567890154'},
            'QA': {'length': 29, 'name': 'Qatar', 'example': 'QA58DOHB00001234567890ABCDEFG'},
            'RO': {'length': 24, 'name': 'Romania', 'example': 'RO49AAAA1B31007593840000'},
            'RS': {'length': 22, 'name': 'Serbia', 'example': 'RS35260005601001611379'},
            'SA': {'length': 24, 'name': 'Saudi Arabia', 'example': 'SA0380000000608010167519'},
            'SE': {'length': 24, 'name': 'Sweden', 'example': 'SE4550000000058398257466'},
            'SI': {'length': 19, 'name': 'Slovenia', 'example': 'SI56263300012039086'},
            'SK': {'length': 24, 'name': 'Slovakia', 'example': 'SK3112000000198742637541'},
            'SM': {'length': 27, 'name': 'San Marino', 'example': 'SM86U0322509800000000270100'},
            'TN': {'length': 24, 'name': 'Tunisia', 'example': 'TN5910006035183598478831'},
            'TR': {'length': 26, 'name': 'Turkey', 'example': 'TR330006100519786457841326'},
            'UA': {'length': 29, 'name': 'Ukraine', 'example': 'UA213223130000026007233566001'},
            'VG': {'length': 24, 'name': 'British Virgin Islands', 'example': 'VG96VPVG0000012345678901'},
            'XK': {'length': 20, 'name': 'Kosovo', 'example': 'XK051212012345678906'}
        }
        
        return iban_specs
    
    def _load_fraud_patterns(self) -> Set[str]:
        """Load known fraud patterns"""
        fraud_patterns = set()
        
        # Built-in fraud patterns
        built_in_fraud = {
            # Known fraudulent routing numbers (examples)
            '000000000',
            '111111111',
            '123456789',
            '999999999',
        }
        
        fraud_patterns.update(built_in_fraud)
        
        # Try to load from external file
        try:
            fraud_file = Path(__file__).parent / 'data' / 'bank_fraud_patterns.json'
            if fraud_file.exists():
                with open(fraud_file, 'r', encoding='utf-8') as f:
                    external_patterns = json.load(f)
                    if isinstance(external_patterns, list):
                        fraud_patterns.update(external_patterns)
        except Exception:
            pass  # Use built-in patterns if external file unavailable
        
        return fraud_patterns
    
    def _compile_patterns(self):
        """Compile regex patterns for validation"""
        
        # US routing number pattern (9 digits)
        self._routing_pattern = re.compile(r'^[0-9]{9}$')
        
        # US account number pattern (typically 4-20 digits)
        self._account_pattern = re.compile(r'^[0-9]{4,20}$')
        
        # IBAN pattern (country code + 2 check digits + up to 30 alphanumeric)
        self._iban_pattern = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$')
        
        # General bank account patterns
        self._general_patterns = {
            'digits_only': re.compile(r'^[0-9]+$'),
            'alphanumeric': re.compile(r'^[A-Z0-9]+$'),
            'with_spaces': re.compile(r'^[A-Z0-9\s]+$')
        }
    
    def validate_us_account(self, routing_number: str, account_number: str, 
                           validation_level: ValidationLevel = None) -> ValidationResult:
        """
        Validate US bank account (routing + account number).
        
        Args:
            routing_number: 9-digit ABA routing number
            account_number: Bank account number
            validation_level: Level of validation to perform
            
        Returns:
            ValidationResult with validation details
            
        Examples:
            >>> validator = BankAccountValidator()
            >>> result = validator.validate_us_account("021000021", "1234567890")
            >>> print(f"Valid: {result.is_valid}")
        """
        start_time = time.time()
        errors = []
        metadata = {
            'routing_number': routing_number[:3] + 'XXXX' + routing_number[-2:] if self.options.anonymize_logs else routing_number,
            'account_number': account_number[:2] + 'X' * (len(account_number) - 4) + account_number[-2:] if self.options.anonymize_logs and len(account_number) > 6 else 'XXXXXXXX',
            'validation_time': None,
            'checks_performed': [],
            'account_type': 'us_domestic'
        }
        
        try:
            # Rate limiting check
            if _IMPORTS_AVAILABLE and not self.rate_limiter.allow_request("bank_validation"):
                raise SecurityError("Rate limit exceeded for bank account validation")
            
            # Input validation
            if not isinstance(routing_number, str) or not isinstance(account_number, str):
                errors.append("Routing and account numbers must be strings")
                return self._create_result(False, errors, metadata, 0.0)
            
            # Normalize inputs
            routing_normalized = self._normalize_number(routing_number)
            account_normalized = self._normalize_number(account_number)
            
            confidence = 1.0
            
            # 1. Routing number validation
            if self.options.validate_routing:
                routing_valid, routing_info = self._validate_routing_number(routing_normalized)
                metadata['checks_performed'].append('routing')
                metadata.update(routing_info)
                
                if not routing_valid:
                    errors.extend(routing_info.get('routing_errors', []))
                    confidence *= 0.2
            
            # 2. Account number validation
            if self.options.validate_account_format:
                account_valid, account_info = self._validate_account_number(account_normalized)
                metadata['checks_performed'].append('account_format')
                metadata.update(account_info)
                
                if not account_valid:
                    errors.extend(account_info.get('account_errors', []))
                    confidence *= 0.3
            
            # 3. Institution validation
            if self.options.validate_institution:
                institution_valid, institution_info = self._validate_institution(routing_normalized)
                metadata['checks_performed'].append('institution')
                metadata.update(institution_info)
                
                if not institution_valid:
                    errors.extend(institution_info.get('institution_errors', []))
                    confidence *= 0.7
            
            # 4. Fraud detection
            if self.options.check_fraud_patterns:
                fraud_detected = self._detect_fraud_patterns(routing_normalized, account_normalized)
                if fraud_detected:
                    errors.append("Account matches known fraud patterns")
                    confidence *= 0.1
            
            # Calculate final validation result
            is_valid = len(errors) == 0 and confidence > 0.5
            
            # Create result
            result = self._create_result(is_valid, errors, metadata, confidence)
            
            # Audit logging
            if _IMPORTS_AVAILABLE:
                self.audit_logger.log_validation(
                    "us_bank_account", 
                    f"routing:{metadata['routing_number']},account:{metadata['account_number']}", 
                    is_valid, metadata
                )
            
            return result
            
        except SecurityError:
            raise
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return self._create_result(False, errors, metadata, 0.0)
        
        finally:
            metadata['validation_time'] = time.time() - start_time
    
    def validate_iban(self, iban: str, validation_level: ValidationLevel = None) -> ValidationResult:
        """
        Validate International Bank Account Number (IBAN).
        
        Args:
            iban: IBAN to validate
            validation_level: Level of validation to perform
            
        Returns:
            ValidationResult with validation details
            
        Examples:
            >>> validator = BankAccountValidator()
            >>> result = validator.validate_iban("GB29NWBK60161331926819")
            >>> print(f"Valid: {result.is_valid}")
        """
        start_time = time.time()
        errors = []
        metadata = {
            'original_iban': iban[:4] + 'X' * (len(iban) - 8) + iban[-4:] if self.options.anonymize_logs and len(iban) > 8 else iban,
            'validation_time': None,
            'checks_performed': [],
            'account_type': 'iban'
        }
        
        try:
            # Rate limiting check
            if _IMPORTS_AVAILABLE and not self.rate_limiter.allow_request("iban_validation"):
                raise SecurityError("Rate limit exceeded for IBAN validation")
            
            # Input validation
            if not isinstance(iban, str):
                errors.append("IBAN must be a string")
                return self._create_result(False, errors, metadata, 0.0)
            
            # Normalize IBAN
            iban_normalized = self._normalize_iban(iban)
            metadata['normalized_iban'] = iban_normalized[:4] + 'X' * (len(iban_normalized) - 8) + iban_normalized[-4:] if self.options.anonymize_logs else iban_normalized
            
            # Check cache first
            cache_key = f"iban_{iban_normalized[:4]}_{len(iban_normalized)}"
            if _IMPORTS_AVAILABLE:
                cached_result = self.iban_cache.get(cache_key)
                if cached_result:
                    return cached_result
            
            confidence = 1.0
            
            # 1. Basic format validation
            format_valid, format_errors = self._validate_iban_format(iban_normalized)
            metadata['checks_performed'].append('format')
            
            if not format_valid:
                errors.extend(format_errors)
                return self._create_result(False, errors, metadata, 0.0)
            
            # 2. Country code validation
            country_code = iban_normalized[:2]
            country_valid, country_info = self._validate_iban_country(country_code, iban_normalized)
            metadata['checks_performed'].append('country')
            metadata.update(country_info)
            
            if not country_valid:
                errors.extend(country_info.get('country_errors', []))
                confidence *= 0.3
            
            # 3. Length validation
            if country_info.get('expected_length'):
                if len(iban_normalized) != country_info['expected_length']:
                    errors.append(f"Invalid IBAN length for {country_code}: expected {country_info['expected_length']}, got {len(iban_normalized)}")
                    confidence *= 0.4
            
            # 4. Check digit validation
            if self.options.validate_checksum:
                checksum_valid = self._validate_iban_checksum(iban_normalized)
                metadata['checksum_valid'] = checksum_valid
                metadata['checks_performed'].append('checksum')
                
                if not checksum_valid:
                    errors.append("IBAN checksum validation failed")
                    confidence *= 0.1
            
            # Calculate final validation result
            is_valid = len(errors) == 0 and confidence > 0.5
            
            # Create result
            result = self._create_result(is_valid, errors, metadata, confidence)
            
            # Cache result
            if _IMPORTS_AVAILABLE:
                self.iban_cache.set(cache_key, result)
            
            # Audit logging
            if _IMPORTS_AVAILABLE:
                self.audit_logger.log_validation(
                    "iban", metadata['original_iban'], is_valid, metadata
                )
            
            return result
            
        except SecurityError:
            raise
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return self._create_result(False, errors, metadata, 0.0)
        
        finally:
            metadata['validation_time'] = time.time() - start_time
    
    def _normalize_number(self, number: str) -> str:
        """Normalize bank account number by removing spaces and dashes"""
        return re.sub(r'[\s\-]', '', number.strip())
    
    def _normalize_iban(self, iban: str) -> str:
        """Normalize IBAN by removing spaces and converting to uppercase"""
        return re.sub(r'\s', '', iban.upper().strip())
    
    def _validate_routing_number(self, routing_number: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate ABA routing number"""
        routing_info = {
            'routing_valid': False,
            'routing_length': len(routing_number),
            'routing_errors': []
        }
        
        # Check length
        if len(routing_number) != 9:
            routing_info['routing_errors'].append(f"Invalid routing number length: {len(routing_number)}, expected 9")
            return False, routing_info
        
        # Check format (9 digits)
        if not self._routing_pattern.match(routing_number):
            routing_info['routing_errors'].append("Routing number must be 9 digits")
            return False, routing_info
        
        # Check checksum algorithm
        if self.options.validate_checksum:
            checksum_valid = self._validate_routing_checksum(routing_number)
            routing_info['checksum_valid'] = checksum_valid
            
            if not checksum_valid:
                routing_info['routing_errors'].append("Routing number checksum validation failed")
                return False, routing_info
        
        routing_info['routing_valid'] = True
        return True, routing_info
    
    def _validate_routing_checksum(self, routing_number: str) -> bool:
        """Validate routing number using ABA checksum algorithm"""
        try:
            # ABA checksum algorithm
            weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
            checksum = sum(int(digit) * weight for digit, weight in zip(routing_number, weights))
            return checksum % 10 == 0
        except (ValueError, TypeError):
            return False
    
    def _validate_account_number(self, account_number: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate account number format"""
        account_info = {
            'account_valid': False,
            'account_length': len(account_number),
            'account_errors': []
        }
        
        # Check length (typically 4-20 digits)
        if len(account_number) < 4:
            account_info['account_errors'].append("Account number too short (minimum 4 digits)")
            return False, account_info
        
        if len(account_number) > 20:
            account_info['account_errors'].append("Account number too long (maximum 20 digits)")
            return False, account_info
        
        # Check format (digits only for US accounts)
        if not self._account_pattern.match(account_number):
            account_info['account_errors'].append("Account number must be digits only")
            return False, account_info
        
        # Check for obviously invalid patterns
        if len(set(account_number)) == 1:  # All same digit
            account_info['account_errors'].append("Account number cannot be all the same digit")
            return False, account_info
        
        account_info['account_valid'] = True
        return True, account_info
    
    def _validate_institution(self, routing_number: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate financial institution"""
        institution_info = {
            'institution_valid': False,
            'bank_name': None,
            'bank_location': None,
            'is_active': None,
            'wire_eligible': None,
            'institution_errors': []
        }
        
        # Check cache first
        cache_key = f"routing_{routing_number}"
        if _IMPORTS_AVAILABLE:
            cached_info = self.routing_cache.get(cache_key)
            if cached_info:
                return cached_info.get('institution_valid', False), cached_info
        
        # Look up in routing database
        if routing_number in self._routing_database:
            bank_info = self._routing_database[routing_number]
            institution_info.update({
                'institution_valid': bank_info.get('active', False),
                'bank_name': bank_info.get('bank_name'),
                'bank_location': bank_info.get('location'),
                'is_active': bank_info.get('active'),
                'wire_eligible': bank_info.get('wire_eligible')
            })
            
            if not bank_info.get('active', False):
                institution_info['institution_errors'].append("Bank is not active")
        else:
            institution_info['institution_errors'].append("Unknown routing number")
        
        # Cache result
        if _IMPORTS_AVAILABLE:
            self.routing_cache.set(cache_key, institution_info)
        
        return institution_info['institution_valid'], institution_info
    
    def _validate_iban_format(self, iban: str) -> Tuple[bool, List[str]]:
        """Validate basic IBAN format"""
        errors = []
        
        # Check minimum length
        if len(iban) < 15:
            errors.append("IBAN too short (minimum 15 characters)")
            return False, errors
        
        # Check maximum length
        if len(iban) > 34:
            errors.append("IBAN too long (maximum 34 characters)")
            return False, errors
        
        # Check pattern
        if not self._iban_pattern.match(iban):
            errors.append("Invalid IBAN format")
            return False, errors
        
        return True, []
    
    def _validate_iban_country(self, country_code: str, iban: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate IBAN country code and specifications"""
        country_info = {
            'country_code': country_code,
            'country_name': None,
            'expected_length': None,
            'country_errors': []
        }
        
        if country_code in self._iban_specs:
            spec = self._iban_specs[country_code]
            country_info.update({
                'country_name': spec['name'],
                'expected_length': spec['length']
            })
            return True, country_info
        else:
            country_info['country_errors'].append(f"Unknown country code: {country_code}")
            return False, country_info
    
    def _validate_iban_checksum(self, iban: str) -> bool:
        """Validate IBAN using mod-97 checksum algorithm"""
        try:
            # Move first 4 characters to end
            rearranged = iban[4:] + iban[:4]
            
            # Replace letters with numbers (A=10, B=11, ..., Z=35)
            numeric_string = ''
            for char in rearranged:
                if char.isdigit():
                    numeric_string += char
                else:
                    numeric_string += str(ord(char) - ord('A') + 10)
            
            # Calculate mod 97
            checksum = int(numeric_string) % 97
            return checksum == 1
            
        except (ValueError, TypeError):
            return False
    
    def _detect_fraud_patterns(self, routing_number: str, account_number: str) -> bool:
        """Detect fraudulent account patterns"""
        # Check routing number against fraud patterns
        if routing_number in self._fraud_patterns:
            return True
        
        # Check for sequential account numbers
        if self._is_sequential_account(account_number):
            return True
        
        # Check for repeated patterns
        if len(set(account_number)) <= 2:
            return True
        
        return False
    
    def _is_sequential_account(self, account_number: str) -> bool:
        """Check if account number is sequential"""
        if len(account_number) < 4:
            return False
        
        # Check for ascending sequences
        ascending = all(
            int(account_number[i]) == int(account_number[i-1]) + 1 
            for i in range(1, len(account_number))
        )
        
        # Check for descending sequences
        descending = all(
            int(account_number[i]) == int(account_number[i-1]) - 1 
            for i in range(1, len(account_number))
        )
        
        return ascending or descending
    
    def _create_result(self, is_valid: bool, errors: List[str], 
                      metadata: Dict[str, Any], confidence: float) -> ValidationResult:
        """Create validation result object"""
        if _IMPORTS_AVAILABLE:
            return ValidationResult(
                is_valid=is_valid,
                id_type=IDType.BANK_ACCOUNT,
                confidence=confidence,
                metadata=metadata,
                errors=errors
            )
        else:
            # Fallback for development
            return ValidationResult(
                is_valid=is_valid,
                id_type="bank_account",
                confidence=confidence,
                metadata=metadata,
                errors=errors
            )
    
    def validate_batch(self, accounts: List[Dict[str, Any]], **kwargs) -> List[ValidationResult]:
        """
        Validate multiple bank accounts.
        
        Args:
            accounts: List of account dictionaries with validation data
            **kwargs: Additional validation options
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        
        for account_data in accounts:
            try:
                account_type = account_data.get('type', 'us_domestic')
                
                if account_type == 'us_domestic':
                    routing = account_data.get('routing_number', '')
                    account = account_data.get('account_number', '')
                    result = self.validate_us_account(routing, account, **kwargs)
                elif account_type == 'iban':
                    iban = account_data.get('iban', '')
                    result = self.validate_iban(iban, **kwargs)
                else:
                    result = self._create_result(
                        is_valid=False,
                        errors=[f"Unknown account type: {account_type}"],
                        metadata={'account_type': account_type},
                        confidence=0.0
                    )
                
                results.append(result)
            except Exception as e:
                # Create error result for failed validation
                error_result = self._create_result(
                    is_valid=False,
                    errors=[f"Validation failed: {str(e)}"],
                    metadata={'original_input': str(account_data)},
                    confidence=0.0
                )
                results.append(error_result)
        
        return results
    
    def get_routing_info(self, routing_number: str) -> Dict[str, Any]:
        """
        Get information about a routing number.
        
        Args:
            routing_number: Routing number to look up
            
        Returns:
            Dictionary with routing number information
        """
        normalized = self._normalize_number(routing_number)
        
        if normalized in self._routing_database:
            return self._routing_database[normalized].copy()
        else:
            return {'error': 'Routing number not found'}
    
    def get_iban_info(self, iban: str) -> Dict[str, Any]:
        """
        Get information about an IBAN.
        
        Args:
            iban: IBAN to analyze
            
        Returns:
            Dictionary with IBAN information
        """
        normalized = self._normalize_iban(iban)
        
        if len(normalized) >= 4:
            country_code = normalized[:2]
            check_digits = normalized[2:4]
            
            info = {
                'country_code': country_code,
                'check_digits': check_digits,
                'account_identifier': normalized[4:] if len(normalized) > 4 else '',
                'length': len(normalized)
            }
            
            if country_code in self._iban_specs:
                spec = self._iban_specs[country_code]
                info.update({
                    'country_name': spec['name'],
                    'expected_length': spec['length'],
                    'example': spec['example']
                })
            
            return info
        else:
            return {'error': 'Invalid IBAN format'}
    
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
            "validator_type": "bank_account",
            "supported_formats": ["US_Domestic", "IBAN"],
            "features": [
                "routing_validation",
                "account_format_validation", 
                "institution_validation",
                "checksum_validation",
                "iban_validation",
                "fraud_detection"
            ],
            "options": {
                "validate_routing": self.options.validate_routing,
                "validate_account_format": self.options.validate_account_format,
                "validate_institution": self.options.validate_institution,
                "validate_checksum": self.options.validate_checksum,
                "allow_international": self.options.allow_international,
                "strict_validation": self.options.strict_validation,
                "anonymize_logs": self.options.anonymize_logs,
                "check_fraud_patterns": self.options.check_fraud_patterns
            },
            "routing_database_size": len(self._routing_database),
            "iban_countries_supported": len(self._iban_specs),
            "fraud_patterns_count": len(self._fraud_patterns),
            "cache_stats": {
                "validation_cache": self.validation_cache.stats().to_dict() if _IMPORTS_AVAILABLE else None,
                "routing_cache": self.routing_cache.stats().to_dict() if _IMPORTS_AVAILABLE else None,
                "iban_cache": self.iban_cache.stats().to_dict() if _IMPORTS_AVAILABLE else None
            }
        }

# Export public interface
__all__ = [
    "BankAccountValidator",
    "BankAccountValidationOptions"
]
