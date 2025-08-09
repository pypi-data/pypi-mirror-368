"""
Composite Validator
==================

This module implements a composite validator that combines multiple validators
and validation rules for complex multi-field validation scenarios.

Features:
- Multi-field validation with cross-field dependencies
- Business rule validation with conditional logic
- Validator chaining and composition
- Custom validation functions and lambdas
- Field mapping and transformation
- Validation result aggregation
- Complex validation workflows

Examples:
    >>> from pyidverify.validators.custom.composite_validator import CompositeValidator
    >>> from pyidverify.validators.personal.email_validator import EmailValidator
    >>> from pyidverify.validators.personal.phone_validator import PhoneValidator
    >>> 
    >>> # Create composite validator for user registration
    >>> validator = CompositeValidator([
    ...     EmailValidator(),
    ...     PhoneValidator()
    ... ])
    >>> 
    >>> # Validate multiple fields
    >>> result = validator.validate({
    ...     'email': 'user@example.com',
    ...     'phone': '+1-555-123-4567'
    ... })
    >>> 
    >>> # Custom business rule validation
    >>> def validate_age_email_consistency(data):
    ...     age = data.get('age', 0)
    ...     email = data.get('email', '')
    ...     if age < 18 and '@business.com' in email:
    ...         return False, "Business email not allowed for minors"
    ...     return True, None
    >>> 
    >>> validator.add_business_rule('age_email_check', validate_age_email_consistency)

Business Rules Support:
- Cross-field validation logic
- Conditional validation based on field values
- Custom business constraints
- Data consistency checks
- Regulatory compliance rules
"""

from typing import Optional, Dict, Any, List, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import json
from pathlib import Path

try:
    from ...core.base_validator import BaseValidator
    from ...core.types import ValidationResult, ValidationLevel
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

class ValidationStrategy(Enum):
    """Strategy for handling multiple validation results"""
    ALL_MUST_PASS = "all_must_pass"           # All validators must pass
    ANY_CAN_PASS = "any_can_pass"             # At least one validator must pass
    MAJORITY_MUST_PASS = "majority_must_pass" # Majority of validators must pass
    WEIGHTED_AVERAGE = "weighted_average"      # Weighted average of confidence scores
    FIRST_PASS = "first_pass"                 # Stop at first passing validator
    ALL_EXECUTE = "all_execute"               # Execute all, aggregate results

class FieldValidationRule:
    """Represents a validation rule for a specific field"""
    
    def __init__(self, 
                 field_name: str, 
                 validator: BaseValidator,
                 required: bool = True,
                 transform_func: Optional[Callable[[Any], Any]] = None,
                 weight: float = 1.0,
                 condition_func: Optional[Callable[[Dict[str, Any]], bool]] = None):
        """
        Initialize field validation rule.
        
        Args:
            field_name: Name of the field to validate
            validator: Validator instance to use
            required: Whether the field is required
            transform_func: Optional function to transform field value before validation
            weight: Weight for this validation in composite scoring
            condition_func: Optional function to determine if validation should run
        """
        self.field_name = field_name
        self.validator = validator
        self.required = required
        self.transform_func = transform_func
        self.weight = weight
        self.condition_func = condition_func
    
    def should_validate(self, data: Dict[str, Any]) -> bool:
        """Check if this rule should be applied"""
        if self.condition_func:
            return self.condition_func(data)
        return True
    
    def get_field_value(self, data: Dict[str, Any]) -> Any:
        """Get and optionally transform field value"""
        value = data.get(self.field_name)
        
        if self.transform_func and value is not None:
            value = self.transform_func(value)
        
        return value

