"""
Configuration Loader and Schema Validation

Advanced configuration loading system with comprehensive schema validation,
type checking, and secure configuration file handling.

Features:
- JSON/YAML/TOML configuration file support
- Comprehensive schema validation with detailed error reporting
- Type conversion and validation
- Configuration merging from multiple sources
- Encrypted configuration values support
- Configuration templates and inheritance
- Schema evolution and migration support

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional, Union, Type, Callable, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import re
from datetime import datetime
import hashlib

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

from .settings import Environment, SecurityLevel

# Configure logging
logger = logging.getLogger('pyidverify.config.loader')


class ConfigFormat(Enum):
    """Supported configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    ENV = "env"


class ValidationSeverity(Enum):
    """Validation error severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Configuration validation issue."""
    severity: ValidationSeverity
    path: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class SchemaField:
    """Schema field definition."""
    name: str
    type: Type
    required: bool = True
    default: Any = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    choices: Optional[List[Any]] = None
    validator: Optional[Callable[[Any], bool]] = None
    description: Optional[str] = None
    sensitive: bool = False
    deprecated: bool = False
    since_version: Optional[str] = None


@dataclass
class SchemaSection:
    """Schema section definition."""
    name: str
    fields: Dict[str, SchemaField]
    required: bool = True
    description: Optional[str] = None
    since_version: Optional[str] = None


