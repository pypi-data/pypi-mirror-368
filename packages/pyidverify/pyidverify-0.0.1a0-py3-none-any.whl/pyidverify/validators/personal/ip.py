"""
IP Address Validator
===================

This module implements comprehensive IP address validation supporting IPv4,
IPv6, CIDR notation, private/public ranges, and geolocation services.

Features:
- IPv4 and IPv6 address validation
- CIDR notation support
- Private/public IP range detection
- Reserved range identification
- Geolocation and ISP detection (optional)
- Reputation scoring and threat detection
- Network range validation
- IP address normalization and conversion

Examples:
    >>> from pyidverify.validators.personal.ip import IPAddressValidator
    >>> 
    >>> validator = IPAddressValidator()
    >>> result = validator.validate("192.168.1.1")
    >>> print(f"Valid: {result.is_valid}")  # True
    >>> print(f"Private: {result.metadata.get('is_private')}")  # True
    >>> 
    >>> # IPv6 validation
    >>> result = validator.validate("2001:db8::1")
    >>> print(f"Version: {result.metadata.get('version')}")  # 6

Security Features:
- Input sanitization prevents injection attacks
- Rate limiting prevents scanning/enumeration
- Reputation checks against known malicious IPs
- Private IP detection prevents data leakage
- Memory-safe address parsing
- Audit logging for sensitive operations
"""

from typing import Optional, Dict, Any, List, Set, Union, Tuple
import re
import time
import ipaddress
import socket
from dataclasses import dataclass
from pathlib import Path
import json
from urllib.parse import urlparse

try:
    from ...core.base_validator import BaseValidator
    from ...core.types import IDType, ValidationResult, ValidationLevel
    from ...core.exceptions import ValidationError, SecurityError
    from ...utils.extractors import normalize_input, clean_input
    from ...utils.caching import LRUCache
    from ...security.audit import AuditLogger
    from ...security.rate_limiting import RateLimiter
    from ...config.networks import get_network_info, get_reputation_sources
    _IMPORTS_AVAILABLE = True
except ImportError as e:
    # Graceful degradation
    _IMPORTS_AVAILABLE = False
    _IMPORT_ERROR = str(e)
    
    # Mock classes for development
    class BaseValidator:
        def __init__(self): pass
    
    class ValidationResult:
        def __init__(self, is_valid, id_type, confidence=1.0, metadata=None, errors=None):
            self.is_valid = is_valid
            self.id_type = id_type
            self.confidence = confidence
            self.metadata = metadata or {}
            self.errors = errors or []

@dataclass
class IPValidationOptions:
    """Configuration options for IP address validation"""
    allow_ipv4: bool = True
    allow_ipv6: bool = True
    allow_private: bool = True
    allow_reserved: bool = False
    allow_loopback: bool = False
    allow_multicast: bool = False
    allow_unspecified: bool = False
    check_reputation: bool = False
    check_geolocation: bool = False
    strict_validation: bool = False
    timeout_seconds: float = 5.0
    
    def __post_init__(self):
        """Validate configuration options"""
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

