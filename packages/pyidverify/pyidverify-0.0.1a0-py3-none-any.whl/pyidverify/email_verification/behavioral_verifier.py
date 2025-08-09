"""
Behavioral Email Verification System
===================================

This module implements behavioral verification for email addresses:
- Email confirmation workflows
- Click-through tracking
- Engagement verification
- Temporary token systems
- Multi-step verification processes
- User behavior analytics

Phase 5 Implementation for PyIDVerify Email Verification Enhancement
"""

import asyncio
import hashlib
import secrets
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import json
import re

# For email sending (optional dependency)
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerificationWorkflowType(Enum):
    """Types of behavioral verification workflows"""
    EMAIL_CONFIRMATION = "email_confirmation"         # Simple click-to-confirm
    DOUBLE_OPTIN = "double_optin"                    # Two-step confirmation
    ENGAGEMENT_TRACKING = "engagement_tracking"       # Track email opens/clicks
    MULTI_FACTOR = "multi_factor"                    # Multiple verification steps
    PROGRESSIVE = "progressive"                       # Gradual verification building

class TokenType(Enum):
    """Types of verification tokens"""
    CONFIRMATION = "confirmation"     # Email confirmation token
    ENGAGEMENT = "engagement"         # Email engagement tracking
    TEMPORARY = "temporary"           # Short-lived verification token
    PERSISTENT = "persistent"         # Long-term verification token

