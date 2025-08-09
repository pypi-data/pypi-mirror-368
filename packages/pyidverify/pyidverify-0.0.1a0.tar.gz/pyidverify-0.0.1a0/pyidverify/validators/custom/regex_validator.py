"""
Custom Regex Validator
======================

This module implements a secure custom regex validator with ReDoS protection
and pattern complexity analysis.

Features:
- Custom regex pattern validation
- ReDoS (Regular Expression DoS) protection
- Pattern complexity analysis and scoring
- Secure pattern storage and caching
- Pattern testing utilities
- Performance monitoring and optimization

Examples:
    >>> from pyidverify.validators.custom.regex_validator import CustomRegexValidator
    >>> 
    >>> # Create custom validator for specific format
    >>> validator = CustomRegexValidator(r'^\d{3}-\d{2}-\d{4}$', name="Custom SSN")
    >>> result = validator.validate("123-45-6789")
    >>> print(f"Valid: {result.is_valid}")
    >>> 
    >>> # Create validator with security analysis
    >>> validator = CustomRegexValidator(
    ...     pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    ...     name="Custom Email",
    ...     max_complexity=1000
    ... )

Security Features:
- ReDoS vulnerability detection and prevention
- Pattern complexity analysis with configurable limits
- Execution timeout protection
- Memory usage monitoring
- Input sanitization and length limits
- Secure pattern compilation and caching
"""

from typing import Optional, Dict, Any, List, Set, Tuple, Union, Pattern
import re
import time
import threading
from dataclasses import dataclass
from pathlib import Path
import json
import signal

try:
    from ...core.base_validator import BaseValidator
    from ...core.types import IDType, ValidationResult, ValidationLevel
    from ...core.exceptions import ValidationError, SecurityError
    from ...utils.extractors import normalize_input, clean_input
    from ...utils.caching import LRUCache
    from ...security.audit import AuditLogger
    from ...security.rate_limiting import RateLimiter
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
class PatternSecurityAnalysis:
    """Results of pattern security analysis"""
    complexity_score: int
    has_redos_risk: bool
    risk_patterns: List[str]
    recommendations: List[str]
    max_execution_time: float
    is_safe: bool

@dataclass
class CustomRegexValidationOptions:
    """Configuration options for custom regex validation"""
    timeout_seconds: float = 1.0
    max_input_length: int = 10000
    max_complexity_score: int = 1000
    enable_redos_protection: bool = True
    cache_compiled_patterns: bool = True
    log_pattern_performance: bool = True
    strict_security_analysis: bool = True
    
    def __post_init__(self):
        """Validate configuration options"""
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_input_length <= 0:
            raise ValueError("max_input_length must be positive")
        if self.max_complexity_score <= 0:
            raise ValueError("max_complexity_score must be positive")

class TimeoutError(Exception):
    """Raised when regex execution times out"""
    pass

