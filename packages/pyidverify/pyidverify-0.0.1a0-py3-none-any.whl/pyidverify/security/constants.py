"""
Security Constants and Enumerations

Defines security-related constants, enumerations, and configuration values
used throughout PyIDVerify for consistent security implementations.

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for sensitive data handling
"""

from enum import Enum, IntEnum, Flag, auto
from typing import Dict, Any, Final
import os

# Version constants
SECURITY_VERSION: Final[str] = "2024.1"
CRYPTO_VERSION: Final[str] = "FIPS-140-2-L1"
COMPLIANCE_VERSION: Final[str] = "GDPR-2024.1,HIPAA-2024.1,PCI-DSS-4.0,SOX-2024"

# Cryptographic constants
MIN_KEY_SIZE: Final[int] = 256  # Minimum key size in bits
MAX_KEY_SIZE: Final[int] = 4096  # Maximum key size in bits
DEFAULT_KEY_SIZE: Final[int] = 256  # Default AES key size
RSA_KEY_SIZE: Final[int] = 4096  # RSA key size for asymmetric operations

# Password hashing constants
ARGON2_TIME_COST: Final[int] = 3  # Argon2 time cost parameter
ARGON2_MEMORY_COST: Final[int] = 65536  # Argon2 memory cost (64 MB)
ARGON2_PARALLELISM: Final[int] = 4  # Argon2 parallelism parameter
ARGON2_SALT_SIZE: Final[int] = 32  # Salt size in bytes
ARGON2_HASH_SIZE: Final[int] = 64  # Hash output size in bytes

# Encryption constants
AES_BLOCK_SIZE: Final[int] = 16  # AES block size in bytes
CHACHA20_KEY_SIZE: Final[int] = 32  # ChaCha20 key size in bytes
CHACHA20_NONCE_SIZE: Final[int] = 12  # ChaCha20 nonce size in bytes
GCM_TAG_SIZE: Final[int] = 16  # GCM authentication tag size in bytes
IV_SIZE: Final[int] = 16  # Initialization vector size in bytes

# Timing attack protection
CONSTANT_TIME_COMPARE_LENGTH: Final[int] = 64  # Length for constant-time comparisons
TIMING_SAFE_ITERATIONS: Final[int] = 10000  # Iterations for timing-safe operations

# Audit and logging constants
AUDIT_LOG_MAX_SIZE: Final[int] = 100_000_000  # 100MB max audit log size
AUDIT_LOG_RETENTION_DAYS: Final[int] = 2555  # 7 years retention
MERKLE_TREE_LEAF_SIZE: Final[int] = 1024  # Merkle tree leaf size in bytes
LOG_ENTRY_MAX_SIZE: Final[int] = 64_000  # Maximum size of single log entry

# Rate limiting constants
DEFAULT_RATE_LIMIT: Final[int] = 1000  # Requests per minute
RATE_LIMIT_WINDOW: Final[int] = 60  # Rate limit window in seconds
MAX_BURST_SIZE: Final[int] = 100  # Maximum burst size
RATE_LIMIT_CLEANUP_INTERVAL: Final[int] = 300  # Cleanup interval in seconds

# Memory management constants
SECURE_MEMORY_PAGE_SIZE: Final[int] = 4096  # Memory page size
MEMORY_CLEAR_PASSES: Final[int] = 3  # Number of memory clearing passes
MEMORY_LOCK_SIZE: Final[int] = 1024 * 1024  # 1MB memory lock size

# Compliance-related constants
GDPR_DATA_RETENTION_DAYS: Final[int] = 2555  # 7 years default retention
HIPAA_AUDIT_RETENTION_DAYS: Final[int] = 2190  # 6 years minimum
PCI_DSS_LOG_RETENTION_DAYS: Final[int] = 365  # 1 year minimum
SOX_AUDIT_RETENTION_DAYS: Final[int] = 2555  # 7 years for financial records


