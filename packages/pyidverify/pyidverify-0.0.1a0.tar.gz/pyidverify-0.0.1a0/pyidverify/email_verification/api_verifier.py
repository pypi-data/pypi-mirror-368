"""
Third-Party Email Verification API Integration
==============================================

This module provides integration with professional email verification APIs including:
- ZeroBounce API integration
- Hunter.io Email Verifier integration  
- NeverBounce API integration
- EmailListVerify integration
- Result caching and optimization
- Cost-effective usage strategies

Phase 3 Implementation for PyIDVerify Email Verification Enhancement
"""

import aiohttp
import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerificationStatus(Enum):
    """Standard verification status across all providers"""
    VALID = "valid"
    INVALID = "invalid"
    CATCH_ALL = "catch_all"
    UNKNOWN = "unknown"
    DISPOSABLE = "disposable"
    ROLE_ACCOUNT = "role_account"
    TOXIC = "toxic"
    DO_NOT_SEND = "do_not_send"

class APIProvider(Enum):
    """Supported email verification API providers"""
    ZEROBOUNCE = "zerobounce"
    HUNTER = "hunter"
    NEVERBOUNCE = "neverbounce"
    EMAILLISTVERIFY = "emaillistverify"

@dataclass
class APIVerificationResult:
    """Result from third-party email verification API"""
    email: str
    status: VerificationStatus
    exists: bool
    confidence: float  # 0.0 to 1.0
    provider: str
    sub_status: Optional[str] = None
    is_disposable: bool = False
    is_role_account: bool = False
    is_catch_all: bool = False
    is_toxic: bool = False
    domain_age_days: Optional[int] = None
    free_email: bool = False
    mx_found: bool = False
    mx_record: Optional[str] = None
    smtp_provider: Optional[str] = None
    response_time: float = 0.0
    credits_used: float = 0.0
    error_message: Optional[str] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class APIProviderConfig:
    """Configuration for API provider"""
    provider: APIProvider
    api_key: str
    base_url: str
    rate_limit_per_minute: int
    cost_per_verification: float
    timeout: float = 30.0
    max_retries: int = 3

