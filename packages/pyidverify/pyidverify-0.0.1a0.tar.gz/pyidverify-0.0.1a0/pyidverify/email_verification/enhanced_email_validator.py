"""
Enhanced Email Validator Integration
===================================

This module integrates all email verification enhancements into the main EmailValidator:
- Enhanced DNS verification
- SMTP email existence checking
- Third-party API integration
- Hybrid verification strategies
- Behavioral verification workflows

Complete integration for PyIDVerify Email Verification Enhancement System
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Import enhanced verification modules
from .enhanced_dns import EnhancedDNSChecker, DNSCheckResult
from .smtp_verifier import SMTPEmailVerifier, SMTPVerificationResult
from .api_verifier import ThirdPartyEmailVerifier, APIVerificationResult, APIProvider
from .hybrid_verifier import (
    HybridEmailVerifier, 
    HybridVerificationConfig,
    VerificationLevel, 
    HybridStrategy,
    ComprehensiveVerificationResult
)
from .behavioral_verifier import (
    BehavioralEmailVerifier,
    BehavioralVerificationResult,
    VerificationWorkflowType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailVerificationMode(Enum):
    """Email verification modes"""
    BASIC = "basic"                    # Format validation only (original behavior)
    STANDARD = "standard"              # Format + DNS validation
    THOROUGH = "thorough"             # Standard + SMTP or API
    COMPREHENSIVE = "comprehensive"    # All methods with hybrid logic
    BEHAVIORAL = "behavioral"         # Includes behavioral verification

@dataclass
class EnhancedEmailValidationResult:
    """Enhanced email validation result combining all verification methods"""
    
    # Basic validation
    email: str
    is_valid: bool = False
    format_valid: bool = False
    
    # Enhanced verification results
    dns_result: Optional[DNSCheckResult] = None
    smtp_result: Optional[SMTPVerificationResult] = None
    api_result: Optional[APIVerificationResult] = None
    hybrid_result: Optional[ComprehensiveVerificationResult] = None
    behavioral_result: Optional[BehavioralVerificationResult] = None
    
    # Aggregated insights
    exists: Optional[bool] = None
    confidence: float = 0.0
    is_disposable: bool = False
    is_role_account: bool = False
    is_catch_all: Optional[bool] = None
    is_toxic: bool = False
    
    # Recommendations
    recommendation: str = "unknown"
    warnings: List[str] = None
    suggestions: List[str] = None
    
    # Metadata
    verification_mode: EmailVerificationMode = EmailVerificationMode.BASIC
    methods_used: List[str] = None
    total_time: float = 0.0
    cost_incurred: float = 0.0
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.suggestions is None:
            self.suggestions = []
        if self.methods_used is None:
            self.methods_used = []

class EnhancedEmailValidator:
    """
    Enhanced Email Validator with comprehensive verification capabilities
    
    This class extends the original EmailValidator with:
    - Multiple verification levels
    - DNS and domain validation
    - SMTP existence checking
    - Third-party API integration
    - Hybrid verification strategies
    - Behavioral verification workflows
    """
    
    def __init__(self, 
                 default_mode: EmailVerificationMode = EmailVerificationMode.STANDARD,
                 api_config: Optional[Dict[str, str]] = None,
                 smtp_config: Optional[Dict[str, str]] = None):
        """
        Initialize enhanced email validator
        
        Args:
            default_mode: Default verification mode
            api_config: API configuration for third-party services
            smtp_config: SMTP configuration for behavioral verification
        """
        self.default_mode = default_mode
        self.api_config = api_config or {}
        self.smtp_config = smtp_config or {}
        
        # Initialize component validators
        self._dns_checker = None
        self._smtp_verifier = None
        self._api_verifier = None
        self._hybrid_verifier = None
        self._behavioral_verifier = None
        
        # Performance tracking
        self.stats = {
            "total_validations": 0,
            "mode_usage": {mode.value: 0 for mode in EmailVerificationMode},
            "accuracy_stats": {},
            "performance_stats": {}
        }
        
        logger.info(f"Enhanced email validator initialized with mode: {default_mode.value}")
    
    def _ensure_dns_checker(self):
        """Lazy initialization of DNS checker"""
        if self._dns_checker is None:
            self._dns_checker = EnhancedDNSChecker()
    
    def _ensure_smtp_verifier(self):
        """Lazy initialization of SMTP verifier"""
        if self._smtp_verifier is None:
            self._smtp_verifier = SMTPEmailVerifier()
    
    def _ensure_api_verifier(self):
        """Lazy initialization of API verifier"""
        if self._api_verifier is None and self.api_config:
            provider = APIProvider(self.api_config.get("provider", "zerobounce"))
            self._api_verifier = ThirdPartyEmailVerifier(provider)
            
            # Add configured providers
            for provider_name, api_key in self.api_config.items():
                if provider_name != "provider" and api_key:
                    try:
                        provider_enum = APIProvider(provider_name.lower())
                        self._api_verifier.add_provider(provider_enum, api_key)
                    except ValueError:
                        logger.warning(f"Unknown API provider: {provider_name}")
    
    def _ensure_hybrid_verifier(self, mode: EmailVerificationMode):
        """Lazy initialization of hybrid verifier"""
        if self._hybrid_verifier is None:
            # Configure based on mode
            if mode == EmailVerificationMode.STANDARD:
                level = VerificationLevel.STANDARD
                enable_smtp = False
                enable_api = False
            elif mode == EmailVerificationMode.THOROUGH:
                level = VerificationLevel.THOROUGH
                enable_smtp = True
                enable_api = bool(self.api_config)
            else:  # COMPREHENSIVE
                level = VerificationLevel.MAXIMUM
                enable_smtp = True
                enable_api = bool(self.api_config)
            
            config = HybridVerificationConfig(
                verification_level=level,
                strategy=HybridStrategy.BALANCED,
                enable_dns=True,
                enable_smtp=enable_smtp,
                enable_api=enable_api
            )
            
            self._hybrid_verifier = HybridEmailVerifier(config)
    
    def _ensure_behavioral_verifier(self):
        """Lazy initialization of behavioral verifier"""
        if self._behavioral_verifier is None:
            self._behavioral_verifier = BehavioralEmailVerifier(
                smtp_config=self.smtp_config
            )
    
    async def validate_email(self, 
                           email: str, 
                           mode: Optional[EmailVerificationMode] = None,
                           **kwargs) -> EnhancedEmailValidationResult:
        """
        Validate email address with specified verification mode
        
        Args:
            email: Email address to validate
            mode: Verification mode (uses default if not specified)
            **kwargs: Additional parameters for specific verification methods
            
        Returns:
            EnhancedEmailValidationResult with comprehensive validation details
        """
        start_time = asyncio.get_event_loop().time()
        mode = mode or self.default_mode
        
        result = EnhancedEmailValidationResult(
            email=email,
            verification_mode=mode
        )
        
        try:
            # Update statistics
            self.stats["total_validations"] += 1
            self.stats["mode_usage"][mode.value] += 1
            
            # Perform validation based on mode
            if mode == EmailVerificationMode.BASIC:
                await self._validate_basic(result)
            elif mode == EmailVerificationMode.STANDARD:
                await self._validate_standard(result)
            elif mode == EmailVerificationMode.THOROUGH:
                await self._validate_thorough(result)
            elif mode == EmailVerificationMode.COMPREHENSIVE:
                await self._validate_comprehensive(result)
            elif mode == EmailVerificationMode.BEHAVIORAL:
                await self._validate_behavioral(result, kwargs)
            
            # Calculate final recommendation
            self._generate_recommendation(result)
            
            # Update performance stats
            result.total_time = asyncio.get_event_loop().time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Email validation failed for {email}: {e}")
            result.warnings.append(f"Validation error: {str(e)}")
            result.total_time = asyncio.get_event_loop().time() - start_time
            return result
    
    async def _validate_basic(self, result: EnhancedEmailValidationResult):
        """Basic format validation only"""
        result.format_valid = self._is_valid_format(result.email)
        result.is_valid = result.format_valid
        result.methods_used.append("format_validation")
        
        if result.format_valid:
            result.confidence = 0.3  # Low confidence for format-only validation
    
    async def _validate_standard(self, result: EnhancedEmailValidationResult):
        """Standard validation with DNS checks"""
        # Basic format validation
        await self._validate_basic(result)
        
        if not result.format_valid:
            return
        
        # DNS validation
        self._ensure_dns_checker()
        domain = result.email.split('@')[1]
        
        try:
            dns_result = await self._dns_checker.check_domain_comprehensive(domain)
            result.dns_result = dns_result
            result.methods_used.append("dns_validation")
            
            # Update result based on DNS
            result.is_valid = dns_result.valid
            result.is_disposable = dns_result.is_disposable
            result.is_catch_all = dns_result.is_catch_all
            result.confidence = 0.7 if dns_result.valid else 0.1
            
        except Exception as e:
            logger.warning(f"DNS validation failed: {e}")
            result.warnings.append(f"DNS check failed: {str(e)}")
    
    async def _validate_thorough(self, result: EnhancedEmailValidationResult):
        """Thorough validation with SMTP/API checks"""
        # Start with standard validation
        await self._validate_standard(result)
        
        if not result.is_valid:
            return
        
        # Try SMTP verification
        if result.dns_result and result.dns_result.mx_records:
            try:
                self._ensure_smtp_verifier()
                smtp_result = await self._smtp_verifier.verify_email_existence(
                    result.email, result.dns_result.mx_records
                )
                result.smtp_result = smtp_result
                result.methods_used.append("smtp_verification")
                
                if smtp_result.exists is not None:
                    result.exists = smtp_result.exists
                    result.confidence = max(result.confidence, smtp_result.confidence)
                    
            except Exception as e:
                logger.warning(f"SMTP verification failed: {e}")
                result.warnings.append(f"SMTP check failed: {str(e)}")
        
        # Try API verification if SMTP failed or unavailable
        if result.exists is None and self.api_config:
            try:
                self._ensure_api_verifier()
                if self._api_verifier:
                    api_result = await self._api_verifier.verify(result.email)
                    result.api_result = api_result
                    result.methods_used.append("api_verification")
                    
                    if not api_result.error_message:
                        result.exists = api_result.exists
                        result.is_role_account = api_result.is_role_account
                        result.is_toxic = api_result.is_toxic
                        result.confidence = max(result.confidence, api_result.confidence)
                        result.cost_incurred += api_result.credits_used * 0.001
                        
            except Exception as e:
                logger.warning(f"API verification failed: {e}")
                result.warnings.append(f"API check failed: {str(e)}")
    
    async def _validate_comprehensive(self, result: EnhancedEmailValidationResult):
        """Comprehensive validation using hybrid approach"""
        self._ensure_hybrid_verifier(EmailVerificationMode.COMPREHENSIVE)
        
        hybrid_result = await self._hybrid_verifier.verify_email_comprehensive(result.email)
        result.hybrid_result = hybrid_result
        
        # Copy results from hybrid verification
        result.format_valid = hybrid_result.format_valid
        result.is_valid = hybrid_result.final_status not in ["invalid_format", "domain_invalid", "invalid"]
        result.exists = hybrid_result.exists
        result.confidence = hybrid_result.confidence
        result.is_disposable = hybrid_result.is_disposable
        result.is_role_account = hybrid_result.is_role_account
        result.is_catch_all = hybrid_result.is_catch_all
        result.is_toxic = hybrid_result.is_toxic
        result.methods_used.extend(hybrid_result.methods_used)
        result.warnings.extend(hybrid_result.warnings)
        result.cost_incurred = hybrid_result.costs_incurred
    
    async def _validate_behavioral(self, result: EnhancedEmailValidationResult, kwargs: Dict[str, Any]):
        """Behavioral validation with workflow verification"""
        # First do comprehensive validation
        await self._validate_comprehensive(result)
        
        # Then add behavioral verification
        workflow_type = kwargs.get("workflow_type", VerificationWorkflowType.EMAIL_CONFIRMATION)
        
        self._ensure_behavioral_verifier()
        behavioral_result = await self._behavioral_verifier.start_verification_workflow(
            result.email, workflow_type
        )
        
        result.behavioral_result = behavioral_result
        result.methods_used.append("behavioral_verification")
        
        # Note: Behavioral verification is asynchronous and requires user interaction
        result.suggestions.append("Behavioral verification requires user email interaction to complete")
    
    def _is_valid_format(self, email: str) -> bool:
        """Basic email format validation"""
        if not email or '@' not in email:
            return False
            
        if email.count('@') != 1:
            return False
            
        local, domain = email.rsplit('@', 1)
        
        if not local or not domain:
            return False
            
        if len(email) > 254:  # RFC 5321 limit
            return False
            
        # Basic character validation
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False
            
        return True
    
    def _generate_recommendation(self, result: EnhancedEmailValidationResult):
        """Generate final recommendation based on all validation results"""
        if not result.format_valid:
            result.recommendation = "invalid_format"
            result.suggestions.append("Email format is invalid")
            return
        
        if result.is_disposable:
            result.recommendation = "disposable_email"
            result.suggestions.append("Consider requiring a permanent email address")
            return
        
        if result.is_toxic:
            result.recommendation = "toxic_email"
            result.suggestions.append("This email should be blocked - known spam trap")
            return
        
        if result.exists is True:
            if result.confidence >= 0.8:
                result.recommendation = "valid_high_confidence"
                result.suggestions.append("Email is valid and highly likely to be deliverable")
            else:
                result.recommendation = "valid_medium_confidence"
                result.suggestions.append("Email appears valid but confidence is moderate")
        elif result.exists is False:
            result.recommendation = "invalid_email"
            result.suggestions.append("Email does not exist or is not deliverable")
        else:
            if result.confidence >= 0.5:
                result.recommendation = "probably_valid"
                result.suggestions.append("Email is likely valid but needs confirmation")
            else:
                result.recommendation = "uncertain"
                result.suggestions.append("Unable to determine email validity with confidence")
        
        # Additional suggestions based on metadata
        if result.is_catch_all:
            result.suggestions.append("Domain accepts all emails - actual existence uncertain")
        
        if result.is_role_account:
            result.suggestions.append("This is a role-based email (may be managed by multiple people)")
        
        if result.warnings:
            result.suggestions.append("Validation encountered some issues - see warnings")
    
    # Convenience methods for backward compatibility
    async def is_valid_email(self, email: str) -> bool:
        """Check if email is valid (simple boolean result)"""
        result = await self.validate_email(email, EmailVerificationMode.STANDARD)
        return result.is_valid
    
    async def email_exists(self, email: str) -> Optional[bool]:
        """Check if email exists (requires thorough validation)"""
        result = await self.validate_email(email, EmailVerificationMode.THOROUGH)
        return result.exists
    
    async def is_disposable_email(self, email: str) -> bool:
        """Check if email is from a disposable provider"""
        result = await self.validate_email(email, EmailVerificationMode.STANDARD)
        return result.is_disposable
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return self.stats.copy()

# Factory function for easy initialization
def create_enhanced_email_validator(
    verification_level: str = "standard",
    api_providers: Optional[Dict[str, str]] = None,
    smtp_config: Optional[Dict[str, str]] = None
) -> EnhancedEmailValidator:
    """
    Factory function to create enhanced email validator
    
    Args:
        verification_level: "basic", "standard", "thorough", or "comprehensive"
        api_providers: Dictionary of API provider configurations
        smtp_config: SMTP configuration for behavioral verification
        
    Returns:
        Configured EnhancedEmailValidator instance
    """
    try:
        mode = EmailVerificationMode(verification_level.lower())
    except ValueError:
        mode = EmailVerificationMode.STANDARD
        logger.warning(f"Unknown verification level '{verification_level}', using 'standard'")
    
    return EnhancedEmailValidator(
        default_mode=mode,
        api_config=api_providers,
        smtp_config=smtp_config
    )

# Example configurations
EXAMPLE_CONFIGURATIONS = {
    "basic": {
        "description": "Format validation only - fastest and free",
        "config": {
            "verification_level": "basic"
        }
    },
    "standard": {
        "description": "Format + DNS validation - good balance of speed and accuracy",
        "config": {
            "verification_level": "standard"
        }
    },
    "thorough": {
        "description": "Includes SMTP/API verification - higher accuracy but slower",
        "config": {
            "verification_level": "thorough",
            "api_providers": {
                "provider": "zerobounce",
                "zerobounce": "your-zerobounce-api-key"
            }
        }
    },
    "comprehensive": {
        "description": "All verification methods with intelligent hybrid approach",
        "config": {
            "verification_level": "comprehensive",
            "api_providers": {
                "provider": "zerobounce",
                "zerobounce": "your-zerobounce-api-key",
                "hunter": "your-hunter-api-key"
            }
        }
    }
}

if __name__ == "__main__":
    # Test the enhanced email validator
    async def test_enhanced_validator():
        """Test enhanced email validator with different modes"""
        
        test_emails = [
            "user@gmail.com",              # Should be valid
            "test@10minutemail.com",       # Disposable
            "invalid@nonexistent.com",     # Invalid domain
            "not-an-email",                # Invalid format
        ]
        
        modes = [
            EmailVerificationMode.BASIC,
            EmailVerificationMode.STANDARD,
            EmailVerificationMode.THOROUGH
        ]
        
        for mode in modes:
            print(f"\n{'='*60}")
            print(f"Testing Mode: {mode.value.upper()}")
            print(f"{'='*60}")
            
            validator = EnhancedEmailValidator(default_mode=mode)
            
            for email in test_emails:
                print(f"\n🔍 Validating: {email}")
                result = await validator.validate_email(email)
                
                print(f"  Valid: {result.is_valid}")
                print(f"  Exists: {result.exists}")
                print(f"  Confidence: {result.confidence:.2f}")
                print(f"  Disposable: {result.is_disposable}")
                print(f"  Recommendation: {result.recommendation}")
                print(f"  Methods: {result.methods_used}")
                print(f"  Time: {result.total_time:.3f}s")
                
                if result.warnings:
                    print(f"  Warnings: {result.warnings}")
                if result.suggestions:
                    print(f"  Suggestions: {result.suggestions}")
            
            print(f"\n📊 Validator Stats: {validator.get_validation_stats()}")
        
        print(f"\n{'='*60}")
        print("Example Configurations")
        print(f"{'='*60}")
        for name, config in EXAMPLE_CONFIGURATIONS.items():
            print(f"\n{name.upper()}: {config['description']}")
    
    # Run the test
    asyncio.run(test_enhanced_validator())
