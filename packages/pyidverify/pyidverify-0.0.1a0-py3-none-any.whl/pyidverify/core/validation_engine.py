"""
PyIDVerify Validation Engine

This module provides the central validation orchestration system that coordinates
all validators, manages security measures, and handles batch processing.

Author: PyIDVerify Team
License: MIT
"""

import asyncio
import logging
from typing import Dict, List, Optional, Type, Union, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum

from .types import IDType, ValidationResult, ValidationLevel
from .base_validator import BaseValidator
from .exceptions import ValidationError, SecurityError, ConfigurationError
from ..security.audit import AuditLogger
from ..security.rate_limiter import RateLimiter
from ..config.settings import ValidationConfig

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing modes for validation engine."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"


@dataclass
class ValidationRequest:
    """Represents a validation request."""
    value: str
    id_type: Optional[IDType] = None
    level: ValidationLevel = ValidationLevel.STANDARD
    metadata: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


@dataclass
class BatchValidationResult:
    """Results from batch validation processing."""
    results: List[ValidationResult]
    total_processed: int
    successful_validations: int
    failed_validations: int
    processing_time_ms: float
    errors: List[str]


class ValidatorRegistry:
    """Registry for managing validator instances."""
    
    def __init__(self):
        self._validators: Dict[IDType, BaseValidator] = {}
        self._auto_detect_validators: List[BaseValidator] = []
        
    def register_validator(self, id_type: IDType, validator: BaseValidator):
        """Register a validator for a specific ID type."""
        self._validators[id_type] = validator
        logger.info(f"Registered validator for {id_type.value}")
        
    def register_auto_detect_validator(self, validator: BaseValidator):
        """Register a validator for auto-detection."""
        self._auto_detect_validators.append(validator)
        logger.info(f"Registered auto-detect validator: {validator.__class__.__name__}")
        
    def get_validator(self, id_type: IDType) -> Optional[BaseValidator]:
        """Get validator for specific ID type."""
        return self._validators.get(id_type)
        
    def get_auto_detect_validators(self) -> List[BaseValidator]:
        """Get all auto-detect validators."""
        return self._auto_detect_validators.copy()
        
    def list_supported_types(self) -> List[IDType]:
        """List all supported ID types."""
        return list(self._validators.keys())


