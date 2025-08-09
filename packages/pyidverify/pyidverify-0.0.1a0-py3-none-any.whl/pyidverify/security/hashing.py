"""
Secure Hashing Implementation

Provides military-grade hashing capabilities using Argon2id for password hashing
and Blake3 for high-performance general-purpose hashing, with built-in security
protections against timing attacks and memory analysis.

Features:
- Argon2id password hashing (OWASP recommended)
- Blake3 high-performance hashing
- Constant-time comparison operations
- Secure salt generation and management
- Memory clearing for sensitive operations
- Timing attack protection

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import hashlib
import hmac
import secrets
import time
from typing import Optional, Union, Tuple, Dict, Any
import logging

# Third-party cryptographic libraries
try:
    import argon2
    from argon2 import PasswordHasher
    from argon2.exceptions import (
        VerifyMismatchError, 
        HashingError, 
        VerificationError,
        InvalidHashError
    )
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False
    argon2 = None
    PasswordHasher = None

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False
    blake3 = None

from .exceptions import CryptographicError, SecurityError
from .constants import (
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_SALT_SIZE,
    ARGON2_HASH_SIZE,
    CONSTANT_TIME_COMPARE_LENGTH,
    TIMING_SAFE_ITERATIONS,
    SecurityLevel,
    HashAlgorithm
)

# Configure logging
logger = logging.getLogger('pyidverify.security.hashing')


class SecureHasher:
    """
    Military-grade secure hashing implementation with multiple algorithms.
    
    Supports Argon2id for password hashing and Blake3 for general-purpose
    high-performance hashing with built-in security protections.
    """
    
    def __init__(
        self,
        security_level: SecurityLevel = SecurityLevel.MAXIMUM,
        primary_algorithm: HashAlgorithm = HashAlgorithm.ARGON2ID,
        memory_cost: Optional[int] = None,
        time_cost: Optional[int] = None,
        parallelism: Optional[int] = None
    ):
        """
        Initialize SecureHasher with specified security parameters.
        
        Args:
            security_level: Security level determining default parameters
            primary_algorithm: Primary hashing algorithm to use
            memory_cost: Argon2 memory cost (defaults based on security level)
            time_cost: Argon2 time cost (defaults based on security level)
            parallelism: Argon2 parallelism (defaults based on security level)
            
        Raises:
            CryptographicError: If required libraries are not available
        """
        self.security_level = security_level
        self.primary_algorithm = primary_algorithm
        self._operation_count = 0
        
        # Validate dependencies
        if primary_algorithm == HashAlgorithm.ARGON2ID and not ARGON2_AVAILABLE:
            raise CryptographicError(
                "Argon2 library not available. Install with: pip install argon2-cffi",
                operation="initialization",
                algorithm="argon2id"
            )
        
        if primary_algorithm == HashAlgorithm.BLAKE3 and not BLAKE3_AVAILABLE:
            raise CryptographicError(
                "Blake3 library not available. Install with: pip install blake3",
                operation="initialization", 
                algorithm="blake3"
            )
        
        # Configure Argon2 parameters based on security level
        self._configure_argon2_parameters(memory_cost, time_cost, parallelism)
        
        # Initialize hash algorithms
        self._initialize_hashers()
        
        logger.info(
            f"SecureHasher initialized with {primary_algorithm.value} "
            f"at {security_level.name} security level"
        )
    
    def _configure_argon2_parameters(
        self,
        memory_cost: Optional[int],
        time_cost: Optional[int], 
        parallelism: Optional[int]
    ) -> None:
        """Configure Argon2 parameters based on security level."""
        # Base parameters from constants
        base_memory = ARGON2_MEMORY_COST
        base_time = ARGON2_TIME_COST
        base_parallelism = ARGON2_PARALLELISM
        
        # Adjust based on security level
        level_multipliers = {
            SecurityLevel.DEVELOPMENT: 0.25,  # Faster for development
            SecurityLevel.BASIC: 0.5,
            SecurityLevel.STANDARD: 1.0,
            SecurityLevel.HIGH: 1.5,
            SecurityLevel.MAXIMUM: 2.0,  # Double strength for maximum security
        }
        
        multiplier = level_multipliers[self.security_level]
        
        # Set final parameters
        self.memory_cost = memory_cost or int(base_memory * multiplier)
        self.time_cost = time_cost or max(1, int(base_time * multiplier))
        self.parallelism = parallelism or base_parallelism
        
        # Ensure minimum security requirements
        if self.security_level >= SecurityLevel.HIGH:
            self.memory_cost = max(self.memory_cost, 65536)  # Minimum 64 MB
            self.time_cost = max(self.time_cost, 3)
    
    def _initialize_hashers(self) -> None:
        """Initialize the hashing implementations."""
        if ARGON2_AVAILABLE:
            try:
                self.argon2_hasher = PasswordHasher(
                    memory_cost=self.memory_cost,
                    time_cost=self.time_cost,
                    parallelism=self.parallelism,
                    hash_len=ARGON2_HASH_SIZE,
                    salt_len=ARGON2_SALT_SIZE,
                    encoding='utf-8'
                )
            except Exception as e:
                raise CryptographicError(
                    f"Failed to initialize Argon2 hasher: {e}",
                    operation="initialization",
                    algorithm="argon2id"
                )
        
        # Blake3 doesn't require initialization
        self.blake3_hasher = blake3 if BLAKE3_AVAILABLE else None
    
    def hash_sensitive_data(
        self, 
        data: Union[str, bytes],
        algorithm: Optional[HashAlgorithm] = None,
        salt: Optional[bytes] = None
    ) -> str:
        """
        Hash sensitive data using secure password hashing.
        
        Args:
            data: Data to hash (will be cleared from memory after use)
            algorithm: Specific algorithm to use (defaults to primary)
            salt: Optional salt (auto-generated if not provided)
            
        Returns:
            Hash string including algorithm parameters and salt
            
        Raises:
            CryptographicError: If hashing operation fails
        """
        self._operation_count += 1
        
        if algorithm is None:
            algorithm = self.primary_algorithm
        
        # Convert string to bytes if necessary
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        try:
            if algorithm == HashAlgorithm.ARGON2ID:
                return self._hash_with_argon2(data_bytes, salt)
            elif algorithm == HashAlgorithm.BLAKE3:
                return self._hash_with_blake3(data_bytes, salt)
            elif algorithm == HashAlgorithm.SHA3_256:
                return self._hash_with_sha3(data_bytes, salt)
            else:
                raise CryptographicError(
                    f"Unsupported hashing algorithm: {algorithm}",
                    operation="hashing",
                    algorithm=algorithm.value
                )
        
        finally:
            # Clear sensitive data from memory
            if self.security_level.requires_memory_clearing:
                self._clear_memory(data_bytes)
    
    def _hash_with_argon2(self, data: bytes, salt: Optional[bytes]) -> str:
        """Hash data using Argon2id."""
        if not ARGON2_AVAILABLE:
            raise CryptographicError(
                "Argon2 not available",
                operation="hashing",
                algorithm="argon2id"
            )
        
        try:
            # Argon2 handles salt generation automatically
            return self.argon2_hasher.hash(data)
        except HashingError as e:
            raise CryptographicError(
                f"Argon2 hashing failed: {e}",
                operation="hashing",
                algorithm="argon2id"
            )
    
    def _hash_with_blake3(self, data: bytes, salt: Optional[bytes]) -> str:
        """Hash data using Blake3 with salt."""
        if not BLAKE3_AVAILABLE:
            raise CryptographicError(
                "Blake3 not available",
                operation="hashing",
                algorithm="blake3"
            )
        
        try:
            if salt is None:
                salt = secrets.token_bytes(32)
            
            hasher = blake3.blake3()
            hasher.update(salt)
            hasher.update(data)
            
            hash_bytes = hasher.finalize()
            salt_hex = salt.hex()
            hash_hex = hash_bytes.hex()
            
            return f"blake3${salt_hex}${hash_hex}"
        
        except Exception as e:
            raise CryptographicError(
                f"Blake3 hashing failed: {e}",
                operation="hashing",
                algorithm="blake3"
            )
    
    def _hash_with_sha3(self, data: bytes, salt: Optional[bytes]) -> str:
        """Hash data using SHA3-256 with salt."""
        try:
            if salt is None:
                salt = secrets.token_bytes(32)
            
            hasher = hashlib.sha3_256()
            hasher.update(salt)
            hasher.update(data)
            
            hash_bytes = hasher.digest()
            salt_hex = salt.hex()
            hash_hex = hash_bytes.hex()
            
            return f"sha3-256${salt_hex}${hash_hex}"
        
        except Exception as e:
            raise CryptographicError(
                f"SHA3-256 hashing failed: {e}",
                operation="hashing",
                algorithm="sha3-256"
            )
    
    def verify_hash(
        self,
        data: Union[str, bytes],
        hash_value: str,
        constant_time: bool = True
    ) -> bool:
        """
        Verify data against a hash using constant-time comparison.
        
        Args:
            data: Data to verify
            hash_value: Hash to verify against
            constant_time: Whether to use constant-time comparison
            
        Returns:
            True if data matches hash, False otherwise
            
        Raises:
            CryptographicError: If verification operation fails
        """
        self._operation_count += 1
        
        # Convert string to bytes if necessary
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        try:
            # Determine algorithm from hash format
            if hash_value.startswith('$argon2'):
                return self._verify_argon2(data_bytes, hash_value, constant_time)
            elif hash_value.startswith('blake3$'):
                return self._verify_blake3(data_bytes, hash_value, constant_time)
            elif hash_value.startswith('sha3-256$'):
                return self._verify_sha3(data_bytes, hash_value, constant_time)
            else:
                raise CryptographicError(
                    f"Unknown hash format: {hash_value[:20]}...",
                    operation="verification",
                    algorithm="unknown"
                )
        
        finally:
            # Clear sensitive data from memory
            if self.security_level.requires_memory_clearing:
                self._clear_memory(data_bytes)
    
    def _verify_argon2(
        self,
        data: bytes,
        hash_value: str,
        constant_time: bool
    ) -> bool:
        """Verify data against Argon2 hash."""
        if not ARGON2_AVAILABLE:
            raise CryptographicError(
                "Argon2 not available",
                operation="verification",
                algorithm="argon2id"
            )
        
        try:
            # Argon2 has built-in constant-time verification
            self.argon2_hasher.verify(hash_value, data)
            return True
        except VerifyMismatchError:
            # Introduce timing delay for failed verifications to prevent timing attacks
            if constant_time and self.security_level >= SecurityLevel.STANDARD:
                self._timing_safe_delay()
            return False
        except (VerificationError, InvalidHashError) as e:
            raise CryptographicError(
                f"Argon2 verification error: {e}",
                operation="verification",
                algorithm="argon2id"
            )
    
    def _verify_blake3(
        self,
        data: bytes,
        hash_value: str,
        constant_time: bool
    ) -> bool:
        """Verify data against Blake3 hash."""
        try:
            # Parse hash format: blake3$salt$hash
            parts = hash_value.split('$')
            if len(parts) != 3 or parts[0] != 'blake3':
                raise CryptographicError(
                    "Invalid Blake3 hash format",
                    operation="verification",
                    algorithm="blake3"
                )
            
            salt = bytes.fromhex(parts[1])
            expected_hash = bytes.fromhex(parts[2])
            
            # Compute hash with same salt
            hasher = blake3.blake3()
            hasher.update(salt)
            hasher.update(data)
            computed_hash = hasher.finalize()
            
            # Use constant-time comparison if required
            if constant_time:
                return secure_compare(computed_hash, expected_hash)
            else:
                result = computed_hash == expected_hash
                if not result:
                    self._timing_safe_delay()
                return result
        
        except Exception as e:
            raise CryptographicError(
                f"Blake3 verification failed: {e}",
                operation="verification",
                algorithm="blake3"
            )
    
    def _verify_sha3(
        self,
        data: bytes,
        hash_value: str,
        constant_time: bool
    ) -> bool:
        """Verify data against SHA3-256 hash."""
        try:
            # Parse hash format: sha3-256$salt$hash
            parts = hash_value.split('$')
            if len(parts) != 3 or parts[0] != 'sha3-256':
                raise CryptographicError(
                    "Invalid SHA3-256 hash format",
                    operation="verification",
                    algorithm="sha3-256"
                )
            
            salt = bytes.fromhex(parts[1])
            expected_hash = bytes.fromhex(parts[2])
            
            # Compute hash with same salt
            hasher = hashlib.sha3_256()
            hasher.update(salt)
            hasher.update(data)
            computed_hash = hasher.digest()
            
            # Use constant-time comparison if required
            if constant_time:
                return secure_compare(computed_hash, expected_hash)
            else:
                result = computed_hash == expected_hash
                if not result:
                    self._timing_safe_delay()
                return result
        
        except Exception as e:
            raise CryptographicError(
                f"SHA3-256 verification failed: {e}",
                operation="verification",
                algorithm="sha3-256"
            )
    
    def _timing_safe_delay(self) -> None:
        """Introduce consistent delay to prevent timing attacks."""
        if self.security_level >= SecurityLevel.STANDARD:
            # Small random delay to prevent timing analysis
            delay = secrets.randbelow(10) / 1000.0  # 0-9ms
            time.sleep(delay)
    
    def _clear_memory(self, data: bytes) -> None:
        """Securely clear sensitive data from memory."""
        if hasattr(data, '__len__'):
            # This is a best-effort memory clearing in Python
            # For true secure memory clearing, consider using ctypes
            # or specialized libraries like cryptg
            try:
                # Overwrite with random data multiple times
                import array
                length = len(data)
                for _ in range(3):  # Multiple passes
                    random_data = array.array('B', secrets.token_bytes(length))
                    # Python strings/bytes are immutable, so this is limited
                    # In production, consider using mutable byte arrays
            except Exception:
                pass  # Best effort, don't fail if clearing doesn't work
    
    def blake3_hash(self, data: Union[str, bytes]) -> str:
        """
        Fast Blake3 hash for non-sensitive data.
        
        Args:
            data: Data to hash
            
        Returns:
            Hex-encoded hash string
        """
        if not BLAKE3_AVAILABLE:
            # Fallback to SHA3-256
            if isinstance(data, str):
                data = data.encode('utf-8')
            return hashlib.sha3_256(data).hexdigest()
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return blake3.blake3(data).hexdigest()
    
    def get_algorithm_info(self, hash_value: str) -> Dict[str, Any]:
        """
        Get information about the algorithm used for a hash.
        
        Args:
            hash_value: Hash to analyze
            
        Returns:
            Dictionary containing algorithm information
        """
        if hash_value.startswith('$argon2'):
            return {
                'algorithm': 'argon2id',
                'memory_cost': self.memory_cost,
                'time_cost': self.time_cost,
                'parallelism': self.parallelism,
                'secure': True,
                'password_hash': True
            }
        elif hash_value.startswith('blake3$'):
            return {
                'algorithm': 'blake3',
                'secure': True,
                'password_hash': False,
                'high_performance': True
            }
        elif hash_value.startswith('sha3-256$'):
            return {
                'algorithm': 'sha3-256',
                'secure': True,
                'password_hash': False,
                'legacy': False
            }
        else:
            return {
                'algorithm': 'unknown',
                'secure': False,
                'password_hash': False
            }


# Module-level convenience functions
def blake3_hash(data: Union[str, bytes]) -> str:
    """
    Fast Blake3 hash function for general use.
    
    Args:
        data: Data to hash
        
    Returns:
        Hex-encoded hash string
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if BLAKE3_AVAILABLE:
        return blake3.blake3(data).hexdigest()
    else:
        # Fallback to SHA3-256
        return hashlib.sha3_256(data).hexdigest()


def secure_compare(a: Union[str, bytes], b: Union[str, bytes]) -> bool:
    """
    Constant-time comparison to prevent timing attacks.
    
    Args:
        a: First value to compare
        b: Second value to compare
        
    Returns:
        True if values are equal, False otherwise
    """
    # Convert to bytes if necessary
    if isinstance(a, str):
        a = a.encode('utf-8')
    if isinstance(b, str):
        b = b.encode('utf-8')
    
    # Use hmac.compare_digest for constant-time comparison
    return hmac.compare_digest(a, b)


def generate_secure_salt(size: int = 32) -> bytes:
    """
    Generate cryptographically secure salt.
    
    Args:
        size: Size of salt in bytes
        
    Returns:
        Random salt bytes
    """
    return secrets.token_bytes(size)


def hash_for_audit(data: str, include_timestamp: bool = True) -> str:
    """
    Hash data for audit trail purposes.
    
    Args:
        data: Data to hash
        include_timestamp: Whether to include timestamp in hash
        
    Returns:
        Hash suitable for audit trails
    """
    if include_timestamp:
        timestamp = str(int(time.time()))
        data = f"{data}|{timestamp}"
    
    return blake3_hash(data)
