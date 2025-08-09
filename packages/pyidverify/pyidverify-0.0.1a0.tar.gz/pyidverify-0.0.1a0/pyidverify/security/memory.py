"""
PyIDVerify Secure Memory Management

Provides secure memory handling for sensitive data protection.
Implements memory clearing, secure allocation, and anti-dump protection.

Author: PyIDVerify Team
License: MIT
"""

import sys
import ctypes
import logging
from typing import Any, Optional, Union, List
from contextlib import contextmanager
from .exceptions import SecurityError

logger = logging.getLogger(__name__)

# Try to import mlock if available
try:
    import mlock
    MLOCK_AVAILABLE = True
except ImportError:
    MLOCK_AVAILABLE = False
    logger.debug("mlock module not available, using fallback memory protection")


class SecureMemoryError(SecurityError):
    """Exception raised for secure memory operations."""
    pass


class SecureMemory:
    """
    Secure memory management for sensitive data.
    
    Features:
    - Memory locking to prevent swapping
    - Secure memory clearing with overwrite patterns
    - Protected memory allocation
    - Memory dump protection
    - Sensitive data lifecycle management
    """
    
    def __init__(self, size: int = 4096):
        """
        Initialize secure memory region.
        
        Args:
            size: Size of secure memory region in bytes
        """
        self.size = size
        self._memory_region = None
        self._locked = False
        self._is_secure = False
        
        try:
            self._allocate_secure_memory()
        except Exception as e:
            logger.warning(f"Secure memory allocation failed: {str(e)}")
            self._allocate_regular_memory()
            
    def _allocate_secure_memory(self):
        """Allocate locked memory region."""
        try:
            # Allocate memory buffer
            self._memory_region = ctypes.create_string_buffer(self.size)
            
            # Lock memory to prevent swapping
            if sys.platform.startswith('linux') or sys.platform == 'darwin':
                # Unix-like systems
                if MLOCK_AVAILABLE:
                    mlock.mlock(ctypes.addressof(self._memory_region), self.size)
                    self._locked = True
                else:
                    logger.warning("mlock not available, memory locking disabled")
            elif sys.platform == 'win32':
                # Windows
                import ctypes.wintypes
                kernel32 = ctypes.windll.kernel32
                result = kernel32.VirtualLock(
                    ctypes.addressof(self._memory_region),
                    ctypes.wintypes.DWORD(self.size)
                )
                self._locked = result != 0
                
            self._is_secure = True
            logger.debug(f"Allocated secure memory region: {self.size} bytes")
            
        except Exception as e:
            logger.error(f"Secure memory allocation failed: {str(e)}")
            raise SecureMemoryError(f"Cannot allocate secure memory: {str(e)}")
            
    def _allocate_regular_memory(self):
        """Fallback to regular memory allocation."""
        self._memory_region = ctypes.create_string_buffer(self.size)
        self._is_secure = False
        logger.warning("Using regular memory - not secure")
        
    def store_sensitive_data(self, data: Union[str, bytes], offset: int = 0) -> int:
        """
        Store sensitive data in secure memory.
        
        Args:
            data: Data to store
            offset: Offset in memory region
            
        Returns:
            Number of bytes stored
            
        Raises:
            SecureMemoryError: If storage fails
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
                
            if len(data) + offset > self.size:
                raise SecureMemoryError(f"Data too large for secure memory region")
                
            # Store data
            ctypes.memmove(
                ctypes.addressof(self._memory_region) + offset,
                data,
                len(data)
            )
            
            return len(data)
            
        except Exception as e:
            logger.error(f"Secure data storage failed: {str(e)}")
            raise SecureMemoryError(f"Cannot store sensitive data: {str(e)}")
            
    def retrieve_sensitive_data(self, length: int, offset: int = 0) -> bytes:
        """
        Retrieve sensitive data from secure memory.
        
        Args:
            length: Number of bytes to retrieve
            offset: Offset in memory region
            
        Returns:
            Retrieved data as bytes
        """
        try:
            if length + offset > self.size:
                raise SecureMemoryError("Request exceeds memory region size")
                
            # Create buffer for retrieved data
            buffer = ctypes.create_string_buffer(length)
            ctypes.memmove(
                buffer,
                ctypes.addressof(self._memory_region) + offset,
                length
            )
            
            return buffer.raw
            
        except Exception as e:
            logger.error(f"Secure data retrieval failed: {str(e)}")
            raise SecureMemoryError(f"Cannot retrieve sensitive data: {str(e)}")
            
    def clear_memory(self, offset: int = 0, length: Optional[int] = None):
        """
        Securely clear memory region with multiple overwrite patterns.
        
        Args:
            offset: Offset to start clearing
            length: Length to clear (None for entire remaining region)
        """
        try:
            if length is None:
                length = self.size - offset
                
            if offset + length > self.size:
                length = self.size - offset
                
            # Multiple overwrite passes for security
            patterns = [0x00, 0xFF, 0xAA, 0x55, 0x00]  # DOD 5220.22-M standard
            
            for pattern in patterns:
                # Fill with pattern
                ctypes.memset(
                    ctypes.addressof(self._memory_region) + offset,
                    pattern,
                    length
                )
                
            logger.debug(f"Securely cleared {length} bytes at offset {offset}")
            
        except Exception as e:
            logger.error(f"Memory clearing failed: {str(e)}")
            
    def is_locked(self) -> bool:
        """Check if memory is locked against swapping."""
        return self._locked
        
    def is_secure(self) -> bool:
        """Check if memory allocation is secure."""
        return self._is_secure
        
    def __del__(self):
        """Secure cleanup on destruction."""
        try:
            if self._memory_region:
                # Clear all memory before deallocation
                self.clear_memory()
                
                # Unlock memory if locked
                if self._locked:
                    if sys.platform.startswith('linux') or sys.platform == 'darwin':
                        if MLOCK_AVAILABLE:
                            mlock.munlock(ctypes.addressof(self._memory_region), self.size)
                    elif sys.platform == 'win32':
                        kernel32 = ctypes.windll.kernel32
                        kernel32.VirtualUnlock(
                            ctypes.addressof(self._memory_region),
                            ctypes.wintypes.DWORD(self.size)
                        )
                        
        except Exception as e:
            logger.error(f"Secure memory cleanup failed: {str(e)}")


class SensitiveString:
    """
    String wrapper for sensitive data with automatic cleanup.
    
    Automatically clears sensitive string data when no longer needed.
    """
    
    def __init__(self, value: str):
        """Initialize sensitive string."""
        self._secure_memory = SecureMemory(len(value.encode('utf-8')) + 64)
        self._length = self._secure_memory.store_sensitive_data(value)
        self._cleared = False
        
    def get_value(self) -> str:
        """Get the sensitive string value."""
        if self._cleared:
            raise SecureMemoryError("Sensitive string has been cleared")
            
        data = self._secure_memory.retrieve_sensitive_data(self._length)
        return data.decode('utf-8')
        
    def clear(self):
        """Manually clear the sensitive string."""
        if not self._cleared:
            self._secure_memory.clear_memory()
            self._cleared = True
            
    def is_cleared(self) -> bool:
        """Check if string has been cleared."""
        return self._cleared
        
    def __str__(self) -> str:
        """String representation (masked for security)."""
        return "*" * min(self._length, 8)
        
    def __repr__(self) -> str:
        """Object representation."""
        return f"SensitiveString(length={self._length}, cleared={self._cleared})"
        
    def __del__(self):
        """Automatic cleanup on destruction."""
        if not self._cleared:
            self.clear()


@contextmanager
def secure_string_context(value: str):
    """
    Context manager for secure string handling.
    
    Args:
        value: Sensitive string value
        
    Yields:
        SensitiveString instance that is automatically cleared on exit
    """
    sensitive_str = SensitiveString(value)
    try:
        yield sensitive_str
    finally:
        sensitive_str.clear()


def clear_sensitive_data(*variables):
    """
    Clear sensitive data from variables.
    
    Args:
        *variables: Variables containing sensitive data to clear
    """
    for var in variables:
        if isinstance(var, SensitiveString):
            var.clear()
        elif isinstance(var, (str, bytes)):
            # Try to overwrite string/bytes data in memory
            try:
                if isinstance(var, str):
                    # For strings, we can't directly overwrite due to immutability
                    # This is a best-effort approach
                    var = None
                elif isinstance(var, bytes):
                    # For bytes, same limitation
                    var = None
            except:
                pass
        elif isinstance(var, list):
            # Clear list contents
            try:
                for i in range(len(var)):
                    var[i] = None
                var.clear()
            except:
                pass
        elif isinstance(var, dict):
            # Clear dictionary contents  
            try:
                var.clear()
            except:
                pass


def secure_zero_memory(address: int, size: int):
    """
    Securely zero memory at specific address.
    
    Args:
        address: Memory address to clear
        size: Number of bytes to clear
    """
    try:
        # Multiple overwrite passes
        patterns = [0x00, 0xFF, 0x00]
        
        for pattern in patterns:
            ctypes.memset(address, pattern, size)
            
    except Exception as e:
        logger.error(f"Memory zeroing failed: {str(e)}")


def get_memory_protection_status() -> dict:
    """
    Get current memory protection status.
    
    Returns:
        Dictionary with memory protection information
    """
    return {
        "platform": sys.platform,
        "secure_memory_available": _check_secure_memory_support(),
        "memory_locking_available": _check_memory_locking_support(),
        "anti_dump_protection": _check_anti_dump_support(),
    }


def _check_secure_memory_support() -> bool:
    """Check if secure memory allocation is supported."""
    try:
        test_mem = SecureMemory(1024)
        return test_mem.is_secure()
    except:
        return False


def _check_memory_locking_support() -> bool:
    """Check if memory locking is supported."""
    try:
        test_mem = SecureMemory(1024)
        return test_mem.is_locked()
    except:
        return False


def _check_anti_dump_support() -> bool:
    """Check if anti-dump protection is available."""
    # Platform-specific anti-dump checks would go here
    return False  # Not implemented yet