class ValidationEngine:
    """
    Central validation engine that orchestrates all validation operations.
    
    Features:
    - Automatic ID type detection
    - Batch processing with parallel execution
    - Security integration with audit logging
    - Rate limiting and abuse prevention
    - Configurable validation levels
    - Async support for I/O-bound operations
    """
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        """Initialize validation engine with configuration."""
        self.config = config or ValidationConfig()
        self.registry = ValidatorRegistry()
        self.audit_logger = AuditLogger(self.config.audit_config)
        self.rate_limiter = RateLimiter(self.config.rate_limit_config)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_workers)
        
        logger.info("ValidationEngine initialized")
        
    def validate(self, 
                value: str, 
                id_type: Optional[IDType] = None,
                level: ValidationLevel = ValidationLevel.STANDARD,
                metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a single ID value.
        
        Args:
            value: The ID value to validate
            id_type: Specific ID type (auto-detected if None)
            level: Validation level (BASIC, STANDARD, STRICT)
            metadata: Additional metadata for validation
            
        Returns:
            ValidationResult with validation outcome
            
        Raises:
            ValidationError: If validation fails critically
            SecurityError: If security checks fail
        """
        try:
            # Rate limiting check
            if not self.rate_limiter.allow_request():
                raise SecurityError("Rate limit exceeded")
                
            # Audit log the request
            request_data = {
                'value_hash': self._hash_value(value),
                'id_type': id_type.value if id_type else None,
                'level': level.value,
                'metadata': metadata
            }
            self.audit_logger.log_validation_request(request_data)
            
            # Get appropriate validator
            validator = self._get_validator(value, id_type)
            if not validator:
                raise ValidationError(f"No validator found for {id_type or 'auto-detected'}")
                
            # Perform validation
            result = validator.validate(value, level=level, metadata=metadata)
            
            # Security post-processing
            result = self._apply_security_measures(result, value)
            
            # Audit log the result
            self.audit_logger.log_validation_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            self.audit_logger.log_error(str(e), {'value_hash': self._hash_value(value)})
            raise
            
    async def validate_async(self, 
                           value: str, 
                           id_type: Optional[IDType] = None,
                           level: ValidationLevel = ValidationLevel.STANDARD,
                           metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Async version of validate method."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.thread_pool, 
            self.validate, 
            value, id_type, level, metadata
        )
        
    def validate_batch(self, 
                      requests: List[ValidationRequest],
                      mode: ProcessingMode = ProcessingMode.PARALLEL) -> BatchValidationResult:
        """
        Validate multiple ID values in batch.
        
        Args:
            requests: List of validation requests
            mode: Processing mode (sequential, parallel, adaptive)
            
        Returns:
            BatchValidationResult with all results and statistics
        """
        import time
        start_time = time.time()
        results = []
        errors = []
        
        try:
            if mode == ProcessingMode.SEQUENTIAL:
                results = self._process_sequential(requests, errors)
            elif mode == ProcessingMode.PARALLEL:
                results = self._process_parallel(requests, errors)
            else:  # ADAPTIVE
                results = self._process_adaptive(requests, errors)
                
            processing_time = (time.time() - start_time) * 1000
            successful = sum(1 for r in results if r.is_valid)
            failed = len(results) - successful
            
            return BatchValidationResult(
                results=results,
                total_processed=len(requests),
                successful_validations=successful,
                failed_validations=failed,
                processing_time_ms=processing_time,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Batch validation error: {str(e)}")
            errors.append(str(e))
            raise ValidationError(f"Batch validation failed: {str(e)}")
            
    async def validate_batch_async(self, 
                                 requests: List[ValidationRequest],
                                 mode: ProcessingMode = ProcessingMode.PARALLEL) -> BatchValidationResult:
        """Async batch validation."""
        tasks = [
            self.validate_async(req.value, req.id_type, req.level, req.metadata)
            for req in requests
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Request {i}: {str(result)}")
                # Create error result
                processed_results.append(ValidationResult(
                    is_valid=False,
                    id_type=requests[i].id_type or IDType.UNKNOWN,
                    confidence=0.0,
                    errors=[str(result)],
                    metadata={}
                ))
            else:
                processed_results.append(result)
                
        successful = sum(1 for r in processed_results if r.is_valid)
        
        return BatchValidationResult(
            results=processed_results,
            total_processed=len(requests),
            successful_validations=successful,
            failed_validations=len(requests) - successful,
            processing_time_ms=0.0,  # Not measured in async
            errors=errors
        )
        
    def register_validator(self, id_type: IDType, validator_class: Type[BaseValidator]):
        """Register a validator for specific ID type."""
        validator = validator_class(self.config)
        self.registry.register_validator(id_type, validator)
        
    def auto_detect_type(self, value: str) -> Optional[IDType]:
        """Auto-detect ID type from value."""
        for validator in self.registry.get_auto_detect_validators():
            if validator.can_validate(value):
                return validator.supported_type
        return None
        
    def get_supported_types(self) -> List[IDType]:
        """Get list of supported ID types."""
        return self.registry.list_supported_types()
        
    def _get_validator(self, value: str, id_type: Optional[IDType]) -> Optional[BaseValidator]:
        """Get appropriate validator for value and type."""
        if id_type:
            return self.registry.get_validator(id_type)
        else:
            detected_type = self.auto_detect_type(value)
            if detected_type:
                return self.registry.get_validator(detected_type)
        return None
        
    def _process_sequential(self, requests: List[ValidationRequest], errors: List[str]) -> List[ValidationResult]:
        """Process requests sequentially."""
        results = []
        for req in requests:
            try:
                result = self.validate(req.value, req.id_type, req.level, req.metadata)
                results.append(result)
            except Exception as e:
                errors.append(f"Sequential processing error: {str(e)}")
                results.append(ValidationResult(
                    is_valid=False,
                    id_type=req.id_type or IDType.UNKNOWN,
                    confidence=0.0,
                    errors=[str(e)],
                    metadata={}
                ))
        return results
        
    def _process_parallel(self, requests: List[ValidationRequest], errors: List[str]) -> List[ValidationResult]:
        """Process requests in parallel using thread pool."""
        futures = []
        for req in requests:
            future = self.thread_pool.submit(
                self.validate, req.value, req.id_type, req.level, req.metadata
            )
            futures.append(future)
            
        results = []
        for i, future in enumerate(futures):
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                errors.append(f"Parallel processing error for request {i}: {str(e)}")
                results.append(ValidationResult(
                    is_valid=False,
                    id_type=requests[i].id_type or IDType.UNKNOWN,
                    confidence=0.0,
                    errors=[str(e)],
                    metadata={}
                ))
        return results
        
    def _process_adaptive(self, requests: List[ValidationRequest], errors: List[str]) -> List[ValidationResult]:
        """Adaptively choose processing mode based on request characteristics."""
        # Use parallel for large batches, sequential for small ones
        if len(requests) > self.config.parallel_threshold:
            return self._process_parallel(requests, errors)
        else:
            return self._process_sequential(requests, errors)
            
    def _apply_security_measures(self, result: ValidationResult, original_value: str) -> ValidationResult:
        """Apply additional security measures to validation result."""
        # Hash sensitive data
        if result.metadata and 'sensitive_data' in result.metadata:
            result.metadata['sensitive_data'] = self._hash_value(str(result.metadata['sensitive_data']))
            
        # Add security hash for result integrity
        result.security_hash = self._hash_value(f"{result.is_valid}{result.confidence}{original_value}")
        
        return result
        
    def _hash_value(self, value: str) -> str:
        """Create secure hash of value for logging."""
        import hashlib
        return hashlib.sha256(value.encode()).hexdigest()[:16]
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.thread_pool.shutdown(wait=True)
        
    def shutdown(self):
        """Clean shutdown of validation engine."""
        self.thread_pool.shutdown(wait=True)
        logger.info("ValidationEngine shutdown complete")
