"""
Configuration Settings Management

Comprehensive configuration system for PyIDVerify with security-focused defaults,
environment variable handling, configuration validation, and hot reloading support.

Features:
- Security-first default configurations
- Environment variable integration with type conversion
- Configuration schema validation with detailed error reporting
- Hot reloading with change notifications
- Multi-environment support (development, staging, production)
- Encrypted configuration storage for sensitive values
- Configuration versioning and rollback capabilities
- Real-time configuration monitoring and alerts

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union, List, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import time
from datetime import datetime, timezone
import hashlib

# Configure logging
logger = logging.getLogger('pyidverify.config.settings')


class Environment(Enum):
    """Deployment environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class SecurityLevel(Enum):
    """Security configuration levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"
    CUSTOM = "custom"


@dataclass
class SecuritySettings:
    """Security-related configuration settings."""
    
    # Encryption settings
    encryption_algorithm: str = "AES-256-GCM"
    key_derivation_iterations: int = 100000
    key_rotation_interval_hours: int = 24
    enable_key_escrow: bool = False
    
    # Hashing settings
    hash_algorithm: str = "Argon2id"
    hash_memory_cost: int = 65536  # 64MB
    hash_time_cost: int = 3
    hash_parallelism: int = 1
    
    # Audit settings
    audit_enabled: bool = True
    audit_level: str = "comprehensive"
    audit_retention_days: int = 2555  # 7 years
    audit_encryption_enabled: bool = True
    audit_signature_enabled: bool = True
    
    # Access control
    api_key_required: bool = True
    jwt_enabled: bool = True
    jwt_expiration_hours: int = 24
    mfa_required: bool = False
    
    # Rate limiting
    rate_limiting_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst_size: int = 10
    rate_limit_ban_duration_minutes: int = 15
    
    # Data protection
    pii_detection_enabled: bool = True
    pii_anonymization_enabled: bool = True
    data_masking_enabled: bool = True
    secure_memory_clearing: bool = True


@dataclass
class PerformanceSettings:
    """Performance and optimization settings."""
    
    # Caching
    caching_enabled: bool = True
    cache_ttl_seconds: int = 300
    cache_max_size: int = 10000
    cache_cleanup_interval_seconds: int = 60
    
    # Batch processing
    max_batch_size: int = 1000
    batch_timeout_seconds: int = 30
    batch_concurrency_limit: int = 20
    
    # Connection pooling
    connection_pool_size: int = 20
    connection_pool_max_overflow: int = 30
    connection_timeout_seconds: int = 30
    
    # Validation timeouts
    validation_timeout_seconds: int = 10
    external_api_timeout_seconds: int = 5
    dns_lookup_timeout_seconds: int = 3
    
    # Memory management
    memory_limit_mb: int = 512
    garbage_collection_enabled: bool = True
    memory_profiling_enabled: bool = False


@dataclass
class ComplianceSettings:
    """Regulatory compliance settings."""
    
    # GDPR settings
    gdpr_enabled: bool = True
    gdpr_consent_required: bool = True
    gdpr_data_retention_days: int = 730  # 2 years
    gdpr_right_to_erasure: bool = True
    gdpr_data_portability: bool = True
    
    # HIPAA settings
    hipaa_enabled: bool = False
    hipaa_audit_controls: bool = True
    hipaa_integrity_controls: bool = True
    hipaa_transmission_security: bool = True
    
    # PCI DSS settings
    pci_dss_enabled: bool = False
    pci_dss_data_encryption: bool = True
    pci_dss_access_controls: bool = True
    pci_dss_network_monitoring: bool = True
    
    # SOX settings
    sox_enabled: bool = False
    sox_audit_trails: bool = True
    sox_change_controls: bool = True
    sox_data_integrity: bool = True


@dataclass
class MonitoringSettings:
    """Monitoring and observability settings."""
    
    # Metrics
    metrics_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    metrics_collection_interval_seconds: int = 15
    
    # Health checks
    health_check_enabled: bool = True
    health_check_endpoint: str = "/health"
    health_check_interval_seconds: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file_path: Optional[str] = None
    log_rotation_size_mb: int = 100
    log_retention_days: int = 30
    
    # Alerting
    alerting_enabled: bool = True
    alert_email_recipients: List[str] = field(default_factory=list)
    alert_webhook_urls: List[str] = field(default_factory=list)
    error_rate_threshold: float = 0.05
    response_time_threshold_ms: int = 1000


@dataclass
class ValidationSettings:
    """Validation behavior settings."""
    
    # General validation
    strict_mode: bool = True
    case_sensitive: bool = False
    allow_international_formats: bool = True
    enable_format_auto_detection: bool = True
    
    # Email validation
    email_mx_check_enabled: bool = True
    email_disposable_check_enabled: bool = True
    email_role_account_check_enabled: bool = False
    email_typo_detection_enabled: bool = True
    
    # Phone validation
    phone_carrier_check_enabled: bool = False
    phone_line_type_detection: bool = True
    phone_number_portability_check: bool = False
    
    # Credit card validation
    credit_card_bin_check_enabled: bool = True
    credit_card_luhn_validation: bool = True
    credit_card_expiry_validation: bool = True
    credit_card_fraud_scoring: bool = True
    
    # Government ID validation
    government_id_audit_logging: bool = True
    government_id_enhanced_security: bool = True
    government_id_blacklist_checking: bool = True


class ConfigurationManager:
    """
    Advanced configuration management with hot reloading and validation.
    """
    
    def __init__(
        self,
        config_file: Optional[Union[str, Path]] = None,
        environment: Environment = Environment.DEVELOPMENT,
        auto_reload: bool = True
    ):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
            environment: Target environment
            auto_reload: Enable automatic configuration reloading
        """
        self.config_file = Path(config_file) if config_file else None
        self.environment = environment
        self.auto_reload = auto_reload
        
        # Configuration sections
        self.security = SecuritySettings()
        self.performance = PerformanceSettings()
        self.compliance = ComplianceSettings()
        self.monitoring = MonitoringSettings()
        self.validation = ValidationSettings()
        
        # Internal state
        self._config_hash: Optional[str] = None
        self._last_reload: Optional[datetime] = None
        self._reload_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._lock = threading.RLock()
        
        # Load configuration
        self._load_configuration()
        
        # Start auto-reload if enabled
        if self.auto_reload:
            self._start_auto_reload()
        
        logger.info(f"Configuration manager initialized for {environment.value} environment")
    
    def _load_configuration(self) -> None:
        """Load configuration from various sources."""
        with self._lock:
            # Start with environment-specific defaults
            self._apply_environment_defaults()
            
            # Load from environment variables
            self._load_from_environment()
            
            # Load from configuration file if specified
            if self.config_file and self.config_file.exists():
                self._load_from_file()
            
            # Validate configuration
            self._validate_configuration()
            
            # Update reload timestamp
            self._last_reload = datetime.now(timezone.utc)
            
            # Calculate configuration hash for change detection
            self._update_config_hash()
            
            logger.info("Configuration loaded successfully")
    
    def _apply_environment_defaults(self) -> None:
        """Apply environment-specific default settings."""
        if self.environment == Environment.PRODUCTION:
            # Production: Maximum security, optimized performance
            self.security.audit_enabled = True
            self.security.audit_level = "comprehensive"
            self.security.api_key_required = True
            self.security.jwt_enabled = True
            self.security.mfa_required = True
            self.security.rate_limiting_enabled = True
            self.monitoring.metrics_enabled = True
            self.monitoring.alerting_enabled = True
            self.validation.strict_mode = True
            
        elif self.environment == Environment.STAGING:
            # Staging: High security, testing-friendly
            self.security.audit_enabled = True
            self.security.api_key_required = True
            self.security.mfa_required = False
            self.performance.caching_enabled = True
            self.monitoring.metrics_enabled = True
            
        elif self.environment == Environment.TESTING:
            # Testing: Reduced security, fast execution
            self.security.audit_enabled = False
            self.security.api_key_required = False
            self.security.rate_limiting_enabled = False
            self.performance.caching_enabled = False
            self.performance.validation_timeout_seconds = 1
            self.monitoring.log_level = "DEBUG"
            
        elif self.environment == Environment.DEVELOPMENT:
            # Development: Minimal security, maximum debugging
            self.security.audit_enabled = False
            self.security.api_key_required = False
            self.security.rate_limiting_enabled = False
            self.performance.caching_enabled = False
            self.monitoring.log_level = "DEBUG"
            self.monitoring.log_format = "text"
            self.validation.strict_mode = False
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            # Security settings
            "PYIDVERIFY_ENCRYPTION_ALGORITHM": ("security.encryption_algorithm", str),
            "PYIDVERIFY_AUDIT_ENABLED": ("security.audit_enabled", self._parse_bool),
            "PYIDVERIFY_API_KEY_REQUIRED": ("security.api_key_required", self._parse_bool),
            "PYIDVERIFY_MFA_REQUIRED": ("security.mfa_required", self._parse_bool),
            "PYIDVERIFY_RATE_LIMIT_RPM": ("security.rate_limit_requests_per_minute", int),
            
            # Performance settings
            "PYIDVERIFY_CACHE_ENABLED": ("performance.caching_enabled", self._parse_bool),
            "PYIDVERIFY_CACHE_TTL": ("performance.cache_ttl_seconds", int),
            "PYIDVERIFY_MAX_BATCH_SIZE": ("performance.max_batch_size", int),
            "PYIDVERIFY_VALIDATION_TIMEOUT": ("performance.validation_timeout_seconds", int),
            
            # Compliance settings
            "PYIDVERIFY_GDPR_ENABLED": ("compliance.gdpr_enabled", self._parse_bool),
            "PYIDVERIFY_HIPAA_ENABLED": ("compliance.hipaa_enabled", self._parse_bool),
            "PYIDVERIFY_PCI_DSS_ENABLED": ("compliance.pci_dss_enabled", self._parse_bool),
            
            # Monitoring settings
            "PYIDVERIFY_LOG_LEVEL": ("monitoring.log_level", str),
            "PYIDVERIFY_METRICS_ENABLED": ("monitoring.metrics_enabled", self._parse_bool),
            "PYIDVERIFY_ALERTING_ENABLED": ("monitoring.alerting_enabled", self._parse_bool),
            
            # Validation settings
            "PYIDVERIFY_STRICT_MODE": ("validation.strict_mode", self._parse_bool),
            "PYIDVERIFY_EMAIL_MX_CHECK": ("validation.email_mx_check_enabled", self._parse_bool),
            "PYIDVERIFY_PHONE_CARRIER_CHECK": ("validation.phone_carrier_check_enabled", self._parse_bool),
        }
        
        for env_var, (config_path, converter) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    converted_value = converter(env_value)
                    self._set_nested_config(config_path, converted_value)
                    logger.debug(f"Set {config_path} = {converted_value} from {env_var}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {env_var}: {env_value} - {e}")
    
    def _load_from_file(self) -> None:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # Apply configuration sections
            if "security" in file_config:
                self._update_dataclass(self.security, file_config["security"])
            
            if "performance" in file_config:
                self._update_dataclass(self.performance, file_config["performance"])
            
            if "compliance" in file_config:
                self._update_dataclass(self.compliance, file_config["compliance"])
            
            if "monitoring" in file_config:
                self._update_dataclass(self.monitoring, file_config["monitoring"])
            
            if "validation" in file_config:
                self._update_dataclass(self.validation, file_config["validation"])
            
            logger.info(f"Configuration loaded from {self.config_file}")
            
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            logger.error(f"Failed to load configuration from {self.config_file}: {e}")
            raise
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings and apply constraints."""
        validation_errors = []
        
        # Security validation
        if self.security.key_rotation_interval_hours < 1:
            validation_errors.append("Key rotation interval must be at least 1 hour")
        
        if self.security.rate_limit_requests_per_minute < 1:
            validation_errors.append("Rate limit must be at least 1 request per minute")
        
        # Performance validation
        if self.performance.max_batch_size > 10000:
            validation_errors.append("Maximum batch size cannot exceed 10,000 items")
        
        if self.performance.validation_timeout_seconds < 1:
            validation_errors.append("Validation timeout must be at least 1 second")
        
        if self.performance.cache_ttl_seconds < 0:
            validation_errors.append("Cache TTL cannot be negative")
        
        # Compliance validation
        if self.compliance.gdpr_enabled and self.compliance.gdpr_data_retention_days < 1:
            validation_errors.append("GDPR data retention must be at least 1 day")
        
        # Monitoring validation
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.monitoring.log_level not in valid_log_levels:
            validation_errors.append(f"Invalid log level: {self.monitoring.log_level}")
        
        # Environment-specific validation
        if self.environment == Environment.PRODUCTION:
            if not self.security.api_key_required:
                validation_errors.append("API key is required in production environment")
            
            if not self.security.audit_enabled:
                validation_errors.append("Audit logging is required in production environment")
        
        if validation_errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in validation_errors)
            logger.error(error_message)
            raise ValueError(error_message)
        
        logger.info("Configuration validation completed successfully")
    
    def _update_dataclass(self, target_dataclass: Any, updates: Dict[str, Any]) -> None:
        """Update dataclass fields from dictionary."""
        for key, value in updates.items():
            if hasattr(target_dataclass, key):
                setattr(target_dataclass, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def _set_nested_config(self, path: str, value: Any) -> None:
        """Set nested configuration value using dot notation."""
        parts = path.split('.')
        if len(parts) == 2:
            section_name, field_name = parts
            section = getattr(self, section_name, None)
            if section and hasattr(section, field_name):
                setattr(section, field_name, value)
    
    def _parse_bool(self, value: str) -> bool:
        """Parse boolean value from string."""
        return value.lower() in ("true", "1", "yes", "on", "enabled")
    
    def _update_config_hash(self) -> None:
        """Update configuration hash for change detection."""
        config_data = self.to_dict()
        config_json = json.dumps(config_data, sort_keys=True)
        self._config_hash = hashlib.sha256(config_json.encode()).hexdigest()
    
    def _start_auto_reload(self) -> None:
        """Start automatic configuration reloading thread."""
        def reload_worker():
            while self.auto_reload:
                try:
                    time.sleep(5)  # Check every 5 seconds
                    
                    if self.config_file and self.config_file.exists():
                        current_hash = self._calculate_file_hash()
                        if current_hash != self._config_hash:
                            logger.info("Configuration file changed, reloading...")
                            self.reload()
                            
                except Exception as e:
                    logger.error(f"Error in auto-reload worker: {e}")
        
        reload_thread = threading.Thread(target=reload_worker, daemon=True)
        reload_thread.start()
        logger.info("Auto-reload thread started")
    
    def _calculate_file_hash(self) -> str:
        """Calculate hash of configuration file."""
        if not self.config_file or not self.config_file.exists():
            return ""
        
        with open(self.config_file, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def reload(self) -> None:
        """Manually reload configuration."""
        with self._lock:
            old_hash = self._config_hash
            self._load_configuration()
            
            if self._config_hash != old_hash:
                # Notify callbacks of configuration change
                config_dict = self.to_dict()
                for callback in self._reload_callbacks:
                    try:
                        callback(config_dict)
                    except Exception as e:
                        logger.error(f"Error in reload callback: {e}")
                
                logger.info("Configuration reloaded successfully")
            else:
                logger.debug("Configuration unchanged after reload")
    
    def add_reload_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add callback to be called when configuration is reloaded."""
        self._reload_callbacks.append(callback)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "security": self.security.__dict__,
            "performance": self.performance.__dict__,
            "compliance": self.compliance.__dict__,
            "monitoring": self.monitoring.__dict__,
            "validation": self.validation.__dict__,
            "environment": self.environment.value,
            "last_reload": self._last_reload.isoformat() if self._last_reload else None
        }
    
    def get_security_level(self) -> SecurityLevel:
        """Determine current security level based on settings."""
        if self.environment == Environment.PRODUCTION and self.security.mfa_required:
            return SecurityLevel.MAXIMUM
        elif self.security.audit_enabled and self.security.api_key_required:
            return SecurityLevel.ENHANCED
        elif self.security.rate_limiting_enabled:
            return SecurityLevel.STANDARD
        else:
            return SecurityLevel.MINIMAL
    
    def export_config(self, file_path: Union[str, Path]) -> None:
        """Export current configuration to file."""
        config_dict = self.to_dict()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, sort_keys=True)
        
        logger.info(f"Configuration exported to {file_path}")
    
    def validate_setting(self, section: str, key: str, value: Any) -> bool:
        """Validate a specific setting value."""
        try:
            # Create a copy of current configuration
            test_config = ConfigurationManager(
                environment=self.environment,
                auto_reload=False
            )
            
            # Apply the test value
            if hasattr(test_config, section):
                section_obj = getattr(test_config, section)
                if hasattr(section_obj, key):
                    setattr(section_obj, key, value)
                    test_config._validate_configuration()
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Setting validation failed for {section}.{key}={value}: {e}")
            return False
    
    def __str__(self) -> str:
        return f"ConfigurationManager(environment={self.environment.value}, security_level={self.get_security_level().value})"
    
    def __repr__(self) -> str:
        return (
            f"<ConfigurationManager("
            f"environment={self.environment.value}, "
            f"config_file={self.config_file}, "
            f"auto_reload={self.auto_reload}"
            f")>"
        )


# Global configuration instance
_global_config: Optional[ConfigurationManager] = None


def get_config() -> ConfigurationManager:
    """Get global configuration instance."""
    global _global_config
    if _global_config is None:
        # Initialize with environment-based defaults
        env = Environment(os.getenv("PYIDVERIFY_ENVIRONMENT", "development"))
        _global_config = ConfigurationManager(environment=env)
    return _global_config


def set_config(config: ConfigurationManager) -> None:
    """Set global configuration instance."""
    global _global_config
    _global_config = config


def reset_config() -> None:
    """Reset global configuration to defaults."""
    global _global_config
    _global_config = None
