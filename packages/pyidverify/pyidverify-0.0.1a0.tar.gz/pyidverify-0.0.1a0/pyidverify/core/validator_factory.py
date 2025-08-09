"""
PyIDVerify Validator Factory

Factory class for creating and managing validator instances.
Provides centralized validator creation with dependency injection
and configuration management.

Author: PyIDVerify Team  
License: MIT
"""

import logging
from typing import Dict, Type, Optional, List
from .types import IDType
from .base_validator import BaseValidator
from .exceptions import ValidationError, ConfigurationError
from ..config.settings import ValidationConfig

logger = logging.getLogger(__name__)


class ValidatorFactory:
    """
    Factory for creating validator instances with proper configuration.
    
    Features:
    - Centralized validator creation
    - Dependency injection
    - Configuration management
    - Lazy loading of validators
    - Plugin system support
    """
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        """Initialize validator factory."""
        self.config = config or ValidationConfig()
        self._validator_classes: Dict[IDType, Type[BaseValidator]] = {}
        self._validator_instances: Dict[IDType, BaseValidator] = {}
        self._registered_plugins: List[str] = []
        
        # Register built-in validators
        self._register_builtin_validators()
        
    def register_validator(self, id_type: IDType, validator_class: Type[BaseValidator]):
        """
        Register a validator class for an ID type.
        
        Args:
            id_type: The ID type this validator handles
            validator_class: The validator class to register
        """
        if not issubclass(validator_class, BaseValidator):
            raise ConfigurationError(f"Validator must inherit from BaseValidator: {validator_class}")
            
        self._validator_classes[id_type] = validator_class
        logger.info(f"Registered validator {validator_class.__name__} for {id_type.value}")
        
    def create_validator(self, id_type: IDType, force_new: bool = False) -> BaseValidator:
        """
        Create or retrieve validator instance for ID type.
        
        Args:
            id_type: The ID type to create validator for
            force_new: Force creation of new instance
            
        Returns:
            BaseValidator instance
            
        Raises:
            ValidationError: If validator not found or creation fails
        """
        # Return cached instance if available and not forcing new
        if not force_new and id_type in self._validator_instances:
            return self._validator_instances[id_type]
            
        # Get validator class
        validator_class = self._validator_classes.get(id_type)
        if not validator_class:
            raise ValidationError(f"No validator registered for {id_type.value}")
            
        try:
            # Create new instance with configuration
            validator = validator_class(self.config)
            
            # Cache instance for reuse
            if not force_new:
                self._validator_instances[id_type] = validator
                
            logger.debug(f"Created validator instance for {id_type.value}")
            return validator
            
        except Exception as e:
            logger.error(f"Failed to create validator for {id_type.value}: {str(e)}")
            raise ValidationError(f"Validator creation failed: {str(e)}")
            
    def get_validator_class(self, id_type: IDType) -> Optional[Type[BaseValidator]]:
        """Get validator class for ID type."""
        return self._validator_classes.get(id_type)
        
    def list_supported_types(self) -> List[IDType]:
        """List all supported ID types."""
        return list(self._validator_classes.keys())
        
    def is_supported(self, id_type: IDType) -> bool:
        """Check if ID type is supported."""
        return id_type in self._validator_classes
        
    def create_all_validators(self) -> Dict[IDType, BaseValidator]:
        """Create instances of all registered validators."""
        validators = {}
        for id_type in self._validator_classes:
            try:
                validators[id_type] = self.create_validator(id_type)
            except Exception as e:
                logger.warning(f"Failed to create validator for {id_type.value}: {str(e)}")
        return validators
        
    def reload_validator(self, id_type: IDType) -> BaseValidator:
        """Reload validator instance with fresh configuration."""
        if id_type in self._validator_instances:
            del self._validator_instances[id_type]
        return self.create_validator(id_type, force_new=True)
        
    def register_plugin(self, plugin_name: str, plugin_module: str):
        """
        Register a validator plugin.
        
        Args:
            plugin_name: Name of the plugin
            plugin_module: Module path containing validators
        """
        try:
            import importlib
            module = importlib.import_module(plugin_module)
            
            # Look for validators in module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseValidator) and 
                    attr != BaseValidator):
                    
                    # Try to determine ID type from validator
                    if hasattr(attr, 'SUPPORTED_TYPE'):
                        id_type = attr.SUPPORTED_TYPE
                        self.register_validator(id_type, attr)
                        
            self._registered_plugins.append(plugin_name)
            logger.info(f"Loaded plugin: {plugin_name}")
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {str(e)}")
            raise ConfigurationError(f"Plugin loading failed: {str(e)}")
            
    def _register_builtin_validators(self):
        """Register built-in validators."""
        try:
            # Import and register built-in validators
            from ..validators.personal.email import EmailValidator
            from ..validators.personal.phone import PhoneValidator
            from ..validators.personal.ip import IPAddressValidator
            from ..validators.financial.credit_card import CreditCardValidator
            from ..validators.financial.bank_account import BankAccountValidator
            from ..validators.government.ssn import SSNValidator
            
            self.register_validator(IDType.EMAIL, EmailValidator)
            self.register_validator(IDType.PHONE, PhoneValidator)
            self.register_validator(IDType.IP_ADDRESS, IPAddressValidator)
            self.register_validator(IDType.CREDIT_CARD, CreditCardValidator)
            self.register_validator(IDType.BANK_ACCOUNT, BankAccountValidator)
            self.register_validator(IDType.SSN, SSNValidator)
            
        except ImportError as e:
            logger.warning(f"Some built-in validators not available: {str(e)}")
        except Exception as e:
            logger.error(f"Error registering built-in validators: {str(e)}")


# Global factory instance
_global_factory: Optional[ValidatorFactory] = None


def get_factory(config: Optional[ValidationConfig] = None) -> ValidatorFactory:
    """Get global validator factory instance."""
    global _global_factory
    if _global_factory is None or config is not None:
        _global_factory = ValidatorFactory(config)
    return _global_factory


def create_validator(id_type: IDType, config: Optional[ValidationConfig] = None) -> BaseValidator:
    """Convenience function to create validator."""
    factory = get_factory(config)
    return factory.create_validator(id_type)


def register_validator(id_type: IDType, validator_class: Type[BaseValidator]):
    """Convenience function to register validator."""
    factory = get_factory()
    factory.register_validator(id_type, validator_class)


def list_supported_types() -> List[IDType]:
    """Convenience function to list supported types."""
    factory = get_factory()
    return factory.list_supported_types()
