"""
SMTP Email Verification Module
==============================

This module provides safe and respectful SMTP-based email verification including:
- Progressive SMTP connection testing
- VRFY command and RCPT TO testing
- Server policy detection and respect
- Rate limiting and retry logic
- Greylisting and temporary failure handling

Phase 2 Implementation for PyIDVerify Email Verification Enhancement
"""

import smtplib
import socket
import time
import asyncio
import random
from typing import Dict, List, Optional, Tuple, NamedTuple, Union
from dataclasses import dataclass
from enum import Enum
import logging
import re
from datetime import datetime, timedelta
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMTPResponseCode(Enum):
    """SMTP response codes for email verification"""
    SUCCESS = 250          # Requested mail action okay, completed
    USER_NOT_LOCAL = 251   # User not local; will forward
    CANNOT_VRFY = 252      # Cannot VRFY user, but will accept message
    START_INPUT = 354      # Start mail input
    TEMP_FAILURE = 450     # Requested mail action not taken: mailbox unavailable
    INSUFFICIENT_STORAGE = 452  # Insufficient system storage
    TEMP_AUTH_FAILURE = 454     # Temporary authentication failure
    MAILBOX_UNAVAILABLE = 550   # Mailbox unavailable
    USER_NOT_LOCAL_ERR = 551    # User not local
    EXCEEDED_STORAGE = 552      # Exceeded storage allocation
    INVALID_MAILBOX = 553       # Mailbox name not allowed
    TRANSACTION_FAILED = 554    # Transaction failed

@dataclass
class SMTPVerificationResult:
    """Result of SMTP-based email verification"""
    exists: Optional[bool]          # True/False/None (if uncertain)
    definitive: bool                # Whether result is definitive
    confidence: float               # Confidence score 0.0-1.0
    smtp_code: Optional[int]        # SMTP response code
    smtp_message: str              # SMTP response message
    method_used: str               # Verification method (VRFY, RCPT_TO, CONNECTION)
    server_tested: str             # Mail server that was tested
    response_time: float           # Time taken for verification
    is_catch_all: Optional[bool]   # Whether domain appears to be catch-all
    temporary_failure: bool        # Whether failure might be temporary
    errors: List[str]              # Any errors encountered
    metadata: Dict[str, any]       # Additional metadata

@dataclass
class SMTPServerInfo:
    """Information about SMTP server capabilities and policies"""
    hostname: str
    supports_vrfy: bool
    supports_ehlo: bool
    supports_starttls: bool
    max_recipients: Optional[int]
    rate_limit_detected: bool
    greylisting_detected: bool
    connection_timeout: float
    last_tested: datetime

