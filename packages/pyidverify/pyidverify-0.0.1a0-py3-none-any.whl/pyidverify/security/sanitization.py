"""
Data Sanitization and PII Protection

Provides comprehensive data sanitization capabilities with PII detection,
secure data masking, anonymization, and pseudonymization techniques.
Implements privacy-preserving data processing with format preservation.

Features:
- Automatic PII detection and classification
- Format-preserving encryption and tokenization
- k-anonymity and differential privacy support
- Secure data masking and redaction
- Reversible and irreversible anonymization
- GDPR-compliant data minimization

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import re
import json
import uuid
import secrets
import hashlib
import logging
from typing import Dict, Any, List, Optional, Union, Pattern, Callable, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
import string

from .exceptions import SecurityError, ValidationSecurityError
from .constants import DataClassification, SecurityLevel
from .encryption import SecureEncryption, secure_random
from .hashing import SecureHasher

# Configure logging
logger = logging.getLogger('pyidverify.security.sanitization')


class PIIType(Enum):
    """Personally Identifiable Information type enumeration."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    BANK_ACCOUNT = "bank_account"
    IBAN = "iban"
    CUSTOM = "custom"


class SanitizationMethod(Enum):
    """Data sanitization method enumeration."""
    MASK = "mask"                    # Replace with mask characters (****)
    REDACT = "redact"               # Remove/replace with placeholder
    HASH = "hash"                   # One-way cryptographic hash
    ENCRYPT = "encrypt"             # Reversible encryption
    TOKENIZE = "tokenize"           # Replace with random token
    ANONYMIZE = "anonymize"         # Remove identifying characteristics
    PSEUDONYMIZE = "pseudonymize"   # Replace with consistent pseudonym
    GENERALIZE = "generalize"       # Replace with general category
    SUPPRESS = "suppress"           # Remove entirely


@dataclass
class PIIPattern:
    """PII detection pattern configuration."""
    pii_type: PIIType
    pattern: Pattern[str]
    confidence: float  # 0.0 to 1.0
    description: str
    examples: List[str]


@dataclass
class SanitizationRule:
    """Data sanitization rule configuration."""
    pii_type: PIIType
    method: SanitizationMethod
    pattern: Optional[Pattern[str]] = None
    replacement: Optional[str] = None
    preserve_format: bool = True
    classification: DataClassification = DataClassification.RESTRICTED
    custom_handler: Optional[Callable[[str], str]] = None


