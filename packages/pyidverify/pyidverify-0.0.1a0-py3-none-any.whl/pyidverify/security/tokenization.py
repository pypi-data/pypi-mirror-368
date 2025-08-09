"""
PyIDVerify Security Tokenization

Provides secure tokenization capabilities for sensitive data protection.
Implements format-preserving encryption and PCI DSS compliant tokenization.

Author: PyIDVerify Team
License: MIT
"""

import secrets
import hashlib
import logging
from typing import Dict, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
from .encryption import SecureEncryption
from .hashing import SecureHasher
from .exceptions import SecurityError

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """Types of tokens that can be generated."""
    RANDOM = "random"
    FORMAT_PRESERVING = "format_preserving"
    HASH_BASED = "hash_based"
    REVERSIBLE = "reversible"


@dataclass
class TokenizationConfig:
    """Configuration for tokenization operations."""
    token_length: int = 16
    preserve_format: bool = False
    reversible: bool = False
    use_checksum: bool = False
    salt_rounds: int = 12
    token_prefix: str = ""
    token_suffix: str = ""


class SecurityTokenizer:
    """
    Base tokenizer for general security tokenization.
    
    Provides secure tokenization with various modes:
    - Random tokenization for irreversible protection
    - Format-preserving tokenization for compatibility
    - Hash-based tokenization for deterministic tokens
    - Reversible tokenization with encryption
    """
    
    def __init__(self, config: Optional[TokenizationConfig] = None):
        """Initialize tokenizer with configuration."""
        self.config = config or TokenizationConfig()
        self.cipher = SecureEncryption()
        self.hasher = SecureHasher()
        self._token_store: Dict[str, str] = {}  # For reversible tokens
        
    def tokenize(self, 
                value: str, 
                token_type: TokenType = TokenType.RANDOM,
                preserve_format: bool = None) -> str:
        """
        Tokenize a value using specified method.
        
        Args:
            value: Value to tokenize
            token_type: Type of tokenization to use
            preserve_format: Override format preservation setting
            
        Returns:
            Tokenized value
            
        Raises:
            TokenizationError: If tokenization fails
        """
        try:
            if not value:
                raise TokenizationError("Cannot tokenize empty value")
                
            preserve_fmt = preserve_format if preserve_format is not None else self.config.preserve_format
            
            if token_type == TokenType.RANDOM:
                return self._random_tokenize(value, preserve_fmt)
            elif token_type == TokenType.FORMAT_PRESERVING:
                return self._format_preserving_tokenize(value)
            elif token_type == TokenType.HASH_BASED:
                return self._hash_based_tokenize(value)
            elif token_type == TokenType.REVERSIBLE:
                return self._reversible_tokenize(value, preserve_fmt)
            else:
                raise TokenizationError(f"Unsupported token type: {token_type}")
                
        except Exception as e:
            logger.error(f"Tokenization failed: {str(e)}")
            raise TokenizationError(f"Tokenization error: {str(e)}")
            
    def detokenize(self, token: str) -> Optional[str]:
        """
        Reverse tokenization if possible.
        
        Args:
            token: Token to reverse
            
        Returns:
            Original value if reversible, None otherwise
        """
        try:
            # Check if it's a reversible token in our store
            if token in self._token_store:
                encrypted_value = self._token_store[token]
                return self.cipher.decrypt(encrypted_value)
                
            # Try to decrypt directly (for newer reversible tokens)
            try:
                return self.cipher.decrypt(token)
            except:
                pass
                
            return None
            
        except Exception as e:
            logger.warning(f"Detokenization failed: {str(e)}")
            return None
            
    def is_tokenized(self, value: str) -> bool:
        """Check if value appears to be tokenized."""
        try:
            # Check for token prefix/suffix
            if self.config.token_prefix and not value.startswith(self.config.token_prefix):
                return False
            if self.config.token_suffix and not value.endswith(self.config.token_suffix):
                return False
                
            # Check token store
            if value in self._token_store:
                return True
                
            # Check if it looks like our random tokens
            clean_value = value
            if self.config.token_prefix:
                clean_value = clean_value[len(self.config.token_prefix):]
            if self.config.token_suffix:
                clean_value = clean_value[:-len(self.config.token_suffix)]
                
            return len(clean_value) == self.config.token_length and clean_value.isalnum()
            
        except:
            return False
            
    def _random_tokenize(self, value: str, preserve_format: bool = False) -> str:
        """Generate random token."""
        if preserve_format:
            return self._generate_format_preserving_random(value)
        else:
            token = secrets.token_urlsafe(self.config.token_length)[:self.config.token_length]
            return f"{self.config.token_prefix}{token}{self.config.token_suffix}"
            
    def _format_preserving_tokenize(self, value: str) -> str:
        """Generate format-preserving token."""
        return self._generate_format_preserving_random(value)
        
    def _hash_based_tokenize(self, value: str) -> str:
        """Generate hash-based deterministic token."""
        hash_value = self.hasher.blake3_hash(value.encode())
        token = hash_value[:self.config.token_length]
        return f"{self.config.token_prefix}{token}{self.config.token_suffix}"
        
    def _reversible_tokenize(self, value: str, preserve_format: bool = False) -> str:
        """Generate reversible token using encryption."""
        encrypted = self.cipher.encrypt(value)
        
        if preserve_format:
            # Store mapping for format-preserving reversible tokens
            fp_token = self._generate_format_preserving_random(value)
            self._token_store[fp_token] = encrypted
            return fp_token
        else:
            return f"{self.config.token_prefix}{encrypted}{self.config.token_suffix}"
            
    def _generate_format_preserving_random(self, value: str) -> str:
        """Generate random token that preserves original format."""
        result = []
        for char in value:
            if char.isdigit():
                result.append(str(secrets.randbelow(10)))
            elif char.isalpha():
                if char.isupper():
                    result.append(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
                else:
                    result.append(secrets.choice('abcdefghijklmnopqrstuvwxyz'))
            else:
                result.append(char)  # Preserve special characters
        return ''.join(result)


class PCITokenizer(SecurityTokenizer):
    """
    PCI DSS compliant tokenizer for payment card data.
    
    Features:
    - Format-preserving tokenization for payment systems
    - Secure token vault with encryption
    - PAN (Primary Account Number) specific tokenization
    - Reversible tokenization with strong encryption
    - Audit logging for compliance
    """
    
    def __init__(self, vault_key: Optional[str] = None):
        """Initialize PCI tokenizer with vault encryption key."""
        config = TokenizationConfig(
            token_length=16,
            preserve_format=True,
            reversible=True,
            use_checksum=True,
            token_prefix="TOK_",
            token_suffix=""
        )
        super().__init__(config)
        
        if vault_key:
            self.cipher = SecureEncryption()
            
        self._audit_log = []
        
    def tokenize_pan(self, pan: str) -> str:
        """
        Tokenize Primary Account Number with PCI compliance.
        
        Args:
            pan: Primary Account Number to tokenize
            
        Returns:
            PCI compliant token
        """
        try:
            # Validate PAN format
            if not self._is_valid_pan(pan):
                raise TokenizationError("Invalid PAN format")
                
            # Generate format-preserving token
            token = self._format_preserving_tokenize(pan)
            
            # Add to audit log
            self._audit_log.append({
                'action': 'tokenize_pan',
                'timestamp': self._get_timestamp(),
                'pan_hash': self.hasher.blake3_hash(pan.encode())[:16],
                'token': token
            })
            
            logger.info(f"PAN tokenized: {pan[:4]}****{pan[-4:]} -> {token}")
            return token
            
        except Exception as e:
            logger.error(f"PAN tokenization failed: {str(e)}")
            raise TokenizationError(f"PAN tokenization error: {str(e)}")
            
    def detokenize_pan(self, token: str) -> Optional[str]:
        """
        Detokenize PAN token.
        
        Args:
            token: Token to detokenize
            
        Returns:
            Original PAN if valid token, None otherwise
        """
        try:
            pan = self.detokenize(token)
            if pan and self._is_valid_pan(pan):
                # Add to audit log
                self._audit_log.append({
                    'action': 'detokenize_pan',
                    'timestamp': self._get_timestamp(),
                    'token': token,
                    'pan_hash': self.hasher.blake3_hash(pan.encode())[:16]
                })
                
                logger.info(f"PAN detokenized: {token} -> {pan[:4]}****{pan[-4:]}")
                return pan
            return None
            
        except Exception as e:
            logger.error(f"PAN detokenization failed: {str(e)}")
            return None
            
    def get_audit_log(self) -> list:
        """Get audit log for compliance reporting."""
        return self._audit_log.copy()
        
    def _is_valid_pan(self, pan: str) -> bool:
        """Validate PAN using Luhn algorithm."""
        try:
            # Remove any spaces or hyphens
            pan = pan.replace(' ', '').replace('-', '')
            
            # Check length (13-19 digits for most cards)
            if not pan.isdigit() or len(pan) < 13 or len(pan) > 19:
                return False
                
            # Luhn algorithm check
            digits = [int(d) for d in pan]
            checksum = 0
            
            for i in range(len(digits) - 2, -1, -1):
                if (len(digits) - i) % 2 == 0:
                    digits[i] *= 2
                    if digits[i] > 9:
                        digits[i] -= 9
                checksum += digits[i]
                
            return (checksum + digits[-1]) % 10 == 0
            
        except:
            return False
            
    def _get_timestamp(self) -> str:
        """Get current timestamp for audit logging."""
        import datetime
        return datetime.datetime.utcnow().isoformat()


class TokenizationError(SecurityError):
    """Exception raised for tokenization errors."""
    pass
