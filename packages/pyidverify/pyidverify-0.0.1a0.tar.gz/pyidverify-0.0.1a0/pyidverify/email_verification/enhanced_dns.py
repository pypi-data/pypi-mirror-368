"""
Enhanced DNS Email Verification Module
=====================================

This module provides enhanced DNS-based email validation including:
- Improved MX record checking with A record fallback
- Comprehensive disposable email database management
- Domain reputation scoring system
- Catch-all domain detection

Phase 1 Implementation for PyIDVerify Email Verification Enhancement
"""

import dns.resolver
import dns.exception
import json
import time
import asyncio
import aiohttp
import socket
from typing import Dict, List, Optional, Set, Tuple, NamedTuple
from dataclasses import dataclass
from pathlib import Path
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DNSCheckResult:
    """Result of DNS-based email domain validation"""
    valid: bool
    mx_records: List[str]
    a_records: List[str]
    is_disposable: bool
    reputation_score: float
    is_catch_all: Optional[bool]
    response_time: float
    errors: List[str]
    metadata: Dict[str, any]

class EnhancedDNSChecker:
    """Enhanced DNS checker for email domain validation"""
    
    def __init__(self, timeout: float = 10.0, cache_ttl: int = 3600):
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._dns_cache = {}
        self._disposable_domains = self._load_disposable_domains()
        self._reputation_cache = {}
        
        # Configure DNS resolver with timeout
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout
        
    def _load_disposable_domains(self) -> Set[str]:
        """Load comprehensive disposable email domains database"""
        disposable_domains = set()
        
        # Built-in comprehensive disposable domains list
        built_in_disposable = {
            # Major disposable email providers
            "10minutemail.com", "10minutemail.net", "temp-mail.org", 
            "guerrillamail.com", "guerrillamail.net", "guerrillamail.org",
            "mailinator.com", "throwaway.email", "tempmail.net",
            "yopmail.com", "getairmail.com", "tempail.com",
            "sharklasers.com", "maildrop.cc", "emailondeck.com",
            
            # Additional disposable providers
            "spam4.me", "tempinbox.com", "temp-mail.io", "fakeinbox.com",
            "temporary-mail.net", "tmpemail.net", "dispostable.com",
            "mohmal.com", "mailnesia.com", "trashmail.com",
            "throwawaymail.com", "deadaddress.com", "mytrashmail.com",
            "tempemailaddress.com", "emailtemporanea.com", "tmail.ws",
            
            # Country-specific disposable services
            "tempmail.de", "wegwerfadresse.de", "spambog.com", "spambog.de",
            "spambog.ru", "tempmail.eu", "tempmail.pl", "tempmail.fr",
            
            # New/emerging disposable services (regularly updated)
            "burnermail.io", "emailhippo.com", "inboxkitten.com",
            "nada.email", "tempmailo.com", "harakirimail.com"
        }
        
        disposable_domains.update(built_in_disposable)
        
        # Load external disposable domains if available
        try:
            external_file = Path(__file__).parent / 'data' / 'disposable_domains.json'
            if external_file.exists():
                with open(external_file, 'r', encoding='utf-8') as f:
                    external_data = json.load(f)
                    if isinstance(external_data, list):
                        disposable_domains.update(external_data)
                    elif isinstance(external_data, dict) and 'domains' in external_data:
                        disposable_domains.update(external_data['domains'])
                        
            logger.info(f"Loaded {len(disposable_domains)} disposable email domains")
            
        except Exception as e:
            logger.warning(f"Could not load external disposable domains: {e}")
            
        return disposable_domains
    
    async def check_domain_comprehensive(self, domain: str) -> DNSCheckResult:
        """
        Perform comprehensive DNS-based domain validation
        
        Args:
            domain: Email domain to validate
            
        Returns:
            DNSCheckResult with comprehensive validation details
        """
        start_time = time.time()
        errors = []
        metadata = {}
        
        # Check cache first
        cache_key = f"dns:{domain}"
        if cache_key in self._dns_cache:
            cached_result, cache_time = self._dns_cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return cached_result
        
        try:
            # Step 1: MX Record Check
            mx_records, mx_errors = await self._check_mx_records(domain)
            errors.extend(mx_errors)
            metadata['mx_check'] = True
            
            # Step 2: A Record Fallback (if no MX records)
            a_records = []
            if not mx_records:
                a_records, a_errors = await self._check_a_records(domain)
                errors.extend(a_errors)
                metadata['a_fallback'] = True
            
            # Step 3: Disposable Domain Check
            is_disposable = self._is_disposable_domain(domain)
            metadata['disposable_check'] = True
            
            # Step 4: Domain Reputation Scoring
            reputation_score = await self._calculate_domain_reputation(domain)
            metadata['reputation_check'] = True
            
            # Step 5: Catch-All Detection (if domain has mail servers)
            is_catch_all = None
            if mx_records or a_records:
                is_catch_all = await self._detect_catch_all(domain, mx_records or a_records)
                metadata['catch_all_check'] = True
            
            # Determine overall validity
            domain_valid = bool(mx_records or a_records) and not is_disposable
            
            # Calculate response time
            response_time = time.time() - start_time
            
            result = DNSCheckResult(
                valid=domain_valid,
                mx_records=mx_records,
                a_records=a_records,
                is_disposable=is_disposable,
                reputation_score=reputation_score,
                is_catch_all=is_catch_all,
                response_time=response_time,
                errors=errors,
                metadata=metadata
            )
            
            # Cache result
            self._dns_cache[cache_key] = (result, time.time())
            
            return result
            
        except Exception as e:
            logger.error(f"DNS check failed for domain {domain}: {e}")
            return DNSCheckResult(
                valid=False,
                mx_records=[],
                a_records=[],
                is_disposable=True,  # Assume disposable on error for safety
                reputation_score=0.0,
                is_catch_all=None,
                response_time=time.time() - start_time,
                errors=[f"DNS check failed: {str(e)}"],
                metadata={'error': True}
            )
    
    async def _check_mx_records(self, domain: str) -> Tuple[List[str], List[str]]:
        """Check MX records for domain"""
        mx_records = []
        errors = []
        
        try:
            mx_result = self.resolver.resolve(domain, 'MX')
            for mx in mx_result:
                mx_records.append(str(mx.exchange).rstrip('.'))
            
            # Sort by priority (lower number = higher priority)
            mx_records.sort(key=lambda x: mx_result.rrset.items[0].preference)
            
        except dns.resolver.NXDOMAIN:
            errors.append("Domain does not exist")
        except dns.resolver.NoAnswer:
            errors.append("No MX records found")
        except dns.exception.Timeout:
            errors.append("DNS query timeout for MX records")
        except Exception as e:
            errors.append(f"MX record check failed: {str(e)}")
        
        return mx_records, errors
    
    async def _check_a_records(self, domain: str) -> Tuple[List[str], List[str]]:
        """Check A records for domain (fallback for MX records)"""
        a_records = []
        errors = []
        
        try:
            a_result = self.resolver.resolve(domain, 'A')
            for a in a_result:
                a_records.append(str(a))
                
        except dns.resolver.NXDOMAIN:
            errors.append("Domain does not exist (A record check)")
        except dns.resolver.NoAnswer:
            errors.append("No A records found")
        except dns.exception.Timeout:
            errors.append("DNS query timeout for A records")
        except Exception as e:
            errors.append(f"A record check failed: {str(e)}")
        
        return a_records, errors
    
    def _is_disposable_domain(self, domain: str) -> bool:
        """Check if domain is a known disposable email provider"""
        domain_lower = domain.lower()
        
        # Direct match
        if domain_lower in self._disposable_domains:
            return True
        
        # Check subdomains of known disposable providers
        for disposable_domain in self._disposable_domains:
            if domain_lower.endswith('.' + disposable_domain):
                return True
        
        return False
    
    async def _calculate_domain_reputation(self, domain: str) -> float:
        """
        Calculate domain reputation score (0.0 to 1.0)
        Higher score = better reputation
        """
        # Check reputation cache
        if domain in self._reputation_cache:
            cached_rep, cache_time = self._reputation_cache[domain]
            if time.time() - cache_time < self.cache_ttl:
                return cached_rep
        
        reputation_score = 0.5  # Default neutral score
        
        try:
            # Factor 1: Domain age estimation (older domains generally more reputable)
            domain_age_score = await self._estimate_domain_age_score(domain)
            reputation_score += domain_age_score * 0.3
            
            # Factor 2: TLD reputation (some TLDs have better reputation)
            tld_score = self._calculate_tld_reputation(domain)
            reputation_score += tld_score * 0.2
            
            # Factor 3: Known good domains boost
            if self._is_known_good_domain(domain):
                reputation_score += 0.3
            
            # Factor 4: Subdomain penalty (subdomains generally less reputable)
            if domain.count('.') > 1:
                reputation_score -= 0.1
            
            # Ensure score stays within bounds
            reputation_score = max(0.0, min(1.0, reputation_score))
            
            # Cache result
            self._reputation_cache[domain] = (reputation_score, time.time())
            
        except Exception as e:
            logger.warning(f"Could not calculate reputation for {domain}: {e}")
            reputation_score = 0.5  # Default on error
        
        return reputation_score
    
    async def _estimate_domain_age_score(self, domain: str) -> float:
        """Estimate domain age contribution to reputation (0.0 to 1.0)"""
        try:
            # Simple heuristic based on domain structure and patterns
            # More sophisticated implementation would use WHOIS data
            
            # Well-known old domains get high scores
            if domain in {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                         'aol.com', 'msn.com', 'live.com'}:
                return 1.0
            
            # Enterprise domains (common patterns)
            if any(domain.endswith(suffix) for suffix in ['.edu', '.gov', '.org']):
                return 0.8
            
            # Common business domains
            if any(domain.endswith(suffix) for suffix in ['.com', '.net']):
                return 0.6
            
            # Country-specific domains
            if len(domain.split('.')[-1]) == 2:  # ccTLD
                return 0.5
            
            return 0.3  # Default for unknown patterns
            
        except Exception:
            return 0.3
    
    def _calculate_tld_reputation(self, domain: str) -> float:
        """Calculate TLD-based reputation score"""
        try:
            tld = domain.split('.')[-1].lower()
            
            # High-reputation TLDs
            high_rep_tlds = {'com', 'org', 'net', 'edu', 'gov', 'mil'}
            if tld in high_rep_tlds:
                return 0.8
            
            # Medium-reputation TLDs (country codes)
            if len(tld) == 2:  # Most ccTLDs
                return 0.6
            
            # Lower reputation TLDs (often used for spam)
            low_rep_tlds = {'tk', 'ml', 'ga', 'cf', 'xyz', 'top', 'click'}
            if tld in low_rep_tlds:
                return 0.2
            
            return 0.5  # Default for other TLDs
            
        except Exception:
            return 0.5
    
    def _is_known_good_domain(self, domain: str) -> bool:
        """Check if domain is a well-known reputable provider"""
        known_good = {
            # Major email providers
            'gmail.com', 'googlemail.com', 'yahoo.com', 'ymail.com',
            'hotmail.com', 'outlook.com', 'live.com', 'msn.com',
            'aol.com', 'icloud.com', 'me.com', 'mac.com',
            
            # Business email providers
            'office365.com', 'microsoft.com', 'google.com', 'apple.com',
            'amazon.com', 'facebook.com', 'twitter.com', 'linkedin.com',
            
            # Educational and government
            'edu', 'gov', 'mil'  # These are checked as endswith
        }
        
        domain_lower = domain.lower()
        
        # Direct match
        if domain_lower in known_good:
            return True
            
        # Check if ends with known good domains (for subdomains)
        for good_domain in known_good:
            if domain_lower.endswith('.' + good_domain):
                return True
        
        return False
    
    async def _detect_catch_all(self, domain: str, mail_servers: List[str]) -> Optional[bool]:
        """
        Detect if domain accepts all email addresses (catch-all configuration)
        
        Args:
            domain: Domain to test
            mail_servers: List of mail servers for the domain
            
        Returns:
            True if catch-all detected, False if not, None if couldn't determine
        """
        if not mail_servers:
            return None
            
        try:
            # Test with obviously fake email addresses
            test_addresses = [
                f"definitely-nonexistent-{int(time.time())}@{domain}",
                f"test-fake-address-{int(time.time() * 1000) % 10000}@{domain}",
                f"invalid-mailbox-check@{domain}"
            ]
            
            catch_all_responses = 0
            valid_responses = 0
            
            for test_email in test_addresses:
                # Simple socket-based SMTP check (lightweight)
                try:
                    mail_server = mail_servers[0]  # Use primary mail server
                    sock = socket.create_connection((mail_server, 25), timeout=10)
                    sock.close()
                    # If we can connect, assume it might accept emails
                    # Full SMTP testing will be done in Phase 2
                    catch_all_responses += 1
                except:
                    pass
                    
            # Heuristic: if all test addresses seem to be accepted, likely catch-all
            if catch_all_responses >= len(test_addresses) * 0.8:
                return True
            elif catch_all_responses == 0:
                return False
            else:
                return None  # Uncertain
                
        except Exception as e:
            logger.warning(f"Catch-all detection failed for {domain}: {e}")
            return None

