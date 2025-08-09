"""
Hybrid Email Verification System
================================

This module combines multiple verification methods for optimal accuracy and cost-effectiveness:
- Progressive verification levels (BASIC, STANDARD, THOROUGH, MAXIMUM)
- Intelligent fallback strategies
- Cost optimization algorithms
- Comprehensive result aggregation
- Confidence scoring system

Phase 4 Implementation for PyIDVerify Email Verification Enhancement
"""

import asyncio
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

# Import our verification modules
from .enhanced_dns import EnhancedDNSChecker, DNSCheckResult
from .smtp_verifier import SMTPEmailVerifier, SMTPVerificationResult
from .api_verifier import ThirdPartyEmailVerifier, APIVerificationResult, APIProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerificationLevel(Enum):
    """Email verification thoroughness levels"""
    BASIC = 1       # Format validation only
    STANDARD = 2    # Format + DNS + Disposable checking
    THOROUGH = 3    # Standard + SMTP or API verification
    MAXIMUM = 4     # All verification methods with redundancy

class HybridStrategy(Enum):
    """Strategies for combining verification methods"""
    COST_OPTIMIZED = "cost_optimized"      # Minimize API costs
    ACCURACY_FOCUSED = "accuracy_focused"   # Maximum accuracy regardless of cost
    SPEED_OPTIMIZED = "speed_optimized"     # Fastest results
    BALANCED = "balanced"                   # Balance of cost, speed, and accuracy

@dataclass
class HybridVerificationConfig:
    """Configuration for hybrid email verification"""
    verification_level: VerificationLevel = VerificationLevel.STANDARD
    strategy: HybridStrategy = HybridStrategy.BALANCED
    
    # Component enablement
    enable_dns: bool = True
    enable_smtp: bool = False  # Default off due to potential blocking
    enable_api: bool = False   # Requires API keys and costs money
    
    # API configuration
    api_provider: Optional[APIProvider] = None
    api_key: Optional[str] = None
    api_fallback_providers: List[APIProvider] = field(default_factory=list)
    
    # Performance settings
    dns_timeout: float = 10.0
    smtp_timeout: float = 30.0
    api_timeout: float = 30.0
    max_concurrent_checks: int = 3
    
    # Cost optimization
    api_cost_threshold: float = 0.01  # Max cost per verification
    cache_results: bool = True
    cache_ttl_hours: int = 24
    
    # Quality thresholds
    min_confidence_threshold: float = 0.7
    require_definitive_result: bool = False

