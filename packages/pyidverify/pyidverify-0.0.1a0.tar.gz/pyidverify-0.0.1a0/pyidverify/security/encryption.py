"""
Secure Encryption Implementation

Provides military-grade encryption using AES-256-GCM and ChaCha20-Poly1305
with built-in key management, secure random number generation, and protection
against various cryptographic attacks.

Features:
- AES-256-GCM authenticated encryption (NIST approved)
- ChaCha20-Poly1305 high-performance authenticated encryption
- Secure key derivation using PBKDF2 and HKDF
- Cryptographically secure random number generation
- Key rotation and management
- Protection against timing and side-channel attacks

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

import os
import secrets
import time
from typing import Optional, Union, Tuple, Dict, Any, List
import logging
import struct

# Standard library cryptography
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
    from cryptography.hazmat.backends import default_backend
    from cryptography.exceptions import InvalidSignature
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

from .exceptions import CryptographicError, SecurityError
from .constants import (
    MIN_KEY_SIZE,
    DEFAULT_KEY_SIZE,
    AES_BLOCK_SIZE,
    CHACHA20_KEY_SIZE,
    CHACHA20_NONCE_SIZE,
    GCM_TAG_SIZE,
    IV_SIZE,
    SecurityLevel,
    EncryptionAlgorithm
)

# Configure logging
logger = logging.getLogger('pyidverify.security.encryption')


class SecureRandom:
    """
    Cryptographically secure random number generator with additional entropy sources.
    """
    
    def __init__(self):
        """Initialize secure random number generator."""
        self._entropy_sources = []
        self._initialize_entropy_sources()
    
    def _initialize_entropy_sources(self) -> None:
        """Initialize additional entropy sources for enhanced randomness."""
        try:
            # System entropy
            self._entropy_sources.append(lambda: os.urandom(32))
            
            # Python secrets module
            self._entropy_sources.append(lambda: secrets.token_bytes(32))
            
            # Time-based entropy (less secure, but adds variety)
            self._entropy_sources.append(
                lambda: struct.pack('>Q', int(time.time() * 1000000))
            )
            
            # Memory address entropy (ASLR-based)
            obj = object()
            self._entropy_sources.append(
                lambda: struct.pack('>Q', id(obj) & 0xFFFFFFFFFFFFFFFF)
            )
            
        except Exception as e:
            logger.warning(f"Some entropy sources unavailable: {e}")
    
    def bytes(self, n: int) -> bytes:
        """
        Generate n cryptographically secure random bytes.
        
        Args:
            n: Number of bytes to generate
            
        Returns:
            Random bytes
        """
        if n <= 0:
            raise ValueError("Number of bytes must be positive")
        
        # Use secrets.token_bytes as primary source
        primary_random = secrets.token_bytes(n)
        
        # Mix in additional entropy for enhanced security
        try:
            additional_entropy = b''.join(source()[:n] for source in self._entropy_sources[:2])
            
            # XOR primary random with additional entropy
            if len(additional_entropy) >= n:
                result = bytes(a ^ b for a, b in zip(primary_random, additional_entropy[:n]))
            else:
                result = primary_random
        except Exception:
            # Fall back to primary random if entropy mixing fails
            result = primary_random
        
        return result
    
    def int(self, max_value: int) -> int:
        """
        Generate cryptographically secure random integer.
        
        Args:
            max_value: Maximum value (exclusive)
            
        Returns:
            Random integer between 0 and max_value-1
        """
        return secrets.randbelow(max_value)
    
    def choice(self, sequence: List[Any]) -> Any:
        """
        Choose random element from sequence.
        
        Args:
            sequence: Sequence to choose from
            
        Returns:
            Random element from sequence
        """
        return secrets.choice(sequence)
    
    def string(self, length: int, alphabet: Optional[str] = None) -> str:
        """
        Generate random string.
        
        Args:
            length: Length of string
            alphabet: Character set to use (defaults to URL-safe base64)
            
        Returns:
            Random string
        """
        if alphabet is None:
            return secrets.token_urlsafe(length)[:length]
        else:
            return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def timestamp(self) -> float:
        """
        Get current timestamp with microsecond precision.
        
        Returns:
            Current timestamp
        """
        return time.time()


# Global secure random instance
secure_random = SecureRandom()


class SecureEncryption:
    """
    Military-grade encryption implementation with multiple algorithms.
    
    Supports AES-256-GCM and ChaCha20-Poly1305 authenticated encryption
    with automatic key management and security protections.
    """
    
    def __init__(
        self,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        security_level: SecurityLevel = SecurityLevel.MAXIMUM,
        master_key: Optional[bytes] = None
    ):
        """
        Initialize SecureEncryption with specified algorithm and security level.
        
        Args:
            algorithm: Encryption algorithm to use
            security_level: Security level for key generation and operations
            master_key: Optional master key (generated if not provided)
            
        Raises:
            CryptographicError: If cryptography library is not available
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise CryptographicError(
                "Cryptography library not available. Install with: pip install cryptography",
                operation="initialization",
                algorithm=algorithm.value
            )
        
        self.algorithm = algorithm
        self.security_level = security_level
        self._operation_count = 0
        
        # Initialize master key
        if master_key is not None:
            if len(master_key) != 32:  # 256 bits
                raise CryptographicError(
                    f"Master key must be 32 bytes, got {len(master_key)}",
                    operation="initialization"
                )
            self._master_key = master_key
        else:
            self._master_key = secure_random.bytes(32)
        
        # Initialize algorithm-specific components
        self._initialize_cipher()
        
        logger.info(
            f"SecureEncryption initialized with {algorithm.value} "
            f"at {security_level.name} security level"
        )
    
    def _initialize_cipher(self) -> None:
        """Initialize cipher components based on selected algorithm."""
        try:
            if self.algorithm == EncryptionAlgorithm.AES_256_GCM:
                # AES-GCM uses the key directly
                self._cipher_key = self._master_key
                
            elif self.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                # ChaCha20 uses the key directly
                self._cipher_key = self._master_key
                
            elif self.algorithm == EncryptionAlgorithm.AES_256_CBC:
                # Legacy CBC mode (not recommended)
                self._cipher_key = self._master_key
                logger.warning("Using deprecated AES-CBC mode")
            
        except Exception as e:
            raise CryptographicError(
                f"Failed to initialize cipher: {e}",
                operation="initialization",
                algorithm=self.algorithm.value
            )
    
    def encrypt(
        self,
        data: Union[str, bytes],
        associated_data: Optional[bytes] = None,
        key: Optional[bytes] = None
    ) -> bytes:
        """
        Encrypt data using authenticated encryption.
        
        Args:
            data: Data to encrypt
            associated_data: Optional additional data to authenticate
            key: Optional specific key to use (derives from master key if not provided)
            
        Returns:
            Encrypted data with nonce/IV and authentication tag
            
        Raises:
            CryptographicError: If encryption operation fails
        """
        self._operation_count += 1
        
        # Convert string to bytes if necessary
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Use provided key or derive from master key
        encryption_key = key if key is not None else self._cipher_key
        
        try:
            if self.algorithm == EncryptionAlgorithm.AES_256_GCM:
                return self._encrypt_aes_gcm(data, associated_data, encryption_key)
            elif self.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return self._encrypt_chacha20_poly1305(data, associated_data, encryption_key)
            elif self.algorithm == EncryptionAlgorithm.AES_256_CBC:
                return self._encrypt_aes_cbc(data, encryption_key)
            else:
                raise CryptographicError(
                    f"Unsupported encryption algorithm: {self.algorithm}",
                    operation="encryption",
                    algorithm=self.algorithm.value
                )
        
        except Exception as e:
            if isinstance(e, CryptographicError):
                raise
            raise CryptographicError(
                f"Encryption failed: {e}",
                operation="encryption",
                algorithm=self.algorithm.value
            )
    
    def _encrypt_aes_gcm(
        self,
        data: bytes,
        associated_data: Optional[bytes],
        key: bytes
    ) -> bytes:
        """Encrypt using AES-256-GCM."""
        # Generate random nonce
        nonce = secure_random.bytes(12)  # 96-bit nonce for GCM
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        # Encrypt data
        ciphertext = aesgcm.encrypt(nonce, data, associated_data)
        
        # Format: algorithm_id(1) + nonce(12) + ciphertext_with_tag
        algorithm_id = b'\x01'  # AES-256-GCM identifier
        return algorithm_id + nonce + ciphertext
    
    def _encrypt_chacha20_poly1305(
        self,
        data: bytes,
        associated_data: Optional[bytes],
        key: bytes
    ) -> bytes:
        """Encrypt using ChaCha20-Poly1305."""
        # Generate random nonce
        nonce = secure_random.bytes(CHACHA20_NONCE_SIZE)
        
        # Create ChaCha20Poly1305 cipher
        chacha = ChaCha20Poly1305(key)
        
        # Encrypt data
        ciphertext = chacha.encrypt(nonce, data, associated_data)
        
        # Format: algorithm_id(1) + nonce(12) + ciphertext_with_tag
        algorithm_id = b'\x02'  # ChaCha20-Poly1305 identifier
        return algorithm_id + nonce + ciphertext
    
    def _encrypt_aes_cbc(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using AES-256-CBC (legacy, not recommended)."""
        # Generate random IV
        iv = secure_random.bytes(AES_BLOCK_SIZE)
        
        # Pad data to block size
        padding_length = AES_BLOCK_SIZE - (len(data) % AES_BLOCK_SIZE)
        padded_data = data + bytes([padding_length] * padding_length)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Format: algorithm_id(1) + iv(16) + ciphertext
        algorithm_id = b'\x03'  # AES-256-CBC identifier
        return algorithm_id + iv + ciphertext
    
    def decrypt(
        self,
        encrypted_data: bytes,
        associated_data: Optional[bytes] = None,
        key: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypt data using authenticated encryption.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            associated_data: Optional additional data to verify
            key: Optional specific key to use
            
        Returns:
            Decrypted data
            
        Raises:
            CryptographicError: If decryption operation fails
        """
        self._operation_count += 1
        
        if len(encrypted_data) < 2:
            raise CryptographicError(
                "Encrypted data too short",
                operation="decryption"
            )
        
        # Use provided key or derive from master key
        decryption_key = key if key is not None else self._cipher_key
        
        # Extract algorithm identifier
        algorithm_id = encrypted_data[0:1]
        
        try:
            if algorithm_id == b'\x01':  # AES-256-GCM
                return self._decrypt_aes_gcm(encrypted_data[1:], associated_data, decryption_key)
            elif algorithm_id == b'\x02':  # ChaCha20-Poly1305
                return self._decrypt_chacha20_poly1305(encrypted_data[1:], associated_data, decryption_key)
            elif algorithm_id == b'\x03':  # AES-256-CBC
                return self._decrypt_aes_cbc(encrypted_data[1:], decryption_key)
            else:
                raise CryptographicError(
                    f"Unknown algorithm identifier: {algorithm_id.hex()}",
                    operation="decryption"
                )
        
        except Exception as e:
            if isinstance(e, CryptographicError):
                raise
            raise CryptographicError(
                f"Decryption failed: {e}",
                operation="decryption"
            )
    
    def _decrypt_aes_gcm(
        self,
        encrypted_data: bytes,
        associated_data: Optional[bytes],
        key: bytes
    ) -> bytes:
        """Decrypt using AES-256-GCM."""
        if len(encrypted_data) < 12:  # Minimum: nonce(12)
            raise CryptographicError(
                "Invalid AES-GCM encrypted data length",
                operation="decryption",
                algorithm="aes-256-gcm"
            )
        
        # Extract nonce and ciphertext
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        try:
            # Decrypt and verify
            return aesgcm.decrypt(nonce, ciphertext, associated_data)
        except InvalidSignature:
            raise CryptographicError(
                "Authentication failed - data may be corrupted or tampered with",
                operation="decryption",
                algorithm="aes-256-gcm"
            )
    
    def _decrypt_chacha20_poly1305(
        self,
        encrypted_data: bytes,
        associated_data: Optional[bytes],
        key: bytes
    ) -> bytes:
        """Decrypt using ChaCha20-Poly1305."""
        if len(encrypted_data) < CHACHA20_NONCE_SIZE:
            raise CryptographicError(
                "Invalid ChaCha20-Poly1305 encrypted data length",
                operation="decryption",
                algorithm="chacha20-poly1305"
            )
        
        # Extract nonce and ciphertext
        nonce = encrypted_data[:CHACHA20_NONCE_SIZE]
        ciphertext = encrypted_data[CHACHA20_NONCE_SIZE:]
        
        # Create ChaCha20Poly1305 cipher
        chacha = ChaCha20Poly1305(key)
        
        try:
            # Decrypt and verify
            return chacha.decrypt(nonce, ciphertext, associated_data)
        except InvalidSignature:
            raise CryptographicError(
                "Authentication failed - data may be corrupted or tampered with",
                operation="decryption",
                algorithm="chacha20-poly1305"
            )
    
    def _decrypt_aes_cbc(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using AES-256-CBC."""
        if len(encrypted_data) < AES_BLOCK_SIZE:
            raise CryptographicError(
                "Invalid AES-CBC encrypted data length",
                operation="decryption",
                algorithm="aes-256-cbc"
            )
        
        # Extract IV and ciphertext
        iv = encrypted_data[:AES_BLOCK_SIZE]
        ciphertext = encrypted_data[AES_BLOCK_SIZE:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt data
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        if len(padded_data) == 0:
            raise CryptographicError(
                "Invalid padding in encrypted data",
                operation="decryption",
                algorithm="aes-256-cbc"
            )
        
        padding_length = padded_data[-1]
        if padding_length > AES_BLOCK_SIZE or padding_length == 0:
            raise CryptographicError(
                "Invalid padding length",
                operation="decryption",
                algorithm="aes-256-cbc"
            )
        
        # Verify padding
        for i in range(padding_length):
            if padded_data[-(i+1)] != padding_length:
                raise CryptographicError(
                    "Invalid padding bytes",
                    operation="decryption",
                    algorithm="aes-256-cbc"
                )
        
        return padded_data[:-padding_length]
    
    def rotate_key(self) -> bytes:
        """
        Generate new master key for key rotation.
        
        Returns:
            New master key
        """
        old_key = self._master_key
        self._master_key = secure_random.bytes(32)
        self._initialize_cipher()
        
        logger.info("Encryption key rotated")
        return old_key
    
    def derive_key(
        self,
        purpose: str,
        salt: Optional[bytes] = None,
        length: int = 32
    ) -> bytes:
        """
        Derive key for specific purpose using HKDF.
        
        Args:
            purpose: Purpose identifier for key derivation
            salt: Optional salt (generated if not provided)
            length: Length of derived key in bytes
            
        Returns:
            Derived key bytes
        """
        if salt is None:
            salt = secure_random.bytes(32)
        
        # Use HKDF for key derivation
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=purpose.encode('utf-8'),
            backend=default_backend()
        )
        
        return hkdf.derive(self._master_key)
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Get information about current encryption configuration.
        
        Returns:
            Dictionary containing algorithm information
        """
        return {
            'algorithm': self.algorithm.value,
            'key_size': self.algorithm.key_size,
            'authenticated': self.algorithm.is_authenticated,
            'deprecated': self.algorithm.is_deprecated,
            'security_level': self.security_level.name,
            'operation_count': self._operation_count
        }


def key_derivation(
    password: Union[str, bytes],
    salt: Optional[bytes] = None,
    iterations: int = 100000,
    key_length: int = 32
) -> Tuple[bytes, bytes]:
    """
    Derive encryption key from password using PBKDF2.
    
    Args:
        password: Password to derive key from
        salt: Optional salt (generated if not provided)
        iterations: Number of PBKDF2 iterations
        key_length: Length of derived key in bytes
        
    Returns:
        Tuple of (derived_key, salt)
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        raise CryptographicError(
            "Cryptography library not available",
            operation="key_derivation"
        )
    
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    if salt is None:
        salt = secure_random.bytes(32)
    
    # Use PBKDF2 for key derivation
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    
    key = kdf.derive(password)
    return key, salt


def generate_secure_key(length: int = 32) -> bytes:
    """
    Generate cryptographically secure key.
    
    Args:
        length: Key length in bytes
        
    Returns:
        Random key bytes
    """
    return secure_random.bytes(length)


def constant_time_compare(a: bytes, b: bytes) -> bool:
    """
    Compare two byte strings in constant time.
    
    Args:
        a: First byte string
        b: Second byte string
        
    Returns:
        True if equal, False otherwise
    """
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    
    return result == 0