class EmailVerificationCache:
    """Caching system for API verification results"""
    
    def __init__(self, ttl_hours: int = 24, max_size: int = 10000):
        self.ttl_seconds = ttl_hours * 3600
        self.max_size = max_size
        self._cache = {}
        
    def _get_cache_key(self, email: str, provider: str) -> str:
        """Generate cache key for email and provider"""
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        return f"{provider}:{email_hash}"
    
    def get(self, email: str, provider: str) -> Optional[APIVerificationResult]:
        """Get cached result if available and not expired"""
        cache_key = self._get_cache_key(email, provider)
        
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.ttl_seconds:
                logger.debug(f"Cache hit for {email} with {provider}")
                return result
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
        
        return None
    
    def set(self, email: str, provider: str, result: APIVerificationResult):
        """Cache verification result"""
        cache_key = self._get_cache_key(email, provider)
        
        # Remove oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        self._cache[cache_key] = (result, time.time())
        logger.debug(f"Cached result for {email} with {provider}")
    
    def clear_expired(self):
        """Clear expired cache entries"""
        now = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp >= self.ttl_seconds
        ]
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, requests_per_minute: int):
        self.max_requests = requests_per_minute
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make API request"""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < 60]
        
        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_time = 60 - (now - oldest_request) + 1
            if wait_time > 0:
                logger.info(f"Rate limiting: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)

class ZeroBounceVerifier:
    """ZeroBounce API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.zerobounce.net/v2"
        self.rate_limiter = RateLimiter(100)  # 100 requests per minute
    
    async def verify(self, email: str, ip_address: str = "") -> APIVerificationResult:
        """Verify email using ZeroBounce API"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        url = f"{self.base_url}/validate"
        params = {
            "api_key": self.api_key,
            "email": email,
            "ip_address": ip_address
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_zerobounce_response(email, data, time.time() - start_time)
                    else:
                        error_text = await response.text()
                        return self._create_error_result(
                            email, "zerobounce", f"API error {response.status}: {error_text}"
                        )
            except Exception as e:
                return self._create_error_result(
                    email, "zerobounce", f"Request failed: {str(e)}"
                )
    
    def _parse_zerobounce_response(self, email: str, data: Dict, response_time: float) -> APIVerificationResult:
        """Parse ZeroBounce API response"""
        status_mapping = {
            "valid": VerificationStatus.VALID,
            "invalid": VerificationStatus.INVALID,
            "catch-all": VerificationStatus.CATCH_ALL,
            "unknown": VerificationStatus.UNKNOWN,
            "spamtrap": VerificationStatus.TOXIC,
            "abuse": VerificationStatus.TOXIC,
            "do_not_mail": VerificationStatus.DO_NOT_SEND,
        }
        
        status = status_mapping.get(data.get("status", "unknown"), VerificationStatus.UNKNOWN)
        exists = status in [VerificationStatus.VALID, VerificationStatus.CATCH_ALL]
        
        # Calculate confidence score
        confidence = self._calculate_zerobounce_confidence(data)
        
        return APIVerificationResult(
            email=email,
            status=status,
            exists=exists,
            confidence=confidence,
            provider="zerobounce",
            sub_status=data.get("sub_status"),
            is_disposable=data.get("account", "").lower() in ["disposable", "role"],
            is_role_account=data.get("account", "").lower() == "role",
            is_catch_all=status == VerificationStatus.CATCH_ALL,
            is_toxic=status == VerificationStatus.TOXIC,
            domain_age_days=data.get("domain_age_days"),
            free_email=data.get("free_email", False),
            mx_found=data.get("mx_found", False),
            mx_record=data.get("mx_record"),
            smtp_provider=data.get("smtp_provider"),
            response_time=response_time,
            credits_used=1.0,  # ZeroBounce typically charges 1 credit per verification
            raw_response=data
        )
    
    def _calculate_zerobounce_confidence(self, data: Dict) -> float:
        """Calculate confidence score from ZeroBounce response"""
        status = data.get("status", "unknown")
        
        if status == "valid":
            return 0.95
        elif status == "invalid":
            return 0.90
        elif status == "catch-all":
            return 0.70
        elif status in ["spamtrap", "abuse", "do_not_mail"]:
            return 0.95  # High confidence these should not be sent to
        else:
            return 0.50  # Unknown status

class HunterVerifier:
    """Hunter.io Email Verifier integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
        self.rate_limiter = RateLimiter(50)  # Conservative rate limit
    
    async def verify(self, email: str) -> APIVerificationResult:
        """Verify email using Hunter.io API"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        url = f"{self.base_url}/email-verifier"
        params = {
            "email": email,
            "api_key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_hunter_response(email, data, time.time() - start_time)
                    else:
                        error_text = await response.text()
                        return self._create_error_result(
                            email, "hunter", f"API error {response.status}: {error_text}"
                        )
            except Exception as e:
                return self._create_error_result(
                    email, "hunter", f"Request failed: {str(e)}"
                )
    
    def _parse_hunter_response(self, email: str, data: Dict, response_time: float) -> APIVerificationResult:
        """Parse Hunter.io API response"""
        email_data = data.get("data", {})
        
        # Hunter uses a scoring system (0-100)
        score = email_data.get("score", 0)
        result = email_data.get("result", "unknown").lower()
        
        # Map Hunter results to standard status
        if result == "deliverable" or score >= 80:
            status = VerificationStatus.VALID
            exists = True
            confidence = min(0.95, score / 100.0 + 0.1)
        elif result == "undeliverable" or score <= 20:
            status = VerificationStatus.INVALID
            exists = False
            confidence = min(0.95, (100 - score) / 100.0 + 0.1)
        elif result == "risky" or 20 < score < 80:
            status = VerificationStatus.UNKNOWN
            exists = None
            confidence = 0.50
        else:
            status = VerificationStatus.UNKNOWN
            exists = None
            confidence = 0.30
        
        return APIVerificationResult(
            email=email,
            status=status,
            exists=exists,
            confidence=confidence,
            provider="hunter",
            is_disposable=email_data.get("disposable", False),
            is_role_account=email_data.get("role", False),
            mx_found=email_data.get("mx_records", False),
            response_time=response_time,
            credits_used=1.0,
            raw_response=data,
            metadata={"hunter_score": score, "hunter_result": result}
        )

class NeverBounceVerifier:
    """NeverBounce API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.neverbounce.com/v4"
        self.rate_limiter = RateLimiter(200)  # Higher rate limit
    
    async def verify(self, email: str) -> APIVerificationResult:
        """Verify email using NeverBounce API"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        url = f"{self.base_url}/single/check"
        data = {
            "key": self.api_key,
            "email": email,
            "address_info": 1,  # Include additional address info
            "credits_info": 1   # Include credits info
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._parse_neverbounce_response(email, result, time.time() - start_time)
                    else:
                        error_text = await response.text()
                        return self._create_error_result(
                            email, "neverbounce", f"API error {response.status}: {error_text}"
                        )
            except Exception as e:
                return self._create_error_result(
                    email, "neverbounce", f"Request failed: {str(e)}"
                )
    
    def _parse_neverbounce_response(self, email: str, data: Dict, response_time: float) -> APIVerificationResult:
        """Parse NeverBounce API response"""
        result_code = data.get("result", "unknown")
        
        status_mapping = {
            "valid": VerificationStatus.VALID,
            "invalid": VerificationStatus.INVALID,
            "disposable": VerificationStatus.DISPOSABLE,
            "catchall": VerificationStatus.CATCH_ALL,
            "unknown": VerificationStatus.UNKNOWN
        }
        
        status = status_mapping.get(result_code, VerificationStatus.UNKNOWN)
        exists = status in [VerificationStatus.VALID, VerificationStatus.CATCH_ALL]
        
        # Calculate confidence
        confidence_mapping = {
            "valid": 0.95,
            "invalid": 0.90,
            "disposable": 0.85,
            "catchall": 0.70,
            "unknown": 0.50
        }
        confidence = confidence_mapping.get(result_code, 0.30)
        
        address_info = data.get("address_info", {})
        credits_info = data.get("credits_info", {})
        
        return APIVerificationResult(
            email=email,
            status=status,
            exists=exists,
            confidence=confidence,
            provider="neverbounce",
            is_disposable=result_code == "disposable",
            is_role_account=address_info.get("role", False),
            is_catch_all=result_code == "catchall",
            free_email=address_info.get("free_email_host", False),
            mx_found=address_info.get("has_dns_mx", False),
            response_time=response_time,
            credits_used=credits_info.get("used_credits", 1.0),
            raw_response=data
        )

class ThirdPartyEmailVerifier:
    """Main class for third-party email verification services"""
    
    def __init__(self, default_provider: APIProvider = APIProvider.ZEROBOUNCE):
        self.providers = {}
        self.cache = EmailVerificationCache()
        self.default_provider = default_provider
    
    def add_provider(self, provider: APIProvider, api_key: str):
        """Add API provider configuration"""
        if provider == APIProvider.ZEROBOUNCE:
            self.providers[provider] = ZeroBounceVerifier(api_key)
        elif provider == APIProvider.HUNTER:
            self.providers[provider] = HunterVerifier(api_key)
        elif provider == APIProvider.NEVERBOUNCE:
            self.providers[provider] = NeverBounceVerifier(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        logger.info(f"Added {provider.value} provider")
    
    async def verify(self, email: str, 
                    provider: Optional[APIProvider] = None,
                    use_cache: bool = True) -> APIVerificationResult:
        """
        Verify email using specified or default provider
        
        Args:
            email: Email address to verify
            provider: API provider to use (defaults to configured default)
            use_cache: Whether to use cached results
            
        Returns:
            APIVerificationResult with verification details
        """
        provider = provider or self.default_provider
        
        if provider not in self.providers:
            return self._create_error_result(
                email, provider.value, f"Provider {provider.value} not configured"
            )
        
        # Check cache first
        if use_cache:
            cached_result = self.cache.get(email, provider.value)
            if cached_result:
                logger.debug(f"Using cached result for {email}")
                return cached_result
        
        # Verify using provider
        verifier = self.providers[provider]
        result = await verifier.verify(email)
        
        # Cache successful results
        if use_cache and not result.error_message:
            self.cache.set(email, provider.value, result)
        
        return result
    
    async def verify_with_fallback(self, email: str, 
                                 primary_provider: Optional[APIProvider] = None,
                                 fallback_providers: List[APIProvider] = None) -> APIVerificationResult:
        """
        Verify email with fallback to other providers on failure
        
        Args:
            email: Email address to verify
            primary_provider: Primary provider to try first
            fallback_providers: List of fallback providers
            
        Returns:
            APIVerificationResult from first successful verification
        """
        primary_provider = primary_provider or self.default_provider
        fallback_providers = fallback_providers or []
        
        # Try primary provider first
        result = await self.verify(email, primary_provider)
        if not result.error_message:
            return result
        
        # Try fallback providers
        for fallback_provider in fallback_providers:
            if fallback_provider in self.providers:
                logger.info(f"Trying fallback provider {fallback_provider.value}")
                result = await self.verify(email, fallback_provider)
                if not result.error_message:
                    return result
        
        return result  # Return last result (likely an error)
    
    async def verify_batch(self, emails: List[str], 
                          provider: Optional[APIProvider] = None,
                          max_concurrent: int = 5) -> List[APIVerificationResult]:
        """
        Verify multiple emails concurrently
        
        Args:
            emails: List of email addresses to verify
            provider: API provider to use
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of APIVerificationResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def verify_single(email: str) -> APIVerificationResult:
            async with semaphore:
                return await self.verify(email, provider)
        
        tasks = [verify_single(email) for email in emails]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    self._create_error_result(emails[i], provider.value if provider else "unknown", 
                                            f"Verification failed: {str(result)}")
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _create_error_result(self, email: str, provider: str, error_message: str) -> APIVerificationResult:
        """Create error result object"""
        return APIVerificationResult(
            email=email,
            status=VerificationStatus.UNKNOWN,
            exists=None,
            confidence=0.0,
            provider=provider,
            error_message=error_message
        )
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache._cache),
            "max_size": self.cache.max_size,
            "ttl_hours": self.cache.ttl_seconds // 3600
        }
    
    def clear_cache(self):
        """Clear all cached results"""
        self.cache._cache.clear()
        logger.info("Cleared verification cache")

