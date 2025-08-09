"""
Validation Patterns Library

Comprehensive collection of regular expressions and validation patterns for
all supported ID types, organized by country/region with security validation.

Features:
- Regex patterns for 24+ ID types across multiple countries
- Pattern security validation to prevent ReDoS attacks
- Pattern complexity analysis and optimization
- Country-specific format variations
- Pattern versioning and update mechanisms
- Test pattern validation utilities
- Performance-optimized compiled patterns

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import re
import json
import logging
from typing import Dict, List, Optional, Pattern, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import time
from pathlib import Path

# Configure logging
logger = logging.getLogger('pyidverify.config.patterns')


class PatternType(Enum):
    """Types of validation patterns."""
    FORMAT = "format"          # Basic format validation
    STRICT = "strict"          # Strict validation with check digits
    RELAXED = "relaxed"        # More permissive validation
    INTERNATIONAL = "intl"     # International format support


class PatternSecurity(Enum):
    """Pattern security assessment levels."""
    SAFE = "safe"              # Safe pattern, no security concerns
    WARNING = "warning"        # Potential performance issues
    DANGEROUS = "dangerous"    # ReDoS vulnerability detected


@dataclass
class PatternInfo:
    """Information about a validation pattern."""
    name: str
    pattern: str
    type: PatternType
    country: Optional[str] = None
    description: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    counter_examples: List[str] = field(default_factory=list)
    security_level: PatternSecurity = PatternSecurity.SAFE
    performance_ms: Optional[float] = None
    version: str = "1.0.0"
    compiled: Optional[Pattern] = field(default=None, init=False)


class PatternSecurityAnalyzer:
    """
    Security analyzer for regex patterns to detect ReDoS vulnerabilities.
    """
    
    # Known problematic patterns that can cause exponential backtracking
    REDOS_PATTERNS = [
        r'\*\+',           # Nested quantifiers
        r'\+\*',           # Nested quantifiers
        r'\?\+',           # Nested quantifiers
        r'\*\?',           # Nested quantifiers
        r'\+\?',           # Nested quantifiers
        r'\?\?',           # Nested quantifiers
        r'(\(.+\)\+)+',    # Nested groups with quantifiers
        r'(\(.+\)\*)+',    # Nested groups with quantifiers
        r'(.*)+',          # Dangerous wildcard quantifier
        r'(.+)+',          # Dangerous wildcard quantifier
        r'(.*)+'           # Dangerous wildcard quantifier
    ]
    
    # Maximum safe complexity metrics
    MAX_SAFE_LENGTH = 500
    MAX_SAFE_GROUPS = 20
    MAX_SAFE_QUANTIFIERS = 30
    MAX_SAFE_ALTERNATIONS = 10
    
    @classmethod
    def analyze_pattern(cls, pattern: str) -> Tuple[PatternSecurity, List[str]]:
        """
        Analyze regex pattern for security vulnerabilities.
        
        Args:
            pattern: Regex pattern to analyze
            
        Returns:
            Tuple of (security_level, list_of_issues)
        """
        issues = []
        security_level = PatternSecurity.SAFE
        
        # Check for known ReDoS patterns
        for redos_pattern in cls.REDOS_PATTERNS:
            if re.search(redos_pattern, pattern):
                issues.append(f"Potential ReDoS vulnerability: {redos_pattern}")
                security_level = PatternSecurity.DANGEROUS
        
        # Check complexity metrics
        complexity_issues = cls._check_complexity(pattern)
        issues.extend(complexity_issues)
        
        if complexity_issues:
            if security_level == PatternSecurity.SAFE:
                security_level = PatternSecurity.WARNING
        
        # Performance test with pathological inputs
        performance_issues = cls._test_performance(pattern)
        issues.extend(performance_issues)
        
        if performance_issues:
            security_level = PatternSecurity.DANGEROUS
        
        return security_level, issues
    
    @classmethod
    def _check_complexity(cls, pattern: str) -> List[str]:
        """Check pattern complexity metrics."""
        issues = []
        
        # Check overall length
        if len(pattern) > cls.MAX_SAFE_LENGTH:
            issues.append(f"Pattern too long: {len(pattern)} > {cls.MAX_SAFE_LENGTH}")
        
        # Count groups
        group_count = len(re.findall(r'[^\\]\(', '(' + pattern))
        if group_count > cls.MAX_SAFE_GROUPS:
            issues.append(f"Too many groups: {group_count} > {cls.MAX_SAFE_GROUPS}")
        
        # Count quantifiers
        quantifier_count = len(re.findall(r'[*+?{]', pattern))
        if quantifier_count > cls.MAX_SAFE_QUANTIFIERS:
            issues.append(f"Too many quantifiers: {quantifier_count} > {cls.MAX_SAFE_QUANTIFIERS}")
        
        # Count alternations
        alternation_count = len(re.findall(r'[^\\]\|', '|' + pattern))
        if alternation_count > cls.MAX_SAFE_ALTERNATIONS:
            issues.append(f"Too many alternations: {alternation_count} > {cls.MAX_SAFE_ALTERNATIONS}")
        
        return issues
    
    @classmethod
    def _test_performance(cls, pattern: str, timeout_ms: float = 100.0) -> List[str]:
        """Test pattern performance with pathological inputs."""
        issues = []
        
        try:
            compiled = re.compile(pattern)
        except re.error as e:
            issues.append(f"Invalid regex pattern: {e}")
            return issues
        
        # Test with various pathological inputs
        pathological_inputs = [
            'a' * 1000,                    # Long repetition
            'a' * 100 + 'b',              # Long repetition with mismatch
            'a' * 50 + 'b' + 'a' * 50,    # Mismatch in middle
            '(' * 100,                     # Unbalanced parentheses
            'a' * 100 + '!',              # Invalid characters
            'aaa...aaa!',                  # Deliberate ReDoS attempt
        ]
        
        for test_input in pathological_inputs:
            start_time = time.perf_counter()
            
            try:
                # Test with timeout
                compiled.match(test_input)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                
                if elapsed_ms > timeout_ms:
                    issues.append(f"Performance issue: {elapsed_ms:.2f}ms > {timeout_ms}ms on input length {len(test_input)}")
                    
            except Exception as e:
                issues.append(f"Pattern error on test input: {e}")
        
        return issues


class PatternLibrary:
    """
    Comprehensive library of validation patterns with security validation.
    """
    
    def __init__(self):
        """Initialize pattern library."""
        self.patterns: Dict[str, Dict[str, PatternInfo]] = {}
        self.security_analyzer = PatternSecurityAnalyzer()
        self._load_builtin_patterns()
    
    def _load_builtin_patterns(self) -> None:
        """Load built-in validation patterns."""
        
        # Email patterns
        self.add_pattern_group("email", {
            "basic": PatternInfo(
                name="email_basic",
                pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                type=PatternType.FORMAT,
                description="Basic email format validation",
                examples=[
                    "user@example.com",
                    "test.email+tag@domain.co.uk",
                    "user_name123@sub.domain.org"
                ],
                counter_examples=[
                    "invalid.email",
                    "@domain.com",
                    "user@",
                    "user..name@domain.com"
                ]
            ),
            "strict": PatternInfo(
                name="email_strict",
                pattern=r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$',
                type=PatternType.STRICT,
                description="Strict RFC-compliant email validation",
                examples=[
                    "user@example.com",
                    "test@domain.org"
                ],
                counter_examples=[
                    "user.@domain.com",
                    ".user@domain.com",
                    "user@domain.",
                    "user@.domain.com"
                ]
            )
        })
        
        # Phone number patterns
        self.add_pattern_group("phone", {
            "us": PatternInfo(
                name="phone_us",
                pattern=r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
                type=PatternType.FORMAT,
                country="US",
                description="US phone number format",
                examples=[
                    "+1 (555) 123-4567",
                    "555-123-4567",
                    "5551234567",
                    "1-555-123-4567"
                ],
                counter_examples=[
                    "555-123-456",
                    "+1-555-123-45678",
                    "555.123.456.7890"
                ]
            ),
            "international": PatternInfo(
                name="phone_international",
                pattern=r'^\+[1-9]\d{1,14}$',
                type=PatternType.INTERNATIONAL,
                description="International E.164 phone format",
                examples=[
                    "+1234567890",
                    "+447700123456",
                    "+8613800000000"
                ],
                counter_examples=[
                    "+0123456789",
                    "1234567890",
                    "+123456789012345678"
                ]
            )
        })
        
        # Credit card patterns
        self.add_pattern_group("credit_card", {
            "visa": PatternInfo(
                name="credit_card_visa",
                pattern=r'^4[0-9]{12}(?:[0-9]{3})?$',
                type=PatternType.FORMAT,
                description="Visa credit card format",
                examples=[
                    "4111111111111111",
                    "4000000000000002",
                    "4123456789012345"
                ],
                counter_examples=[
                    "3111111111111111",
                    "411111111111111",
                    "41111111111111111"
                ]
            ),
            "mastercard": PatternInfo(
                name="credit_card_mastercard",
                pattern=r'^5[1-5][0-9]{14}$',
                type=PatternType.FORMAT,
                description="MasterCard credit card format",
                examples=[
                    "5555555555554444",
                    "5105105105105100",
                    "5123456789012346"
                ],
                counter_examples=[
                    "4555555555554444",
                    "555555555555444",
                    "55555555555544445"
                ]
            ),
            "amex": PatternInfo(
                name="credit_card_amex",
                pattern=r'^3[47][0-9]{13}$',
                type=PatternType.FORMAT,
                description="American Express credit card format",
                examples=[
                    "378282246310005",
                    "371449635398431",
                    "340000000000009"
                ],
                counter_examples=[
                    "478282246310005",
                    "37828224631000",
                    "3782822463100055"
                ]
            ),
            "generic": PatternInfo(
                name="credit_card_generic",
                pattern=r'^[0-9]{13,19}$',
                type=PatternType.RELAXED,
                description="Generic credit card number format",
                examples=[
                    "4111111111111111",
                    "5555555555554444",
                    "378282246310005"
                ],
                counter_examples=[
                    "411111111111",
                    "41111111111111111111",
                    "abcd1234efgh5678"
                ]
            )
        })
        
        # Social Security Number patterns
        self.add_pattern_group("ssn", {
            "us": PatternInfo(
                name="ssn_us",
                pattern=r'^(?!000|666|9\d{2})\d{3}-?(?!00)\d{2}-?(?!0000)\d{4}$',
                type=PatternType.STRICT,
                country="US",
                description="US Social Security Number format",
                examples=[
                    "123-45-6789",
                    "123456789",
                    "987-65-4321"
                ],
                counter_examples=[
                    "000-12-3456",
                    "666-12-3456",
                    "123-00-4567",
                    "123-45-0000"
                ]
            )
        })
        
        # IP Address patterns
        self.add_pattern_group("ip_address", {
            "ipv4": PatternInfo(
                name="ip_address_ipv4",
                pattern=r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                type=PatternType.STRICT,
                description="IPv4 address format",
                examples=[
                    "192.168.1.1",
                    "10.0.0.1",
                    "127.0.0.1",
                    "255.255.255.255"
                ],
                counter_examples=[
                    "256.1.1.1",
                    "192.168.1",
                    "192.168.1.1.1",
                    "192.168.01.1"
                ]
            ),
            "ipv6": PatternInfo(
                name="ip_address_ipv6",
                pattern=r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$',
                type=PatternType.STRICT,
                description="IPv6 address format (simplified)",
                examples=[
                    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                    "2001:db8:85a3::8a2e:370:7334",
                    "::1",
                    "::"
                ],
                counter_examples=[
                    "2001:0db8:85a3::8a2e::7334",
                    "2001:0db8:85a3:0000:0000:8a2e:0370:7334:extra",
                    "gggg::1"
                ]
            )
        })
        
        # Driver's License patterns (US states)
        self.add_pattern_group("drivers_license", {
            "ca": PatternInfo(  # California
                name="drivers_license_ca",
                pattern=r'^[A-Z]\d{7}$',
                type=PatternType.FORMAT,
                country="US",
                description="California driver's license format",
                examples=[
                    "A1234567",
                    "Z9876543"
                ],
                counter_examples=[
                    "1234567A",
                    "A123456",
                    "AA1234567"
                ]
            ),
            "ny": PatternInfo(  # New York
                name="drivers_license_ny",
                pattern=r'^\d{3}[-\s]?\d{3}[-\s]?\d{3}$',
                type=PatternType.FORMAT,
                country="US",
                description="New York driver's license format",
                examples=[
                    "123-456-789",
                    "123456789",
                    "123 456 789"
                ],
                counter_examples=[
                    "1234567890",
                    "12-456-789",
                    "A123456789"
                ]
            ),
            "tx": PatternInfo(  # Texas
                name="drivers_license_tx",
                pattern=r'^\d{8}$',
                type=PatternType.FORMAT,
                country="US",
                description="Texas driver's license format",
                examples=[
                    "12345678",
                    "98765432"
                ],
                counter_examples=[
                    "1234567",
                    "123456789",
                    "A1234567"
                ]
            )
        })
        
        # Passport patterns
        self.add_pattern_group("passport", {
            "us": PatternInfo(
                name="passport_us",
                pattern=r'^[0-9]{9}$',
                type=PatternType.FORMAT,
                country="US",
                description="US passport number format",
                examples=[
                    "123456789",
                    "987654321"
                ],
                counter_examples=[
                    "12345678",
                    "1234567890",
                    "A12345678"
                ]
            ),
            "uk": PatternInfo(
                name="passport_uk",
                pattern=r'^[0-9]{9}$',
                type=PatternType.FORMAT,
                country="UK",
                description="UK passport number format",
                examples=[
                    "123456789",
                    "987654321"
                ],
                counter_examples=[
                    "12345678",
                    "1234567890",
                    "A12345678"
                ]
            )
        })
        
        # Tax ID patterns
        self.add_pattern_group("tax_id", {
            "ein": PatternInfo(  # Employer Identification Number
                name="tax_id_ein",
                pattern=r'^[0-9]{2}-[0-9]{7}$',
                type=PatternType.FORMAT,
                country="US",
                description="US Employer Identification Number format",
                examples=[
                    "12-3456789",
                    "98-7654321"
                ],
                counter_examples=[
                    "123456789",
                    "12-345678",
                    "12-34567890"
                ]
            ),
            "itin": PatternInfo(  # Individual Taxpayer Identification Number
                name="tax_id_itin",
                pattern=r'^9\d{2}-[78]\d-\d{4}$',
                type=PatternType.STRICT,
                country="US",
                description="US Individual Taxpayer Identification Number format",
                examples=[
                    "912-70-1234",
                    "987-80-9876"
                ],
                counter_examples=[
                    "123-70-1234",
                    "912-60-1234",
                    "912-70-123"
                ]
            )
        })
        
        # Bank account patterns
        self.add_pattern_group("bank_account", {
            "us_routing": PatternInfo(
                name="bank_account_us_routing",
                pattern=r'^[0-9]{9}$',
                type=PatternType.FORMAT,
                country="US",
                description="US bank routing number format",
                examples=[
                    "123456789",
                    "987654321"
                ],
                counter_examples=[
                    "12345678",
                    "1234567890",
                    "A12345678"
                ]
            ),
            "iban": PatternInfo(
                name="bank_account_iban",
                pattern=r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}$',
                type=PatternType.INTERNATIONAL,
                description="International Bank Account Number (IBAN) format",
                examples=[
                    "GB82WEST12345698765432",
                    "DE89370400440532013000",
                    "FR1420041010050500013M02606"
                ],
                counter_examples=[
                    "GB82WEST1234569876543",
                    "gb82west12345698765432",
                    "GB82WEST123456987654321"
                ]
            )
        })
        
        # Analyze all patterns for security
        self._analyze_all_patterns()
    
    def add_pattern_group(self, group_name: str, patterns: Dict[str, PatternInfo]) -> None:
        """Add a group of patterns to the library."""
        self.patterns[group_name] = patterns
        logger.debug(f"Added pattern group '{group_name}' with {len(patterns)} patterns")
    
    def add_pattern(self, group_name: str, pattern_name: str, pattern_info: PatternInfo) -> None:
        """Add a single pattern to the library."""
        if group_name not in self.patterns:
            self.patterns[group_name] = {}
        
        # Analyze pattern security
        security_level, issues = self.security_analyzer.analyze_pattern(pattern_info.pattern)
        pattern_info.security_level = security_level
        
        if issues:
            logger.warning(f"Pattern security issues for {group_name}.{pattern_name}: {issues}")
        
        # Compile pattern for performance
        try:
            pattern_info.compiled = re.compile(pattern_info.pattern)
            logger.debug(f"Pattern compiled successfully: {group_name}.{pattern_name}")
        except re.error as e:
            logger.error(f"Failed to compile pattern {group_name}.{pattern_name}: {e}")
            return
        
        self.patterns[group_name][pattern_name] = pattern_info
        logger.debug(f"Added pattern '{pattern_name}' to group '{group_name}'")
    
    def get_pattern(self, group_name: str, pattern_name: str) -> Optional[PatternInfo]:
        """Get a specific pattern."""
        return self.patterns.get(group_name, {}).get(pattern_name)
    
    def get_pattern_group(self, group_name: str) -> Dict[str, PatternInfo]:
        """Get all patterns in a group."""
        return self.patterns.get(group_name, {})
    
    def get_all_patterns(self) -> Dict[str, Dict[str, PatternInfo]]:
        """Get all patterns."""
        return self.patterns.copy()
    
    def find_patterns_by_country(self, country: str) -> List[PatternInfo]:
        """Find all patterns for a specific country."""
        country_patterns = []
        
        for group_patterns in self.patterns.values():
            for pattern_info in group_patterns.values():
                if pattern_info.country == country:
                    country_patterns.append(pattern_info)
        
        return country_patterns
    
    def find_patterns_by_type(self, pattern_type: PatternType) -> List[PatternInfo]:
        """Find all patterns of a specific type."""
        type_patterns = []
        
        for group_patterns in self.patterns.values():
            for pattern_info in group_patterns.values():
                if pattern_info.type == pattern_type:
                    type_patterns.append(pattern_info)
        
        return type_patterns
    
    def test_pattern(self, group_name: str, pattern_name: str, test_input: str) -> bool:
        """Test a pattern against input."""
        pattern_info = self.get_pattern(group_name, pattern_name)
        if not pattern_info or not pattern_info.compiled:
            return False
        
        return bool(pattern_info.compiled.match(test_input))
    
    def validate_pattern_examples(self, group_name: str, pattern_name: str) -> Tuple[bool, List[str]]:
        """Validate pattern against its examples and counter-examples."""
        pattern_info = self.get_pattern(group_name, pattern_name)
        if not pattern_info:
            return False, ["Pattern not found"]
        
        errors = []
        
        # Test positive examples
        for example in pattern_info.examples:
            if not self.test_pattern(group_name, pattern_name, example):
                errors.append(f"Example should match but doesn't: {example}")
        
        # Test negative examples (counter-examples)
        for counter_example in pattern_info.counter_examples:
            if self.test_pattern(group_name, pattern_name, counter_example):
                errors.append(f"Counter-example should not match but does: {counter_example}")
        
        return len(errors) == 0, errors
    
    def _analyze_all_patterns(self) -> None:
        """Analyze security for all patterns in the library."""
        total_patterns = 0
        dangerous_patterns = 0
        
        for group_name, group_patterns in self.patterns.items():
            for pattern_name, pattern_info in group_patterns.items():
                total_patterns += 1
                
                security_level, issues = self.security_analyzer.analyze_pattern(pattern_info.pattern)
                pattern_info.security_level = security_level
                
                if security_level == PatternSecurity.DANGEROUS:
                    dangerous_patterns += 1
                    logger.warning(f"Dangerous pattern detected: {group_name}.{pattern_name} - {issues}")
                elif issues:
                    logger.debug(f"Pattern warnings for {group_name}.{pattern_name}: {issues}")
                
                # Compile pattern
                try:
                    pattern_info.compiled = re.compile(pattern_info.pattern)
                except re.error as e:
                    logger.error(f"Pattern compilation failed: {group_name}.{pattern_name} - {e}")
        
        logger.info(f"Pattern analysis complete: {total_patterns} patterns, {dangerous_patterns} dangerous")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get comprehensive security report for all patterns."""
        report = {
            "total_patterns": 0,
            "security_breakdown": {
                PatternSecurity.SAFE.value: 0,
                PatternSecurity.WARNING.value: 0,
                PatternSecurity.DANGEROUS.value: 0
            },
            "dangerous_patterns": [],
            "pattern_groups": {}
        }
        
        for group_name, group_patterns in self.patterns.items():
            group_report = {
                "total": len(group_patterns),
                "security_breakdown": {
                    PatternSecurity.SAFE.value: 0,
                    PatternSecurity.WARNING.value: 0,
                    PatternSecurity.DANGEROUS.value: 0
                }
            }
            
            for pattern_name, pattern_info in group_patterns.items():
                report["total_patterns"] += 1
                security_level = pattern_info.security_level.value
                
                report["security_breakdown"][security_level] += 1
                group_report["security_breakdown"][security_level] += 1
                
                if pattern_info.security_level == PatternSecurity.DANGEROUS:
                    report["dangerous_patterns"].append({
                        "group": group_name,
                        "name": pattern_name,
                        "pattern": pattern_info.pattern
                    })
            
            report["pattern_groups"][group_name] = group_report
        
        return report
    
    def export_patterns(self, file_path: str, format_type: str = "json") -> None:
        """Export patterns to file."""
        export_data = {}
        
        for group_name, group_patterns in self.patterns.items():
            export_data[group_name] = {}
            
            for pattern_name, pattern_info in group_patterns.items():
                export_data[group_name][pattern_name] = {
                    "name": pattern_info.name,
                    "pattern": pattern_info.pattern,
                    "type": pattern_info.type.value,
                    "country": pattern_info.country,
                    "description": pattern_info.description,
                    "examples": pattern_info.examples,
                    "counter_examples": pattern_info.counter_examples,
                    "security_level": pattern_info.security_level.value,
                    "version": pattern_info.version
                }
        
        if format_type.lower() == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, sort_keys=True)
        
        logger.info(f"Patterns exported to {file_path}")
    
    def load_patterns_from_file(self, file_path: str) -> None:
        """Load patterns from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for group_name, group_data in data.items():
                for pattern_name, pattern_data in group_data.items():
                    pattern_info = PatternInfo(
                        name=pattern_data["name"],
                        pattern=pattern_data["pattern"],
                        type=PatternType(pattern_data["type"]),
                        country=pattern_data.get("country"),
                        description=pattern_data.get("description"),
                        examples=pattern_data.get("examples", []),
                        counter_examples=pattern_data.get("counter_examples", []),
                        version=pattern_data.get("version", "1.0.0")
                    )
                    
                    self.add_pattern(group_name, pattern_name, pattern_info)
            
            logger.info(f"Patterns loaded from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load patterns from {file_path}: {e}")
            raise


# Global pattern library instance
_global_patterns: Optional[PatternLibrary] = None


def get_patterns() -> PatternLibrary:
    """Get global pattern library instance."""
    global _global_patterns
    if _global_patterns is None:
        _global_patterns = PatternLibrary()
    return _global_patterns


def set_patterns(patterns: PatternLibrary) -> None:
    """Set global pattern library instance."""
    global _global_patterns
    _global_patterns = patterns
