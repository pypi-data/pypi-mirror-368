"""
Base Validator Framework

Provides the foundational validator class with common functionality including
security integration, caching, metrics, async support, and batch processing.
All concrete validators inherit from this framework.

Features:
- Security-first design with audit integration
- High-performance caching with configurable TTL
- Comprehensive metrics and monitoring
- Async validation support with thread pool execution
- Efficient batch processing capabilities
- Extensible configuration system
- Error handling and recovery mechanisms

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Set, Union, Callable
from abc import abstractmethod
from datetime import datetime, timezone
import uuid
import inspect

from .interfaces import (
    BaseValidator as BaseValidatorInterface,
    ValidatorInfo,
    ValidatorCapability,
    ConfigProvider,
    CacheProvider,
    SecurityProvider,
    MetricsProvider,
    create_validator_info
)
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
    TimeoutError,
    create_validation_error
)
from ..security.exceptions import SecurityError

# Configure logging
logger = logging.getLogger('pyidverify.core.base_validator')


class BaseValidator(BaseValidatorInterface):
    """
    Enhanced base validator with comprehensive functionality.
    
    Provides security integration, performance optimization, monitoring,
    and standardized validation patterns for all concrete validators.
    """
    
    # Class-level configuration
    DEFAULT_TIMEOUT_SECONDS = 30.0
    DEFAULT_CACHE_TTL_SECONDS = 300
    DEFAULT_MAX_BATCH_SIZE = 1000
    DEFAULT_MAX_CONCURRENT = 10
    
    def __init__(
        self,
        config_provider: Optional[ConfigProvider] = None,
        cache_provider: Optional[CacheProvider] = None,
        security_provider: Optional[SecurityProvider] = None,
        metrics_provider: Optional[MetricsProvider] = None,
        **kwargs: Any
    ):
        """
        Initialize enhanced base validator.
        
        Args:
            config_provider: Configuration provider for dynamic settings
            cache_provider: Cache provider for performance optimization
            security_provider: Security provider for audit and protection
            metrics_provider: Metrics provider for monitoring
            **kwargs: Additional validator-specific configuration
        """
        # Initialize parent class
        super().__init__(
            config_provider=config_provider,
            cache_provider=cache_provider,
            security_provider=security_provider,
            metrics_provider=metrics_provider
        )
        
        # Additional configuration
        self.max_batch_size = kwargs.get('max_batch_size', self.DEFAULT_MAX_BATCH_SIZE)
        self.max_concurrent = kwargs.get('max_concurrent', self.DEFAULT_MAX_CONCURRENT)
        self.enable_security_scanning = kwargs.get('enable_security_scanning', True)
        self.enable_detailed_logging = kwargs.get('enable_detailed_logging', False)
        
        # Performance tracking
        self._total_processing_time = 0.0
        self._avg_processing_time = 0.0
        self._max_processing_time = 0.0
        self._min_processing_time = float('inf')
        
        # Validation context
        self._validation_context = {}
        
        logger.info(f"Enhanced BaseValidator initialized: {self.name} v{self.version}")
    
    def _load_validator_config(self, config: Dict[str, Any]) -> None:
        """Load validator-specific configuration with validation."""
        try:
            # Load performance settings
            self.validation_timeout = config.get('timeout_seconds', self.DEFAULT_TIMEOUT_SECONDS)
            self.cache_ttl = config.get('cache_ttl_seconds', self.DEFAULT_CACHE_TTL_SECONDS)
            self.max_batch_size = config.get('max_batch_size', self.DEFAULT_MAX_BATCH_SIZE)
            self.max_concurrent = config.get('max_concurrent', self.DEFAULT_MAX_CONCURRENT)
            
            # Load feature flags
            self.enable_caching = config.get('enable_caching', True)
            self.enable_security_scanning = config.get('enable_security_scanning', True)
            self.enable_detailed_logging = config.get('enable_detailed_logging', False)
            
            # Validate configuration values
            self._validate_configuration()
            
            # Load validator-specific configuration
            self._load_custom_config(config)
            
        except Exception as e:
            raise ConfigurationError(
                f"Invalid configuration for validator {self.name}",
                config_section="validators",
                config_key=self.name.lower(),
                cause=e
            )
    
    def _load_custom_config(self, config: Dict[str, Any]) -> None:
        """Load custom validator configuration. Override in subclasses."""
        pass
    
    def _validate_configuration(self) -> None:
        """Validate configuration values."""
        if self.validation_timeout <= 0:
            raise ConfigurationError(
                "Validation timeout must be positive",
                config_key="timeout_seconds",
                actual_value=self.validation_timeout
            )
        
        if self.cache_ttl < 0:
            raise ConfigurationError(
                "Cache TTL must be non-negative",
                config_key="cache_ttl_seconds",
                actual_value=self.cache_ttl
            )
        
        if self.max_batch_size <= 0 or self.max_batch_size > 10000:
            raise ConfigurationError(
                "Max batch size must be between 1 and 10000",
                config_key="max_batch_size",
                actual_value=self.max_batch_size
            )
        
        if self.max_concurrent <= 0 or self.max_concurrent > 100:
            raise ConfigurationError(
                "Max concurrent must be between 1 and 100",
                config_key="max_concurrent",
                actual_value=self.max_concurrent
            )
    
    @abstractmethod
    def _create_validator_info(self) -> ValidatorInfo:
        """Create validator information. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _validate_internal(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Internal validation logic. Must be implemented by subclasses."""
        pass
    
    def _preprocess_value(self, value: str) -> str:
        """
        Preprocess input value before validation.
        
        Override in subclasses for custom preprocessing.
        
        Args:
            value: Raw input value
            
        Returns:
            Preprocessed value
        """
        # Basic preprocessing
        if not isinstance(value, str):
            value = str(value)
        
        # Strip whitespace
        value = value.strip()
        
        return value
    
    def _postprocess_result(self, result: ValidationResult, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Postprocess validation result.
        
        Override in subclasses for custom postprocessing.
        
        Args:
            result: Raw validation result
            context: Validation context
            
        Returns:
            Enhanced validation result
        """
        # Add security scanning if enabled
        if self.enable_security_scanning and self.security_provider:
            try:
                security_flags = self.security_provider.check_security_flags(
                    result.original_value,
                    result.id_type
                )
                result.security_flags.update(security_flags)
                
                # Calculate risk score based on security flags
                if security_flags:
                    high_risk_flags = {
                        SecurityFlags.KNOWN_FRAUD,
                        SecurityFlags.HIGH_RISK,
                        SecurityFlags.SUSPICIOUS_PATTERN
                    }
                    
                    if any(flag in security_flags for flag in high_risk_flags):
                        result.risk_score = max(result.risk_score, 0.8)
                    else:
                        result.risk_score = max(result.risk_score, 0.3)
                
            except Exception as e:
                logger.warning(f"Security scanning failed: {e}")
                result.add_warning(f"Security scan incomplete: {e}")
        
        # Add security hash if available
        if self.security_provider and not result.security_hash:
            try:
                result.security_hash = self.security_provider.hash_sensitive_data(
                    f"{result.id_type.value}:{result.normalized_value}"
                )
            except Exception as e:
                logger.warning(f"Security hash generation failed: {e}")
        
        return result
    
    def _validate_input(self, value: str) -> None:
        """
        Validate input before processing.
        
        Args:
            value: Input value to validate
            
        Raises:
            ValidationError: If input is invalid
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Expected string input, got {type(value).__name__}",
                original_value=str(value) if value is not None else "None"
            )
        
        if not value or not value.strip():
            raise ValidationError(
                "Input value cannot be empty or whitespace-only",
                original_value=value
            )
        
        # Check length constraints
        if len(value) > 1000:  # Reasonable upper limit
            raise ValidationError(
                f"Input value too long: {len(value)} characters (max: 1000)",
                original_value=value[:50] + "..." if len(value) > 50 else value
            )
    
    def _update_performance_stats(self, processing_time_ms: float) -> None:
        """Update performance statistics."""
        self._total_processing_time += processing_time_ms
        
        if self._validation_count > 0:
            self._avg_processing_time = self._total_processing_time / self._validation_count
        
        self._max_processing_time = max(self._max_processing_time, processing_time_ms)
        self._min_processing_time = min(self._min_processing_time, processing_time_ms)
    
    def validate(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Enhanced validate method with comprehensive functionality.
        
        Args:
            value: The ID value to validate
            context: Optional validation context
            
        Returns:
            Comprehensive validation result
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Input validation and preprocessing
            self._validate_input(value)
            processed_value = self._preprocess_value(value)
            
            # Detailed logging if enabled
            if self.enable_detailed_logging:
                logger.debug(
                    f"Starting validation - Validator: {self.name}, "
                    f"Value: {self.security_provider.sanitize_for_logging(processed_value) if self.security_provider else '***'}, "
                    f"Request ID: {request_id}"
                )
            
            # Check cache if enabled
            cached_result = None
            cache_key = None
            
            if self.enable_caching and self.cache_provider:
                cache_key = self._generate_cache_key(processed_value, context)
                cached_result = self.cache_provider.get(cache_key)
                
                if cached_result:
                    # Update metadata for cached result
                    processing_time = (time.time() - start_time) * 1000
                    cached_result.metadata = ValidationMetadata(
                        validator_name=self.name,
                        validator_version=self.version,
                        validation_timestamp=datetime.now(timezone.utc),
                        processing_time_ms=processing_time,
                        validation_level=context.get('validation_level', ValidationLevel.STANDARD) if context else ValidationLevel.STANDARD,
                        cached_result=True
                    )
                    
                    # Update stats and metrics
                    self._validation_count += 1
                    self._update_performance_stats(processing_time)
                    
                    if self.metrics_provider:
                        self.metrics_provider.increment_counter(
                            "validator.cache.hits",
                            {"validator": self.name}
                        )
                        self.metrics_provider.record_timer(
                            "validator.validation.duration",
                            processing_time,
                            {"validator": self.name, "cached": "true"}
                        )
                    
                    return cached_result
            
            # Perform actual validation with timeout
            result = self._validate_with_timeout(processed_value, context)
            
            # Postprocess result
            result = self._postprocess_result(result, context)
            
            # Calculate processing time and update metadata
            processing_time = (time.time() - start_time) * 1000
            result.metadata = ValidationMetadata(
                validator_name=self.name,
                validator_version=self.version,
                validation_timestamp=datetime.now(timezone.utc),
                processing_time_ms=processing_time,
                validation_level=context.get('validation_level', ValidationLevel.STANDARD) if context else ValidationLevel.STANDARD,
                cached_result=False,
                security_scan_performed=self.enable_security_scanning,
                external_checks_performed=self._get_external_checks_performed(),
                compliance_checks=self._get_compliance_checks_performed()
            )
            
            # Cache result if enabled
            if self.enable_caching and self.cache_provider and cache_key and result.is_valid:
                self.cache_provider.set(cache_key, result, self.cache_ttl)
            
            # Update statistics
            self._validation_count += 1
            self._update_performance_stats(processing_time)
            
            # Record metrics
            if self.metrics_provider:
                self.metrics_provider.increment_counter(
                    "validator.validations.total",
                    {"validator": self.name, "status": "success", "valid": str(result.is_valid)}
                )
                self.metrics_provider.record_timer(
                    "validator.validation.duration",
                    processing_time,
                    {"validator": self.name, "cached": "false"}
                )
                self.metrics_provider.record_histogram(
                    "validator.confidence.score",
                    result.confidence_score,
                    {"validator": self.name}
                )
            
            # Audit validation if security provider available
            if self.security_provider:
                try:
                    from .types import ValidationRequest
                    request = ValidationRequest(
                        value=processed_value,
                        context=context
                    )
                    self.security_provider.audit_validation(request, result)
                except Exception as e:
                    logger.warning(f"Audit logging failed: {e}")
                    result.add_warning(f"Audit incomplete: {e}")
            
            # Detailed logging if enabled
            if self.enable_detailed_logging:
                logger.debug(
                    f"Validation completed - Request ID: {request_id}, "
                    f"Valid: {result.is_valid}, "
                    f"Confidence: {result.confidence_score:.3f}, "
                    f"Time: {processing_time:.2f}ms"
                )
            
            return result
            
        except ValidationError:
            self._error_count += 1
            raise
            
        except Exception as e:
            self._error_count += 1
            
            # Record error metrics
            if self.metrics_provider:
                self.metrics_provider.increment_counter(
                    "validator.validations.total",
                    {"validator": self.name, "status": "error"}
                )
            
            logger.error(f"Validation error in {self.name}: {e}", exc_info=True)
            
            raise ValidatorError(
                f"Validation failed in {self.name}: {e}",
                validator_name=self.name,
                validator_version=self.version,
                operation="validate",
                cause=e
            )
    
    def _validate_with_timeout(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate with timeout protection.
        
        Args:
            value: Value to validate
            context: Validation context
            
        Returns:
            Validation result
            
        Raises:
            TimeoutError: If validation exceeds timeout
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(
                f"Validation timeout after {self.validation_timeout} seconds",
                timeout_seconds=self.validation_timeout,
                operation="validate"
            )
        
        # Set up timeout (Unix-like systems only)
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(self.validation_timeout))
        
        try:
            result = self._validate_internal(value, context)
            return result
        finally:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancel alarm
                signal.signal(signal.SIGALRM, old_handler)  # Restore handler
    
    def _get_external_checks_performed(self) -> List[str]:
        """Get list of external checks performed. Override in subclasses."""
        return []
    
    def _get_compliance_checks_performed(self) -> List[str]:
        """Get list of compliance checks performed. Override in subclasses."""
        return []
    
    async def validate_async(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Enhanced async validation with proper concurrency handling.
        
        Args:
            value: The ID value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        # If validator has true async support, use it
        if hasattr(self, '_validate_async_internal'):
            return await self._validate_async_internal(value, context)
        
        # Otherwise, run sync validation in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.validate, value, context)
    
    def validate_batch(self, values: List[str], context: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """
        Enhanced batch validation with size limits and error handling.
        
        Args:
            values: List of ID values to validate
            context: Optional validation context
            
        Returns:
            List of validation results
        """
        if not values:
            return []
        
        if len(values) > self.max_batch_size:
            raise ValidationError(
                f"Batch size {len(values)} exceeds maximum {self.max_batch_size}",
                errors=[f"Maximum batch size is {self.max_batch_size}"]
            )
        
        start_time = time.time()
        results = []
        
        # Check if validator has optimized batch processing
        if hasattr(self, '_validate_batch_internal'):
            try:
                results = self._validate_batch_internal(values, context)
            except Exception as e:
                logger.error(f"Batch validation failed in {self.name}: {e}")
                # Fall back to individual validation
                results = self._validate_batch_fallback(values, context)
        else:
            # Use individual validation
            results = self._validate_batch_fallback(values, context)
        
        # Record batch metrics
        processing_time = (time.time() - start_time) * 1000
        
        if self.metrics_provider:
            self.metrics_provider.increment_counter(
                "validator.batch.validations.total",
                {"validator": self.name, "size": str(len(values))}
            )
            self.metrics_provider.record_timer(
                "validator.batch.duration",
                processing_time,
                {"validator": self.name}
            )
        
        return results
    
    def _validate_batch_fallback(self, values: List[str], context: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """Fallback batch validation using individual validation."""
        results = []
        
        for value in values:
            try:
                result = self.validate(value, context)
                results.append(result)
            except Exception as e:
                # Create error result for failed validation
                error_result = create_error_result(
                    id_type=self.supported_types.pop() if self.supported_types else IDType.CUSTOM,
                    original_value=value,
                    error_message=str(e)
                )
                results.append(error_result)
        
        return results
    
    async def validate_batch_async(
        self,
        values: List[str],
        context: Optional[Dict[str, Any]] = None,
        max_concurrent: Optional[int] = None
    ) -> List[ValidationResult]:
        """
        Enhanced async batch validation with concurrency control.
        
        Args:
            values: List of ID values to validate
            context: Optional validation context
            max_concurrent: Maximum concurrent validations
            
        Returns:
            List of validation results
        """
        if not values:
            return []
        
        if len(values) > self.max_batch_size:
            raise ValidationError(
                f"Batch size {len(values)} exceeds maximum {self.max_batch_size}",
                errors=[f"Maximum batch size is {self.max_batch_size}"]
            )
        
        # Use provided max_concurrent or default
        concurrent_limit = max_concurrent or self.max_concurrent
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def validate_with_semaphore(value: str) -> ValidationResult:
            async with semaphore:
                return await self.validate_async(value, context)
        
        # Execute batch with controlled concurrency
        start_time = time.time()
        tasks = [validate_with_semaphore(value) for value in values]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = create_error_result(
                    id_type=self.supported_types.pop() if self.supported_types else IDType.CUSTOM,
                    original_value=values[i],
                    error_message=str(result)
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
        
        # Record metrics
        processing_time = (time.time() - start_time) * 1000
        
        if self.metrics_provider:
            self.metrics_provider.increment_counter(
                "validator.batch.async.validations.total",
                {"validator": self.name, "size": str(len(values))}
            )
            self.metrics_provider.record_timer(
                "validator.batch.async.duration",
                processing_time,
                {"validator": self.name}
            )
        
        return final_results
    
    @property
    def performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return {
            "validation_count": self._validation_count,
            "error_count": self._error_count,
            "success_rate": self.success_rate,
            "avg_processing_time_ms": self._avg_processing_time,
            "max_processing_time_ms": self._max_processing_time,
            "min_processing_time_ms": self._min_processing_time if self._min_processing_time != float('inf') else 0.0,
            "total_processing_time_ms": self._total_processing_time,
            "throughput_per_second": (
                self._validation_count / (self._total_processing_time / 1000)
                if self._total_processing_time > 0 else 0.0
            )
        }
    
    def clear_cache(self) -> None:
        """Clear validator cache if available."""
        if self.cache_provider:
            # Clear only this validator's cache entries
            # This is a simplified implementation - real cache providers 
            # would need pattern-based clearing
            logger.info(f"Cache clear requested for validator {self.name}")
    
    def warm_cache(self, values: List[str], context: Optional[Dict[str, Any]] = None) -> int:
        """
        Warm cache with commonly used values.
        
        Args:
            values: List of values to pre-validate and cache
            context: Validation context
            
        Returns:
            Number of values successfully cached
        """
        if not self.enable_caching or not self.cache_provider:
            return 0
        
        cached_count = 0
        
        for value in values:
            try:
                result = self.validate(value, context)
                cached_count += 1
            except Exception as e:
                logger.warning(f"Failed to warm cache for value: {e}")
        
        return cached_count
    
    def __str__(self) -> str:
        return f"{self.name} v{self.version} (validations: {self._validation_count}, errors: {self._error_count})"
    
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"types={len(self.supported_types)}, "
            f"validations={self._validation_count}"
            f")>"
        )