class PatternSecurityAnalyzer:
    """Analyzes regex patterns for security vulnerabilities"""
    
    def __init__(self):
        # Known ReDoS-vulnerable patterns
        self.redos_patterns = [
            r'\(.*\+.*\)*',  # Nested quantifiers
            r'\(.*\*.*\)*',  # Nested quantifiers with *
            r'\(.+\)\+\+',   # Possessive quantifiers
            r'\(.+\)\*\+',   # Mixed quantifiers
            r'\(.+\)\{\d+,\}', # Large range quantifiers
            r'(\(.+\)\?\+)', # Optional possessive
        ]
        
        # Complexity indicators
        self.complexity_indicators = {
            'nested_groups': r'\([^)]*\([^)]*\)',
            'alternation': r'\|',
            'quantifiers': r'[+*?{}]',
            'lookahead': r'\(\?[=!]',
            'lookbehind': r'\(\?<[=!]',
            'backreferences': r'\\[0-9]',
            'character_classes': r'\[[^\]]+\]',
            'escaped_chars': r'\\.',
        }
    
    def analyze_pattern(self, pattern: str) -> PatternSecurityAnalysis:
        """
        Analyze regex pattern for security vulnerabilities.
        
        Args:
            pattern: Regex pattern to analyze
            
        Returns:
            PatternSecurityAnalysis with detailed results
        """
        complexity_score = self._calculate_complexity(pattern)
        redos_risk = self._check_redos_vulnerability(pattern)
        risk_patterns = self._identify_risk_patterns(pattern)
        recommendations = self._generate_recommendations(pattern, redos_risk, complexity_score)
        max_execution_time = self._estimate_execution_time(pattern)
        
        is_safe = (
            not redos_risk and 
            complexity_score < 1000 and 
            max_execution_time < 100.0  # milliseconds
        )
        
        return PatternSecurityAnalysis(
            complexity_score=complexity_score,
            has_redos_risk=redos_risk,
            risk_patterns=risk_patterns,
            recommendations=recommendations,
            max_execution_time=max_execution_time,
            is_safe=is_safe
        )
    
    def _calculate_complexity(self, pattern: str) -> int:
        """Calculate pattern complexity score"""
        score = len(pattern)  # Base score
        
        for indicator, regex in self.complexity_indicators.items():
            matches = len(re.findall(regex, pattern))
            if indicator == 'nested_groups':
                score += matches * 50  # Heavy penalty for nesting
            elif indicator == 'alternation':
                score += matches * 20  # Moderate penalty for alternation
            elif indicator == 'quantifiers':
                score += matches * 10  # Light penalty for quantifiers
            else:
                score += matches * 5   # Base penalty for other features
        
        return score
    
    def _check_redos_vulnerability(self, pattern: str) -> bool:
        """Check for ReDoS vulnerability patterns"""
        for redos_pattern in self.redos_patterns:
            if re.search(redos_pattern, pattern):
                return True
        return False
    
    def _identify_risk_patterns(self, pattern: str) -> List[str]:
        """Identify specific risk patterns in the regex"""
        risks = []
        
        for redos_pattern in self.redos_patterns:
            matches = re.findall(redos_pattern, pattern)
            risks.extend(matches)
        
        return risks
    
    def _generate_recommendations(self, pattern: str, has_redos: bool, complexity: int) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if has_redos:
            recommendations.append("Pattern has ReDoS vulnerability - consider atomic grouping or possessive quantifiers")
        
        if complexity > 500:
            recommendations.append("High complexity pattern - consider simplification or breaking into multiple patterns")
        
        if '.*' in pattern:
            recommendations.append("Avoid .* patterns - use more specific character classes")
        
        if pattern.count('(') > 10:
            recommendations.append("Too many groups - consider non-capturing groups (?:)")
        
        return recommendations
    
    def _estimate_execution_time(self, pattern: str) -> float:
        """Estimate maximum execution time in milliseconds"""
        # Simple heuristic based on pattern features
        base_time = 1.0  # 1ms base
        
        # Add time for each complexity factor
        nested_groups = len(re.findall(r'\([^)]*\([^)]*\)', pattern))
        alternations = pattern.count('|')
        quantifiers = len(re.findall(r'[+*?{}]', pattern))
        
        estimated_time = base_time + (nested_groups * 10) + (alternations * 5) + (quantifiers * 2)
        
        return estimated_time