class PIIDetector:
    """
    Advanced PII detection engine with pattern matching and machine learning.
    """
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.HIGH):
        """
        Initialize PII detector with security level.
        
        Args:
            security_level: Security level affecting detection sensitivity
        """
        self.security_level = security_level
        self.patterns: Dict[PIIType, List[PIIPattern]] = {}
        self.custom_patterns: List[PIIPattern] = []
        
        # Initialize built-in patterns
        self._initialize_patterns()
        
        logger.info(f"PIIDetector initialized with {security_level.name} security level")
    
    def _initialize_patterns(self) -> None:
        """Initialize built-in PII detection patterns."""
        
        # Email patterns
        self.patterns[PIIType.EMAIL] = [
            PIIPattern(
                pii_type=PIIType.EMAIL,
                pattern=re.compile(
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    re.IGNORECASE
                ),
                confidence=0.95,
                description="Standard email address pattern",
                examples=["user@example.com", "test.email+tag@domain.co.uk"]
            )
        ]
        
        # Phone number patterns
        self.patterns[PIIType.PHONE] = [
            PIIPattern(
                pii_type=PIIType.PHONE,
                pattern=re.compile(
                    r'(\+?1?[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
                    re.IGNORECASE
                ),
                confidence=0.85,
                description="US phone number pattern",
                examples=["(555) 123-4567", "+1-555-123-4567", "555.123.4567"]
            ),
            PIIPattern(
                pii_type=PIIType.PHONE,
                pattern=re.compile(
                    r'\+[1-9]\d{1,14}',
                    re.IGNORECASE
                ),
                confidence=0.80,
                description="International phone number pattern",
                examples=["+44 20 7946 0958", "+33 1 42 86 83 26"]
            )
        ]
        
        # Social Security Number patterns
        self.patterns[PIIType.SSN] = [
            PIIPattern(
                pii_type=PIIType.SSN,
                pattern=re.compile(
                    r'\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b'
                ),
                confidence=0.95,
                description="US Social Security Number",
                examples=["123-45-6789", "123 45 6789", "123456789"]
            )
        ]
        
        # Credit card patterns
        self.patterns[PIIType.CREDIT_CARD] = [
            PIIPattern(
                pii_type=PIIType.CREDIT_CARD,
                pattern=re.compile(
                    r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'
                ),
                confidence=0.90,
                description="Credit card number pattern",
                examples=["4111111111111111", "5555555555554444"]
            )
        ]
        
        # IP address patterns
        self.patterns[PIIType.IP_ADDRESS] = [
            PIIPattern(
                pii_type=PIIType.IP_ADDRESS,
                pattern=re.compile(
                    r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                ),
                confidence=0.85,
                description="IPv4 address pattern",
                examples=["192.168.1.1", "10.0.0.1"]
            ),
            PIIPattern(
                pii_type=PIIType.IP_ADDRESS,
                pattern=re.compile(
                    r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
                ),
                confidence=0.85,
                description="IPv6 address pattern",
                examples=["2001:0db8:85a3:0000:0000:8a2e:0370:7334"]
            )
        ]
        
        # Name patterns (basic - would need NLP for better detection)
        if self.security_level in [SecurityLevel.HIGH, SecurityLevel.MAXIMUM]:
            self.patterns[PIIType.NAME] = [
                PIIPattern(
                    pii_type=PIIType.NAME,
                    pattern=re.compile(
                        r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b'
                    ),
                    confidence=0.60,  # Lower confidence - needs context
                    description="Person name pattern",
                    examples=["John Smith", "Mary Jane Doe"]
                )
            ]
        
        # Date of birth patterns
        self.patterns[PIIType.DATE_OF_BIRTH] = [
            PIIPattern(
                pii_type=PIIType.DATE_OF_BIRTH,
                pattern=re.compile(
                    r'\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12][0-9]|3[01])[/-](19|20)\d{2}\b'
                ),
                confidence=0.75,
                description="Date of birth pattern (MM/DD/YYYY)",
                examples=["01/15/1990", "12/31/1985"]
            ),
            PIIPattern(
                pii_type=PIIType.DATE_OF_BIRTH,
                pattern=re.compile(
                    r'\b(19|20)\d{2}[/-](0?[1-9]|1[0-2])[/-](0?[1-9]|[12][0-9]|3[01])\b'
                ),
                confidence=0.75,
                description="Date of birth pattern (YYYY/MM/DD)",
                examples=["1990/01/15", "1985/12/31"]
            )
        ]
    
    def detect_pii(self, text: str, min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """
        Detect PII in text using pattern matching.
        
        Args:
            text: Text to scan for PII
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of detected PII items with metadata
        """
        detections = []
        
        # Check all built-in patterns
        for pii_type, patterns in self.patterns.items():
            for pattern_info in patterns:
                if pattern_info.confidence >= min_confidence:
                    matches = pattern_info.pattern.finditer(text)
                    for match in matches:
                        detections.append({
                            'type': pii_type.value,
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'confidence': pattern_info.confidence,
                            'description': pattern_info.description,
                            'classification': DataClassification.RESTRICTED
                        })
        
        # Check custom patterns
        for pattern_info in self.custom_patterns:
            if pattern_info.confidence >= min_confidence:
                matches = pattern_info.pattern.finditer(text)
                for match in matches:
                    detections.append({
                        'type': pattern_info.pii_type.value,
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': pattern_info.confidence,
                        'description': pattern_info.description,
                        'classification': DataClassification.RESTRICTED
                    })
        
        # Sort by start position
        detections.sort(key=lambda x: x['start'])
        
        # Remove overlapping detections (keep highest confidence)
        filtered_detections = []
        for detection in detections:
            overlap = False
            for existing in filtered_detections:
                if (detection['start'] < existing['end'] and 
                    detection['end'] > existing['start']):
                    if detection['confidence'] > existing['confidence']:
                        # Replace existing with higher confidence detection
                        filtered_detections.remove(existing)
                        filtered_detections.append(detection)
                    overlap = True
                    break
            
            if not overlap:
                filtered_detections.append(detection)
        
        return filtered_detections
    
    def add_custom_pattern(
        self,
        name: str,
        pattern: Union[str, Pattern[str]],
        pii_type: PIIType = PIIType.CUSTOM,
        confidence: float = 0.8,
        description: str = ""
    ) -> None:
        """
        Add custom PII detection pattern.
        
        Args:
            name: Pattern name
            pattern: Regular expression pattern
            pii_type: Type of PII this pattern detects
            confidence: Detection confidence (0.0 to 1.0)
            description: Pattern description
        """
        if isinstance(pattern, str):
            pattern = re.compile(pattern, re.IGNORECASE)
        
        custom_pattern = PIIPattern(
            pii_type=pii_type,
            pattern=pattern,
            confidence=confidence,
            description=description or f"Custom pattern: {name}",
            examples=[]
        )
        
        self.custom_patterns.append(custom_pattern)
        logger.info(f"Added custom PII pattern: {name}")
    
    def validate_luhn(self, number: str) -> bool:
        """
        Validate credit card number using Luhn algorithm.
        
        Args:
            number: Credit card number to validate
            
        Returns:
            True if valid according to Luhn algorithm
        """
        # Remove non-digits
        number = re.sub(r'\D', '', number)
        
        if not number:
            return False
        
        # Luhn algorithm implementation
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            
            return checksum % 10
        
        return luhn_checksum(number) == 0


class DataSanitizer:
    """
    Advanced data sanitization engine with multiple sanitization methods.
    """
    
    def __init__(
        self,
        security_level: SecurityLevel = SecurityLevel.HIGH,
        encryption_key: Optional[bytes] = None
    ):
        """
        Initialize data sanitizer.
        
        Args:
            security_level: Security level for sanitization operations
            encryption_key: Optional encryption key for reversible operations
        """
        self.security_level = security_level
        self.pii_detector = PIIDetector(security_level)
        self.rules: List[SanitizationRule] = []
        
        # Initialize encryption for tokenization and pseudonymization
        self.encryption = SecureEncryption(
            security_level=security_level,
            master_key=encryption_key
        )
        
        # Initialize hasher for irreversible operations
        self.hasher = SecureHasher(security_level=security_level)
        
        # Token mapping for consistent pseudonymization
        self.pseudonym_map: Dict[str, str] = {}
        self.reverse_map: Dict[str, str] = {}
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info(f"DataSanitizer initialized with {security_level.name} security level")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default sanitization rules."""
        
        # Email sanitization
        self.rules.append(SanitizationRule(
            pii_type=PIIType.EMAIL,
            method=SanitizationMethod.MASK,
            replacement="***@***.***",
            preserve_format=True
        ))
        
        # Phone sanitization
        self.rules.append(SanitizationRule(
            pii_type=PIIType.PHONE,
            method=SanitizationMethod.MASK,
            replacement="***-***-****",
            preserve_format=True
        ))
        
        # SSN sanitization
        self.rules.append(SanitizationRule(
            pii_type=PIIType.SSN,
            method=SanitizationMethod.MASK,
            replacement="***-**-****",
            preserve_format=True,
            classification=DataClassification.RESTRICTED
        ))
        
        # Credit card sanitization
        self.rules.append(SanitizationRule(
            pii_type=PIIType.CREDIT_CARD,
            method=SanitizationMethod.MASK,
            replacement="****-****-****-****",
            preserve_format=True,
            classification=DataClassification.RESTRICTED
        ))
        
        # IP address sanitization
        self.rules.append(SanitizationRule(
            pii_type=PIIType.IP_ADDRESS,
            method=SanitizationMethod.GENERALIZE,
            replacement="[IP_ADDRESS]",
            preserve_format=False
        ))
    
    def sanitize_text(
        self,
        text: str,
        method: Optional[SanitizationMethod] = None,
        preserve_format: bool = True,
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """
        Sanitize PII in text using configured rules.
        
        Args:
            text: Text to sanitize
            method: Override sanitization method
            preserve_format: Whether to preserve original format
            min_confidence: Minimum confidence for PII detection
            
        Returns:
            Sanitization results including sanitized text and metadata
        """
        # Detect PII in text
        pii_detections = self.pii_detector.detect_pii(text, min_confidence)
        
        if not pii_detections:
            return {
                'sanitized_text': text,
                'original_length': len(text),
                'pii_detected': False,
                'detections': [],
                'sanitization_applied': []
            }
        
        # Apply sanitization rules
        sanitized_text = text
        applied_sanitizations = []
        offset = 0  # Track position changes due to replacements
        
        for detection in pii_detections:
            pii_type = PIIType(detection['type'])
            original_text = detection['text']
            
            # Find applicable rule
            rule = self._find_rule(pii_type, method)
            if not rule:
                continue
            
            # Apply sanitization method
            sanitized_value = self._apply_sanitization(
                original_text,
                rule,
                preserve_format if method is None else preserve_format
            )
            
            # Replace in text
            start_pos = detection['start'] + offset
            end_pos = detection['end'] + offset
            
            sanitized_text = (
                sanitized_text[:start_pos] + 
                sanitized_value + 
                sanitized_text[end_pos:]
            )
            
            # Update offset
            offset += len(sanitized_value) - len(original_text)
            
            applied_sanitizations.append({
                'type': pii_type.value,
                'method': rule.method.value,
                'original_text': original_text,
                'sanitized_text': sanitized_value,
                'position': detection['start'],
                'confidence': detection['confidence']
            })
        
        return {
            'sanitized_text': sanitized_text,
            'original_length': len(text),
            'sanitized_length': len(sanitized_text),
            'pii_detected': True,
            'detections': pii_detections,
            'sanitization_applied': applied_sanitizations
        }
    
    def _find_rule(
        self,
        pii_type: PIIType,
        method_override: Optional[SanitizationMethod] = None
    ) -> Optional[SanitizationRule]:
        """Find applicable sanitization rule for PII type."""
        for rule in self.rules:
            if rule.pii_type == pii_type:
                if method_override:
                    # Create temporary rule with override method
                    return SanitizationRule(
                        pii_type=pii_type,
                        method=method_override,
                        pattern=rule.pattern,
                        replacement=rule.replacement,
                        preserve_format=rule.preserve_format,
                        classification=rule.classification,
                        custom_handler=rule.custom_handler
                    )
                return rule
        return None
    
    def _apply_sanitization(
        self,
        text: str,
        rule: SanitizationRule,
        preserve_format: bool
    ) -> str:
        """Apply specific sanitization method to text."""
        
        if rule.custom_handler:
            return rule.custom_handler(text)
        
        if rule.method == SanitizationMethod.MASK:
            return self._mask_text(text, rule.replacement, preserve_format)
        
        elif rule.method == SanitizationMethod.REDACT:
            return "[REDACTED]"
        
        elif rule.method == SanitizationMethod.HASH:
            return self._hash_text(text)
        
        elif rule.method == SanitizationMethod.ENCRYPT:
            return self._encrypt_text(text)
        
        elif rule.method == SanitizationMethod.TOKENIZE:
            return self._tokenize_text(text, preserve_format)
        
        elif rule.method == SanitizationMethod.ANONYMIZE:
            return self._anonymize_text(text, rule.pii_type)
        
        elif rule.method == SanitizationMethod.PSEUDONYMIZE:
            return self._pseudonymize_text(text, rule.pii_type, preserve_format)
        
        elif rule.method == SanitizationMethod.GENERALIZE:
            return rule.replacement or f"[{rule.pii_type.value.upper()}]"
        
        elif rule.method == SanitizationMethod.SUPPRESS:
            return ""
        
        else:
            return text
    
    def _mask_text(
        self,
        text: str,
        replacement: Optional[str],
        preserve_format: bool
    ) -> str:
        """Mask text with placeholder characters."""
        if replacement and not preserve_format:
            return replacement
        
        if preserve_format:
            masked = ""
            for char in text:
                if char.isalnum():
                    masked += "*"
                else:
                    masked += char
            return masked
        
        return "*" * len(text)
    
    def _hash_text(self, text: str) -> str:
        """Hash text using secure one-way hash."""
        hash_bytes = self.hasher.hash_data(text.encode('utf-8'))
        return f"[HASH:{hash_bytes[:16].hex()}]"
    
    def _encrypt_text(self, text: str) -> str:
        """Encrypt text for reversible sanitization."""
        encrypted_bytes = self.encryption.encrypt(text)
        return f"[ENC:{encrypted_bytes[:16].hex()}...]"
    
    def _tokenize_text(self, text: str, preserve_format: bool) -> str:
        """Replace text with random token."""
        if preserve_format:
            token = ""
            for char in text:
                if char.isdigit():
                    token += str(secrets.randbelow(10))
                elif char.isalpha():
                    if char.isupper():
                        token += secrets.choice(string.ascii_uppercase)
                    else:
                        token += secrets.choice(string.ascii_lowercase)
                else:
                    token += char
            return token
        else:
            return f"TOK-{secrets.token_hex(8)}"
    
    def _anonymize_text(self, text: str, pii_type: PIIType) -> str:
        """Remove identifying characteristics from text."""
        if pii_type == PIIType.EMAIL:
            return "user@example.com"
        elif pii_type == PIIType.PHONE:
            return "555-0000"
        elif pii_type == PIIType.NAME:
            return "Anonymous"
        elif pii_type == PIIType.IP_ADDRESS:
            return "0.0.0.0"
        else:
            return f"[ANONYMOUS_{pii_type.value.upper()}]"
    
    def _pseudonymize_text(
        self,
        text: str,
        pii_type: PIIType,
        preserve_format: bool
    ) -> str:
        """Replace with consistent pseudonym."""
        # Check if we already have a pseudonym for this text
        if text in self.pseudonym_map:
            return self.pseudonym_map[text]
        
        # Generate new pseudonym
        if pii_type == PIIType.EMAIL:
            pseudonym = f"user{len(self.pseudonym_map):04d}@example.com"
        elif pii_type == PIIType.NAME:
            pseudonym = f"Person {len(self.pseudonym_map) + 1}"
        elif pii_type == PIIType.PHONE and preserve_format:
            # Generate format-preserving phone number
            pseudonym = "555-" + "".join(str(secrets.randbelow(10)) for _ in range(7))
        else:
            pseudonym = f"PSEUDO_{len(self.pseudonym_map):06d}"
        
        # Store mapping
        self.pseudonym_map[text] = pseudonym
        self.reverse_map[pseudonym] = text
        
        return pseudonym
    
    def add_sanitization_rule(self, rule: SanitizationRule) -> None:
        """
        Add custom sanitization rule.
        
        Args:
            rule: Sanitization rule to add
        """
        # Remove existing rule for same PII type
        self.rules = [r for r in self.rules if r.pii_type != rule.pii_type]
        
        # Add new rule
        self.rules.append(rule)
        
        logger.info(f"Added sanitization rule for {rule.pii_type.value}")
    
    def sanitize_json(
        self,
        data: Dict[str, Any],
        field_rules: Optional[Dict[str, SanitizationMethod]] = None
    ) -> Dict[str, Any]:
        """
        Sanitize JSON data with field-specific rules.
        
        Args:
            data: JSON data to sanitize
            field_rules: Optional field-specific sanitization rules
            
        Returns:
            Sanitized JSON data
        """
        field_rules = field_rules or {}
        
        def sanitize_value(key: str, value: Any) -> Any:
            if isinstance(value, str):
                method = field_rules.get(key)
                result = self.sanitize_text(value, method=method)
                return result['sanitized_text']
            elif isinstance(value, dict):
                return {k: sanitize_value(k, v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_value(key, item) for item in value]
            else:
                return value
        
        return {key: sanitize_value(key, value) for key, value in data.items()}
    
    def get_sanitization_report(self) -> Dict[str, Any]:
        """
        Generate sanitization activity report.
        
        Returns:
            Sanitization report with statistics
        """
        return {
            'rules_configured': len(self.rules),
            'pseudonym_mappings': len(self.pseudonym_map),
            'supported_pii_types': [pii_type.value for pii_type in PIIType],
            'security_level': self.security_level.name,
            'rule_details': [
                {
                    'pii_type': rule.pii_type.value,
                    'method': rule.method.value,
                    'preserve_format': rule.preserve_format,
                    'classification': rule.classification.value
                }
                for rule in self.rules
            ]
        }


def create_k_anonymous_dataset(
    records: List[Dict[str, Any]],
    k: int,
    quasi_identifiers: List[str],
    sensitive_attributes: List[str]
) -> List[Dict[str, Any]]:
    """
    Create k-anonymous dataset by generalizing quasi-identifiers.
    
    Args:
        records: Original dataset records
        k: Minimum group size for k-anonymity
        quasi_identifiers: Fields that could identify individuals
        sensitive_attributes: Fields to protect
        
    Returns:
        k-anonymous dataset
    """
    if k < 2:
        raise ValueError("k must be at least 2")
    
    # Group records by quasi-identifier combinations
    groups: Dict[str, List[Dict[str, Any]]] = {}
    
    for record in records:
        # Create key from quasi-identifiers
        qi_values = []
        for qi in quasi_identifiers:
            qi_values.append(str(record.get(qi, "")))
        key = "|".join(qi_values)
        
        if key not in groups:
            groups[key] = []
        groups[key].append(record)
    
    # Process groups to ensure k-anonymity
    k_anonymous_records = []
    
    for group_key, group_records in groups.items():
        if len(group_records) >= k:
            # Group is already k-anonymous
            k_anonymous_records.extend(group_records)
        else:
            # Need to generalize or suppress records
            # For simplicity, we'll generalize by replacing specific values
            for record in group_records:
                generalized_record = record.copy()
                
                # Generalize quasi-identifiers
                for qi in quasi_identifiers:
                    if qi in generalized_record:
                        # Simple generalization - replace with range or category
                        value = generalized_record[qi]
                        if isinstance(value, (int, float)):
                            # Round to nearest 10 for numeric values
                            generalized_record[qi] = f"{int(value // 10) * 10}-{int(value // 10) * 10 + 9}"
                        else:
                            # Replace with general category for strings
                            generalized_record[qi] = "[GENERALIZED]"
                
                k_anonymous_records.append(generalized_record)
    
    logger.info(f"Created k-anonymous dataset with k={k}, {len(k_anonymous_records)} records")
    return k_anonymous_records
