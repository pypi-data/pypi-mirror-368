"""
PyIDVerify Rate Limiter

Provides rate limiting and abuse prevention capabilities.
Implements sliding window, token bucket, and adaptive algorithms.

Author: PyIDVerify Team
License: MIT
"""

import time
import threading
import logging
from typing import Dict, Optional, Tuple, Any, List
from dataclasses import dataclass
from enum import Enum
from collections import deque, defaultdict
from .exceptions import SecurityError

logger = logging.getLogger(__name__)


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms."""
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    burst_capacity: int = 50
    window_size_seconds: int = 60
    cleanup_interval: int = 300
    enable_user_limits: bool = True
    enable_ip_limits: bool = True
    enable_global_limits: bool = True
    block_duration_seconds: int = 300
    adaptive_threshold: float = 0.8


class RateLimitExceededError(SecurityError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class SlidingWindowLimiter:
    """Sliding window rate limiter implementation."""
    
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = threading.Lock()
        
    def allow_request(self) -> bool:
        """Check if request is allowed under sliding window."""
        current_time = time.time()
        
        with self.lock:
            # Remove expired requests
            while self.requests and self.requests[0] <= current_time - self.window_seconds:
                self.requests.popleft()
                
            # Check if under limit
            if len(self.requests) < self.limit:
                self.requests.append(current_time)
                return True
                
            return False
            
    def get_remaining_requests(self) -> int:
        """Get number of remaining requests."""
        current_time = time.time()
        
        with self.lock:
            # Remove expired requests
            while self.requests and self.requests[0] <= current_time - self.window_seconds:
                self.requests.popleft()
                
            return max(0, self.limit - len(self.requests))
            
    def get_reset_time(self) -> float:
        """Get time when limit resets."""
        with self.lock:
            if not self.requests:
                return time.time()
            return self.requests[0] + self.window_seconds


class TokenBucketLimiter:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
        self.lock = threading.Lock()
        
    def allow_request(self, tokens_required: int = 1) -> bool:
        """Check if request is allowed under token bucket."""
        with self.lock:
            self._refill_tokens()
            
            if self.tokens >= tokens_required:
                self.tokens -= tokens_required
                return True
                
            return False
            
    def _refill_tokens(self):
        """Refill tokens based on time elapsed."""
        current_time = time.time()
        time_elapsed = current_time - self.last_refill
        tokens_to_add = time_elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = current_time
        
    def get_available_tokens(self) -> int:
        """Get number of available tokens."""
        with self.lock:
            self._refill_tokens()
            return int(self.tokens)


class AdaptiveLimiter:
    """Adaptive rate limiter that adjusts based on system load."""
    
    def __init__(self, base_limit: int, window_seconds: int, threshold: float = 0.8):
        self.base_limit = base_limit
        self.window_seconds = window_seconds
        self.threshold = threshold
        self.current_limit = base_limit
        self.success_rate_tracker = deque(maxlen=100)
        self.lock = threading.Lock()
        
        # Use sliding window as underlying mechanism
        self.limiter = SlidingWindowLimiter(self.current_limit, window_seconds)
        
    def allow_request(self, success_rate: Optional[float] = None) -> bool:
        """Check if request is allowed with adaptive limits."""
        if success_rate is not None:
            self._update_success_rate(success_rate)
            
        self._adjust_limit()
        
        # Update limiter if limit changed
        with self.lock:
            if self.limiter.limit != self.current_limit:
                self.limiter = SlidingWindowLimiter(self.current_limit, self.window_seconds)
                
        return self.limiter.allow_request()
        
    def _update_success_rate(self, success_rate: float):
        """Update success rate tracking."""
        with self.lock:
            self.success_rate_tracker.append(success_rate)
            
    def _adjust_limit(self):
        """Adjust rate limit based on success rate."""
        if not self.success_rate_tracker:
            return
            
        with self.lock:
            avg_success_rate = sum(self.success_rate_tracker) / len(self.success_rate_tracker)
            
            if avg_success_rate < self.threshold:
                # Decrease limit if success rate is low
                self.current_limit = max(1, int(self.current_limit * 0.9))
            elif avg_success_rate > 0.95:
                # Increase limit if success rate is very high
                self.current_limit = min(self.base_limit * 2, int(self.current_limit * 1.1))


class RateLimiter:
    """
    Comprehensive rate limiter with multiple algorithms and scopes.
    
    Features:
    - Multiple rate limiting algorithms
    - User-based, IP-based, and global limits
    - Automatic cleanup of expired data
    - Configurable block duration
    - Rate limit information for clients
    - Adaptive limits based on system performance
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """Initialize rate limiter with configuration."""
        self.config = config or RateLimitConfig()
        
        # Storage for different scopes
        self.user_limiters: Dict[str, Any] = {}
        self.ip_limiters: Dict[str, Any] = {}
        self.global_limiter = self._create_limiter()
        
        # Blocked entities
        self.blocked_users: Dict[str, float] = {}  # user_id -> unblock_time
        self.blocked_ips: Dict[str, float] = {}    # ip -> unblock_time
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        logger.info("RateLimiter initialized")
        
    def allow_request(self, 
                     user_id: Optional[str] = None,
                     ip_address: Optional[str] = None,
                     endpoint: Optional[str] = None) -> bool:
        """
        Check if request is allowed.
        
        Args:
            user_id: User identifier
            ip_address: Client IP address
            endpoint: API endpoint being accessed
            
        Returns:
            True if request allowed, False otherwise
            
        Raises:
            RateLimitExceededError: If rate limit exceeded
        """
        current_time = time.time()
        
        # Check if user is blocked
        if user_id and self._is_blocked_user(user_id, current_time):
            retry_after = int(self.blocked_users[user_id] - current_time)
            raise RateLimitExceededError(
                f"User {user_id} is temporarily blocked",
                retry_after=retry_after
            )
            
        # Check if IP is blocked
        if ip_address and self._is_blocked_ip(ip_address, current_time):
            retry_after = int(self.blocked_ips[ip_address] - current_time)
            raise RateLimitExceededError(
                f"IP {ip_address} is temporarily blocked",
                retry_after=retry_after
            )
            
        # Check global limits
        if self.config.enable_global_limits and not self.global_limiter.allow_request():
            raise RateLimitExceededError("Global rate limit exceeded")
            
        # Check user-specific limits
        if user_id and self.config.enable_user_limits:
            user_limiter = self._get_user_limiter(user_id)
            if not user_limiter.allow_request():
                self._block_user(user_id, current_time)
                raise RateLimitExceededError(
                    f"Rate limit exceeded for user {user_id}",
                    retry_after=self.config.block_duration_seconds
                )
                
        # Check IP-specific limits
        if ip_address and self.config.enable_ip_limits:
            ip_limiter = self._get_ip_limiter(ip_address)
            if not ip_limiter.allow_request():
                self._block_ip(ip_address, current_time)
                raise RateLimitExceededError(
                    f"Rate limit exceeded for IP {ip_address}",
                    retry_after=self.config.block_duration_seconds
                )
                
        return True
        
    def get_rate_limit_info(self, 
                          user_id: Optional[str] = None,
                          ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get rate limit information for client.
        
        Returns:
            Dictionary with rate limit status information
        """
        info = {
            'global': self._get_limiter_info(self.global_limiter),
            'limits': {
                'requests_per_minute': self.config.requests_per_minute,
                'requests_per_hour': self.config.requests_per_hour,
                'burst_capacity': self.config.burst_capacity
            }
        }
        
        if user_id and self.config.enable_user_limits:
            user_limiter = self._get_user_limiter(user_id)
            info['user'] = self._get_limiter_info(user_limiter)
            info['user']['blocked'] = self._is_blocked_user(user_id, time.time())
            
        if ip_address and self.config.enable_ip_limits:
            ip_limiter = self._get_ip_limiter(ip_address)
            info['ip'] = self._get_limiter_info(ip_limiter)
            info['ip']['blocked'] = self._is_blocked_ip(ip_address, time.time())
            
        return info
        
    def reset_limits(self, user_id: Optional[str] = None, ip_address: Optional[str] = None):
        """Reset rate limits for user or IP."""
        with self.lock:
            if user_id:
                self.user_limiters.pop(user_id, None)
                self.blocked_users.pop(user_id, None)
                logger.info(f"Reset rate limits for user {user_id}")
                
            if ip_address:
                self.ip_limiters.pop(ip_address, None)
                self.blocked_ips.pop(ip_address, None)
                logger.info(f"Reset rate limits for IP {ip_address}")
                
    def get_blocked_entities(self) -> Dict[str, List[str]]:
        """Get list of currently blocked users and IPs."""
        current_time = time.time()
        
        blocked_users = [
            user_id for user_id, unblock_time in self.blocked_users.items()
            if unblock_time > current_time
        ]
        
        blocked_ips = [
            ip for ip, unblock_time in self.blocked_ips.items()
            if unblock_time > current_time
        ]
        
        return {
            'users': blocked_users,
            'ips': blocked_ips
        }
        
    def _create_limiter(self):
        """Create rate limiter instance based on configuration."""
        if self.config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return SlidingWindowLimiter(
                self.config.requests_per_minute,
                self.config.window_size_seconds
            )
        elif self.config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return TokenBucketLimiter(
                self.config.burst_capacity,
                self.config.requests_per_minute / 60.0  # per second
            )
        elif self.config.algorithm == RateLimitAlgorithm.ADAPTIVE:
            return AdaptiveLimiter(
                self.config.requests_per_minute,
                self.config.window_size_seconds,
                self.config.adaptive_threshold
            )
        else:
            return SlidingWindowLimiter(
                self.config.requests_per_minute,
                self.config.window_size_seconds
            )
            
    def _get_user_limiter(self, user_id: str):
        """Get or create rate limiter for user."""
        if user_id not in self.user_limiters:
            with self.lock:
                if user_id not in self.user_limiters:
                    self.user_limiters[user_id] = self._create_limiter()
        return self.user_limiters[user_id]
        
    def _get_ip_limiter(self, ip_address: str):
        """Get or create rate limiter for IP address."""
        if ip_address not in self.ip_limiters:
            with self.lock:
                if ip_address not in self.ip_limiters:
                    self.ip_limiters[ip_address] = self._create_limiter()
        return self.ip_limiters[ip_address]
        
    def _is_blocked_user(self, user_id: str, current_time: float) -> bool:
        """Check if user is currently blocked."""
        unblock_time = self.blocked_users.get(user_id, 0)
        return unblock_time > current_time
        
    def _is_blocked_ip(self, ip_address: str, current_time: float) -> bool:
        """Check if IP is currently blocked."""
        unblock_time = self.blocked_ips.get(ip_address, 0)
        return unblock_time > current_time
        
    def _block_user(self, user_id: str, current_time: float):
        """Block user for configured duration."""
        with self.lock:
            self.blocked_users[user_id] = current_time + self.config.block_duration_seconds
        logger.warning(f"Blocked user {user_id} for {self.config.block_duration_seconds} seconds")
        
    def _block_ip(self, ip_address: str, current_time: float):
        """Block IP address for configured duration."""
        with self.lock:
            self.blocked_ips[ip_address] = current_time + self.config.block_duration_seconds
        logger.warning(f"Blocked IP {ip_address} for {self.config.block_duration_seconds} seconds")
        
    def _get_limiter_info(self, limiter) -> Dict[str, Any]:
        """Get information about a rate limiter."""
        if isinstance(limiter, SlidingWindowLimiter):
            return {
                'remaining_requests': limiter.get_remaining_requests(),
                'reset_time': limiter.get_reset_time(),
                'limit': limiter.limit,
                'window_seconds': limiter.window_seconds
            }
        elif isinstance(limiter, TokenBucketLimiter):
            return {
                'available_tokens': limiter.get_available_tokens(),
                'capacity': limiter.capacity,
                'refill_rate': limiter.refill_rate
            }
        else:
            return {'type': 'unknown'}
            
    def _cleanup_expired_data(self):
        """Clean up expired blocks and limiters."""
        current_time = time.time()
        
        with self.lock:
            # Clean up expired blocks
            self.blocked_users = {
                user_id: unblock_time for user_id, unblock_time in self.blocked_users.items()
                if unblock_time > current_time
            }
            
            self.blocked_ips = {
                ip: unblock_time for ip, unblock_time in self.blocked_ips.items()
                if unblock_time > current_time
            }
            
            # Optionally clean up old limiters (implementation specific)
            # This could be based on last access time, etc.
            
    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_loop():
            while True:
                try:
                    time.sleep(self.config.cleanup_interval)
                    self._cleanup_expired_data()
                except Exception as e:
                    logger.error(f"Cleanup thread error: {str(e)}")
                    
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