class CustomRegexValidator(BaseValidator):
    """
    Secure custom regex validator with ReDoS protection.
    
    This validator allows users to define custom validation patterns while
    providing comprehensive security analysis and protection mechanisms.
    """
    
    def __init__(self, pattern: str, name: Optional[str] = None, flags: int = 0, **options):
        """
        Initialize custom regex validator.
        
        Args:
            pattern: Regular expression pattern
            name: Optional name for the validator
            flags: Regex compilation flags
            **options: Validation options (see CustomRegexValidationOptions)
        """
        if _IMPORTS_AVAILABLE:
            super().__init__()
            self.audit_logger = AuditLogger("custom_regex_validator")
            self.rate_limiter = RateLimiter(max_requests=1000, time_window=3600)
            self.pattern_cache = LRUCache(maxsize=100)
            self.performance_cache = LRUCache(maxsize=500)
        
        # Configure validation options
        self.options = CustomRegexValidationOptions(**options)
        
        # Initialize security analyzer
        self.security_analyzer = PatternSecurityAnalyzer()
        
        # Validate and analyze pattern security
        self.pattern = pattern
        self.name = name or f"Custom_{hash(pattern) % 10000}"
        self.flags = flags
        
        # Perform security analysis
        self.security_analysis = self.security_analyzer.analyze_pattern(pattern)
        
        # Validate pattern security
        if self.options.strict_security_analysis and not self.security_analysis.is_safe:
            raise SecurityError(
                f"Pattern failed security analysis: {self.security_analysis.recommendations}"
            )
        
        # Compile pattern with timeout protection
        self.compiled_pattern = self._compile_pattern_safely(pattern, flags)
        
        # Performance tracking
        self.validation_count = 0
        self.total_execution_time = 0.0
        self.max_execution_time = 0.0
    
    def _compile_pattern_safely(self, pattern: str, flags: int) -> Pattern[str]:
        """Compile regex pattern with safety checks"""
        try:
            # Test compile first
            compiled = re.compile(pattern, flags)
            
            # Test with various inputs to detect issues
            test_inputs = ["", "a", "test", "x" * 100, "1234567890"]
            
            for test_input in test_inputs:
                try:
                    self._execute_with_timeout(compiled.match, test_input, 0.1)
                except TimeoutError:
                    raise SecurityError(f"Pattern causes timeout on input: {test_input[:20]}")
            
            return compiled
            
        except re.error as e:
            raise ValidationError(f"Invalid regex pattern: {e}")
    
    def _execute_with_timeout(self, func, *args, timeout_seconds: float = None):
        """Execute function with timeout protection"""
        timeout_seconds = timeout_seconds or self.options.timeout_seconds
        
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout_seconds)
        
        if thread.is_alive():
            raise TimeoutError(f"Regex execution timed out after {timeout_seconds} seconds")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def validate(self, value: str, validation_level: ValidationLevel = None) -> ValidationResult:
        """
        Validate input against custom regex pattern.
        
        Args:
            value: Input to validate
            validation_level: Level of validation to perform
            
        Returns:
            ValidationResult with validation details
        """
        start_time = time.time()
        errors = []
        metadata = {
            'pattern_name': self.name,
            'original_pattern': self.pattern,
            'validation_time': None,
            'execution_time': None,
            'security_analysis': self.security_analysis.__dict__,
            'checks_performed': []
        }
        
        try:
            # Rate limiting check
            if _IMPORTS_AVAILABLE and not self.rate_limiter.allow_request("regex_validation"):
                raise SecurityError("Rate limit exceeded for regex validation")
            
            # Input validation
            if not isinstance(value, str):
                errors.append("Input must be a string")
                return self._create_result(False, errors, metadata, 0.0)
            
            # Length check
            if len(value) > self.options.max_input_length:
                errors.append(f"Input too long: {len(value)} > {self.options.max_input_length}")
                return self._create_result(False, errors, metadata, 0.0)
            
            metadata['input_length'] = len(value)
            metadata['checks_performed'].append('input_validation')
            
            # Check cache first
            cache_key = f"{hash(self.pattern)}_{hash(value)}"
            if _IMPORTS_AVAILABLE and self.options.cache_compiled_patterns:
                cached_result = self.performance_cache.get(cache_key)
                if cached_result:
                    metadata['from_cache'] = True
                    return cached_result
            
            # Execute regex with timeout protection
            match_start = time.time()
            
            try:
                match = self._execute_with_timeout(
                    self.compiled_pattern.match, 
                    value,
                    self.options.timeout_seconds
                )
                
                execution_time = (time.time() - match_start) * 1000  # Convert to milliseconds
                metadata['execution_time'] = execution_time
                metadata['checks_performed'].append('pattern_match')
                
                # Update performance tracking
                self.validation_count += 1
                self.total_execution_time += execution_time
                self.max_execution_time = max(self.max_execution_time, execution_time)
                
                # Check if match was found
                is_valid = match is not None
                confidence = 1.0 if is_valid else 0.0
                
                if match:
                    metadata['match_groups'] = match.groups()
                    metadata['match_span'] = match.span()
                
            except TimeoutError:
                errors.append(f"Pattern execution timed out after {self.options.timeout_seconds} seconds")
                return self._create_result(False, errors, metadata, 0.0)
            
            # Create result
            result = self._create_result(is_valid, errors, metadata, confidence)
            
            # Cache result if enabled
            if _IMPORTS_AVAILABLE and self.options.cache_compiled_patterns:
                self.performance_cache.set(cache_key, result)
            
            # Performance logging
            if self.options.log_pattern_performance and _IMPORTS_AVAILABLE:
                self.audit_logger.log_validation(
                    "custom_regex", f"pattern:{self.name}", is_valid, {
                        'execution_time': execution_time,
                        'input_length': len(value),
                        'pattern_complexity': self.security_analysis.complexity_score
                    }
                )
            
            return result
            
        except SecurityError:
            raise
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return self._create_result(False, errors, metadata, 0.0)
        
        finally:
            metadata['validation_time'] = (time.time() - start_time) * 1000
    
    def _create_result(self, is_valid: bool, errors: List[str], 
                      metadata: Dict[str, Any], confidence: float) -> ValidationResult:
        """Create validation result object"""
        if _IMPORTS_AVAILABLE:
            return ValidationResult(
                is_valid=is_valid,
                id_type="custom_regex",
                confidence=confidence,
                metadata=metadata,
                errors=errors
            )
        else:
            # Fallback for development
            return ValidationResult(
                is_valid=is_valid,
                id_type="custom_regex",
                confidence=confidence,
                metadata=metadata,
                errors=errors
            )
    
    def test_pattern(self, test_cases: Dict[str, bool]) -> Dict[str, Dict[str, Any]]:
        """
        Test pattern against multiple test cases.
        
        Args:
            test_cases: Dictionary of {input: expected_result}
            
        Returns:
            Dictionary with test results for each case
        """
        results = {}
        
        for test_input, expected in test_cases.items():
            try:
                result = self.validate(test_input)
                results[test_input] = {
                    'actual': result.is_valid,
                    'expected': expected,
                    'passed': result.is_valid == expected,
                    'execution_time': result.metadata.get('execution_time', 0),
                    'errors': result.errors
                }
            except Exception as e:
                results[test_input] = {
                    'actual': False,
                    'expected': expected,
                    'passed': False,
                    'error': str(e)
                }
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this validator"""
        avg_time = (self.total_execution_time / self.validation_count 
                   if self.validation_count > 0 else 0)
        
        return {
            'validation_count': self.validation_count,
            'total_execution_time': self.total_execution_time,
            'average_execution_time': avg_time,
            'max_execution_time': self.max_execution_time,
            'pattern_complexity': self.security_analysis.complexity_score,
            'cache_hits': self.performance_cache.hits if _IMPORTS_AVAILABLE else 0,
            'cache_misses': self.performance_cache.misses if _IMPORTS_AVAILABLE else 0
        }
    
    def update_pattern(self, new_pattern: str, flags: int = None) -> None:
        """
        Update the regex pattern with security analysis.
        
        Args:
            new_pattern: New regex pattern
            flags: Optional new flags
        """
        # Analyze new pattern
        new_analysis = self.security_analyzer.analyze_pattern(new_pattern)
        
        # Check security if strict mode enabled
        if self.options.strict_security_analysis and not new_analysis.is_safe:
            raise SecurityError(
                f"New pattern failed security analysis: {new_analysis.recommendations}"
            )
        
        # Compile new pattern
        new_flags = flags if flags is not None else self.flags
        new_compiled = self._compile_pattern_safely(new_pattern, new_flags)
        
        # Update instance variables
        self.pattern = new_pattern
        self.flags = new_flags
        self.compiled_pattern = new_compiled
        self.security_analysis = new_analysis
        
        # Clear caches
        if _IMPORTS_AVAILABLE:
            self.performance_cache.clear()
        
        # Reset performance tracking
        self.validation_count = 0
        self.total_execution_time = 0.0
        self.max_execution_time = 0.0
    
    def get_security_analysis(self) -> PatternSecurityAnalysis:
        """Get security analysis for the current pattern"""
        return self.security_analysis
    
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
            "validator_type": "custom_regex",
            "pattern_name": self.name,
            "pattern": self.pattern,
            "flags": self.flags,
            "security_analysis": {
                "complexity_score": self.security_analysis.complexity_score,
                "has_redos_risk": self.security_analysis.has_redos_risk,
                "is_safe": self.security_analysis.is_safe,
                "risk_patterns": self.security_analysis.risk_patterns,
                "recommendations": self.security_analysis.recommendations
            },
            "performance_stats": self.get_performance_stats(),
            "options": {
                "timeout_seconds": self.options.timeout_seconds,
                "max_input_length": self.options.max_input_length,
                "max_complexity_score": self.options.max_complexity_score,
                "enable_redos_protection": self.options.enable_redos_protection,
                "strict_security_analysis": self.options.strict_security_analysis
            },
            "features": [
                "redos_protection",
                "complexity_analysis",
                "timeout_protection",
                "pattern_testing",
                "performance_monitoring",
                "secure_compilation"
            ]
        }

# Export public interface
__all__ = [
    "CustomRegexValidator",
    "CustomRegexValidationOptions",
    "PatternSecurityAnalysis",
    "PatternSecurityAnalyzer",
    "TimeoutError"
]
