"""
Validation Engine

Central orchestration system for all ID validators. Provides validator discovery,
registration, routing, batch processing, and comprehensive result aggregation.

Features:
- Automatic validator discovery and registration
- Intelligent validator routing based on ID type
- High-performance batch processing with load balancing
- Result aggregation and consensus scoring
- Plugin architecture for extensibility
- Comprehensive monitoring and metrics
- Advanced caching with cross-validator optimization

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Set, Union, Any, Type, Callable, Tuple
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
from collections import defaultdict
from abc import ABC, abstractmethod

from .interfaces import BaseValidator, ValidatorInfo, ConfigProvider
from .types import (
    IDType,
    ValidationLevel,
    ValidationResult,
    ValidationStatus,
    ValidationMetadata,
    SecurityFlags,
    create_validation_result,
    create_error_result
)
from .exceptions import (
    ValidationError,
    ValidatorError,
    ConfigurationError,
    EngineError,
    create_validation_error
)
from ..security.exceptions import SecurityError

# Configure logging
logger = logging.getLogger('pyidverify.core.engine')


class ValidatorRegistry:
    """
    Thread-safe validator registry with discovery and lifecycle management.
    """
    
    def __init__(self):
        self._validators: Dict[str, BaseValidator] = {}
        self._validators_by_type: Dict[IDType, List[BaseValidator]] = defaultdict(list)
        self._validator_priorities: Dict[str, int] = {}
        self._lock = asyncio.Lock()
    
    async def register(self, validator: BaseValidator, priority: int = 100) -> None:
        """
        Register a validator with the registry.
        
        Args:
            validator: Validator instance to register
            priority: Priority for validator selection (lower = higher priority)
        """
        async with self._lock:
            validator_name = validator.name
            
            # Check for conflicts
            if validator_name in self._validators:
                existing = self._validators[validator_name]
                if existing.version != validator.version:
                    logger.warning(
                        f"Replacing validator {validator_name} "
                        f"v{existing.version} with v{validator.version}"
                    )
                else:
                    logger.debug(f"Re-registering validator {validator_name}")
            
            # Register validator
            self._validators[validator_name] = validator
            self._validator_priorities[validator_name] = priority
            
            # Register by supported types
            for id_type in validator.supported_types:
                if validator not in self._validators_by_type[id_type]:
                    self._validators_by_type[id_type].append(validator)
                    # Sort by priority
                    self._validators_by_type[id_type].sort(
                        key=lambda v: self._validator_priorities.get(v.name, 100)
                    )
            
            logger.info(f"Registered validator: {validator_name} v{validator.version}")
    
    async def unregister(self, validator_name: str) -> bool:
        """
        Unregister a validator.
        
        Args:
            validator_name: Name of validator to unregister
            
        Returns:
            True if validator was removed, False if not found
        """
        async with self._lock:
            if validator_name not in self._validators:
                return False
            
            validator = self._validators.pop(validator_name)
            self._validator_priorities.pop(validator_name, None)
            
            # Remove from type mappings
            for validators_list in self._validators_by_type.values():
                if validator in validators_list:
                    validators_list.remove(validator)
            
            logger.info(f"Unregistered validator: {validator_name}")
            return True
    
    def get_validator(self, validator_name: str) -> Optional[BaseValidator]:
        """Get validator by name."""
        return self._validators.get(validator_name)
    
    def get_validators_for_type(self, id_type: IDType) -> List[BaseValidator]:
        """Get all validators that support a specific ID type."""
        return self._validators_by_type.get(id_type, []).copy()
    
    def get_best_validator_for_type(self, id_type: IDType) -> Optional[BaseValidator]:
        """Get the highest priority validator for an ID type."""
        validators = self.get_validators_for_type(id_type)
        return validators[0] if validators else None
    
    def list_validators(self) -> Dict[str, ValidatorInfo]:
        """List all registered validators."""
        return {
            name: validator.info
            for name, validator in self._validators.items()
        }
    
    def get_supported_types(self) -> Set[IDType]:
        """Get all supported ID types across all validators."""
        return set(self._validators_by_type.keys())
    
    @property
    def validator_count(self) -> int:
        """Get total number of registered validators."""
        return len(self._validators)


class ValidationStrategy(ABC):
    """Abstract base class for validation strategies."""
    
    @abstractmethod
    async def validate(
        self,
        value: str,
        id_type: Optional[IDType],
        validators: List[BaseValidator],
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Execute validation strategy."""
        pass