class BusinessRule:
    """Represents a custom business validation rule"""
    
    def __init__(self, 
                 name: str,
                 rule_func: Callable[[Dict[str, Any]], Tuple[bool, Optional[str]]],
                 description: str = "",
                 weight: float = 1.0,
                 critical: bool = False):
        """
        Initialize business rule.
        
        Args:
            name: Unique name for the rule
            rule_func: Function that takes data dict and returns (is_valid, error_message)
            description: Human-readable description
            weight: Weight in overall validation scoring
            critical: If True, failure of this rule fails entire validation
        """
        self.name = name
        self.rule_func = rule_func
        self.description = description
        self.weight = weight
        self.critical = critical
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Execute the business rule.
        
        Args:
            data: Data dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message, metadata)
        """
        try:
            start_time = time.time()
            is_valid, error_message = self.rule_func(data)
            execution_time = (time.time() - start_time) * 1000
            
            metadata = {
                'rule_name': self.name,
                'execution_time': execution_time,
                'critical': self.critical,
                'weight': self.weight
            }
            
            return is_valid, error_message, metadata
            
        except Exception as e:
            return False, f"Business rule error: {str(e)}", {
                'rule_name': self.name,
                'error': str(e),
                'critical': self.critical
            }

@dataclass
class CompositeValidationResult:
    """Result of composite validation with detailed breakdown"""
    is_valid: bool
    overall_confidence: float
    field_results: Dict[str, ValidationResult] = field(default_factory=dict)
    business_rule_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    failed_fields: List[str] = field(default_factory=list)
    failed_business_rules: List[str] = field(default_factory=list)
    validation_strategy: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

class CompositeValidator:
    """
    Composite validator for multi-field and business rule validation.
    
    This validator combines multiple field validators and business rules to
    perform complex validation scenarios with configurable strategies.
    """
    
    def __init__(self, 
                 field_rules: Optional[List[FieldValidationRule]] = None,
                 validation_strategy: ValidationStrategy = ValidationStrategy.ALL_MUST_PASS,
                 name: str = "CompositeValidator"):
        """
        Initialize composite validator.
        
        Args:
            field_rules: List of field validation rules
            validation_strategy: Strategy for combining validation results
            name: Name for this composite validator
        """
        if _IMPORTS_AVAILABLE:
            self.audit_logger = AuditLogger("composite_validator")
            self.rate_limiter = RateLimiter(max_requests=500, time_window=3600)
            self.result_cache = LRUCache(maxsize=100)
        
        self.field_rules = field_rules or []
        self.business_rules: Dict[str, BusinessRule] = {}
        self.validation_strategy = validation_strategy
        self.name = name
        
        # Performance tracking
        self.validation_count = 0
        self.total_execution_time = 0.0
        
        # Field mapping for aliases
        self.field_aliases: Dict[str, str] = {}
    
    def add_field_rule(self, rule: FieldValidationRule) -> None:
        """Add a field validation rule"""
        self.field_rules.append(rule)
    
    def add_business_rule(self, name: str, rule_func: Callable[[Dict[str, Any]], Tuple[bool, Optional[str]]],
                         description: str = "", weight: float = 1.0, critical: bool = False) -> None:
        """
        Add a business validation rule.
        
        Args:
            name: Unique name for the rule
            rule_func: Function that validates business logic
            description: Description of the rule
            weight: Weight in overall scoring
            critical: If True, failure fails entire validation
        """
        rule = BusinessRule(name, rule_func, description, weight, critical)
        self.business_rules[name] = rule
    
    def add_field_alias(self, alias: str, field_name: str) -> None:
        """Add field name alias for flexible field mapping"""
        self.field_aliases[alias] = field_name
    
    def remove_business_rule(self, name: str) -> bool:
        """Remove a business rule by name"""
        if name in self.business_rules:
            del self.business_rules[name]
            return True
        return False
    
    def validate(self, data: Dict[str, Any], 
                validation_level: ValidationLevel = None) -> CompositeValidationResult:
        """
        Validate data using composite rules and strategy.
        
        Args:
            data: Dictionary of data to validate
            validation_level: Level of validation to perform
            
        Returns:
            CompositeValidationResult with detailed results
        """
        start_time = time.time()
        
        try:
            # Rate limiting check
            if _IMPORTS_AVAILABLE and not self.rate_limiter.allow_request("composite_validation"):
                raise SecurityError("Rate limit exceeded for composite validation")
            
            # Input validation
            if not isinstance(data, dict):
                return CompositeValidationResult(
                    is_valid=False,
                    overall_confidence=0.0,
                    errors=["Input must be a dictionary"]
                )
            
            # Resolve field aliases
            resolved_data = self._resolve_aliases(data)
            
            # Check cache
            cache_key = self._generate_cache_key(resolved_data)
            if _IMPORTS_AVAILABLE:
                cached_result = self.result_cache.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Validate individual fields
            field_results = self._validate_fields(resolved_data, validation_level)
            
            # Validate business rules
            business_rule_results = self._validate_business_rules(resolved_data)
            
            # Apply validation strategy
            overall_result = self._apply_validation_strategy(field_results, business_rule_results)
            
            # Create composite result
            result = CompositeValidationResult(
                is_valid=overall_result['is_valid'],
                overall_confidence=overall_result['confidence'],
                field_results=field_results,
                business_rule_results=business_rule_results,
                failed_fields=overall_result['failed_fields'],
                failed_business_rules=overall_result['failed_business_rules'],
                validation_strategy=self.validation_strategy.value,
                metadata={
                    'validation_time': (time.time() - start_time) * 1000,
                    'total_fields': len(self.field_rules),
                    'total_business_rules': len(self.business_rules),
                    'strategy': self.validation_strategy.value,
                    'data_keys': list(resolved_data.keys())
                },
                errors=overall_result['errors']
            )
            
            # Cache result
            if _IMPORTS_AVAILABLE:
                self.result_cache.set(cache_key, result)
            
            # Update performance tracking
            self.validation_count += 1
            self.total_execution_time += (time.time() - start_time) * 1000
            
            # Audit logging
            if _IMPORTS_AVAILABLE:
                self.audit_logger.log_validation(
                    "composite", self.name, result.is_valid, result.metadata
                )
            
            return result
            
        except Exception as e:
            return CompositeValidationResult(
                is_valid=False,
                overall_confidence=0.0,
                errors=[f"Composite validation error: {str(e)}"],
                metadata={
                    'validation_time': (time.time() - start_time) * 1000,
                    'error': str(e)
                }
            )
    
    def _resolve_aliases(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve field aliases to actual field names"""
        resolved = {}
        
        for key, value in data.items():
            actual_key = self.field_aliases.get(key, key)
            resolved[actual_key] = value
        
        return resolved
    
    def _validate_fields(self, data: Dict[str, Any], 
                        validation_level: ValidationLevel) -> Dict[str, ValidationResult]:
        """Validate all field rules"""
        field_results = {}
        
        for rule in self.field_rules:
            try:
                # Check if rule should be applied
                if not rule.should_validate(data):
                    continue
                
                # Get field value
                field_value = rule.get_field_value(data)
                
                # Check if required field is missing
                if field_value is None:
                    if rule.required:
                        field_results[rule.field_name] = ValidationResult(
                            is_valid=False,
                            id_type="composite_field",
                            confidence=0.0,
                            errors=[f"Required field '{rule.field_name}' is missing"]
                        )
                    continue
                
                # Validate field
                result = rule.validator.validate(field_value, validation_level)
                
                # Add rule metadata
                result.metadata.update({
                    'field_name': rule.field_name,
                    'required': rule.required,
                    'weight': rule.weight,
                    'validator_type': type(rule.validator).__name__
                })
                
                field_results[rule.field_name] = result
                
            except Exception as e:
                field_results[rule.field_name] = ValidationResult(
                    is_valid=False,
                    id_type="composite_field",
                    confidence=0.0,
                    errors=[f"Field validation error: {str(e)}"]
                )
        
        return field_results
    
    def _validate_business_rules(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Validate all business rules"""
        business_results = {}
        
        for rule_name, rule in self.business_rules.items():
            try:
                is_valid, error_message, metadata = rule.validate(data)
                
                business_results[rule_name] = {
                    'is_valid': is_valid,
                    'error_message': error_message,
                    'metadata': metadata,
                    'critical': rule.critical,
                    'weight': rule.weight
                }
                
            except Exception as e:
                business_results[rule_name] = {
                    'is_valid': False,
                    'error_message': f"Business rule execution error: {str(e)}",
                    'metadata': {'error': str(e)},
                    'critical': rule.critical,
                    'weight': rule.weight
                }
        
        return business_results
    
    def _apply_validation_strategy(self, field_results: Dict[str, ValidationResult],
                                 business_rule_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Apply the configured validation strategy"""
        failed_fields = [name for name, result in field_results.items() if not result.is_valid]
        failed_business_rules = [name for name, result in business_rule_results.items() 
                               if not result['is_valid']]
        
        # Check for critical business rule failures
        critical_failures = [name for name, result in business_rule_results.items() 
                           if not result['is_valid'] and result['critical']]
        
        if critical_failures:
            return {
                'is_valid': False,
                'confidence': 0.0,
                'failed_fields': failed_fields,
                'failed_business_rules': failed_business_rules,
                'errors': [f"Critical business rule failed: {', '.join(critical_failures)}"]
            }
        
        if self.validation_strategy == ValidationStrategy.ALL_MUST_PASS:
            is_valid = len(failed_fields) == 0 and len(failed_business_rules) == 0
            confidence = 1.0 if is_valid else 0.0
            
        elif self.validation_strategy == ValidationStrategy.ANY_CAN_PASS:
            is_valid = len(failed_fields) < len(field_results) or len(failed_business_rules) < len(business_rule_results)
            confidence = 1.0 if is_valid else 0.0
            
        elif self.validation_strategy == ValidationStrategy.MAJORITY_MUST_PASS:
            total_validations = len(field_results) + len(business_rule_results)
            failed_validations = len(failed_fields) + len(failed_business_rules)
            is_valid = failed_validations < (total_validations / 2)
            confidence = 1.0 - (failed_validations / total_validations) if total_validations > 0 else 0.0
            
        elif self.validation_strategy == ValidationStrategy.WEIGHTED_AVERAGE:
            total_weight = 0.0
            weighted_score = 0.0
            
            # Add field weights and scores
            for rule in self.field_rules:
                if rule.field_name in field_results:
                    result = field_results[rule.field_name]
                    total_weight += rule.weight
                    if result.is_valid:
                        weighted_score += rule.weight * result.confidence
            
            # Add business rule weights and scores
            for rule in self.business_rules.values():
                if rule.name in business_rule_results:
                    result = business_rule_results[rule.name]
                    total_weight += rule.weight
                    if result['is_valid']:
                        weighted_score += rule.weight
            
            confidence = weighted_score / total_weight if total_weight > 0 else 0.0
            is_valid = confidence >= 0.7  # Configurable threshold
            
        elif self.validation_strategy == ValidationStrategy.FIRST_PASS:
            # Check fields first
            is_valid = False
            confidence = 0.0
            
            for rule in self.field_rules:
                if rule.field_name in field_results:
                    result = field_results[rule.field_name]
                    if result.is_valid:
                        is_valid = True
                        confidence = result.confidence
                        break
            
            # Check business rules if no field passed
            if not is_valid:
                for rule_name, result in business_rule_results.items():
                    if result['is_valid']:
                        is_valid = True
                        confidence = 1.0
                        break
        
        else:  # ALL_EXECUTE (default fallback)
            is_valid = len(failed_fields) == 0 and len(failed_business_rules) == 0
            confidence = 1.0 if is_valid else 0.0
        
        errors = []
        if failed_fields:
            errors.append(f"Failed field validation: {', '.join(failed_fields)}")
        if failed_business_rules:
            errors.append(f"Failed business rules: {', '.join(failed_business_rules)}")
        
        return {
            'is_valid': is_valid,
            'confidence': confidence,
            'failed_fields': failed_fields,
            'failed_business_rules': failed_business_rules,
            'errors': errors
        }
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate cache key for validation data"""
        # Sort keys for consistent hashing
        sorted_items = sorted(data.items())
        return str(hash(tuple(sorted_items)))
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation rules and configuration"""
        return {
            'name': self.name,
            'validation_strategy': self.validation_strategy.value,
            'field_rules': [
                {
                    'field_name': rule.field_name,
                    'validator_type': type(rule.validator).__name__,
                    'required': rule.required,
                    'weight': rule.weight,
                    'has_condition': rule.condition_func is not None,
                    'has_transform': rule.transform_func is not None
                }
                for rule in self.field_rules
            ],
            'business_rules': [
                {
                    'name': rule.name,
                    'description': rule.description,
                    'weight': rule.weight,
                    'critical': rule.critical
                }
                for rule in self.business_rules.values()
            ],
            'field_aliases': self.field_aliases,
            'performance_stats': {
                'validation_count': self.validation_count,
                'average_execution_time': (self.total_execution_time / self.validation_count 
                                         if self.validation_count > 0 else 0),
                'cache_hits': self.result_cache.hits if _IMPORTS_AVAILABLE else 0,
                'cache_misses': self.result_cache.misses if _IMPORTS_AVAILABLE else 0
            }
        }
    
    def configure_strategy(self, strategy: ValidationStrategy) -> None:
        """Change validation strategy"""
        self.validation_strategy = strategy
        
        # Clear cache when strategy changes
        if _IMPORTS_AVAILABLE:
            self.result_cache.clear()

# Utility functions for common validation scenarios

def create_user_registration_validator() -> CompositeValidator:
    """Create a composite validator for user registration"""
    # This would be implemented with actual validators once they're available
    validator = CompositeValidator(name="UserRegistration")
    
    # Add business rule example
    def check_age_consistency(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        age = data.get('age', 0)
        birth_year = data.get('birth_year', 0)
        current_year = 2024  # Would use actual current year
        
        if birth_year > 0:
            calculated_age = current_year - birth_year
            if abs(calculated_age - age) > 1:  # Allow 1 year variance
                return False, "Age and birth year are inconsistent"
        
        return True, None
    
    validator.add_business_rule(
        "age_birth_year_consistency",
        check_age_consistency,
        "Validates consistency between age and birth year",
        weight=1.0,
        critical=False
    )
    
    return validator

def create_financial_profile_validator() -> CompositeValidator:
    """Create a composite validator for financial profiles"""
    validator = CompositeValidator(name="FinancialProfile")
    
    # Business rule for income-expense validation
    def validate_income_expense_ratio(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        income = data.get('monthly_income', 0)
        expenses = data.get('monthly_expenses', 0)
        
        if income > 0 and expenses > income * 1.5:
            return False, "Monthly expenses exceed 150% of reported income"
        
        return True, None
    
    validator.add_business_rule(
        "income_expense_ratio",
        validate_income_expense_ratio,
        "Validates reasonable income to expense ratio",
        weight=2.0,
        critical=False
    )
    
    return validator

# Export public interface
__all__ = [
    "CompositeValidator",
    "CompositeValidationResult",
    "FieldValidationRule",
    "BusinessRule",
    "ValidationStrategy",
    "create_user_registration_validator",
    "create_financial_profile_validator"
]