class SecurityLevel(IntEnum):
    """
    Security level enumeration defining different security postures.
    Higher values indicate stronger security requirements.
    """
    DEVELOPMENT = 1  # Development/testing with reduced security
    BASIC = 2  # Basic security for non-critical applications
    STANDARD = 3  # Standard security for typical applications
    HIGH = 4  # High security for sensitive applications
    MAXIMUM = 5  # Maximum security for critical/regulated applications
    
    def __str__(self) -> str:
        return self.name.lower()
    
    @property
    def description(self) -> str:
        descriptions = {
            SecurityLevel.DEVELOPMENT: "Development/testing environment with minimal security",
            SecurityLevel.BASIC: "Basic security suitable for non-critical applications",
            SecurityLevel.STANDARD: "Standard security for typical business applications",
            SecurityLevel.HIGH: "High security for sensitive data applications",
            SecurityLevel.MAXIMUM: "Maximum security for critical/regulated environments"
        }
        return descriptions[self]
    
    @property
    def requires_audit(self) -> bool:
        """Returns True if this security level requires audit logging."""
        return self >= SecurityLevel.STANDARD
    
    @property
    def requires_encryption(self) -> bool:
        """Returns True if this security level requires encryption."""
        return self >= SecurityLevel.BASIC
    
    @property
    def requires_memory_clearing(self) -> bool:
        """Returns True if this security level requires secure memory clearing."""
        return self >= SecurityLevel.HIGH


class EncryptionAlgorithm(Enum):
    """
    Supported encryption algorithms with their specifications.
    """
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"  # Legacy support only
    CHACHA20_POLY1305 = "chacha20-poly1305"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def key_size(self) -> int:
        """Returns the key size in bits for this algorithm."""
        key_sizes = {
            EncryptionAlgorithm.AES_256_GCM: 256,
            EncryptionAlgorithm.AES_256_CBC: 256,
            EncryptionAlgorithm.CHACHA20_POLY1305: 256,
        }
        return key_sizes[self]
    
    @property
    def is_authenticated(self) -> bool:
        """Returns True if this algorithm provides authentication."""
        authenticated = {
            EncryptionAlgorithm.AES_256_GCM: True,
            EncryptionAlgorithm.AES_256_CBC: False,
            EncryptionAlgorithm.CHACHA20_POLY1305: True,
        }
        return authenticated[self]
    
    @property
    def is_deprecated(self) -> bool:
        """Returns True if this algorithm is deprecated."""
        return self == EncryptionAlgorithm.AES_256_CBC


class HashAlgorithm(Enum):
    """
    Supported hashing algorithms with their specifications.
    """
    ARGON2ID = "argon2id"  # Recommended for password hashing
    BLAKE3 = "blake3"      # High-performance general-purpose hashing
    SHA256 = "sha256"      # Legacy support only
    SHA3_256 = "sha3-256"  # Alternative to SHA-2
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def is_password_hash(self) -> bool:
        """Returns True if this algorithm is suitable for password hashing."""
        return self == HashAlgorithm.ARGON2ID
    
    @property
    def is_deprecated(self) -> bool:
        """Returns True if this algorithm is deprecated."""
        return self == HashAlgorithm.SHA256
    
    @property
    def output_size(self) -> int:
        """Returns the output size in bytes for this algorithm."""
        sizes = {
            HashAlgorithm.ARGON2ID: ARGON2_HASH_SIZE,
            HashAlgorithm.BLAKE3: 32,
            HashAlgorithm.SHA256: 32,
            HashAlgorithm.SHA3_256: 32,
        }
        return sizes[self]


class AuditEventType(Enum):
    """
    Types of events that can be logged in the audit system.
    """
    # Authentication events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    TOKEN_ISSUED = "auth.token.issued"
    TOKEN_REVOKED = "auth.token.revoked"
    
    # Validation events
    VALIDATION_SUCCESS = "validation.success"
    VALIDATION_FAILURE = "validation.failure"
    VALIDATION_ERROR = "validation.error"
    BATCH_VALIDATION = "validation.batch"
    
    # Security events
    SECURITY_VIOLATION = "security.violation"
    RATE_LIMIT_EXCEEDED = "security.rate_limit"
    ACCESS_DENIED = "security.access_denied"
    ENCRYPTION_OPERATION = "security.encryption"
    KEY_ROTATION = "security.key_rotation"
    
    # Data events
    DATA_ACCESS = "data.access"
    DATA_MODIFICATION = "data.modification"
    DATA_DELETION = "data.deletion"
    DATA_EXPORT = "data.export"
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    CONFIG_CHANGE = "system.config_change"
    ERROR_OCCURRED = "system.error"
    
    # Compliance events
    GDPR_REQUEST = "compliance.gdpr.request"
    HIPAA_ACCESS = "compliance.hipaa.access"
    PCI_OPERATION = "compliance.pci.operation"
    SOX_AUDIT = "compliance.sox.audit"


