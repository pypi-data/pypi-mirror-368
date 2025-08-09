"""
Configuration Management Module

Comprehensive configuration system for PyIDVerify including settings management,
schema validation, pattern libraries, and country-specific data.

This module provides:
- Security-focused configuration management with hot reloading
- Comprehensive schema validation with detailed error reporting
- Extensive pattern library with ReDoS protection
- Country-specific validation rules and regulatory compliance
- Multi-format configuration file support (JSON, YAML, TOML)
- Environment variable integration with type conversion
- Configuration templates and documentation generation

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Core configuration management
from .settings import (
    Environment,
    SecurityLevel,
    SecuritySettings,
    PerformanceSettings,
    ComplianceSettings,
    MonitoringSettings,
    ValidationSettings,
    ConfigurationManager,
    get_config,
    set_config,
    reset_config
)

# Configuration loading and validation
from .loader import (
    ConfigFormat,
    ValidationSeverity,
    ValidationIssue,
    SchemaField,
    SchemaSection,
    ConfigurationSchema,
    ConfigurationLoader
)

# Pattern library and security
from .patterns import (
    PatternType,
    PatternSecurity,
    PatternInfo,
    PatternSecurityAnalyzer,
    PatternLibrary,
    get_patterns,
    set_patterns
)

# Country-specific data
from .countries import (
    Region,
    RegulatoryFramework,
    PhoneNumberInfo,
    PostalCodeInfo,
    IDFormatInfo,
    CountryInfo,
    CountryDatabase,
    get_countries,
    set_countries
)

# Configure logging
logger = logging.getLogger('pyidverify.config')

# Module metadata
__version__ = "1.0.0"
__api_version__ = "1.0"

# Export public API
__all__ = [
    # Core Settings
    'Environment',
    'SecurityLevel',
    'SecuritySettings',
    'PerformanceSettings',
    'ComplianceSettings',
    'MonitoringSettings',
    'ValidationSettings',
    'ConfigurationManager',
    'get_config',
    'set_config',
    'reset_config',
    
    # Configuration Loading
    'ConfigFormat',
    'ValidationSeverity',
    'ValidationIssue',
    'SchemaField',
    'SchemaSection',
    'ConfigurationSchema',
    'ConfigurationLoader',
    
    # Pattern Management
    'PatternType',
    'PatternSecurity',
    'PatternInfo',
    'PatternSecurityAnalyzer',
    'PatternLibrary',
    'get_patterns',
    'set_patterns',
    
    # Country Data
    'Region',
    'RegulatoryFramework',
    'PhoneNumberInfo',
    'PostalCodeInfo',
    'IDFormatInfo',
    'CountryInfo',
    'CountryDatabase',
    'get_countries',
    'set_countries',
    
    # Utilities
    'create_default_config',
    'load_config_from_file',
    'validate_config_file',
    'generate_config_template',
    'get_pattern_security_report',
    'get_country_validation_rules',
    'get_config_info'
]


def create_default_config(environment: Environment = Environment.DEVELOPMENT) -> ConfigurationManager:
    """
    Create a default configuration for the specified environment.
    
    Args:
        environment: Target environment
        
    Returns:
        Configured ConfigurationManager instance
    """
    config = ConfigurationManager(
        environment=environment,
        auto_reload=environment != Environment.PRODUCTION
    )
    
    logger.info(f"Created default configuration for {environment.value} environment")
    return config


def load_config_from_file(
    file_path: Union[str, Path],
    environment: Environment = Environment.DEVELOPMENT,
    auto_reload: bool = True
) -> ConfigurationManager:
    """
    Load configuration from file.
    
    Args:
        file_path: Path to configuration file
        environment: Target environment
        auto_reload: Enable automatic reloading
        
    Returns:
        Configured ConfigurationManager instance
    """
    config = ConfigurationManager(
        config_file=file_path,
        environment=environment,
        auto_reload=auto_reload
    )
    
    logger.info(f"Loaded configuration from {file_path}")
    return config


def validate_config_file(file_path: Union[str, Path]) -> List[ValidationIssue]:
    """
    Validate a configuration file against the schema.
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        List of validation issues
    """
    loader = ConfigurationLoader()
    
    try:
        config_dict = loader.load_from_file(file_path)
        issues = loader.schema.validate_config(config_dict)
        
        logger.info(f"Configuration validation completed: {len(issues)} issues found")
        return issues
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR,
            path="file",
            message=f"Failed to load configuration file: {e}"
        )]


def generate_config_template(
    file_path: Union[str, Path],
    format_type: ConfigFormat = ConfigFormat.JSON
) -> None:
    """
    Generate a configuration template file.
    
    Args:
        file_path: Output file path
        format_type: Configuration file format
    """
    loader = ConfigurationLoader()
    loader.generate_template(file_path, format_type)
    
    logger.info(f"Configuration template generated: {file_path}")


def get_pattern_security_report() -> Dict[str, Any]:
    """
    Get comprehensive security report for all validation patterns.
    
    Returns:
        Pattern security report
    """
    patterns = get_patterns()
    report = patterns.get_security_report()
    
    logger.info("Generated pattern security report")
    return report


def get_country_validation_rules(country_code: str) -> Dict[str, Any]:
    """
    Get validation rules for a specific country.
    
    Args:
        country_code: ISO Alpha-2 country code
        
    Returns:
        Country validation rules
    """
    countries = get_countries()
    rules = countries.get_validation_requirements(country_code.upper())
    
    if rules:
        logger.debug(f"Retrieved validation rules for {country_code}")
    else:
        logger.warning(f"No validation rules found for country: {country_code}")
    
    return rules


def get_config_info() -> Dict[str, Any]:
    """
    Get comprehensive configuration module information.
    
    Returns:
        Configuration module information
    """
    patterns = get_patterns()
    countries = get_countries()
    config = get_config()
    
    return {
        "module_version": __version__,
        "api_version": __api_version__,
        "environment": config.environment.value,
        "security_level": config.get_security_level().value,
        "pattern_statistics": {
            "total_groups": len(patterns.patterns),
            "total_patterns": sum(len(group) for group in patterns.patterns.values()),
            "security_report": patterns.get_security_report()
        },
        "country_statistics": countries.get_statistics(),
        "configuration_sections": [
            "security",
            "performance", 
            "compliance",
            "monitoring",
            "validation"
        ],
        "supported_formats": [
            ConfigFormat.JSON.value,
            ConfigFormat.YAML.value if hasattr(loader, '_load_yaml') else None,
            ConfigFormat.TOML.value if hasattr(loader, '_load_toml') else None
        ],
        "features": [
            "Hot configuration reloading",
            "Comprehensive schema validation",
            "ReDoS pattern protection",
            "Country-specific validation rules",
            "Regulatory compliance support",
            "Multi-format configuration files",
            "Environment variable integration",
            "Security-focused defaults"
        ]
    }


# Initialize configuration components
def _initialize_config_module() -> None:
    """Initialize configuration module components."""
    logger.info(f"PyIDVerify Configuration Module v{__version__} initialized")
    
    # Initialize global instances (lazy loading)
    # They will be created when first accessed via get_* functions
    
    # Log feature availability
    features = []
    
    try:
        import yaml
        features.append("YAML configuration support")
    except ImportError:
        logger.debug("YAML support not available (install PyYAML)")
    
    try:
        import toml
        features.append("TOML configuration support")
    except ImportError:
        logger.debug("TOML support not available (install toml)")
    
    if features:
        logger.info(f"Configuration features available: {', '.join(features)}")


# Initialize on import
_initialize_config_module()
