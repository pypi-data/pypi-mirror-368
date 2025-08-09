"""
Core Interfaces and Protocols

Defines the fundamental interfaces, protocols, and abstract base classes
that establish contracts for validators, engines, and other components.
Ensures consistent behavior and enables extensibility.

Features:
- Protocol-based interfaces for type safety
- Abstract base classes for common functionality
- Plugin architecture support
- Dependency injection interfaces
- Configuration management protocols

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

from abc import ABC, abstractmethod
from typing import (
    Dict, Any, List, Optional, Set, Union, Protocol, runtime_checkable,
    AsyncIterator, Iterator, Callable, TypeVar, Generic, ClassVar
)
import asyncio
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

from .types import (
    IDType, ValidationLevel, ValidationResult, ValidationRequest,
    BatchValidationRequest, ValidationMetadata, SecurityFlags, ValidationStatus
)
from .exceptions import ValidationError, ConfigurationError, ValidatorError


# Type variables for generic interfaces
T = TypeVar('T')
R = TypeVar('R')
Config = TypeVar('Config', bound=Dict[str, Any])


class ValidatorCapability(Enum):
    """Enumeration of validator capabilities."""
    
    FORMAT_VALIDATION = "format_validation"
    ALGORITHM_VALIDATION = "algorithm_validation"
    EXTERNAL_VALIDATION = "external_validation"
    BATCH_PROCESSING = "batch_processing"
    ASYNC_PROCESSING = "async_processing"
    CACHING = "caching"
    RATE_LIMITING = "rate_limiting"
    SECURITY_SCANNING = "security_scanning"
    COMPLIANCE_CHECKING = "compliance_checking"
    REAL_TIME_VALIDATION = "real_time_validation"


@runtime_checkable
class ConfigProvider(Protocol):
    """Protocol for configuration providers."""
    
    def get_config(self, section: str, key: Optional[str] = None) -> Any:
        """Get configuration value."""
        ...
    
    def set_config(self, section: str, key: str, value: Any) -> None:
        """Set configuration value."""
        ...
    
    def has_config(self, section: str, key: Optional[str] = None) -> bool:
        """Check if configuration exists."""
        ...
    
    def reload_config(self) -> None:
        """Reload configuration from source."""
        ...


@runtime_checkable
class CacheProvider(Protocol):
    """Protocol for cache providers."""
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ...
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        ...
    
    def clear(self) -> None:
        """Clear all cache entries."""
        ...
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...


@runtime_checkable
class SecurityProvider(Protocol):
    """Protocol for security providers."""
    
    def hash_sensitive_data(self, data: str) -> str:
        """Create secure hash of sensitive data."""
        ...
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data."""
        ...
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data."""
        ...
    
    def audit_validation(self, request: ValidationRequest, result: ValidationResult) -> None:
        """Audit validation operation."""
        ...
    
    def check_security_flags(self, value: str, id_type: IDType) -> Set[SecurityFlags]:
        """Check for security flags on ID value."""
        ...
    
    def sanitize_for_logging(self, value: str) -> str:
        """Sanitize value for safe logging."""
        ...


@runtime_checkable
class MetricsProvider(Protocol):
    """Protocol for metrics providers."""
    
    def increment_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment counter metric."""
        ...
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record histogram metric."""
        ...
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set gauge metric."""
        ...
    
    def record_timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record timing metric."""
        ...


@dataclass
class ValidatorInfo:
    """Information about a validator."""
    
    name: str
    version: str
    description: str
    supported_types: Set[IDType]
    capabilities: Set[ValidatorCapability]
    author: str
    license: str
    documentation_url: Optional[str] = None
    source_url: Optional[str] = None
    
    def supports_type(self, id_type: IDType) -> bool:
        """Check if validator supports specific ID type."""
        return id_type in self.supported_types
    
    def has_capability(self, capability: ValidatorCapability) -> bool:
        """Check if validator has specific capability."""
        return capability in self.capabilities


class BaseValidator(ABC):
    """
    Abstract base class for all ID validators.
    
    Provides common functionality and enforces the validator contract.
    All concrete validators should inherit from this class.
    """
    
    def __init__(
        self,
        config_provider: Optional[ConfigProvider] = None,
        cache_provider: Optional[CacheProvider] = None,
        security_provider: Optional[SecurityProvider] = None,
        metrics_provider: Optional[MetricsProvider] = None
    ):
        """
        Initialize base validator with dependency injection.
        
        Args:
            config_provider: Configuration provider
            cache_provider: Cache provider for performance
            security_provider: Security provider for audit and hashing
            metrics_provider: Metrics provider for monitoring
        """
        self.config_provider = config_provider
        self.cache_provider = cache_provider
        self.security_provider = security_provider
        self.metrics_provider = metrics_provider
        
        # Initialize validator metadata
        self._info = self._create_validator_info()
        self._validation_count = 0
        self._error_count = 0
        
        # Load configuration
        self._load_configuration()
    
    @abstractmethod
    def _create_validator_info(self) -> ValidatorInfo:
        """Create validator information. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _validate_internal(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Internal validation logic. Must be implemented by subclasses.
        
        Args:
            value: Value to validate
            context: Optional validation context
            
        Returns:
            Validation result
        """
        pass
    
    def _load_configuration(self) -> None:
        """Load validator-specific configuration."""
        if self.config_provider:
            try:
                # Load common configuration
                self.validation_timeout = self.config_provider.get_config(
                    "validators", "timeout_seconds"
                ) or 30.0
                
                self.cache_ttl = self.config_provider.get_config(
                    "validators", "cache_ttl_seconds"
                ) or 300
                
                self.enable_caching = self.config_provider.get_config(
                    "validators", "enable_caching"
                ) or True
                
                # Load validator-specific configuration
                validator_config = self.config_provider.get_config(
                    "validators", self.name.lower()
                ) or {}
                
                self._load_validator_config(validator_config)
                
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to load configuration for validator {self.name}",
                    cause=e,
                    config_section="validators",
                    config_key=self.name.lower()
                )
        else:
            # Set defaults when no config provider
            self.validation_timeout = 30.0
            self.cache_ttl = 300
            self.enable_caching = True
    
    def _load_validator_config(self, config: Dict[str, Any]) -> None:
        """Load validator-specific configuration. Override in subclasses."""
        pass
    
    def validate(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a single ID value with caching and metrics.
        
        Args:
            value: The ID value to validate
            context: Optional validation context
            
        Returns:
            Validation result with detailed information
        """
        import time
        start_time = time.time()
        
        try:
            # Input validation
            if not isinstance(value, str):
                raise ValidationError(
                    f"Expected string value, got {type(value).__name__}",
                    original_value=str(value) if value is not None else "None"
                )
            
            if not value.strip():
                raise ValidationError(
                    "Empty or whitespace-only value provided",
                    original_value=value
                )
            
            # Check cache if enabled
            cache_key = None
            if self.enable_caching and self.cache_provider:
                cache_key = self._generate_cache_key(value, context)
                cached_result = self.cache_provider.get(cache_key)
                if cached_result:
                    if self.metrics_provider:
                        self.metrics_provider.increment_counter(
                            "validator.cache.hits",
                            {"validator": self.name}
                        )
                    return cached_result
            
            # Perform validation
            result = self._validate_internal(value, context)
            
            # Add metadata
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            result.metadata = ValidationMetadata(
                validator_name=self.name,
                validator_version=self.version,
                validation_timestamp=result.metadata.validation_timestamp if result.metadata else None,
                processing_time_ms=processing_time,
                validation_level=context.get('validation_level', ValidationLevel.STANDARD) if context else ValidationLevel.STANDARD,
                cached_result=False
            )
            
            # Cache result if enabled
            if self.enable_caching and self.cache_provider and cache_key:
                self.cache_provider.set(cache_key, result, self.cache_ttl)
            
            # Record metrics
            if self.metrics_provider:
                self.metrics_provider.increment_counter(
                    "validator.validations.total",
                    {"validator": self.name, "status": "success"}
                )
                self.metrics_provider.record_timer(
                    "validator.validation.duration",
                    processing_time,
                    {"validator": self.name}
                )
            
            # Audit if security provider available
            if self.security_provider:
                request = ValidationRequest(
                    value=value,
                    context=context
                )
                self.security_provider.audit_validation(request, result)
            
            self._validation_count += 1
            return result
            
        except Exception as e:
            self._error_count += 1
            
            # Record error metrics
            if self.metrics_provider:
                self.metrics_provider.increment_counter(
                    "validator.validations.total",
                    {"validator": self.name, "status": "error"}
                )
            
            if isinstance(e, ValidationError):
                raise
            else:
                raise ValidatorError(
                    f"Validation failed for {self.name}: {e}",
                    validator_name=self.name,
                    validator_version=self.version,
                    operation="validate",
                    cause=e
                )
    
    async def validate_async(self, value: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Asynchronously validate a single ID value.
        
        Default implementation runs sync validation in thread pool.
        Override for true async validation.
        
        Args:
            value: The ID value to validate
            context: Optional validation context
            
        Returns:
            Validation result with detailed information
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.validate, value, context)
    
    def validate_batch(self, values: List[str], context: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """
        Validate multiple ID values efficiently.
        
        Default implementation validates each value individually.
        Override for optimized batch processing.
        
        Args:
            values: List of ID values to validate
            context: Optional validation context
            
        Returns:
            List of validation results
        """
        results = []
        for value in values:
            try:
                result = self.validate(value, context)
                results.append(result)
            except Exception as e:
                # Create error result for failed validation
                error_result = ValidationResult(
                    is_valid=False,
                    id_type=self.supported_types.pop() if self.supported_types else IDType.CUSTOM,
                    original_value=value,
                    normalized_value=value,
                    confidence_score=0.0,
                    risk_score=1.0,
                    status=ValidationStatus.ERROR
                )
                error_result.add_error(str(e))
                results.append(error_result)
        
        return results
    
    async def validate_batch_async(self, values: List[str], context: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """
        Asynchronously validate multiple ID values.
        
        Args:
            values: List of ID values to validate
            context: Optional validation context
            
        Returns:
            List of validation results
        """
        tasks = [self.validate_async(value, context) for value in values]
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    def _generate_cache_key(self, value: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for value and context."""
        import hashlib
        
        # Create a hash of the value and relevant context
        key_data = f"{self.name}:{self.version}:{value}"
        if context:
            # Only include serializable context data
            context_str = str(sorted(context.items()))
            key_data += f":{context_str}"
        
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    @property
    def info(self) -> ValidatorInfo:
        """Get validator information."""
        return self._info
    
    @property
    def name(self) -> str:
        """Get validator name."""
        return self._info.name
    
    @property
    def version(self) -> str:
        """Get validator version."""
        return self._info.version
    
    @property
    def supported_types(self) -> Set[IDType]:
        """Get supported ID types."""
        return self._info.supported_types
    
    @property
    def capabilities(self) -> Set[ValidatorCapability]:
        """Get validator capabilities."""
        return self._info.capabilities
    
    @property
    def validation_count(self) -> int:
        """Get total validation count."""
        return self._validation_count
    
    @property
    def error_count(self) -> int:
        """Get total error count."""
        return self._error_count
    
    @property
    def success_rate(self) -> float:
        """Get validation success rate."""
        if self._validation_count == 0:
            return 0.0
        return (self._validation_count - self._error_count) / self._validation_count
    
    def reset_stats(self) -> None:
        """Reset validation statistics."""
        self._validation_count = 0
        self._error_count = 0
    
    def supports_type(self, id_type: IDType) -> bool:
        """Check if validator supports specific ID type."""
        return id_type in self.supported_types
    
    def has_capability(self, capability: ValidatorCapability) -> bool:
        """Check if validator has specific capability."""
        return capability in self.capabilities
    
    def __str__(self) -> str:
        return f"{self.name} v{self.version}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', version='{self.version}')>"


@runtime_checkable
class ValidatorRegistry(Protocol):
    """Protocol for validator registries."""
    
    def register_validator(self, validator: BaseValidator) -> None:
        """Register a validator."""
        ...
    
    def unregister_validator(self, name: str) -> None:
        """Unregister a validator by name."""
        ...
    
    def get_validator(self, name: str) -> Optional[BaseValidator]:
        """Get validator by name."""
        ...
    
    def get_validators_for_type(self, id_type: IDType) -> List[BaseValidator]:
        """Get all validators that support a specific ID type."""
        ...
    
    def list_validators(self) -> List[ValidatorInfo]:
        """List all registered validators."""
        ...
    
    def auto_detect_validator(self, value: str) -> Optional[BaseValidator]:
        """Automatically detect the best validator for a value."""
        ...


@runtime_checkable
class ValidationEngine(Protocol):
    """Protocol for validation engines."""
    
    def validate(
        self,
        value: str,
        id_type: Optional[IDType] = None,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate a single ID value."""
        ...
    
    async def validate_async(
        self,
        value: str,
        id_type: Optional[IDType] = None,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Asynchronously validate a single ID value."""
        ...
    
    def validate_batch(
        self,
        request: BatchValidationRequest
    ) -> List[ValidationResult]:
        """Validate multiple ID values."""
        ...
    
    async def validate_batch_async(
        self,
        request: BatchValidationRequest
    ) -> List[ValidationResult]:
        """Asynchronously validate multiple ID values."""
        ...


class Plugin(ABC):
    """
    Abstract base class for plugins.
    
    Enables extensibility through plugin architecture.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get plugin version."""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown plugin and cleanup resources."""
        pass
    
    def get_dependencies(self) -> List[str]:
        """Get list of plugin dependencies."""
        return []
    
    def is_compatible(self, api_version: str) -> bool:
        """Check if plugin is compatible with API version."""
        return True


@runtime_checkable
class PluginManager(Protocol):
    """Protocol for plugin managers."""
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin."""
        ...
    
    def unregister_plugin(self, name: str) -> None:
        """Unregister a plugin."""
        ...
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get plugin by name."""
        ...
    
    def list_plugins(self) -> List[str]:
        """List all registered plugins."""
        ...
    
    def initialize_plugins(self, config: Dict[str, Any]) -> None:
        """Initialize all plugins."""
        ...
    
    def shutdown_plugins(self) -> None:
        """Shutdown all plugins."""
        ...


# Context managers for resource management
@contextmanager
def validation_context(
    config_provider: Optional[ConfigProvider] = None,
    security_provider: Optional[SecurityProvider] = None,
    metrics_provider: Optional[MetricsProvider] = None
):
    """
    Context manager for validation operations with proper resource cleanup.
    
    Args:
        config_provider: Configuration provider
        security_provider: Security provider
        metrics_provider: Metrics provider
        
    Yields:
        Tuple of (config_provider, security_provider, metrics_provider)
    """
    try:
        yield (config_provider, security_provider, metrics_provider)
    finally:
        # Cleanup any resources if needed
        pass


# Factory functions for creating standard implementations
def create_validator_info(
    name: str,
    version: str,
    description: str,
    supported_types: Set[IDType],
    capabilities: Optional[Set[ValidatorCapability]] = None,
    author: str = "PyIDVerify Contributors",
    license: str = "MIT",
    **kwargs
) -> ValidatorInfo:
    """
    Factory function for creating ValidatorInfo instances.
    
    Args:
        name: Validator name
        version: Validator version
        description: Validator description
        supported_types: Set of supported ID types
        capabilities: Set of validator capabilities
        author: Author name
        license: License information
        **kwargs: Additional fields
        
    Returns:
        ValidatorInfo instance
    """
    return ValidatorInfo(
        name=name,
        version=version,
        description=description,
        supported_types=supported_types,
        capabilities=capabilities or set(),
        author=author,
        license=license,
        **kwargs
    )