class ComplianceFramework(Flag):
    """
    Compliance frameworks that can be enabled (supports multiple simultaneous frameworks).
    """
    NONE = 0
    GDPR = auto()  # General Data Protection Regulation
    HIPAA = auto()  # Health Insurance Portability and Accountability Act
    PCI_DSS = auto()  # Payment Card Industry Data Security Standard
    SOX = auto()  # Sarbanes-Oxley Act
    ISO_27001 = auto()  # ISO/IEC 27001 Information Security Management
    NIST_CSF = auto()  # NIST Cybersecurity Framework
    
    def __str__(self) -> str:
        if self == ComplianceFramework.NONE:
            return "none"
        
        frameworks = []
        if self & ComplianceFramework.GDPR:
            frameworks.append("GDPR")
        if self & ComplianceFramework.HIPAA:
            frameworks.append("HIPAA")
        if self & ComplianceFramework.PCI_DSS:
            frameworks.append("PCI-DSS")
        if self & ComplianceFramework.SOX:
            frameworks.append("SOX")
        if self & ComplianceFramework.ISO_27001:
            frameworks.append("ISO-27001")
        if self & ComplianceFramework.NIST_CSF:
            frameworks.append("NIST-CSF")
        
        return ",".join(frameworks)


class ThreatType(Enum):
    """
    Types of security threats that can be detected.
    """
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    TIMING_ATTACK = "timing_attack"
    BRUTE_FORCE = "brute_force"
    DATA_EXFILTRATION = "data_exfiltration"
    MALFORMED_INPUT = "malformed_input"
    REPLAY_ATTACK = "replay_attack"
    CSRF_ATTACK = "csrf_attack"
    INJECTION_ATTACK = "injection_attack"
    ENUMERATION_ATTACK = "enumeration_attack"


# Environment-based configuration defaults
def get_environment_security_level() -> SecurityLevel:
    """
    Determine security level based on environment variables.
    
    Returns:
        SecurityLevel based on environment or MAXIMUM as default
    """
    env_level = os.getenv('PYIDVERIFY_SECURITY_LEVEL', '').upper()
    
    level_mapping = {
        'DEVELOPMENT': SecurityLevel.DEVELOPMENT,
        'BASIC': SecurityLevel.BASIC,
        'STANDARD': SecurityLevel.STANDARD,
        'HIGH': SecurityLevel.HIGH,
        'MAXIMUM': SecurityLevel.MAXIMUM,
    }
    
    return level_mapping.get(env_level, SecurityLevel.MAXIMUM)


def get_environment_compliance() -> ComplianceFramework:
    """
    Determine compliance frameworks based on environment variables.
    
    Returns:
        ComplianceFramework flags based on environment
    """
    env_compliance = os.getenv('PYIDVERIFY_COMPLIANCE', '').upper()
    
    compliance = ComplianceFramework.NONE
    
    if 'GDPR' in env_compliance:
        compliance |= ComplianceFramework.GDPR
    if 'HIPAA' in env_compliance:
        compliance |= ComplianceFramework.HIPAA
    if 'PCI' in env_compliance or 'PCI_DSS' in env_compliance:
        compliance |= ComplianceFramework.PCI_DSS
    if 'SOX' in env_compliance:
        compliance |= ComplianceFramework.SOX
    if 'ISO' in env_compliance:
        compliance |= ComplianceFramework.ISO_27001
    if 'NIST' in env_compliance:
        compliance |= ComplianceFramework.NIST_CSF
    
    return compliance