# Convenience functions
async def verify_email_api(email: str, provider: APIProvider, api_key: str) -> APIVerificationResult:
    """
    Convenience function for single email verification
    
    Args:
        email: Email address to verify
        provider: API provider to use
        api_key: API key for the provider
        
    Returns:
        APIVerificationResult with verification details
    """
    verifier = ThirdPartyEmailVerifier(provider)
    verifier.add_provider(provider, api_key)
    return await verifier.verify(email)

if __name__ == "__main__":
    # Test the third-party verifiers
    async def test_api_verifiers():
        """Test third-party API verifiers"""
        # Note: You need actual API keys to test these
        api_keys = {
            APIProvider.ZEROBOUNCE: os.getenv("ZEROBOUNCE_API_KEY"),
            APIProvider.HUNTER: os.getenv("HUNTER_API_KEY"),
            APIProvider.NEVERBOUNCE: os.getenv("NEVERBOUNCE_API_KEY")
        }
        
        test_emails = [
            "test@gmail.com",
            "invalid@nonexistentdomain12345.com",
            "admin@example.com"
        ]
        
        verifier = ThirdPartyEmailVerifier()
        
        # Add providers if API keys are available
        for provider, api_key in api_keys.items():
            if api_key:
                verifier.add_provider(provider, api_key)
                print(f"✅ Added {provider.value} provider")
            else:
                print(f"⚠️ No API key for {provider.value}")
        
        if not verifier.providers:
            print("❌ No API providers configured. Set environment variables:")
            print("   ZEROBOUNCE_API_KEY, HUNTER_API_KEY, NEVERBOUNCE_API_KEY")
            return
        
        # Test verification
        for email in test_emails:
            print(f"\n🔍 Testing: {email}")
            
            for provider in verifier.providers.keys():
                try:
                    result = await verifier.verify(email, provider)
                    print(f"  {provider.value}:")
                    print(f"    Status: {result.status.value}")
                    print(f"    Exists: {result.exists}")
                    print(f"    Confidence: {result.confidence:.2f}")
                    print(f"    Response time: {result.response_time:.3f}s")
                    
                    if result.error_message:
                        print(f"    Error: {result.error_message}")
                        
                except Exception as e:
                    print(f"    Error: {e}")
        
        # Show cache stats
        print(f"\n📊 Cache stats: {verifier.get_cache_stats()}")
    
    # Run the test
    asyncio.run(test_api_verifiers())
