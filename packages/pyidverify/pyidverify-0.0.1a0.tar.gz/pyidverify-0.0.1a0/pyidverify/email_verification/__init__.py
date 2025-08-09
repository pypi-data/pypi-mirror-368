"""
PyIDVerify Enhanced Email Verification Package
============================================

This package provides comprehensive email verification capabilities including:

- Enhanced DNS validation with disposable domain detection
- SMTP email existence verification  
- Third-party API integration (ZeroBounce, Hunter.io, NeverBounce)
- Hybrid verification strategies
- Behavioral verification workflows
- Progressive verification levels

Quick Start:
-----------

Basic Usage:
```python
from pyidverify.email_verification import EnhancedEmailValidator

validator = EnhancedEmailValidator()
result = await validator.validate_email("user@example.com")
print(f"Valid: {result.is_valid}, Confidence: {result.confidence}")
```

Advanced Usage:
```python
from pyidverify.email_verification import (
    EnhancedEmailValidator, 
    EmailVerificationMode,
    create_enhanced_email_validator
)

# Create validator with API integration
validator = create_enhanced_email_validator(
    verification_level="comprehensive",
    api_providers={
        "provider": "zerobounce",
        "zerobounce": "your-api-key"
    }
)

result = await validator.validate_email(
    "user@example.com", 
    mode=EmailVerificationMode.COMPREHENSIVE
)
```

Component Modules:
-----------------

- enhanced_dns: Advanced DNS validation with reputation scoring
- smtp_verifier: Safe SMTP email existence checking  
- api_verifier: Third-party API integration layer
- hybrid_verifier: Intelligent multi-method verification
- behavioral_verifier: Email confirmation workflows
- enhanced_email_validator: Main integrated validator

Verification Levels:
------------------

BASIC: Format validation only
STANDARD: Format + DNS validation
THOROUGH: Standard + SMTP/API verification
COMPREHENSIVE: All methods with hybrid intelligence  
BEHAVIORAL: Includes user interaction workflows
"""

# Main classes and functions
from .enhanced_email_validator import (
    EnhancedEmailValidator,
    EmailVerificationMode, 
    EnhancedEmailValidationResult,
    create_enhanced_email_validator,
    EXAMPLE_CONFIGURATIONS
)

# Hybrid verification system
from .hybrid_verifier import (
    HybridEmailVerifier,
    HybridVerificationConfig,
    VerificationLevel,
    HybridStrategy,
    ComprehensiveVerificationResult,
    verify_email_hybrid
)

# Behavioral verification system
from .behavioral_verifier import (
    BehavioralEmailVerifier,
    BehavioralVerificationResult,
    VerificationWorkflowType,
    VerificationToken,
    TokenType,
    verify_email_behavioral
)

# Component verifiers
from .enhanced_dns import (
    EnhancedDNSChecker,
    DNSCheckResult
)

from .smtp_verifier import (
    SMTPEmailVerifier,
    SMTPVerificationResult
)

from .api_verifier import (
    ThirdPartyEmailVerifier,
    APIVerificationResult,
    APIProvider
)

# Convenience functions
from .enhanced_email_validator import create_enhanced_email_validator

# Version info
__version__ = "1.0.0"
__author__ = "PyIDVerify Team"
__description__ = "Enhanced email verification with DNS, SMTP, API, and behavioral validation"

# Package metadata
__all__ = [
    # Main validator
    "EnhancedEmailValidator",
    "EmailVerificationMode",
    "EnhancedEmailValidationResult",
    "create_enhanced_email_validator",
    
    # Hybrid verification
    "HybridEmailVerifier",
    "HybridVerificationConfig", 
    "VerificationLevel",
    "HybridStrategy",
    "ComprehensiveVerificationResult",
    "verify_email_hybrid",
    
    # Behavioral verification
    "BehavioralEmailVerifier",
    "BehavioralVerificationResult",
    "VerificationWorkflowType",
    "VerificationToken",
    "TokenType",
    "verify_email_behavioral",
    
    # Component verifiers
    "EnhancedDNSChecker",
    "DNSCheckResult",
    "SMTPEmailVerifier", 
    "SMTPVerificationResult",
    "ThirdPartyEmailVerifier",
    "APIVerificationResult",
    "APIProvider",
    
    # Configuration examples
    "EXAMPLE_CONFIGURATIONS"
]

# Backward compatibility aliases
EmailValidator = EnhancedEmailValidator
validate_email = lambda email, **kwargs: create_enhanced_email_validator().validate_email(email, **kwargs)

def get_package_info():
    """Get package information"""
    return {
        "name": "pyidverify.email_verification", 
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "components": [
            "Enhanced DNS Checker",
            "SMTP Email Verifier", 
            "Third-party API Integration",
            "Hybrid Verification System",
            "Behavioral Verification Workflows"
        ],
        "verification_levels": [level.value for level in EmailVerificationMode],
        "supported_api_providers": [provider.value for provider in APIProvider]
    }

def print_usage_examples():
    """Print usage examples"""
    examples = """
PyIDVerify Enhanced Email Verification - Usage Examples
======================================================

1. Basic Format Validation:
   validator = EnhancedEmailValidator(default_mode=EmailVerificationMode.BASIC)
   result = await validator.validate_email("user@example.com")

2. Standard DNS Validation:
   validator = EnhancedEmailValidator(default_mode=EmailVerificationMode.STANDARD)
   result = await validator.validate_email("user@example.com")

3. Thorough Verification with API:
   validator = create_enhanced_email_validator(
       verification_level="thorough",
       api_providers={"zerobounce": "your-api-key"}
   )
   result = await validator.validate_email("user@example.com")

4. Comprehensive Hybrid Verification:
   result = await verify_email_hybrid(
       "user@example.com", 
       level=VerificationLevel.MAXIMUM,
       strategy=HybridStrategy.ACCURACY_FOCUSED
   )

5. Behavioral Verification Workflow:
   result = await verify_email_behavioral(
       "user@example.com",
       workflow_type=VerificationWorkflowType.DOUBLE_OPTIN,
       smtp_config={"host": "smtp.gmail.com", ...}
   )

6. Quick Validation Functions:
   validator = EnhancedEmailValidator()
   is_valid = await validator.is_valid_email("user@example.com")
   exists = await validator.email_exists("user@example.com") 
   is_disposable = await validator.is_disposable_email("test@10minutemail.com")
"""
    print(examples)

# Initialize logging for the package
import logging
logger = logging.getLogger(__name__)
logger.info(f"PyIDVerify Enhanced Email Verification v{__version__} loaded")