# Security configuration templates
SECURITY_TEMPLATES: Dict[SecurityLevel, Dict[str, Any]] = {
    SecurityLevel.DEVELOPMENT: {
        'encryption_algorithm': EncryptionAlgorithm.AES_256_GCM,
        'hash_algorithm': HashAlgorithm.BLAKE3,  # Faster for development
        'audit_enabled': False,
        'memory_clearing_enabled': False,
        'timing_attack_protection': False,
        'key_rotation_days': 365,  # Less frequent rotation
        'rate_limit_enabled': False,
        'compliance_frameworks': ComplianceFramework.NONE,
    },
    
    SecurityLevel.BASIC: {
        'encryption_algorithm': EncryptionAlgorithm.AES_256_GCM,
        'hash_algorithm': HashAlgorithm.ARGON2ID,
        'audit_enabled': False,
        'memory_clearing_enabled': False,
        'timing_attack_protection': True,
        'key_rotation_days': 180,
        'rate_limit_enabled': True,
        'compliance_frameworks': ComplianceFramework.NONE,
    },
    
    SecurityLevel.STANDARD: {
        'encryption_algorithm': EncryptionAlgorithm.AES_256_GCM,
        'hash_algorithm': HashAlgorithm.ARGON2ID,
        'audit_enabled': True,
        'memory_clearing_enabled': False,
        'timing_attack_protection': True,
        'key_rotation_days': 90,
        'rate_limit_enabled': True,
        'compliance_frameworks': ComplianceFramework.GDPR,
    },
    
    SecurityLevel.HIGH: {
        'encryption_algorithm': EncryptionAlgorithm.AES_256_GCM,
        'hash_algorithm': HashAlgorithm.ARGON2ID,
        'audit_enabled': True,
        'memory_clearing_enabled': True,
        'timing_attack_protection': True,
        'key_rotation_days': 30,
        'rate_limit_enabled': True,
        'compliance_frameworks': ComplianceFramework.GDPR | ComplianceFramework.HIPAA,
    },
    
    SecurityLevel.MAXIMUM: {
        'encryption_algorithm': EncryptionAlgorithm.AES_256_GCM,
        'hash_algorithm': HashAlgorithm.ARGON2ID,
        'audit_enabled': True,
        'memory_clearing_enabled': True,
        'timing_attack_protection': True,
        'key_rotation_days': 7,  # Weekly key rotation
        'rate_limit_enabled': True,
        'compliance_frameworks': (
            ComplianceFramework.GDPR | 
            ComplianceFramework.HIPAA | 
            ComplianceFramework.PCI_DSS | 
            ComplianceFramework.SOX
        ),
    },
}


def get_security_template(level: SecurityLevel) -> Dict[str, Any]:
    """
    Get security configuration template for a given security level.
    
    Args:
        level: SecurityLevel to get template for
        
    Returns:
        Dictionary containing security configuration
    """
    return SECURITY_TEMPLATES[level].copy()


# Regex patterns for security validation
SECURITY_PATTERNS = {
    'sql_injection': [
        r'(\bunion\b.*\bselect\b)|(\bselect\b.*\bunion\b)',
        r'(\bor\b\s+\d+\s*=\s*\d+)|(\band\b\s+\d+\s*=\s*\d+)',
        r'(\bdrop\b\s+\btable\b)|(\bdelete\b\s+\bfrom\b)',
        r'(\binsert\b\s+\binto\b)|(\bupdate\b.*\bset\b)',
    ],
    'xss_patterns': [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
    ],
    'path_traversal': [
        r'\.\./',
        r'\.\.\.',
        r'%2e%2e%2f',
        r'%2e%2e/',
    ],
}

# Error codes for consistent error handling
ERROR_CODES = {
    # General security errors (SEC_xxx)
    'SEC_GENERAL': 'General security error',
    'SEC_CONFIG': 'Security configuration error',
    'SEC_ACCESS_DENIED': 'Access denied',
    'SEC_RATE_LIMIT': 'Rate limit exceeded',
    
    # Cryptographic errors (CRYPTO_xxx)
    'CRYPTO_ERROR': 'General cryptographic error',
    'CRYPTO_KEY_ERROR': 'Cryptographic key error',
    'CRYPTO_ENCRYPT_ERROR': 'Encryption error',
    'CRYPTO_DECRYPT_ERROR': 'Decryption error',
    'CRYPTO_HASH_ERROR': 'Hashing error',
    'CRYPTO_VERIFY_ERROR': 'Hash verification error',
    
    # Audit errors (AUDIT_xxx)
    'AUDIT_ERROR': 'General audit error',
    'AUDIT_LOG_ERROR': 'Audit log error',
    'AUDIT_INTEGRITY_ERROR': 'Audit log integrity error',
    'AUDIT_STORAGE_ERROR': 'Audit storage error',
    
    # Validation errors (VAL_xxx)
    'VAL_SECURITY_ERROR': 'Validation security error',
    'VAL_THREAT_DETECTED': 'Security threat detected in validation',
    'VAL_MALICIOUS_INPUT': 'Malicious input detected',
    
    # Compliance errors (COMP_xxx)
    'COMP_GDPR_VIOLATION': 'GDPR compliance violation',
    'COMP_HIPAA_VIOLATION': 'HIPAA compliance violation',
    'COMP_PCI_VIOLATION': 'PCI DSS compliance violation',
    'COMP_SOX_VIOLATION': 'SOX compliance violation',
}