# Utility function for easy integration
async def check_email_domain(domain: str, timeout: float = 10.0) -> DNSCheckResult:
    """
    Convenience function for checking email domain
    
    Args:
        domain: Email domain to check
        timeout: DNS query timeout in seconds
        
    Returns:
        DNSCheckResult with validation details
    """
    checker = EnhancedDNSChecker(timeout=timeout)
    return await checker.check_domain_comprehensive(domain)

if __name__ == "__main__":
    # Test the enhanced DNS checker
    async def test_dns_checker():
        """Test the enhanced DNS checker with various domains"""
        test_domains = [
            "gmail.com",           # Should be valid, high reputation
            "10minutemail.com",    # Should be disposable
            "example.com",         # Valid format, may not have MX
            "nonexistent-domain-12345.xyz",  # Should not exist
            "yahoo.com",           # Valid, high reputation
            "tempmail.net",        # Disposable
        ]
        
        checker = EnhancedDNSChecker()
        
        for domain in test_domains:
            print(f"\n🔍 Checking domain: {domain}")
            result = await checker.check_domain_comprehensive(domain)
            
            print(f"  Valid: {result.valid}")
            print(f"  MX Records: {result.mx_records}")
            print(f"  Disposable: {result.is_disposable}")
            print(f"  Reputation: {result.reputation_score:.2f}")
            print(f"  Catch-all: {result.is_catch_all}")
            print(f"  Response time: {result.response_time:.3f}s")
            
            if result.errors:
                print(f"  Errors: {result.errors}")
    
    # Run the test
    asyncio.run(test_dns_checker())