class ConfigurationSchema:
    """
    Configuration schema definition and validation system.
    """
    
    def __init__(self):
        """Initialize configuration schema."""
        self.sections = self._build_schema()
    
    def _build_schema(self) -> Dict[str, SchemaSection]:
        """Build comprehensive configuration schema."""
        return {
            "security": self._build_security_schema(),
            "performance": self._build_performance_schema(),
            "compliance": self._build_compliance_schema(),
            "monitoring": self._build_monitoring_schema(),
            "validation": self._build_validation_schema()
        }
    
    def _build_security_schema(self) -> SchemaSection:
        """Build security configuration schema."""
        fields = {
            "encryption_algorithm": SchemaField(
                name="encryption_algorithm",
                type=str,
                choices=["AES-256-GCM", "ChaCha20-Poly1305", "AES-256-CBC"],
                default="AES-256-GCM",
                description="Primary encryption algorithm for sensitive data"
            ),
            "key_derivation_iterations": SchemaField(
                name="key_derivation_iterations",
                type=int,
                min_value=10000,
                max_value=1000000,
                default=100000,
                description="PBKDF2 iteration count for key derivation"
            ),
            "key_rotation_interval_hours": SchemaField(
                name="key_rotation_interval_hours",
                type=int,
                min_value=1,
                max_value=8760,  # 1 year
                default=24,
                description="Hours between automatic key rotations"
            ),
            "hash_algorithm": SchemaField(
                name="hash_algorithm",
                type=str,
                choices=["Argon2id", "bcrypt", "scrypt"],
                default="Argon2id",
                description="Password hashing algorithm"
            ),
            "hash_memory_cost": SchemaField(
                name="hash_memory_cost",
                type=int,
                min_value=1024,
                max_value=1048576,  # 1GB
                default=65536,
                description="Memory cost for Argon2 hashing (KB)"
            ),
            "hash_time_cost": SchemaField(
                name="hash_time_cost",
                type=int,
                min_value=1,
                max_value=10,
                default=3,
                description="Time cost for Argon2 hashing"
            ),
            "audit_enabled": SchemaField(
                name="audit_enabled",
                type=bool,
                default=True,
                description="Enable comprehensive audit logging"
            ),
            "audit_retention_days": SchemaField(
                name="audit_retention_days",
                type=int,
                min_value=30,
                max_value=3650,  # 10 years
                default=2555,  # 7 years
                description="Days to retain audit logs"
            ),
            "api_key_required": SchemaField(
                name="api_key_required",
                type=bool,
                default=True,
                description="Require API key authentication"
            ),
            "mfa_required": SchemaField(
                name="mfa_required",
                type=bool,
                default=False,
                description="Require multi-factor authentication"
            ),
            "rate_limiting_enabled": SchemaField(
                name="rate_limiting_enabled",
                type=bool,
                default=True,
                description="Enable request rate limiting"
            ),
            "rate_limit_requests_per_minute": SchemaField(
                name="rate_limit_requests_per_minute",
                type=int,
                min_value=1,
                max_value=10000,
                default=100,
                description="Maximum requests per minute per client"
            ),
            "pii_detection_enabled": SchemaField(
                name="pii_detection_enabled",
                type=bool,
                default=True,
                description="Enable automatic PII detection and protection"
            )
        }
        
        return SchemaSection(
            name="security",
            fields=fields,
            description="Security and encryption configuration"
        )
    
    def _build_performance_schema(self) -> SchemaSection:
        """Build performance configuration schema."""
        fields = {
            "caching_enabled": SchemaField(
                name="caching_enabled",
                type=bool,
                default=True,
                description="Enable result caching for improved performance"
            ),
            "cache_ttl_seconds": SchemaField(
                name="cache_ttl_seconds",
                type=int,
                min_value=0,
                max_value=86400,  # 24 hours
                default=300,
                description="Cache time-to-live in seconds"
            ),
            "cache_max_size": SchemaField(
                name="cache_max_size",
                type=int,
                min_value=100,
                max_value=1000000,
                default=10000,
                description="Maximum number of cached entries"
            ),
            "max_batch_size": SchemaField(
                name="max_batch_size",
                type=int,
                min_value=1,
                max_value=10000,
                default=1000,
                description="Maximum items per batch validation request"
            ),
            "batch_timeout_seconds": SchemaField(
                name="batch_timeout_seconds",
                type=int,
                min_value=1,
                max_value=300,
                default=30,
                description="Timeout for batch processing operations"
            ),
            "validation_timeout_seconds": SchemaField(
                name="validation_timeout_seconds",
                type=int,
                min_value=1,
                max_value=60,
                default=10,
                description="Timeout for individual validation operations"
            ),
            "connection_pool_size": SchemaField(
                name="connection_pool_size",
                type=int,
                min_value=1,
                max_value=100,
                default=20,
                description="Database connection pool size"
            ),
            "memory_limit_mb": SchemaField(
                name="memory_limit_mb",
                type=int,
                min_value=128,
                max_value=8192,
                default=512,
                description="Memory limit in megabytes"
            )
        }
        
        return SchemaSection(
            name="performance",
            fields=fields,
            description="Performance and optimization settings"
        )
    
    def _build_compliance_schema(self) -> SchemaSection:
        """Build compliance configuration schema."""
        fields = {
            "gdpr_enabled": SchemaField(
                name="gdpr_enabled",
                type=bool,
                default=True,
                description="Enable GDPR compliance features"
            ),
            "gdpr_data_retention_days": SchemaField(
                name="gdpr_data_retention_days",
                type=int,
                min_value=1,
                max_value=3650,
                default=730,
                description="GDPR data retention period in days"
            ),
            "hipaa_enabled": SchemaField(
                name="hipaa_enabled",
                type=bool,
                default=False,
                description="Enable HIPAA compliance features"
            ),
            "pci_dss_enabled": SchemaField(
                name="pci_dss_enabled",
                type=bool,
                default=False,
                description="Enable PCI DSS compliance features"
            ),
            "sox_enabled": SchemaField(
                name="sox_enabled",
                type=bool,
                default=False,
                description="Enable SOX compliance features"
            )
        }
        
        return SchemaSection(
            name="compliance",
            fields=fields,
            description="Regulatory compliance settings"
        )
    
    def _build_monitoring_schema(self) -> SchemaSection:
        """Build monitoring configuration schema."""
        fields = {
            "metrics_enabled": SchemaField(
                name="metrics_enabled",
                type=bool,
                default=True,
                description="Enable metrics collection"
            ),
            "health_check_enabled": SchemaField(
                name="health_check_enabled",
                type=bool,
                default=True,
                description="Enable health check endpoint"
            ),
            "log_level": SchemaField(
                name="log_level",
                type=str,
                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                default="INFO",
                description="Logging level"
            ),
            "log_format": SchemaField(
                name="log_format",
                type=str,
                choices=["json", "text"],
                default="json",
                description="Log output format"
            ),
            "alerting_enabled": SchemaField(
                name="alerting_enabled",
                type=bool,
                default=True,
                description="Enable alerting system"
            ),
            "error_rate_threshold": SchemaField(
                name="error_rate_threshold",
                type=float,
                min_value=0.0,
                max_value=1.0,
                default=0.05,
                description="Error rate threshold for alerts"
            )
        }
        
        return SchemaSection(
            name="monitoring",
            fields=fields,
            description="Monitoring and observability settings"
        )
    
    def _build_validation_schema(self) -> SchemaSection:
        """Build validation configuration schema."""
        fields = {
            "strict_mode": SchemaField(
                name="strict_mode",
                type=bool,
                default=True,
                description="Enable strict validation mode"
            ),
            "email_mx_check_enabled": SchemaField(
                name="email_mx_check_enabled",
                type=bool,
                default=True,
                description="Enable email MX record validation"
            ),
            "phone_carrier_check_enabled": SchemaField(
                name="phone_carrier_check_enabled",
                type=bool,
                default=False,
                description="Enable phone carrier validation"
            ),
            "credit_card_luhn_validation": SchemaField(
                name="credit_card_luhn_validation",
                type=bool,
                default=True,
                description="Enable Luhn algorithm validation for credit cards"
            ),
            "government_id_audit_logging": SchemaField(
                name="government_id_audit_logging",
                type=bool,
                default=True,
                description="Enable enhanced audit logging for government IDs"
            )
        }
        
        return SchemaSection(
            name="validation",
            fields=fields,
            description="Validation behavior settings"
        )
    
    def validate_config(self, config: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check for unknown sections
        for section_name in config.keys():
            if section_name not in self.sections:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    path=section_name,
                    message=f"Unknown configuration section: {section_name}",
                    suggestion=f"Valid sections: {', '.join(self.sections.keys())}"
                ))
        
        # Validate each known section
        for section_name, section_schema in self.sections.items():
            section_config = config.get(section_name, {})
            section_issues = self._validate_section(section_name, section_config, section_schema)
            issues.extend(section_issues)
        
        return issues
    
    def _validate_section(self, section_name: str, section_config: Dict[str, Any], schema: SchemaSection) -> List[ValidationIssue]:
        """Validate a configuration section."""
        issues = []
        
        # Check for unknown fields
        for field_name in section_config.keys():
            if field_name not in schema.fields:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    path=f"{section_name}.{field_name}",
                    message=f"Unknown configuration field: {field_name}",
                    suggestion=f"Valid fields: {', '.join(schema.fields.keys())}"
                ))
        
        # Validate each schema field
        for field_name, field_schema in schema.fields.items():
            field_path = f"{section_name}.{field_name}"
            field_value = section_config.get(field_name)
            
            field_issues = self._validate_field(field_path, field_value, field_schema)
            issues.extend(field_issues)
        
        return issues
    
    def _validate_field(self, field_path: str, value: Any, schema: SchemaField) -> List[ValidationIssue]:
        """Validate a single configuration field."""
        issues = []
        
        # Check if required field is missing
        if schema.required and value is None:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                path=field_path,
                message=f"Required field missing: {schema.name}",
                suggestion=f"Set {field_path} to a valid {schema.type.__name__} value"
            ))
            return issues
        
        # Skip validation if field is not provided and not required
        if value is None:
            return issues
        
        # Check deprecated fields
        if schema.deprecated:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                path=field_path,
                message=f"Deprecated field: {schema.name}",
                suggestion="Consider updating configuration to remove deprecated field"
            ))
        
        # Type validation
        if not isinstance(value, schema.type):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                path=field_path,
                message=f"Invalid type for {schema.name}",
                expected=schema.type.__name__,
                actual=type(value).__name__,
                suggestion=f"Convert {field_path} to {schema.type.__name__}"
            ))
            return issues  # Skip further validation if type is wrong
        
        # Range validation for numeric types
        if isinstance(value, (int, float)):
            if schema.min_value is not None and value < schema.min_value:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    path=field_path,
                    message=f"Value below minimum: {value} < {schema.min_value}",
                    suggestion=f"Set {field_path} to at least {schema.min_value}"
                ))
            
            if schema.max_value is not None and value > schema.max_value:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    path=field_path,
                    message=f"Value above maximum: {value} > {schema.max_value}",
                    suggestion=f"Set {field_path} to at most {schema.max_value}"
                ))
        
        # Length validation for strings and collections
        if hasattr(value, '__len__'):
            if schema.min_length is not None and len(value) < schema.min_length:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    path=field_path,
                    message=f"Length below minimum: {len(value)} < {schema.min_length}",
                    suggestion=f"Ensure {field_path} has at least {schema.min_length} characters/items"
                ))
            
            if schema.max_length is not None and len(value) > schema.max_length:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    path=field_path,
                    message=f"Length above maximum: {len(value)} > {schema.max_length}",
                    suggestion=f"Ensure {field_path} has at most {schema.max_length} characters/items"
                ))
        
        # Pattern validation for strings
        if isinstance(value, str) and schema.pattern:
            if not re.match(schema.pattern, value):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    path=field_path,
                    message=f"Value does not match required pattern: {schema.pattern}",
                    actual=value,
                    suggestion=f"Ensure {field_path} matches the required pattern"
                ))
        
        # Choice validation
        if schema.choices and value not in schema.choices:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                path=field_path,
                message=f"Invalid choice: {value}",
                actual=str(value),
                expected=f"One of: {', '.join(str(c) for c in schema.choices)}",
                suggestion=f"Set {field_path} to one of the valid choices"
            ))
        
        # Custom validator
        if schema.validator and not schema.validator(value):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                path=field_path,
                message=f"Custom validation failed for {schema.name}",
                actual=str(value),
                suggestion="Check the value meets custom validation requirements"
            ))
        
        return issues