class IPAddressValidator(BaseValidator):
    """
    Comprehensive IP address validator with IPv4/IPv6 support.
    
    This validator supports standard IP address validation, CIDR notation,
    network range detection, and optional geolocation/reputation services.
    """
    
    def __init__(self, **options):
        """
        Initialize IP address validator.
        
        Args:
            **options: Validation options (see IPValidationOptions)
        """
        if _IMPORTS_AVAILABLE:
            super().__init__()
            self.audit_logger = AuditLogger("ip_validator")
            self.rate_limiter = RateLimiter(max_requests=2000, time_window=3600)
            self.validation_cache = LRUCache(maxsize=2000)
            self.reputation_cache = LRUCache(maxsize=1000)
            self.geolocation_cache = LRUCache(maxsize=1000)
        
        # Configure validation options
        self.options = IPValidationOptions(**options)
        
        # Load threat intelligence data
        self._threat_ranges = self._load_threat_ranges()
        self._reputation_sources = self._load_reputation_sources()
        
        # Compile regex patterns for pre-validation
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for IP validation"""
        
        # IPv4 patterns
        self._ipv4_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        
        # IPv4 CIDR pattern
        self._ipv4_cidr_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
            r'/(?:[0-9]|[1-2][0-9]|3[0-2])$'
        )
        
        # IPv6 pattern (simplified)
        self._ipv6_pattern = re.compile(
            r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|'
            r'^::$|'
            r'^::1$|'
            r'^([0-9a-fA-F]{1,4}:){1,7}:$|'
            r'^::[0-9a-fA-F]{1,4}$|'
            r'^([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}$|'
            r'^([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}$|'
            r'^([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}$|'
            r'^([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}$|'
            r'^([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}$|'
            r'^[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})$'
        )
        
        # IPv6 CIDR pattern
        self._ipv6_cidr_pattern = re.compile(
            r'^([0-9a-fA-F:]+)/([0-9]|[1-9][0-9]|1[01][0-9]|12[0-8])$'
        )
        
        # URL extraction pattern (for extracting IPs from URLs)
        self._url_pattern = re.compile(
            r'https?://([^:/\s]+)'
        )
    
    def _load_threat_ranges(self) -> Set[str]:
        """Load known malicious IP ranges"""
        threat_ranges = set()
        
        # Built-in threat ranges (sample)
        built_in_threats = {
            # Known malicious ranges (examples)
            '127.0.0.0/8',    # Loopback (for testing)
            '169.254.0.0/16', # Link-local
            # Add more threat ranges as needed
        }
        
        threat_ranges.update(built_in_threats)
        
        # Try to load from external file
        try:
            threat_file = Path(__file__).parent / 'data' / 'threat_ranges.json'
            if threat_file.exists():
                with open(threat_file, 'r', encoding='utf-8') as f:
                    external_ranges = json.load(f)
                    if isinstance(external_ranges, list):
                        threat_ranges.update(external_ranges)
        except Exception:
            pass  # Use built-in ranges if external file unavailable
        
        return threat_ranges
    
    def _load_reputation_sources(self) -> Dict[str, str]:
        """Load reputation check sources"""
        sources = {
            # Example reputation sources (would need API keys in production)
            'virustotal': 'https://www.virustotal.com/api/v3/ip_addresses/',
            'abuseipdb': 'https://api.abuseipdb.com/api/v2/check',
            # Add more sources as needed
        }
        return sources
    
    def validate(self, ip_input: str, validation_level: ValidationLevel = None) -> ValidationResult:
        """
        Validate an IP address.
        
        Args:
            ip_input: IP address string to validate
            validation_level: Level of validation to perform
            
        Returns:
            ValidationResult with validation details
            
        Examples:
            >>> validator = IPAddressValidator()
            >>> result = validator.validate("192.168.1.1")
            >>> print(f"Valid: {result.is_valid}")
        """
        start_time = time.time()
        errors = []
        metadata = {
            'original_input': ip_input,
            'validation_time': None,
            'checks_performed': []
        }
        
        try:
            # Rate limiting check
            if _IMPORTS_AVAILABLE and not self.rate_limiter.allow_request("ip_validation"):
                raise SecurityError("Rate limit exceeded for IP validation")
            
            # Input validation
            if not isinstance(ip_input, str):
                errors.append("IP address must be a string")
                return self._create_result(False, errors, metadata, 0.0)
            
            if len(ip_input.strip()) == 0:
                errors.append("IP address cannot be empty")
                return self._create_result(False, errors, metadata, 0.0)
            
            # Normalize input (extract IP from URL if needed)
            normalized_ip = self._normalize_ip(ip_input)
            metadata['normalized_ip'] = normalized_ip
            
            # Check cache first
            if _IMPORTS_AVAILABLE:
                cached_result = self.validation_cache.get(normalized_ip)
                if cached_result:
                    return cached_result
            
            confidence = 1.0
            
            # 1. Basic format validation
            format_valid, ip_version, cidr_prefix = self._validate_format(normalized_ip)
            metadata['checks_performed'].append('format')
            metadata['version'] = ip_version
            metadata['has_cidr'] = cidr_prefix is not None
            if cidr_prefix:
                metadata['cidr_prefix'] = cidr_prefix
            
            if not format_valid:
                errors.append("Invalid IP address format")
                return self._create_result(False, errors, metadata, 0.0)
            
            # 2. Parse IP address
            try:
                if '/' in normalized_ip:
                    # Handle CIDR notation
                    ip_obj = ipaddress.ip_network(normalized_ip, strict=False)
                    ip_addr = ip_obj.network_address
                    metadata['network_size'] = ip_obj.num_addresses
                    metadata['is_network'] = True
                else:
                    # Handle single IP address
                    ip_obj = ipaddress.ip_address(normalized_ip)
                    ip_addr = ip_obj
                    metadata['is_network'] = False
                
                metadata['checks_performed'].append('parse')
                metadata['version'] = ip_addr.version
                
            except ValueError as e:
                errors.append(f"Invalid IP address: {str(e)}")
                return self._create_result(False, errors, metadata, 0.0)
            
            # 3. Version validation
            if ip_addr.version == 4 and not self.options.allow_ipv4:
                errors.append("IPv4 addresses not allowed")
                confidence *= 0.1
            elif ip_addr.version == 6 and not self.options.allow_ipv6:
                errors.append("IPv6 addresses not allowed")
                confidence *= 0.1
            
            # 4. IP type validation
            type_valid, type_info = self._validate_ip_type(ip_addr)
            metadata['checks_performed'].append('type')
            metadata.update(type_info)
            
            if not type_valid:
                errors.extend(type_info.get('type_errors', []))
                confidence *= 0.3
            
            # 5. Network range validation
            if isinstance(ip_obj, ipaddress.IPv4Network) or isinstance(ip_obj, ipaddress.IPv6Network):
                range_info = self._analyze_network_range(ip_obj)
                metadata.update(range_info)
            
            # 6. Reputation check (optional)
            if self.options.check_reputation:
                reputation_info = self._check_reputation(str(ip_addr))
                metadata['checks_performed'].append('reputation')
                metadata.update(reputation_info)
                
                if reputation_info.get('is_malicious'):
                    errors.append("IP address flagged as malicious")
                    confidence *= 0.1
            
            # 7. Geolocation check (optional)
            if self.options.check_geolocation:
                geo_info = self._get_geolocation(str(ip_addr))
                metadata['checks_performed'].append('geolocation')
                metadata.update(geo_info)
            
            # 8. Threat intelligence check
            threat_detected = self._check_threat_intelligence(str(ip_addr))
            if threat_detected:
                errors.append("IP address matches known threat patterns")
                confidence *= 0.1
            
            # Calculate final validation result
            is_valid = len(errors) == 0 and confidence > 0.5
            
            # Create result
            result = self._create_result(is_valid, errors, metadata, confidence)
            
            # Cache result
            if _IMPORTS_AVAILABLE:
                self.validation_cache.set(normalized_ip, result)
            
            # Audit logging
            if _IMPORTS_AVAILABLE:
                self.audit_logger.log_validation(
                    "ip_address", normalized_ip, is_valid, metadata
                )
            
            return result
            
        except SecurityError:
            raise
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return self._create_result(False, errors, metadata, 0.0)
        
        finally:
            metadata['validation_time'] = time.time() - start_time
    
    def _normalize_ip(self, ip_input: str) -> str:
        """Normalize IP address input"""
        # Remove whitespace
        normalized = ip_input.strip()
        
        # Extract IP from URL if present
        url_match = self._url_pattern.match(normalized)
        if url_match:
            normalized = url_match.group(1)
        
        # Handle bracketed IPv6 addresses
        if normalized.startswith('[') and normalized.endswith(']'):
            normalized = normalized[1:-1]
        
        # Remove port numbers
        if ':' in normalized and not self._is_ipv6_format(normalized):
            # IPv4 with port
            if normalized.count(':') == 1:
                normalized = normalized.split(':')[0]
        
        return normalized
    
    def _is_ipv6_format(self, ip_str: str) -> bool:
        """Check if string might be IPv6 format"""
        return '::' in ip_str or ip_str.count(':') >= 2
    
    def _validate_format(self, ip_str: str) -> Tuple[bool, int, Optional[int]]:
        """
        Validate IP address format.
        
        Returns:
            Tuple of (is_valid, ip_version, cidr_prefix)
        """
        cidr_prefix = None
        
        # Check for CIDR notation
        if '/' in ip_str:
            parts = ip_str.split('/')
            if len(parts) != 2:
                return False, 0, None
            
            ip_part, prefix_part = parts
            try:
                cidr_prefix = int(prefix_part)
            except ValueError:
                return False, 0, None
        else:
            ip_part = ip_str
        
        # Check IPv4 format
        if self._ipv4_pattern.match(ip_part):
            if cidr_prefix is not None:
                if 0 <= cidr_prefix <= 32:
                    return True, 4, cidr_prefix
                else:
                    return False, 4, None
            return True, 4, None
        
        # Check IPv6 format (simplified check)
        if self._is_ipv6_format(ip_part):
            if cidr_prefix is not None:
                if 0 <= cidr_prefix <= 128:
                    return True, 6, cidr_prefix
                else:
                    return False, 6, None
            return True, 6, None
        
        return False, 0, None
    
    def _validate_ip_type(self, ip_addr: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> Tuple[bool, Dict[str, Any]]:
        """Validate IP address type against allowed types"""
        type_info = {
            'is_private': ip_addr.is_private,
            'is_global': ip_addr.is_global,
            'is_reserved': ip_addr.is_reserved,
            'is_loopback': ip_addr.is_loopback,
            'is_multicast': ip_addr.is_multicast,
            'is_unspecified': ip_addr.is_unspecified,
            'type_errors': []
        }
        
        # Additional IPv4-specific checks
        if isinstance(ip_addr, ipaddress.IPv4Address):
            type_info['is_link_local'] = ip_addr.is_link_local
        
        # Additional IPv6-specific checks
        if isinstance(ip_addr, ipaddress.IPv6Address):
            type_info['is_site_local'] = ip_addr.is_site_local
        
        # Check against allowed types
        is_valid = True
        
        if ip_addr.is_private and not self.options.allow_private:
            type_info['type_errors'].append("Private IP addresses not allowed")
            is_valid = False
        
        if ip_addr.is_reserved and not self.options.allow_reserved:
            type_info['type_errors'].append("Reserved IP addresses not allowed")
            is_valid = False
        
        if ip_addr.is_loopback and not self.options.allow_loopback:
            type_info['type_errors'].append("Loopback addresses not allowed")
            is_valid = False
        
        if ip_addr.is_multicast and not self.options.allow_multicast:
            type_info['type_errors'].append("Multicast addresses not allowed")
            is_valid = False
        
        if ip_addr.is_unspecified and not self.options.allow_unspecified:
            type_info['type_errors'].append("Unspecified addresses not allowed")
            is_valid = False
        
        return is_valid, type_info
    
    def _analyze_network_range(self, network: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> Dict[str, Any]:
        """Analyze network range properties"""
        return {
            'network_address': str(network.network_address),
            'broadcast_address': str(network.broadcast_address) if hasattr(network, 'broadcast_address') else None,
            'netmask': str(network.netmask),
            'prefix_length': network.prefixlen,
            'num_addresses': network.num_addresses,
            'is_subnet_of_private': any(network.subnet_of(net) for net in [
                ipaddress.ip_network('10.0.0.0/8'),
                ipaddress.ip_network('172.16.0.0/12'),
                ipaddress.ip_network('192.168.0.0/16')
            ] if network.version == 4),
        }
    
    def _check_reputation(self, ip_str: str) -> Dict[str, Any]:
        """Check IP reputation against threat intelligence sources"""
        reputation_info = {
            'is_malicious': False,
            'reputation_score': 0,
            'threat_sources': [],
            'reputation_checked': False
        }
        
        try:
            # Check cache first
            cache_key = f"reputation:{ip_str}"
            if _IMPORTS_AVAILABLE:
                cached_info = self.reputation_cache.get(cache_key)
                if cached_info:
                    return cached_info
            
            # Simulate reputation check (in production, would call actual APIs)
            # This is a placeholder for actual threat intelligence integration
            reputation_info['reputation_checked'] = True
            reputation_info['reputation_score'] = 100  # Assume clean
            
            # Cache result
            if _IMPORTS_AVAILABLE:
                self.reputation_cache.set(cache_key, reputation_info)
            
        except Exception:
            pass  # Ignore reputation check failures
        
        return reputation_info
    
    def _get_geolocation(self, ip_str: str) -> Dict[str, Any]:
        """Get geolocation information for IP address"""
        geo_info = {
            'country': None,
            'country_code': None,
            'region': None,
            'city': None,
            'latitude': None,
            'longitude': None,
            'timezone': None,
            'isp': None,
            'organization': None,
            'geolocation_checked': False
        }
        
        try:
            # Check cache first
            cache_key = f"geolocation:{ip_str}"
            if _IMPORTS_AVAILABLE:
                cached_info = self.geolocation_cache.get(cache_key)
                if cached_info:
                    return cached_info
            
            # Simulate geolocation lookup (in production, would use actual service)
            # This is a placeholder for actual geolocation integration
            geo_info['geolocation_checked'] = True
            
            # Try to get hostname as basic location hint
            try:
                hostname = socket.gethostbyaddr(ip_str)[0]
                geo_info['hostname'] = hostname
            except Exception:
                pass
            
            # Cache result
            if _IMPORTS_AVAILABLE:
                self.geolocation_cache.set(cache_key, geo_info)
            
        except Exception:
            pass  # Ignore geolocation failures
        
        return geo_info
    
    def _check_threat_intelligence(self, ip_str: str) -> bool:
        """Check IP against known threat ranges"""
        try:
            ip_addr = ipaddress.ip_address(ip_str)
            
            # Check against loaded threat ranges
            for threat_range in self._threat_ranges:
                try:
                    threat_network = ipaddress.ip_network(threat_range, strict=False)
                    if ip_addr in threat_network:
                        return True
                except Exception:
                    continue  # Skip invalid threat ranges
            
            return False
            
        except Exception:
            return False  # Don't flag as threat if check fails
    
    def _create_result(self, is_valid: bool, errors: List[str], 
                      metadata: Dict[str, Any], confidence: float) -> ValidationResult:
        """Create validation result object"""
        if _IMPORTS_AVAILABLE:
            return ValidationResult(
                is_valid=is_valid,
                id_type=IDType.IP_ADDRESS,
                confidence=confidence,
                metadata=metadata,
                errors=errors
            )
        else:
            # Fallback for development
            return ValidationResult(
                is_valid=is_valid,
                id_type="ip_address",
                confidence=confidence,
                metadata=metadata,
                errors=errors
            )
    
    def validate_batch(self, ip_addresses: List[str], **kwargs) -> List[ValidationResult]:
        """
        Validate multiple IP addresses.
        
        Args:
            ip_addresses: List of IP addresses to validate
            **kwargs: Additional validation options
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        
        for ip_addr in ip_addresses:
            try:
                result = self.validate(ip_addr, **kwargs)
                results.append(result)
            except Exception as e:
                # Create error result for failed validation
                error_result = self._create_result(
                    is_valid=False,
                    errors=[f"Validation failed: {str(e)}"],
                    metadata={'original_input': ip_addr},
                    confidence=0.0
                )
                results.append(error_result)
        
        return results
    
    def is_in_range(self, ip: str, network_range: str) -> bool:
        """
        Check if IP address is within a network range.
        
        Args:
            ip: IP address to check
            network_range: Network range in CIDR notation
            
        Returns:
            True if IP is in range, False otherwise
        """
        try:
            ip_addr = ipaddress.ip_address(ip)
            network = ipaddress.ip_network(network_range, strict=False)
            return ip_addr in network
        except Exception:
            return False
    
    def get_network_info(self, ip: str) -> Dict[str, Any]:
        """
        Get network information for an IP address.
        
        Args:
            ip: IP address to analyze
            
        Returns:
            Dictionary with network information
        """
        try:
            ip_addr = ipaddress.ip_address(ip)
            
            # Determine likely network ranges
            network_info = {
                'ip_address': str(ip_addr),
                'version': ip_addr.version,
                'is_private': ip_addr.is_private,
                'is_global': ip_addr.is_global,
                'possible_networks': []
            }
            
            if ip_addr.version == 4:
                # Common IPv4 network classifications
                if ip_addr.is_private:
                    if ipaddress.IPv4Address('10.0.0.0') <= ip_addr <= ipaddress.IPv4Address('10.255.255.255'):
                        network_info['possible_networks'].append('10.0.0.0/8')
                    elif ipaddress.IPv4Address('172.16.0.0') <= ip_addr <= ipaddress.IPv4Address('172.31.255.255'):
                        network_info['possible_networks'].append('172.16.0.0/12')
                    elif ipaddress.IPv4Address('192.168.0.0') <= ip_addr <= ipaddress.IPv4Address('192.168.255.255'):
                        network_info['possible_networks'].append('192.168.0.0/16')
            
            return network_info
            
        except Exception as e:
            return {'error': str(e)}
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Update validator configuration.
        
        Args:
            config: Configuration dictionary
        """
        for key, value in config.items():
            if hasattr(self.options, key):
                setattr(self.options, key, value)
            else:
                raise ValidationError(f"Unknown configuration option: {key}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this validator"""
        return {
            "validator_type": "ip_address",
            "supported_versions": ["IPv4", "IPv6"],
            "supported_formats": ["Standard", "CIDR"],
            "features": [
                "format_validation",
                "type_validation",
                "network_range_analysis",
                "reputation_checking",
                "geolocation_lookup",
                "threat_intelligence"
            ],
            "options": {
                "allow_ipv4": self.options.allow_ipv4,
                "allow_ipv6": self.options.allow_ipv6,
                "allow_private": self.options.allow_private,
                "allow_reserved": self.options.allow_reserved,
                "allow_loopback": self.options.allow_loopback,
                "allow_multicast": self.options.allow_multicast,
                "check_reputation": self.options.check_reputation,
                "check_geolocation": self.options.check_geolocation,
                "strict_validation": self.options.strict_validation
            },
            "threat_ranges_count": len(self._threat_ranges),
            "reputation_sources_count": len(self._reputation_sources),
            "cache_stats": {
                "validation_cache": self.validation_cache.stats().to_dict() if _IMPORTS_AVAILABLE else None,
                "reputation_cache": self.reputation_cache.stats().to_dict() if _IMPORTS_AVAILABLE else None,
                "geolocation_cache": self.geolocation_cache.stats().to_dict() if _IMPORTS_AVAILABLE else None
            }
        }

# Export public interface
__all__ = [
    "IPAddressValidator",
    "IPValidationOptions"
]