@dataclass
class VerificationToken:
    """Token for email verification workflows"""
    token_id: str
    token_type: TokenType
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Token properties
    is_used: bool = False
    used_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3
    
    # Behavioral tracking
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        if self.is_used or self.attempts >= self.max_attempts:
            return False
            
        if self.expires_at and datetime.now() > self.expires_at:
            return False
            
        return True
    
    def use_token(self, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Mark token as used"""
        if not self.is_valid():
            raise ValueError("Token is no longer valid")
            
        self.is_used = True
        self.used_at = datetime.now()
        if ip_address:
            self.ip_address = ip_address
        if user_agent:
            self.user_agent = user_agent

@dataclass
class BehavioralVerificationResult:
    """Result of behavioral email verification"""
    email: str
    workflow_type: VerificationWorkflowType
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Verification status
    status: str = "pending"  # pending, confirmed, failed, expired, suspicious
    confirmed: bool = False
    confidence: float = 0.0
    
    # Behavioral data
    response_time: Optional[float] = None  # Time to respond in seconds
    click_count: int = 0
    open_count: int = 0
    unique_opens: int = 0
    engagement_score: float = 0.0
    
    # Security indicators
    suspicious_activity: bool = False
    bot_indicators: List[str] = field(default_factory=list)
    location_consistency: bool = True
    device_consistency: bool = True
    
    # Workflow tracking
    steps_completed: List[str] = field(default_factory=list)
    steps_remaining: List[str] = field(default_factory=list)
    total_attempts: int = 0
    
    # Analytics
    devices_used: List[Dict[str, str]] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    referrers: List[str] = field(default_factory=list)
    
    # Additional details
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class BehavioralEmailVerifier:
    """
    Behavioral email verification system
    """
    
    def __init__(self, 
                 smtp_config: Optional[Dict[str, str]] = None,
                 base_url: str = "https://verify.example.com",
                 default_token_ttl_hours: int = 24):
        """
        Initialize behavioral verifier
        
        Args:
            smtp_config: SMTP configuration for sending emails
            base_url: Base URL for verification links
            default_token_ttl_hours: Default token time-to-live
        """
        self.smtp_config = smtp_config or {}
        self.base_url = base_url.rstrip('/')
        self.default_token_ttl_hours = default_token_ttl_hours
        
        # Token storage (in production, use persistent storage)
        self.tokens: Dict[str, VerificationToken] = {}
        self.verification_results: Dict[str, BehavioralVerificationResult] = {}
        
        # Email templates
        self.email_templates = self._load_email_templates()
        
        # Analytics tracking
        self.analytics: Dict[str, List[Dict]] = {
            "clicks": [],
            "opens": [],
            "confirmations": [],
            "failures": []
        }
        
        logger.info(f"Initialized behavioral verifier with base URL: {base_url}")
    
    def _load_email_templates(self) -> Dict[str, Dict[str, str]]:
        """Load email templates for different verification workflows"""
        return {
            "confirmation": {
                "subject": "Please confirm your email address",
                "html": """
                <html>
                <body>
                    <h2>Email Confirmation Required</h2>
                    <p>Please confirm your email address by clicking the link below:</p>
                    <p><a href="{confirmation_url}" style="background-color: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Confirm Email</a></p>
                    <p>Or copy and paste this URL into your browser:</p>
                    <p>{confirmation_url}</p>
                    <p>This link will expire in {expiry_hours} hours.</p>
                    <p>If you didn't request this verification, please ignore this email.</p>
                    
                    <!-- Tracking pixel -->
                    <img src="{tracking_url}" width="1" height="1" style="display:none;" alt="">
                </body>
                </html>
                """,
                "text": """
                Email Confirmation Required
                
                Please confirm your email address by visiting this URL:
                {confirmation_url}
                
                This link will expire in {expiry_hours} hours.
                
                If you didn't request this verification, please ignore this email.
                """
            },
            "double_optin": {
                "subject": "Complete your email verification - Step 2 of 2",
                "html": """
                <html>
                <body>
                    <h2>Final Verification Step</h2>
                    <p>Thanks for confirming your email! Please complete the verification process:</p>
                    <p><a href="{verification_url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Complete Verification</a></p>
                    <p>This is the final step to verify your email address.</p>
                    
                    <!-- Tracking pixel -->
                    <img src="{tracking_url}" width="1" height="1" style="display:none;" alt="">
                </body>
                </html>
                """
            }
        }
    
    async def start_verification_workflow(self, 
                                        email: str, 
                                        workflow_type: VerificationWorkflowType = VerificationWorkflowType.EMAIL_CONFIRMATION,
                                        user_context: Optional[Dict] = None) -> BehavioralVerificationResult:
        """
        Start a behavioral verification workflow for an email address
        
        Args:
            email: Email address to verify
            workflow_type: Type of verification workflow
            user_context: Additional user context
            
        Returns:
            BehavioralVerificationResult tracking workflow progress
        """
        # Create verification result
        result = BehavioralVerificationResult(
            email=email,
            workflow_type=workflow_type,
            status="pending"
        )
        
        # Store result
        result_id = self._generate_result_id(email)
        self.verification_results[result_id] = result
        
        try:
            if workflow_type == VerificationWorkflowType.EMAIL_CONFIRMATION:
                await self._start_email_confirmation(result, user_context)
            elif workflow_type == VerificationWorkflowType.DOUBLE_OPTIN:
                await self._start_double_optin(result, user_context)
            elif workflow_type == VerificationWorkflowType.ENGAGEMENT_TRACKING:
                await self._start_engagement_tracking(result, user_context)
            elif workflow_type == VerificationWorkflowType.MULTI_FACTOR:
                await self._start_multi_factor(result, user_context)
            elif workflow_type == VerificationWorkflowType.PROGRESSIVE:
                await self._start_progressive_verification(result, user_context)
            else:
                raise ValueError(f"Unsupported workflow type: {workflow_type}")
                
            result.status = "email_sent"
            return result
            
        except Exception as e:
            logger.error(f"Failed to start verification workflow for {email}: {e}")
            result.status = "failed"
            result.notes.append(f"Workflow start failed: {str(e)}")
            return result
    
    async def _start_email_confirmation(self, result: BehavioralVerificationResult, user_context: Optional[Dict]):
        """Start simple email confirmation workflow"""
        # Generate confirmation token
        token = self._create_token(
            result.email,
            TokenType.CONFIRMATION,
            expires_in_hours=self.default_token_ttl_hours
        )
        
        # Create confirmation URL
        confirmation_url = f"{self.base_url}/confirm?token={token.token_id}"
        tracking_url = f"{self.base_url}/track/open?token={token.token_id}"
        
        # Send confirmation email
        template = self.email_templates["confirmation"]
        await self._send_verification_email(
            result.email,
            template["subject"],
            template["html"].format(
                confirmation_url=confirmation_url,
                tracking_url=tracking_url,
                expiry_hours=self.default_token_ttl_hours
            ),
            template["text"].format(
                confirmation_url=confirmation_url,
                expiry_hours=self.default_token_ttl_hours
            )
        )
        
        result.steps_remaining = ["click_confirmation"]
        result.metadata["confirmation_token"] = token.token_id
    
    async def _start_double_optin(self, result: BehavioralVerificationResult, user_context: Optional[Dict]):
        """Start double opt-in verification workflow"""
        # First, start regular confirmation
        await self._start_email_confirmation(result, user_context)
        
        # Add second step
        result.steps_remaining = ["click_confirmation", "final_verification"]
        result.metadata["workflow_step"] = 1
    
    async def _start_engagement_tracking(self, result: BehavioralVerificationResult, user_context: Optional[Dict]):
        """Start engagement tracking verification"""
        # Create engagement token
        token = self._create_token(
            result.email,
            TokenType.ENGAGEMENT,
            expires_in_hours=self.default_token_ttl_hours * 7  # Longer for engagement
        )
        
        # Send engagement email with multiple trackable elements
        await self._send_engagement_email(result.email, token)
        
        result.steps_remaining = ["email_open", "link_click", "engagement_threshold"]
        result.metadata["engagement_token"] = token.token_id
    
    async def _start_multi_factor(self, result: BehavioralVerificationResult, user_context: Optional[Dict]):
        """Start multi-factor verification"""
        # Start with email confirmation
        await self._start_email_confirmation(result, user_context)
        
        # Add additional verification steps
        result.steps_remaining = ["click_confirmation", "additional_verification", "final_approval"]
        result.metadata["mfa_enabled"] = True
    
    async def _start_progressive_verification(self, result: BehavioralVerificationResult, user_context: Optional[Dict]):
        """Start progressive verification building confidence over time"""
        # Start with basic confirmation
        await self._start_email_confirmation(result, user_context)
        
        # Set up progressive verification steps
        result.steps_remaining = ["basic_confirmation", "engagement_check", "time_validation", "final_verification"]
        result.metadata["progressive_level"] = 1
    
    def _create_token(self, email: str, token_type: TokenType, expires_in_hours: int = 24) -> VerificationToken:
        """Create a verification token"""
        # Generate secure token ID
        token_id = self._generate_secure_token()
        
        # Calculate expiration
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        
        # Create token
        token = VerificationToken(
            token_id=token_id,
            token_type=token_type,
            email=email,
            expires_at=expires_at
        )
        
        # Store token
        self.tokens[token_id] = token
        
        return token
    
    def _generate_secure_token(self) -> str:
        """Generate a cryptographically secure token"""
        return secrets.token_urlsafe(32)
    
    def _generate_result_id(self, email: str) -> str:
        """Generate a unique result ID for an email"""
        return hashlib.sha256(f"{email}-{time.time()}".encode()).hexdigest()
    
    async def _send_verification_email(self, email: str, subject: str, html_body: str, text_body: str):
        """Send verification email via SMTP"""
        if not SMTP_AVAILABLE:
            logger.warning("SMTP not available - email sending disabled")
            return
            
        if not self.smtp_config:
            logger.warning("SMTP configuration not provided - email sending disabled")
            return
            
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_config.get("from_email", "noreply@example.com")
            msg["To"] = email
            
            # Add text and HTML parts
            text_part = MIMEText(text_body, "plain")
            html_part = MIMEText(html_body, "html")
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_config.get("host", "localhost"), 
                            self.smtp_config.get("port", 587)) as server:
                if self.smtp_config.get("use_tls"):
                    server.starttls()
                    
                if self.smtp_config.get("username") and self.smtp_config.get("password"):
                    server.login(self.smtp_config["username"], self.smtp_config["password"])
                    
                server.send_message(msg)
                
            logger.info(f"Verification email sent to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            raise
    
    async def _send_engagement_email(self, email: str, token: VerificationToken):
        """Send engagement tracking email"""
        tracking_params = f"?token={token.token_id}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome! Let's verify your engagement</h2>
            <p>Please interact with this email to verify your address:</p>
            
            <p><a href="{self.base_url}/click{tracking_params}&action=primary">Primary Action</a></p>
            <p><a href="{self.base_url}/click{tracking_params}&action=secondary">Learn More</a></p>
            
            <div style="margin: 20px 0;">
                <img src="{self.base_url}/track/image{tracking_params}" alt="Content" style="max-width: 100%;">
            </div>
            
            <p><a href="{self.base_url}/unsubscribe{tracking_params}">Unsubscribe</a></p>
            
            <!-- Tracking pixels -->
            <img src="{self.base_url}/track/open{tracking_params}" width="1" height="1" style="display:none;">
        </body>
        </html>
        """
        
        await self._send_verification_email(
            email,
            "Email Engagement Verification",
            html_content,
            "Please visit our website to complete verification."
        )
    
    async def handle_confirmation(self, token_id: str, 
                                ip_address: Optional[str] = None, 
                                user_agent: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle email confirmation click
        
        Args:
            token_id: Verification token ID
            ip_address: User's IP address
            user_agent: User's user agent
            
        Returns:
            Confirmation result
        """
        try:
            # Find token
            token = self.tokens.get(token_id)
            if not token:
                return {"success": False, "error": "Invalid token"}
                
            if not token.is_valid():
                return {"success": False, "error": "Token expired or already used"}
            
            # Find verification result
            result = self._find_result_by_email(token.email)
            if not result:
                return {"success": False, "error": "Verification session not found"}
            
            # Use token
            token.use_token(ip_address, user_agent)
            
            # Calculate response time
            response_time = (datetime.now() - token.created_at).total_seconds()
            result.response_time = response_time
            
            # Update result
            result.click_count += 1
            result.total_attempts += 1
            result.steps_completed.append("click_confirmation")
            
            if "click_confirmation" in result.steps_remaining:
                result.steps_remaining.remove("click_confirmation")
            
            # Check for suspicious activity
            await self._analyze_behavior(result, token, ip_address, user_agent)
            
            # Handle workflow progression
            if result.workflow_type == VerificationWorkflowType.EMAIL_CONFIRMATION:
                result.confirmed = True
                result.status = "confirmed"
                result.confidence = 0.9
                
            elif result.workflow_type == VerificationWorkflowType.DOUBLE_OPTIN:
                if result.metadata.get("workflow_step", 1) == 1:
                    # Start second step
                    await self._send_second_optin_email(result)
                    result.metadata["workflow_step"] = 2
                else:
                    result.confirmed = True
                    result.status = "confirmed"
                    result.confidence = 0.95
            
            # Record analytics
            self.analytics["confirmations"].append({
                "email": token.email,
                "timestamp": datetime.now().isoformat(),
                "response_time": response_time,
                "ip_address": ip_address,
                "user_agent": user_agent
            })
            
            return {
                "success": True,
                "status": result.status,
                "confirmed": result.confirmed,
                "confidence": result.confidence,
                "next_steps": result.steps_remaining
            }
            
        except Exception as e:
            logger.error(f"Confirmation handling failed for token {token_id}: {e}")
            return {"success": False, "error": "Internal error"}
    
    async def handle_email_open(self, token_id: str, 
                              ip_address: Optional[str] = None, 
                              user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Handle email open tracking"""
        try:
            token = self.tokens.get(token_id)
            if not token:
                return {"success": False, "error": "Invalid token"}
            
            result = self._find_result_by_email(token.email)
            if not result:
                return {"success": False, "error": "Verification session not found"}
            
            # Track email open
            result.open_count += 1
            
            # Check for unique open
            device_fingerprint = self._create_device_fingerprint(ip_address, user_agent)
            existing_devices = [d.get("fingerprint") for d in result.devices_used]
            
            if device_fingerprint not in existing_devices:
                result.unique_opens += 1
                result.devices_used.append({
                    "fingerprint": device_fingerprint,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "timestamp": datetime.now().isoformat()
                })
            
            if ip_address and ip_address not in result.ip_addresses:
                result.ip_addresses.append(ip_address)
            
            # Update engagement score
            result.engagement_score = min(1.0, result.open_count * 0.1 + result.unique_opens * 0.3)
            
            # Record analytics
            self.analytics["opens"].append({
                "email": token.email,
                "timestamp": datetime.now().isoformat(),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "unique": device_fingerprint not in existing_devices
            })
            
            return {"success": True, "tracked": True}
            
        except Exception as e:
            logger.error(f"Email open tracking failed: {e}")
            return {"success": False, "error": "Tracking failed"}
    
    async def handle_link_click(self, token_id: str, action: str,
                              ip_address: Optional[str] = None, 
                              user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Handle link click tracking"""
        try:
            token = self.tokens.get(token_id)
            if not token:
                return {"success": False, "error": "Invalid token"}
            
            result = self._find_result_by_email(token.email)
            if not result:
                return {"success": False, "error": "Verification session not found"}
            
            # Track click
            result.click_count += 1
            result.engagement_score = min(1.0, result.engagement_score + 0.2)
            
            # Record analytics
            self.analytics["clicks"].append({
                "email": token.email,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "ip_address": ip_address,
                "user_agent": user_agent
            })
            
            # Check engagement threshold for engagement tracking workflow
            if result.workflow_type == VerificationWorkflowType.ENGAGEMENT_TRACKING:
                if result.engagement_score >= 0.5:  # Threshold for meaningful engagement
                    result.confirmed = True
                    result.status = "confirmed"
                    result.confidence = min(1.0, result.engagement_score)
                    
                    if "engagement_threshold" in result.steps_remaining:
                        result.steps_remaining.remove("engagement_threshold")
            
            return {"success": True, "action": action, "engagement_score": result.engagement_score}
            
        except Exception as e:
            logger.error(f"Link click tracking failed: {e}")
            return {"success": False, "error": "Tracking failed"}
    
    def _find_result_by_email(self, email: str) -> Optional[BehavioralVerificationResult]:
        """Find verification result by email address"""
        for result in self.verification_results.values():
            if result.email == email:
                return result
        return None
    
    def _create_device_fingerprint(self, ip_address: Optional[str], user_agent: Optional[str]) -> str:
        """Create a device fingerprint from IP and user agent"""
        fingerprint_data = f"{ip_address or 'unknown'}-{user_agent or 'unknown'}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    async def _analyze_behavior(self, result: BehavioralVerificationResult, 
                               token: VerificationToken,
                               ip_address: Optional[str], 
                               user_agent: Optional[str]):
        """Analyze user behavior for suspicious activity"""
        # Response time analysis
        if result.response_time and result.response_time < 2:  # Very quick response
            result.bot_indicators.append("very_fast_response")
        
        # User agent analysis
        if user_agent:
            if re.search(r'bot|crawler|spider|scraper', user_agent, re.IGNORECASE):
                result.bot_indicators.append("bot_user_agent")
        
        # Location consistency check
        if len(result.ip_addresses) > 3:  # Multiple different IPs
            result.location_consistency = False
            result.bot_indicators.append("multiple_locations")
        
        # Device consistency check  
        if len(result.devices_used) > 2:  # Multiple devices
            result.device_consistency = False
        
        # Suspicious activity determination
        result.suspicious_activity = len(result.bot_indicators) > 0
        
        if result.suspicious_activity:
            result.confidence = max(0.1, result.confidence - 0.3)  # Reduce confidence
            result.notes.append(f"Suspicious indicators: {result.bot_indicators}")
    
    async def _send_second_optin_email(self, result: BehavioralVerificationResult):
        """Send second opt-in email for double opt-in workflow"""
        # Create second token
        token = self._create_token(
            result.email,
            TokenType.CONFIRMATION,
            expires_in_hours=48  # Longer expiry for second step
        )
        
        verification_url = f"{self.base_url}/confirm?token={token.token_id}&step=2"
        tracking_url = f"{self.base_url}/track/open?token={token.token_id}"
        
        template = self.email_templates["double_optin"]
        await self._send_verification_email(
            result.email,
            template["subject"],
            template["html"].format(
                verification_url=verification_url,
                tracking_url=tracking_url
            ),
            f"Please complete verification: {verification_url}"
        )
        
        result.metadata["second_optin_token"] = token.token_id
    
    def get_verification_status(self, email: str) -> Optional[Dict[str, Any]]:
        """Get current verification status for an email"""
        result = self._find_result_by_email(email)
        if not result:
            return None
        
        return {
            "email": result.email,
            "status": result.status,
            "confirmed": result.confirmed,
            "confidence": result.confidence,
            "workflow_type": result.workflow_type.value,
            "steps_completed": result.steps_completed,
            "steps_remaining": result.steps_remaining,
            "engagement_score": result.engagement_score,
            "suspicious_activity": result.suspicious_activity,
            "response_time": result.response_time,
            "timestamp": result.timestamp.isoformat()
        }
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        total_verifications = len(self.verification_results)
        confirmed = sum(1 for r in self.verification_results.values() if r.confirmed)
        suspicious = sum(1 for r in self.verification_results.values() if r.suspicious_activity)
        
        avg_response_time = 0
        response_times = [r.response_time for r in self.verification_results.values() if r.response_time]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "total_verifications": total_verifications,
            "confirmed_verifications": confirmed,
            "confirmation_rate": confirmed / max(total_verifications, 1),
            "suspicious_activity_rate": suspicious / max(total_verifications, 1),
            "average_response_time_seconds": avg_response_time,
            "total_email_opens": sum(len(self.analytics["opens"]), 0),
            "total_link_clicks": len(self.analytics["clicks"]),
            "total_confirmations": len(self.analytics["confirmations"])
        }
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens and results"""
        now = datetime.now()
        expired_tokens = []
        
        for token_id, token in self.tokens.items():
            if not token.is_valid():
                expired_tokens.append(token_id)
        
        for token_id in expired_tokens:
            del self.tokens[token_id]
        
        logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")

# Convenience functions
async def verify_email_behavioral(email: str, 
                                workflow_type: VerificationWorkflowType = VerificationWorkflowType.EMAIL_CONFIRMATION,
                                smtp_config: Optional[Dict[str, str]] = None) -> BehavioralVerificationResult:
    """
    Convenience function for behavioral email verification
    
    Args:
        email: Email address to verify
        workflow_type: Type of verification workflow
        smtp_config: SMTP configuration for sending emails
        
    Returns:
        BehavioralVerificationResult with workflow status
    """
    verifier = BehavioralEmailVerifier(smtp_config=smtp_config)
    return await verifier.start_verification_workflow(email, workflow_type)

if __name__ == "__main__":
    # Test behavioral verification system
    async def test_behavioral_verifier():
        """Test behavioral verification system"""
        
        # Mock SMTP configuration (use your actual SMTP settings)
        smtp_config = {
            "host": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "from_email": "noreply@yourservice.com"
        }
        
        verifier = BehavioralEmailVerifier(
            smtp_config=smtp_config,
            base_url="https://verify.yourservice.com"
        )
        
        test_email = "test@example.com"
        
        # Test different workflow types
        workflows = [
            VerificationWorkflowType.EMAIL_CONFIRMATION,
            VerificationWorkflowType.DOUBLE_OPTIN,
            VerificationWorkflowType.ENGAGEMENT_TRACKING
        ]
        
        for workflow in workflows:
            print(f"\n{'='*50}")
            print(f"Testing {workflow.value}")
            print(f"{'='*50}")
            
            # Start verification
            result = await verifier.start_verification_workflow(test_email, workflow)
            print(f"Started verification: {result.status}")
            print(f"Steps remaining: {result.steps_remaining}")
            
            # Simulate user interactions
            tokens = [token for token in verifier.tokens.values() if token.email == test_email]
            if tokens:
                token = tokens[0]
                
                # Simulate email open
                await verifier.handle_email_open(token.token_id, "192.168.1.1", "Mozilla/5.0...")
                
                # Simulate confirmation click
                confirmation_result = await verifier.handle_confirmation(
                    token.token_id, "192.168.1.1", "Mozilla/5.0..."
                )
                print(f"Confirmation result: {confirmation_result}")
                
                # Check final status
                status = verifier.get_verification_status(test_email)
                print(f"Final status: {status}")
        
        # Show analytics
        print(f"\n{'='*50}")
        print("Analytics Summary")
        print(f"{'='*50}")
        analytics = verifier.get_analytics_summary()
        for key, value in analytics.items():
            print(f"{key}: {value}")
    
    # Run test (commented out to avoid sending emails during import)
    # asyncio.run(test_behavioral_verifier())