class FirstSuccessStrategy(ValidationStrategy):
    """Use first validator that succeeds or has highest confidence."""
    
    async def validate(
        self,
        value: str,
        id_type: Optional[IDType],
        validators: List[BaseValidator],
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Use first successful validation or best result."""
        best_result = None
        best_confidence = -1.0
        
        for validator in validators:
            try:
                result = await validator.validate_async(value, context)
                
                # Return first successful validation
                if result.is_valid:
                    return result
                
                # Track best result by confidence
                if result.confidence_score > best_confidence:
                    best_confidence = result.confidence_score
                    best_result = result
                    
            except Exception as e:
                logger.warning(f"Validator {validator.name} failed: {e}")
                continue
        
        # Return best result or create error result
        if best_result:
            return best_result
        
        return create_error_result(
            id_type=id_type or IDType.CUSTOM,
            original_value=value,
            error_message="All validators failed"
        )


class ConsensusStrategy(ValidationStrategy):
    """Use consensus from multiple validators."""
    
    def __init__(self, min_consensus: float = 0.6):
        self.min_consensus = min_consensus
    
    async def validate(
        self,
        value: str,
        id_type: Optional[IDType],
        validators: List[BaseValidator],
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Use consensus validation from multiple validators."""
        if len(validators) < 2:
            # Fall back to first success for single validator
            strategy = FirstSuccessStrategy()
            return await strategy.validate(value, id_type, validators, context)
        
        # Run all validators concurrently
        tasks = []
        for validator in validators:
            task = asyncio.create_task(
                self._safe_validate(validator, value, context)
            )
            tasks.append((validator, task))
        
        # Collect results
        results = []
        for validator, task in tasks:
            try:
                result = await task
                if result:
                    results.append((validator, result))
            except Exception as e:
                logger.warning(f"Validator {validator.name} failed in consensus: {e}")
        
        if not results:
            return create_error_result(
                id_type=id_type or IDType.CUSTOM,
                original_value=value,
                error_message="All validators failed in consensus"
            )
        
        # Calculate consensus
        return self._calculate_consensus(value, id_type, results)
    
    async def _safe_validate(
        self,
        validator: BaseValidator,
        value: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[ValidationResult]:
        """Safely validate with error handling."""
        try:
            return await validator.validate_async(value, context)
        except Exception as e:
            logger.warning(f"Validator {validator.name} error: {e}")
            return None
    
    def _calculate_consensus(
        self,
        value: str,
        id_type: Optional[IDType],
        results: List[Tuple[BaseValidator, ValidationResult]]
    ) -> ValidationResult:
        """Calculate consensus result from multiple validation results."""
        valid_count = sum(1 for _, result in results if result.is_valid)
        total_count = len(results)
        
        # Calculate consensus score
        consensus_score = valid_count / total_count if total_count > 0 else 0.0
        is_valid = consensus_score >= self.min_consensus
        
        # Aggregate confidence scores (weighted average)
        total_confidence = 0.0
        total_weight = 0.0
        
        for validator, result in results:
            # Use validator priority as weight (lower priority = higher weight)
            weight = 1.0  # Could be enhanced with actual priority weights
            total_confidence += result.confidence_score * weight
            total_weight += weight
        
        avg_confidence = total_confidence / total_weight if total_weight > 0 else 0.0
        
        # Aggregate security flags
        all_security_flags = set()
        all_warnings = []
        all_errors = []
        max_risk_score = 0.0
        
        for _, result in results:
            all_security_flags.update(result.security_flags)
            all_warnings.extend(result.warnings)
            all_errors.extend(result.errors)
            max_risk_score = max(max_risk_score, result.risk_score)
        
        # Get best normalized value
        best_result = max(results, key=lambda x: x[1].confidence_score)[1]
        
        return create_validation_result(
            id_type=id_type or best_result.id_type,
            original_value=value,
            normalized_value=best_result.normalized_value,
            is_valid=is_valid,
            confidence_score=avg_confidence,
            validation_level=best_result.validation_level,
            security_flags=all_security_flags,
            risk_score=max_risk_score,
            warnings=all_warnings,
            errors=all_errors,
            details={
                "consensus_score": consensus_score,
                "validator_count": total_count,
                "valid_count": valid_count,
                "strategy": "consensus"
            }
        )


class ValidationEngine:
    """
    Central validation engine with advanced orchestration capabilities.
    """
    
    def __init__(
        self,
        config_provider: Optional[ConfigProvider] = None,
        max_concurrent: int = 20,
        default_timeout: float = 30.0
    ):
        """
        Initialize validation engine.
        
        Args:
            config_provider: Configuration provider
            max_concurrent: Maximum concurrent validations
            default_timeout: Default validation timeout
        """
        self.config_provider = config_provider
        self.max_concurrent = max_concurrent
        self.default_timeout = default_timeout
        
        # Core components
        self.registry = ValidatorRegistry()
        self.strategies = {
            "first_success": FirstSuccessStrategy(),
            "consensus": ConsensusStrategy()
        }
        
        # Performance tracking
        self._total_validations = 0
        self._total_errors = 0
        self._total_processing_time = 0.0
        self._start_time = time.time()
        
        # Caching
        self._result_cache: Dict[str, Tuple[ValidationResult, float]] = {}
        self._cache_ttl = 300  # 5 minutes
        
        logger.info("ValidationEngine initialized")
    
    async def register_validator(self, validator: BaseValidator, priority: int = 100) -> None:
        """Register a validator with the engine."""
        await self.registry.register(validator, priority)
    
    async def unregister_validator(self, validator_name: str) -> bool:
        """Unregister a validator from the engine."""
        return await self.registry.unregister(validator_name)
    
    def add_strategy(self, name: str, strategy: ValidationStrategy) -> None:
        """Add a custom validation strategy."""
        self.strategies[name] = strategy
        logger.info(f"Added validation strategy: {name}")
    
    async def validate(
        self,
        value: str,
        id_type: Optional[IDType] = None,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        strategy: str = "first_success",
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate an ID value using the specified strategy.
        
        Args:
            value: ID value to validate
            id_type: Specific ID type to validate against (optional)
            validation_level: Level of validation rigor
            strategy: Validation strategy to use
            context: Additional validation context
            
        Returns:
            Comprehensive validation result
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Input validation
            if not value or not isinstance(value, str):
                raise ValidationError("Invalid input value")
            
            # Check cache
            cache_key = self._generate_cache_key(value, id_type, validation_level, strategy, context)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Prepare context
            if not context:
                context = {}
            context.update({
                "validation_level": validation_level,
                "request_id": request_id,
                "engine_version": "1.0.0"
            })
            
            # Get appropriate validators
            validators = await self._get_validators_for_request(id_type, validation_level)
            if not validators:
                return create_error_result(
                    id_type=id_type or IDType.CUSTOM,
                    original_value=value,
                    error_message=f"No validators available for type: {id_type}"
                )
            
            # Get validation strategy
            validation_strategy = self.strategies.get(strategy)
            if not validation_strategy:
                raise ConfigurationError(f"Unknown validation strategy: {strategy}")
            
            # Execute validation
            result = await validation_strategy.validate(value, id_type, validators, context)
            
            # Enhance result with engine metadata
            processing_time = (time.time() - start_time) * 1000
            result.metadata = ValidationMetadata(
                validator_name="ValidationEngine",
                validator_version="1.0.0",
                validation_timestamp=datetime.now(timezone.utc),
                processing_time_ms=processing_time,
                validation_level=validation_level,
                cached_result=False,
                additional_info={
                    "strategy": strategy,
                    "validators_used": [v.name for v in validators],
                    "request_id": request_id
                }
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            
            # Update statistics
            self._total_validations += 1
            self._total_processing_time += processing_time
            
            return result
            
        except Exception as e:
            self._total_errors += 1
            logger.error(f"Validation engine error: {e}", exc_info=True)
            
            if isinstance(e, (ValidationError, ValidatorError, ConfigurationError)):
                raise
            
            raise EngineError(
                f"Validation engine failure: {e}",
                operation="validate",
                context=context,
                cause=e
            )
    
    async def validate_batch(
        self,
        values: List[str],
        id_type: Optional[IDType] = None,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        strategy: str = "first_success",
        context: Optional[Dict[str, Any]] = None,
        max_concurrent: Optional[int] = None
    ) -> List[ValidationResult]:
        """
        Validate multiple ID values with optimal concurrency.
        
        Args:
            values: List of ID values to validate
            id_type: Specific ID type (optional)
            validation_level: Validation level
            strategy: Validation strategy
            context: Validation context
            max_concurrent: Maximum concurrent validations
            
        Returns:
            List of validation results
        """
        if not values:
            return []
        
        concurrent_limit = min(
            max_concurrent or self.max_concurrent,
            len(values)
        )
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def validate_single(value: str) -> ValidationResult:
            async with semaphore:
                return await self.validate(value, id_type, validation_level, strategy, context)
        
        # Execute batch validation
        start_time = time.time()
        tasks = [validate_single(value) for value in values]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = create_error_result(
                    id_type=id_type or IDType.CUSTOM,
                    original_value=values[i],
                    error_message=str(result)
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Batch validation completed: {len(values)} items in {processing_time:.2f}ms")
        
        return final_results
    
    async def detect_id_type(self, value: str, confidence_threshold: float = 0.7) -> Optional[IDType]:
        """
        Automatically detect the most likely ID type for a value.
        
        Args:
            value: ID value to analyze
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            Detected ID type or None if uncertain
        """
        if not value:
            return None
        
        # Test against all available validators
        type_scores = {}
        
        for id_type in self.registry.get_supported_types():
            validators = self.registry.get_validators_for_type(id_type)
            if not validators:
                continue
            
            # Use best validator for this type
            validator = validators[0]
            try:
                result = await validator.validate_async(value)
                type_scores[id_type] = result.confidence_score
            except Exception as e:
                logger.debug(f"Detection failed for {id_type}: {e}")
                continue
        
        if not type_scores:
            return None
        
        # Find best match
        best_type = max(type_scores.items(), key=lambda x: x[1])
        
        if best_type[1] >= confidence_threshold:
            return best_type[0]
        
        return None
    
    async def _get_validators_for_request(
        self,
        id_type: Optional[IDType],
        validation_level: ValidationLevel
    ) -> List[BaseValidator]:
        """Get appropriate validators for a validation request."""
        if id_type:
            # Get validators for specific type
            validators = self.registry.get_validators_for_type(id_type)
        else:
            # Get all available validators for auto-detection
            validators = []
            for supported_type in self.registry.get_supported_types():
                type_validators = self.registry.get_validators_for_type(supported_type)
                validators.extend(type_validators)
        
        # Filter by validation level capabilities
        suitable_validators = []
        for validator in validators:
            if validation_level in validator.capabilities.supported_levels:
                suitable_validators.append(validator)
        
        return suitable_validators
    
    def _generate_cache_key(
        self,
        value: str,
        id_type: Optional[IDType],
        validation_level: ValidationLevel,
        strategy: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate cache key for validation request."""
        import hashlib
        
        # Create deterministic cache key
        key_data = f"{value}:{id_type}:{validation_level}:{strategy}"
        if context:
            # Sort context items for consistency
            context_str = ":".join(f"{k}={v}" for k, v in sorted(context.items()))
            key_data += f":{context_str}"
        
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    def _get_cached_result(self, cache_key: str) -> Optional[ValidationResult]:
        """Get cached result if still valid."""
        if cache_key in self._result_cache:
            result, timestamp = self._result_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                # Update metadata to indicate cached result
                if result.metadata:
                    result.metadata.cached_result = True
                return result
            else:
                # Remove expired entry
                del self._result_cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, result: ValidationResult) -> None:
        """Cache validation result."""
        self._result_cache[cache_key] = (result, time.time())
        
        # Simple cache cleanup (remove 10% oldest entries if cache is too large)
        if len(self._result_cache) > 1000:
            # Remove oldest 100 entries
            sorted_items = sorted(
                self._result_cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            for key, _ in sorted_items[:100]:
                del self._result_cache[key]
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics."""
        uptime = time.time() - self._start_time
        
        return {
            "uptime_seconds": uptime,
            "total_validations": self._total_validations,
            "total_errors": self._total_errors,
            "success_rate": (
                (self._total_validations - self._total_errors) / self._total_validations
                if self._total_validations > 0 else 0.0
            ),
            "avg_processing_time_ms": (
                self._total_processing_time / self._total_validations
                if self._total_validations > 0 else 0.0
            ),
            "validations_per_second": (
                self._total_validations / uptime if uptime > 0 else 0.0
            ),
            "registered_validators": self.registry.validator_count,
            "supported_types": list(self.registry.get_supported_types()),
            "cache_size": len(self._result_cache),
            "available_strategies": list(self.strategies.keys())
        }
    
    def clear_cache(self) -> None:
        """Clear the validation result cache."""
        self._result_cache.clear()
        logger.info("Engine cache cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive engine health check."""
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engine_stats": self.get_engine_stats(),
            "validators": {},
            "issues": []
        }
        
        # Check each registered validator
        for name, validator in self.registry._validators.items():
            try:
                # Basic health check
                validator_health = {
                    "status": "healthy",
                    "version": validator.version,
                    "supported_types": [t.value for t in validator.supported_types],
                    "validation_count": validator._validation_count,
                    "error_count": validator._error_count,
                    "success_rate": validator.success_rate
                }
                
                # Test basic functionality if possible
                if hasattr(validator, 'health_check'):
                    await validator.health_check()
                
                health["validators"][name] = validator_health
                
            except Exception as e:
                health["validators"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health["issues"].append(f"Validator {name} unhealthy: {e}")
        
        # Determine overall health
        unhealthy_validators = [
            name for name, info in health["validators"].items()
            if info.get("status") != "healthy"
        ]
        
        if unhealthy_validators:
            health["status"] = "degraded" if len(unhealthy_validators) < len(health["validators"]) else "unhealthy"
        
        return health
    
    def __str__(self) -> str:
        return f"ValidationEngine (validators: {self.registry.validator_count}, validations: {self._total_validations})"
    
    def __repr__(self) -> str:
        return (
            f"<ValidationEngine("
            f"validators={self.registry.validator_count}, "
            f"strategies={len(self.strategies)}, "
            f"validations={self._total_validations}"
            f")>"
        )