@dataclass 
class ComprehensiveVerificationResult:
    """Comprehensive result combining all verification methods"""
    email: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Overall results
    final_status: str = "unknown"          # verified, invalid, probably_valid, etc.
    exists: Optional[bool] = None          # True/False/None if uncertain
    confidence: float = 0.0                # Overall confidence 0.0-1.0
    definitive: bool = False               # Whether result is definitive
    
    # Component results
    format_valid: bool = False
    format_errors: List[str] = field(default_factory=list)
    
    dns_result: Optional[DNSCheckResult] = None
    smtp_result: Optional[SMTPVerificationResult] = None
    api_result: Optional[APIVerificationResult] = None
    
    # Aggregated metadata
    is_disposable: bool = False
    is_role_account: bool = False
    is_catch_all: Optional[bool] = None
    is_toxic: bool = False
    mx_records: List[str] = field(default_factory=list)
    domain_reputation: float = 0.5
    
    # Performance metrics
    total_verification_time: float = 0.0
    methods_used: List[str] = field(default_factory=list)
    costs_incurred: float = 0.0
    
    # Additional details
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class HybridEmailVerifier:
    """
    Hybrid email verification system combining multiple methods
    """
    
    def __init__(self, config: HybridVerificationConfig):
        self.config = config
        
        # Initialize component verifiers
        self.dns_checker = EnhancedDNSChecker(
            timeout=config.dns_timeout
        ) if config.enable_dns else None
        
        self.smtp_verifier = SMTPEmailVerifier(
            timeout=config.smtp_timeout
        ) if config.enable_smtp else None
        
        self.api_verifier = None
        if config.enable_api and config.api_key:
            self.api_verifier = ThirdPartyEmailVerifier(config.api_provider or APIProvider.ZEROBOUNCE)
            self.api_verifier.add_provider(config.api_provider, config.api_key)
            
            # Add fallback providers
            for fallback_provider, fallback_key in zip(config.api_fallback_providers, 
                                                     [config.api_key] * len(config.api_fallback_providers)):
                try:
                    self.api_verifier.add_provider(fallback_provider, fallback_key)
                except Exception as e:
                    logger.warning(f"Could not add fallback provider {fallback_provider}: {e}")
        
        # Performance tracking
        self._verification_count = 0
        self._total_cost = 0.0
        
        logger.info(f"Initialized hybrid verifier with level {config.verification_level.name}")
    
    async def verify_email_comprehensive(self, email: str, 
                                       user_context: Optional[Dict] = None) -> ComprehensiveVerificationResult:
        """
        Perform comprehensive email verification using hybrid approach
        
        Args:
            email: Email address to verify
            user_context: Optional user context for logging/tracking
            
        Returns:
            ComprehensiveVerificationResult with combined results
        """
        start_time = time.time()
        result = ComprehensiveVerificationResult(email=email)
        
        try:
            # Stage 1: Format validation (always performed)
            await self._perform_format_validation(result)
            
            if not result.format_valid:
                result.final_status = "invalid_format"
                result.confidence = 0.0
                result.total_verification_time = time.time() - start_time
                return result
            
            # Stage 2: DNS and domain checks
            if self.dns_checker and self.config.verification_level.value >= VerificationLevel.STANDARD.value:
                await self._perform_dns_checks(result)
                
                if result.dns_result and not result.dns_result.valid:
                    result.final_status = "domain_invalid"
                    result.confidence = 0.1
                    result.total_verification_time = time.time() - start_time
                    return result
            
            # Stage 3: Advanced verification based on strategy and level
            await self._perform_advanced_verification(result)
            
            # Stage 4: Aggregate results and calculate final status
            self._aggregate_results(result)
            
            result.total_verification_time = time.time() - start_time
            self._verification_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Comprehensive verification failed for {email}: {e}")
            result.final_status = "verification_error"
            result.confidence = 0.0
            result.warnings.append(f"Verification error: {str(e)}")
            result.total_verification_time = time.time() - start_time
            return result
    
    async def _perform_format_validation(self, result: ComprehensiveVerificationResult):
        """Perform basic format validation"""
        email = result.email
        
        # Basic format checks
        if not email or '@' not in email:
            result.format_errors.append("Invalid email format")
            return
            
        if email.count('@') != 1:
            result.format_errors.append("Email must contain exactly one @ symbol")
            return
            
        local, domain = email.rsplit('@', 1)
        
        if not local or not domain:
            result.format_errors.append("Missing local part or domain")
            return
            
        if len(email) > 254:  # RFC 5321 limit
            result.format_errors.append("Email address too long")
            return
            
        # More comprehensive format validation could be added here
        result.format_valid = True
        result.methods_used.append("format_validation")
    
    async def _perform_dns_checks(self, result: ComprehensiveVerificationResult):
        """Perform DNS-based domain validation"""
        domain = result.email.split('@')[1]
        
        try:
            dns_result = await self.dns_checker.check_domain_comprehensive(domain)
            result.dns_result = dns_result
            result.methods_used.append("dns_validation")
            
            # Extract relevant information
            result.is_disposable = dns_result.is_disposable
            result.mx_records = dns_result.mx_records
            result.domain_reputation = dns_result.reputation_score
            result.is_catch_all = dns_result.is_catch_all
            
            if dns_result.errors:
                result.warnings.extend(dns_result.errors)
                
        except Exception as e:
            logger.warning(f"DNS checks failed for {domain}: {e}")
            result.warnings.append(f"DNS validation failed: {str(e)}")
    
    async def _perform_advanced_verification(self, result: ComprehensiveVerificationResult):
        """Perform advanced verification based on configuration and strategy"""
        if self.config.verification_level.value < VerificationLevel.THOROUGH.value:
            return
            
        # Determine verification approach based on strategy
        if self.config.strategy == HybridStrategy.COST_OPTIMIZED:
            await self._cost_optimized_verification(result)
        elif self.config.strategy == HybridStrategy.ACCURACY_FOCUSED:
            await self._accuracy_focused_verification(result)
        elif self.config.strategy == HybridStrategy.SPEED_OPTIMIZED:
            await self._speed_optimized_verification(result)
        else:  # BALANCED
            await self._balanced_verification(result)
    
    async def _cost_optimized_verification(self, result: ComprehensiveVerificationResult):
        """Cost-optimized verification - prefer free methods"""
        # Try SMTP first if enabled (free but may be blocked)
        if self.smtp_verifier and result.mx_records:
            try:
                smtp_result = await self.smtp_verifier.verify_email_existence(
                    result.email, result.mx_records
                )
                result.smtp_result = smtp_result
                result.methods_used.append("smtp_verification")
                
                # If SMTP gives definitive result, use it
                if smtp_result.definitive:
                    return
                    
            except Exception as e:
                logger.warning(f"SMTP verification failed: {e}")
        
        # Use API only if SMTP failed and within cost threshold
        if (self.api_verifier and 
            self._total_cost + self.config.api_cost_threshold <= self.config.api_cost_threshold * 100):
            await self._perform_api_verification(result)
    
    async def _accuracy_focused_verification(self, result: ComprehensiveVerificationResult):
        """Accuracy-focused verification - use all available methods"""
        tasks = []
        
        # Run SMTP and API verification concurrently if both enabled
        if self.smtp_verifier and result.mx_records:
            tasks.append(self._perform_smtp_verification(result))
            
        if self.api_verifier:
            tasks.append(self._perform_api_verification(result))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _speed_optimized_verification(self, result: ComprehensiveVerificationResult):
        """Speed-optimized verification - use fastest method"""
        # Use API first if available (usually fastest)
        if self.api_verifier:
            await self._perform_api_verification(result)
            if result.api_result and not result.api_result.error_message:
                return
        
        # Fall back to SMTP if API failed
        if self.smtp_verifier and result.mx_records:
            await self._perform_smtp_verification(result)
    
    async def _balanced_verification(self, result: ComprehensiveVerificationResult):
        """Balanced verification - good mix of speed, cost, and accuracy"""
        # Start with the most reliable method based on domain characteristics
        if result.is_disposable:
            # For disposable domains, don't waste API credits
            result.final_status = "disposable_domain"
            result.confidence = 0.9
            return
            
        if result.is_catch_all:
            # For catch-all domains, prefer API verification
            if self.api_verifier:
                await self._perform_api_verification(result)
                return
        
        # For regular domains, try SMTP first, then API if needed
        if self.smtp_verifier and result.mx_records:
            await self._perform_smtp_verification(result)
            
            # If SMTP is definitive, use it
            if result.smtp_result and result.smtp_result.definitive:
                return
        
        # Use API for uncertain cases
        if self.api_verifier and (not result.smtp_result or not result.smtp_result.definitive):
            await self._perform_api_verification(result)
    
    async def _perform_smtp_verification(self, result: ComprehensiveVerificationResult):
        """Perform SMTP verification"""
        try:
            smtp_result = await self.smtp_verifier.verify_email_existence(
                result.email, result.mx_records
            )
            result.smtp_result = smtp_result
            result.methods_used.append("smtp_verification")
            
            if smtp_result.is_catch_all is not None:
                result.is_catch_all = smtp_result.is_catch_all
                
        except Exception as e:
            logger.warning(f"SMTP verification failed: {e}")
            result.warnings.append(f"SMTP verification failed: {str(e)}")
    
    async def _perform_api_verification(self, result: ComprehensiveVerificationResult):
        """Perform API verification"""
        try:
            api_result = await self.api_verifier.verify(result.email)
            result.api_result = api_result
            result.methods_used.append("api_verification")
            result.costs_incurred += api_result.credits_used * 0.001  # Estimate cost
            self._total_cost += result.costs_incurred
            
            # Update metadata from API
            if not api_result.error_message:
                result.is_role_account = api_result.is_role_account
                result.is_toxic = api_result.is_toxic
                if result.is_catch_all is None:
                    result.is_catch_all = api_result.is_catch_all
                    
        except Exception as e:
            logger.warning(f"API verification failed: {e}")
            result.warnings.append(f"API verification failed: {str(e)}")
    
    def _aggregate_results(self, result: ComprehensiveVerificationResult):
        """Aggregate results from all verification methods"""
        confidence_scores = []
        existence_votes = []
        
        # DNS contribution
        if result.dns_result:
            dns_confidence = 0.3 if result.dns_result.valid else 0.0
            confidence_scores.append(dns_confidence)
            existence_votes.append(result.dns_result.valid)
        
        # SMTP contribution
        if result.smtp_result:
            confidence_scores.append(result.smtp_result.confidence)
            if result.smtp_result.exists is not None:
                existence_votes.append(result.smtp_result.exists)
        
        # API contribution (highest weight)
        if result.api_result and not result.api_result.error_message:
            confidence_scores.append(result.api_result.confidence)
            if result.api_result.exists is not None:
                existence_votes.append(result.api_result.exists)
        
        # Calculate overall confidence
        if confidence_scores:
            result.confidence = max(confidence_scores)  # Use highest confidence
        
        # Determine existence based on votes
        if existence_votes:
            positive_votes = sum(existence_votes)
            result.exists = positive_votes > len(existence_votes) / 2
            result.definitive = len(existence_votes) > 1 or result.confidence > 0.8
        
        # Determine final status
        if result.is_disposable:
            result.final_status = "disposable"
            result.confidence = max(result.confidence, 0.8)
        elif result.is_toxic:
            result.final_status = "toxic"
            result.confidence = max(result.confidence, 0.9)
        elif result.exists is True:
            if result.is_catch_all:
                result.final_status = "catch_all_valid"
            elif result.is_role_account:
                result.final_status = "role_account_valid"
            else:
                result.final_status = "valid"
        elif result.exists is False:
            result.final_status = "invalid"
        else:
            if result.confidence > 0.7:
                result.final_status = "probably_valid"
            else:
                result.final_status = "unknown"
        
        # Add recommendations
        self._add_recommendations(result)
    
    def _add_recommendations(self, result: ComprehensiveVerificationResult):
        """Add recommendations based on verification results"""
        if result.final_status == "valid":
            result.recommendations.append("Email appears to be valid and deliverable")
            
        elif result.final_status == "invalid":
            result.recommendations.append("Email is invalid and should not be used")
            
        elif result.final_status == "disposable":
            result.recommendations.append("Disposable email - consider requiring permanent email")
            
        elif result.final_status == "catch_all_valid":
            result.recommendations.append("Domain accepts all emails - address may not exist")
            
        elif result.final_status == "role_account_valid":
            result.recommendations.append("Role-based email - may be managed by multiple people")
            
        elif result.final_status == "toxic":
            result.recommendations.append("Toxic email - known spam trap or abuse address")
            
        elif result.confidence < 0.5:
            result.recommendations.append("Low confidence result - consider additional verification")
            
        if result.domain_reputation < 0.5:
            result.recommendations.append("Domain has poor reputation - proceed with caution")
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get verification statistics"""
        return {
            "total_verifications": self._verification_count,
            "total_costs_incurred": self._total_cost,
            "average_cost_per_verification": self._total_cost / max(self._verification_count, 1),
            "configuration": {
                "level": self.config.verification_level.name,
                "strategy": self.config.strategy.value,
                "dns_enabled": self.config.enable_dns,
                "smtp_enabled": self.config.enable_smtp,
                "api_enabled": self.config.enable_api
            }
        }

# Convenience functions for easy usage
async def verify_email_hybrid(email: str, 
                            level: VerificationLevel = VerificationLevel.STANDARD,
                            strategy: HybridStrategy = HybridStrategy.BALANCED) -> ComprehensiveVerificationResult:
    """
    Convenience function for hybrid email verification
    
    Args:
        email: Email address to verify
        level: Verification thoroughness level
        strategy: Verification strategy
        
    Returns:
        ComprehensiveVerificationResult with verification details
    """
    config = HybridVerificationConfig(
        verification_level=level,
        strategy=strategy
    )
    
    verifier = HybridEmailVerifier(config)
    return await verifier.verify_email_comprehensive(email)

if __name__ == "__main__":
    # Test the hybrid verification system
    async def test_hybrid_verifier():
        """Test hybrid verification system"""
        test_emails = [
            "user@gmail.com",              # Should be valid
            "test@10minutemail.com",       # Disposable
            "invalid@nonexistent.com",     # Invalid domain
            "admin@example.com",           # Uncertain
        ]
        
        # Test different verification levels
        levels = [
            VerificationLevel.BASIC,
            VerificationLevel.STANDARD,
            VerificationLevel.THOROUGH
        ]
        
        for level in levels:
            print(f"\n{'='*60}")
            print(f"Testing Verification Level: {level.name}")
            print(f"{'='*60}")
            
            config = HybridVerificationConfig(
                verification_level=level,
                strategy=HybridStrategy.BALANCED,
                enable_dns=True,
                enable_smtp=False,  # Disable SMTP to avoid blocking issues in tests
                enable_api=False    # Disable API to avoid requiring keys
            )
            
            verifier = HybridEmailVerifier(config)
            
            for email in test_emails:
                print(f"\n🔍 Verifying: {email}")
                result = await verifier.verify_email_comprehensive(email)
                
                print(f"  Status: {result.final_status}")
                print(f"  Exists: {result.exists}")
                print(f"  Confidence: {result.confidence:.2f}")
                print(f"  Definitive: {result.definitive}")
                print(f"  Methods used: {result.methods_used}")
                print(f"  Time: {result.total_verification_time:.3f}s")
                
                if result.warnings:
                    print(f"  Warnings: {result.warnings}")
                    
                if result.recommendations:
                    print(f"  Recommendations: {result.recommendations}")
            
            print(f"\n📊 Stats: {verifier.get_verification_stats()}")
    
    # Run the test
    asyncio.run(test_hybrid_verifier())