class ConfigurationLoader:
    """
    Advanced configuration loader with multi-format support and validation.
    """
    
    def __init__(self, schema: Optional[ConfigurationSchema] = None):
        """
        Initialize configuration loader.
        
        Args:
            schema: Configuration schema for validation
        """
        self.schema = schema or ConfigurationSchema()
    
    def load_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Determine format from extension
        format_type = self._detect_format(file_path)
        
        # Load configuration based on format
        if format_type == ConfigFormat.JSON:
            return self._load_json(file_path)
        elif format_type == ConfigFormat.YAML:
            return self._load_yaml(file_path)
        elif format_type == ConfigFormat.TOML:
            return self._load_toml(file_path)
        else:
            raise ValueError(f"Unsupported configuration format: {file_path.suffix}")
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load and validate configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Validated configuration dictionary
        """
        # Validate configuration
        issues = self.schema.validate_config(config_dict)
        
        # Check for validation errors
        errors = [issue for issue in issues if issue.severity == ValidationSeverity.ERROR]
        if errors:
            error_messages = [f"{issue.path}: {issue.message}" for issue in errors]
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(error_messages))
        
        # Log warnings
        warnings = [issue for issue in issues if issue.severity == ValidationSeverity.WARNING]
        for warning in warnings:
            logger.warning(f"Configuration warning - {warning.path}: {warning.message}")
        
        return config_dict
    
    def load_from_environment(self, prefix: str = "PYIDVERIFY_") -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Args:
            prefix: Environment variable prefix
            
        Returns:
            Configuration dictionary
        """
        config = {}
        
        # Map environment variables to configuration structure
        env_mappings = self._get_environment_mappings(prefix)
        
        for env_var, (config_path, converter) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    converted_value = converter(env_value)
                    self._set_nested_value(config, config_path, converted_value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment variable {env_var}={env_value}: {e}")
        
        return config
    
    def merge_configurations(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.
        
        Args:
            *configs: Configuration dictionaries to merge
            
        Returns:
            Merged configuration dictionary
        """
        merged = {}
        
        for config in configs:
            merged = self._deep_merge(merged, config)
        
        return merged
    
    def _detect_format(self, file_path: Path) -> ConfigFormat:
        """Detect configuration file format from extension."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.json':
            return ConfigFormat.JSON
        elif suffix in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML is required for YAML configuration files")
            return ConfigFormat.YAML
        elif suffix == '.toml':
            if not TOML_AVAILABLE:
                raise ImportError("toml is required for TOML configuration files")
            return ConfigFormat.TOML
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}")
    
    def _load_toml(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except toml.TomlDecodeError as e:
            raise ValueError(f"Invalid TOML in {file_path}: {e}")
    
    def _get_environment_mappings(self, prefix: str) -> Dict[str, tuple]:
        """Get mappings from environment variables to configuration paths."""
        return {
            f"{prefix}ENCRYPTION_ALGORITHM": ("security.encryption_algorithm", str),
            f"{prefix}AUDIT_ENABLED": ("security.audit_enabled", self._parse_bool),
            f"{prefix}API_KEY_REQUIRED": ("security.api_key_required", self._parse_bool),
            f"{prefix}CACHE_ENABLED": ("performance.caching_enabled", self._parse_bool),
            f"{prefix}CACHE_TTL": ("performance.cache_ttl_seconds", int),
            f"{prefix}MAX_BATCH_SIZE": ("performance.max_batch_size", int),
            f"{prefix}LOG_LEVEL": ("monitoring.log_level", str),
            f"{prefix}METRICS_ENABLED": ("monitoring.metrics_enabled", self._parse_bool),
            f"{prefix}STRICT_MODE": ("validation.strict_mode", self._parse_bool),
            f"{prefix}GDPR_ENABLED": ("compliance.gdpr_enabled", self._parse_bool),
        }
    
    def _parse_bool(self, value: str) -> bool:
        """Parse boolean value from string."""
        return value.lower() in ("true", "1", "yes", "on", "enabled")
    
    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any) -> None:
        """Set nested value in configuration dictionary."""
        parts = path.split('.')
        current = config
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def generate_template(self, file_path: Union[str, Path], format_type: ConfigFormat = ConfigFormat.JSON) -> None:
        """
        Generate configuration template file.
        
        Args:
            file_path: Output file path
            format_type: Configuration format
        """
        template = self._build_template()
        
        if format_type == ConfigFormat.JSON:
            self._write_json_template(file_path, template)
        elif format_type == ConfigFormat.YAML:
            self._write_yaml_template(file_path, template)
        elif format_type == ConfigFormat.TOML:
            self._write_toml_template(file_path, template)
        
        logger.info(f"Configuration template generated: {file_path}")
    
    def _build_template(self) -> Dict[str, Any]:
        """Build configuration template with defaults and documentation."""
        template = {}
        
        for section_name, section_schema in self.schema.sections.items():
            section_template = {}
            
            for field_name, field_schema in section_schema.fields.items():
                if field_schema.default is not None:
                    section_template[field_name] = field_schema.default
                else:
                    # Provide example values based on type
                    if field_schema.type == str:
                        section_template[field_name] = "example_value"
                    elif field_schema.type == int:
                        section_template[field_name] = 0
                    elif field_schema.type == float:
                        section_template[field_name] = 0.0
                    elif field_schema.type == bool:
                        section_template[field_name] = False
                    elif field_schema.type == list:
                        section_template[field_name] = []
            
            template[section_name] = section_template
        
        return template
    
    def _write_json_template(self, file_path: Union[str, Path], template: Dict[str, Any]) -> None:
        """Write JSON configuration template."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, sort_keys=True)
    
    def _write_yaml_template(self, file_path: Union[str, Path], template: Dict[str, Any]) -> None:
        """Write YAML configuration template."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required to generate YAML templates")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=True)
    
    def _write_toml_template(self, file_path: Union[str, Path], template: Dict[str, Any]) -> None:
        """Write TOML configuration template."""
        if not TOML_AVAILABLE:
            raise ImportError("toml is required to generate TOML templates")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            toml.dump(template, f)