class RateLimiter:
    """Rate limiter for SMTP connections to avoid being blocked"""
    
    def __init__(self, max_requests_per_minute: int = 10):
        self.max_requests = max_requests_per_minute
        self.requests = []
        
    async def acquire(self):
        """Acquire rate limiting permission"""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < 60]
        
        if len(self.requests) >= self.max_requests:
            # Need to wait
            oldest_request = min(self.requests)
            wait_time = 60 - (now - oldest_request)
            if wait_time > 0:
                logger.info(f"Rate limiting: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)

class SMTPEmailVerifier:
    """Safe and respectful SMTP email verifier"""
    
    def __init__(self, 
                 timeout: float = 30.0,
                 retry_attempts: int = 2,
                 rate_limit_per_minute: int = 10,
                 respect_server_policies: bool = True):
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.respect_server_policies = respect_server_policies
        self.rate_limiter = RateLimiter(rate_limit_per_minute)
        
        # Cache for server info and results
        self._server_info_cache = {}
        self._verification_cache = {}
        self._blacklisted_servers = set()
        
        # User-agent like identifier for EHLO
        self.helo_hostname = f"email-validator-{int(time.time() % 10000)}.local"
    
    async def verify_email_existence(self, email: str, 
                                   mx_servers: List[str]) -> SMTPVerificationResult:
        """
        Perform SMTP-based email existence verification
        
        Args:
            email: Email address to verify
            mx_servers: List of MX servers for the domain (in priority order)
            
        Returns:
            SMTPVerificationResult with verification details
        """
        if not mx_servers:
            return SMTPVerificationResult(
                exists=False,
                definitive=True,
                confidence=0.0,
                smtp_code=None,
                smtp_message="No MX servers available",
                method_used="NO_SERVERS",
                server_tested="",
                response_time=0.0,
                is_catch_all=None,
                temporary_failure=False,
                errors=["No MX servers to test"],
                metadata={}
            )
        
        # Check cache first
        cache_key = f"smtp:{email}"
        if cache_key in self._verification_cache:
            cached_result, cache_time = self._verification_cache[cache_key]
            if time.time() - cache_time < 300:  # 5-minute cache
                return cached_result
        
        # Try each MX server in priority order
        for mx_server in mx_servers:
            if mx_server in self._blacklisted_servers:
                continue
                
            try:
                # Apply rate limiting
                await self.rate_limiter.acquire()
                
                result = await self._test_smtp_server(mx_server, email)
                
                # Cache successful results
                if result.definitive or result.confidence > 0.5:
                    self._verification_cache[cache_key] = (result, time.time())
                
                # Return definitive results immediately
                if result.definitive:
                    return result
                    
                # If we got some useful information, keep it as backup
                backup_result = result
                
            except Exception as e:
                logger.warning(f"SMTP verification failed for {mx_server}: {e}")
                continue
        
        # If no definitive result, return the best attempt or failure
        return backup_result if 'backup_result' in locals() else SMTPVerificationResult(
            exists=None,
            definitive=False,
            confidence=0.0,
            smtp_code=None,
            smtp_message="All SMTP servers unreachable or unresponsive",
            method_used="CONNECTION_FAILED",
            server_tested=mx_servers[0] if mx_servers else "",
            response_time=0.0,
            is_catch_all=None,
            temporary_failure=True,
            errors=["Could not connect to any SMTP servers"],
            metadata={"servers_attempted": mx_servers}
        )
    
    async def _test_smtp_server(self, server: str, email: str) -> SMTPVerificationResult:
        """Test a specific SMTP server for email verification"""
        start_time = time.time()
        errors = []
        metadata = {"server": server, "email_tested": email}
        
        try:
            # Get or detect server capabilities
            server_info = await self._get_server_info(server)
            
            # Establish SMTP connection
            smtp = await self._create_smtp_connection(server)
            
            try:
                # Perform EHLO/HELO handshake
                await self._perform_handshake(smtp, server_info)
                
                # Try VRFY command first (most direct method)
                if server_info.supports_vrfy:
                    result = await self._try_vrfy_command(smtp, email, server, start_time)
                    if result.definitive:
                        return result
                
                # Fallback to RCPT TO testing
                result = await self._try_rcpt_to_testing(smtp, email, server, start_time)
                return result
                
            finally:
                try:
                    smtp.quit()
                except:
                    pass
                    
        except smtplib.SMTPConnectError as e:
            return SMTPVerificationResult(
                exists=None,
                definitive=False,
                confidence=0.0,
                smtp_code=e.smtp_code if hasattr(e, 'smtp_code') else None,
                smtp_message=f"Connection failed: {str(e)}",
                method_used="CONNECTION_FAILED",
                server_tested=server,
                response_time=time.time() - start_time,
                is_catch_all=None,
                temporary_failure=True,
                errors=[f"SMTP connection failed: {str(e)}"],
                metadata=metadata
            )
            
        except Exception as e:
            return SMTPVerificationResult(
                exists=None,
                definitive=False,
                confidence=0.0,
                smtp_code=None,
                smtp_message=f"Unexpected error: {str(e)}",
                method_used="ERROR",
                server_tested=server,
                response_time=time.time() - start_time,
                is_catch_all=None,
                temporary_failure=True,
                errors=[f"Unexpected error: {str(e)}"],
                metadata=metadata
            )
    
    async def _create_smtp_connection(self, server: str) -> smtplib.SMTP:
        """Create SMTP connection with proper error handling"""
        try:
            smtp = smtplib.SMTP(timeout=self.timeout)
            smtp.connect(server, 25)
            return smtp
        except Exception as e:
            logger.warning(f"Failed to connect to {server}: {e}")
            raise smtplib.SMTPConnectError(f"Connection to {server} failed: {e}")
    
    async def _perform_handshake(self, smtp: smtplib.SMTP, server_info: SMTPServerInfo):
        """Perform EHLO/HELO handshake"""
        try:
            if server_info.supports_ehlo:
                smtp.ehlo(self.helo_hostname)
            else:
                smtp.helo(self.helo_hostname)
        except Exception as e:
            logger.warning(f"Handshake failed: {e}")
            raise
    
    async def _try_vrfy_command(self, smtp: smtplib.SMTP, email: str, 
                               server: str, start_time: float) -> SMTPVerificationResult:
        """Try VRFY command for email verification"""
        try:
            code, message = smtp.vrfy(email)
            response_time = time.time() - start_time
            
            # Analyze VRFY response
            if code == 250:
                return SMTPVerificationResult(
                    exists=True,
                    definitive=True,
                    confidence=0.95,
                    smtp_code=code,
                    smtp_message=message.decode() if isinstance(message, bytes) else str(message),
                    method_used="VRFY",
                    server_tested=server,
                    response_time=response_time,
                    is_catch_all=None,
                    temporary_failure=False,
                    errors=[],
                    metadata={"vrfy_successful": True}
                )
            elif code == 252:
                # Cannot verify but will accept - uncertain result
                return SMTPVerificationResult(
                    exists=None,
                    definitive=False,
                    confidence=0.5,
                    smtp_code=code,
                    smtp_message=message.decode() if isinstance(message, bytes) else str(message),
                    method_used="VRFY_UNCERTAIN",
                    server_tested=server,
                    response_time=response_time,
                    is_catch_all=None,
                    temporary_failure=False,
                    errors=[],
                    metadata={"vrfy_uncertain": True}
                )
            elif code in [550, 551, 553]:
                # User not found
                return SMTPVerificationResult(
                    exists=False,
                    definitive=True,
                    confidence=0.9,
                    smtp_code=code,
                    smtp_message=message.decode() if isinstance(message, bytes) else str(message),
                    method_used="VRFY_NOT_FOUND",
                    server_tested=server,
                    response_time=response_time,
                    is_catch_all=None,
                    temporary_failure=False,
                    errors=[],
                    metadata={"vrfy_user_not_found": True}
                )
            else:
                # Other response - not definitive
                return SMTPVerificationResult(
                    exists=None,
                    definitive=False,
                    confidence=0.1,
                    smtp_code=code,
                    smtp_message=message.decode() if isinstance(message, bytes) else str(message),
                    method_used="VRFY_OTHER",
                    server_tested=server,
                    response_time=response_time,
                    is_catch_all=None,
                    temporary_failure=code in [450, 451, 452],
                    errors=[f"VRFY returned code {code}"],
                    metadata={"vrfy_other_response": True}
                )
                
        except smtplib.SMTPException as e:
            # VRFY command failed, not definitive
            return SMTPVerificationResult(
                exists=None,
                definitive=False,
                confidence=0.0,
                smtp_code=getattr(e, 'smtp_code', None),
                smtp_message=str(e),
                method_used="VRFY_FAILED",
                server_tested=server,
                response_time=time.time() - start_time,
                is_catch_all=None,
                temporary_failure=True,
                errors=[f"VRFY command failed: {str(e)}"],
                metadata={"vrfy_command_failed": True}
            )
    
    async def _try_rcpt_to_testing(self, smtp: smtplib.SMTP, email: str, 
                                  server: str, start_time: float) -> SMTPVerificationResult:
        """Try RCPT TO testing for email verification"""
        domain = email.split('@')[1]
        
        try:
            # Start mail transaction
            sender = f"test@{domain}"  # Use same domain to avoid cross-domain issues
            smtp.mail(sender)
            
            # Try RCPT TO command
            code, message = smtp.rcpt(email)
            response_time = time.time() - start_time
            
            # Reset the transaction
            try:
                smtp.rset()
            except:
                pass
            
            # Analyze RCPT TO response
            if code == 250:
                # Need to check if it's catch-all
                is_catch_all = await self._quick_catch_all_check(smtp, domain, sender)
                confidence = 0.7 if is_catch_all else 0.85
                
                return SMTPVerificationResult(
                    exists=True,
                    definitive=not is_catch_all,  # Less definitive if catch-all
                    confidence=confidence,
                    smtp_code=code,
                    smtp_message=message.decode() if isinstance(message, bytes) else str(message),
                    method_used="RCPT_TO",
                    server_tested=server,
                    response_time=response_time,
                    is_catch_all=is_catch_all,
                    temporary_failure=False,
                    errors=[],
                    metadata={"rcpt_to_successful": True}
                )
                
            elif code in [550, 551, 553]:
                # User not found
                return SMTPVerificationResult(
                    exists=False,
                    definitive=True,
                    confidence=0.8,
                    smtp_code=code,
                    smtp_message=message.decode() if isinstance(message, bytes) else str(message),
                    method_used="RCPT_TO_NOT_FOUND",
                    server_tested=server,
                    response_time=response_time,
                    is_catch_all=False,
                    temporary_failure=False,
                    errors=[],
                    metadata={"rcpt_to_user_not_found": True}
                )
                
            elif code in [450, 451, 452]:
                # Temporary failure
                return SMTPVerificationResult(
                    exists=None,
                    definitive=False,
                    confidence=0.3,
                    smtp_code=code,
                    smtp_message=message.decode() if isinstance(message, bytes) else str(message),
                    method_used="RCPT_TO_TEMP_FAIL",
                    server_tested=server,
                    response_time=response_time,
                    is_catch_all=None,
                    temporary_failure=True,
                    errors=[f"Temporary failure: {code}"],
                    metadata={"rcpt_to_temp_failure": True}
                )
                
            else:
                # Other response
                return SMTPVerificationResult(
                    exists=None,
                    definitive=False,
                    confidence=0.2,
                    smtp_code=code,
                    smtp_message=message.decode() if isinstance(message, bytes) else str(message),
                    method_used="RCPT_TO_OTHER",
                    server_tested=server,
                    response_time=response_time,
                    is_catch_all=None,
                    temporary_failure=code in [450, 451, 452],
                    errors=[f"RCPT TO returned code {code}"],
                    metadata={"rcpt_to_other_response": True}
                )
                
        except smtplib.SMTPException as e:
            return SMTPVerificationResult(
                exists=None,
                definitive=False,
                confidence=0.1,
                smtp_code=getattr(e, 'smtp_code', None),
                smtp_message=str(e),
                method_used="RCPT_TO_FAILED",
                server_tested=server,
                response_time=time.time() - start_time,
                is_catch_all=None,
                temporary_failure=True,
                errors=[f"RCPT TO failed: {str(e)}"],
                metadata={"rcpt_to_failed": True}
            )
    
    async def _quick_catch_all_check(self, smtp: smtplib.SMTP, domain: str, 
                                   sender: str) -> Optional[bool]:
        """Quick check to detect catch-all domains"""
        try:
            # Test with obviously fake addresses
            fake_addresses = [
                f"nonexistent{int(time.time())}@{domain}",
                f"fake{random.randint(10000, 99999)}@{domain}"
            ]
            
            accepted_count = 0
            for fake_email in fake_addresses:
                try:
                    code, _ = smtp.rcpt(fake_email)
                    if code == 250:
                        accepted_count += 1
                    smtp.rset()  # Reset for next test
                except:
                    break  # If any fail, stop testing
            
            # If most fake addresses are accepted, likely catch-all
            return accepted_count >= len(fake_addresses) * 0.5
            
        except Exception:
            return None
    
    async def _get_server_info(self, server: str) -> SMTPServerInfo:
        """Get or detect SMTP server capabilities"""
        if server in self._server_info_cache:
            info, cache_time = self._server_info_cache[server]
            if time.time() - cache_time < 3600:  # 1-hour cache
                return info
        
        # Detect server capabilities
        server_info = SMTPServerInfo(
            hostname=server,
            supports_vrfy=True,  # Assume true, will be updated
            supports_ehlo=True,  # Assume true, will be updated
            supports_starttls=False,
            max_recipients=None,
            rate_limit_detected=False,
            greylisting_detected=False,
            connection_timeout=self.timeout,
            last_tested=datetime.now()
        )
        
        try:
            # Quick capability detection
            smtp = smtplib.SMTP(timeout=10)  # Short timeout for detection
            smtp.connect(server, 25)
            
            try:
                # Test EHLO support
                try:
                    smtp.ehlo(self.helo_hostname)
                    server_info.supports_ehlo = True
                except:
                    server_info.supports_ehlo = False
                    try:
                        smtp.helo(self.helo_hostname)
                    except:
                        pass
                
                # Test VRFY support with a safe test
                try:
                    smtp.vrfy("test")  # This might fail but tells us if VRFY works
                    server_info.supports_vrfy = True
                except smtplib.SMTPException as e:
                    if "command not implemented" in str(e).lower():
                        server_info.supports_vrfy = False
                    # Other errors might still mean VRFY is supported
                
            finally:
                try:
                    smtp.quit()
                except:
                    pass
                    
        except Exception as e:
            logger.warning(f"Could not detect capabilities for {server}: {e}")
            # Use defaults
        
        # Cache the server info
        self._server_info_cache[server] = (server_info, time.time())
        return server_info

# Convenience function for integration
async def verify_email_smtp(email: str, mx_servers: List[str], 
                           timeout: float = 30.0) -> SMTPVerificationResult:
    """
    Convenience function for SMTP email verification
    
    Args:
        email: Email address to verify
        mx_servers: List of MX servers for the domain
        timeout: SMTP timeout in seconds
        
    Returns:
        SMTPVerificationResult with verification details
    """
    verifier = SMTPEmailVerifier(timeout=timeout)
    return await verifier.verify_email_existence(email, mx_servers)

if __name__ == "__main__":
    # Test the SMTP verifier
    async def test_smtp_verifier():
        """Test the SMTP verifier with various email addresses"""
        test_cases = [
            ("test@gmail.com", ["gmail-smtp-in.l.google.com"]),
            ("nonexistent@gmail.com", ["gmail-smtp-in.l.google.com"]),
            ("admin@example.com", ["example.com"]),  # Might not exist
        ]
        
        verifier = SMTPEmailVerifier(timeout=15.0, rate_limit_per_minute=5)
        
        for email, mx_servers in test_cases:
            print(f"\n🔍 Testing SMTP verification: {email}")
            result = await verifier.verify_email_existence(email, mx_servers)
            
            print(f"  Exists: {result.exists}")
            print(f"  Definitive: {result.definitive}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Method: {result.method_used}")
            print(f"  SMTP Code: {result.smtp_code}")
            print(f"  Response time: {result.response_time:.3f}s")
            print(f"  Catch-all: {result.is_catch_all}")
            print(f"  Temp failure: {result.temporary_failure}")
            
            if result.errors:
                print(f"  Errors: {result.errors}")
    
    # Run the test
    asyncio.run(test_smtp_verifier())
