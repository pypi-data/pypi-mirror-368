"""
PyIDVerify IP Address Validator

Validates IP addresses (IPv4 and IPv6) with comprehensive security checks.
Includes geolocation, reputation analysis, and threat detection.

Author: PyIDVerify Team
License: MIT
"""

import re
import socket
import ipaddress
import logging
from typing import Dict, Optional, Any, List, Union
from dataclasses import dataclass
from enum import Enum
from ..core.base_validator import BaseValidator
from ..core.types import IDType, ValidationResult, ValidationLevel
from ..core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class IPType(Enum):
    """Types of IP addresses."""
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    UNKNOWN = "unknown"


class IPClass(Enum):
    """IP address classes."""
    PUBLIC = "public"
    PRIVATE = "private"
    LOOPBACK = "loopback"
    MULTICAST = "multicast"
    RESERVED = "reserved"
    UNSPECIFIED = "unspecified"


@dataclass
class IPAddressInfo:
    """Information about an IP address."""
    ip_address: str
    ip_type: IPType
    ip_class: IPClass
    network: Optional[str] = None
    is_valid: bool = True
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    is_vpn: bool = False
    is_proxy: bool = False
    is_tor: bool = False
    threat_score: float = 0.0
    reputation_score: float = 1.0


class IPAddressValidator(BaseValidator):
    """
    Comprehensive IP address validator.
    
    Features:
    - IPv4 and IPv6 validation
    - Format validation and normalization
    - Private/public classification
    - Geolocation lookup (optional)
    - Reputation and threat analysis
    - VPN/Proxy/Tor detection
    - Range and subnet validation
    - Performance optimized with caching
    """
    
    SUPPORTED_TYPE = IDType.IP_ADDRESS
    
    def __init__(self, config=None):
        """Initialize IP address validator."""
        super().__init__(config)
        
        # Known threat IP ranges (simplified - in production use threat intel feeds)
        self.threat_ranges = [
            # Example threat ranges - replace with real threat intel
            ipaddress.IPv4Network('192.168.100.0/24'),  # Example malicious range
        ]
        
        # Common VPN/Proxy IP ranges
        self.vpn_ranges = [
            # Example VPN ranges - replace with real VPN detection
            ipaddress.IPv4Network('10.0.0.0/8'),  # Private range often used by VPNs
        ]
        
        # Tor exit node IPs (would be updated from Tor directory)
        self.tor_exit_nodes = set()
        
        logger.debug("IPAddressValidator initialized")
        
    def validate(self, 
                ip_address: str, 
                level: ValidationLevel = ValidationLevel.STANDARD,
                metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate IP address with comprehensive checks.
        
        Args:
            ip_address: IP address to validate
            level: Validation level (BASIC, STANDARD, STRICT)
            metadata: Additional validation metadata
            
        Returns:
            ValidationResult with detailed IP information
        """
        try:
            # Basic format validation
            ip_info = self._parse_ip_address(ip_address)
            if not ip_info.is_valid:
                return ValidationResult(
                    is_valid=False,
                    id_type=IDType.IP_ADDRESS,
                    confidence=0.0,
                    errors=['Invalid IP address format'],
                    metadata={}
                )
                
            # Standard validation
            confidence = 0.8
            errors = []
            validation_metadata = {
                'ip_type': ip_info.ip_type.value,
                'ip_class': ip_info.ip_class.value,
                'network': ip_info.network,
                'is_private': ip_info.ip_class in [IPClass.PRIVATE, IPClass.LOOPBACK],
            }
            
            if level in [ValidationLevel.STANDARD, ValidationLevel.STRICT]:
                # Enhanced validation
                self._perform_security_checks(ip_info)
                validation_metadata.update({
                    'is_vpn': ip_info.is_vpn,
                    'is_proxy': ip_info.is_proxy,
                    'is_tor': ip_info.is_tor,
                    'threat_score': ip_info.threat_score,
                    'reputation_score': ip_info.reputation_score,
                })
                
                # Adjust confidence based on security checks
                if ip_info.threat_score > 0.7:
                    confidence = 0.2
                    errors.append('High threat score detected')
                elif ip_info.threat_score > 0.3:
                    confidence = 0.6
                    errors.append('Moderate threat indicators')
                    
                if ip_info.is_tor:
                    confidence = 0.3
                    errors.append('Tor exit node detected')
                    
                if level == ValidationLevel.STRICT:
                    # Geolocation and ISP info
                    if self._can_geolocate():
                        geo_info = self._get_geolocation(ip_info)
                        validation_metadata.update({
                            'country': geo_info.get('country'),
                            'region': geo_info.get('region'),
                            'city': geo_info.get('city'),
                            'isp': geo_info.get('isp'),
                        })
                        
                    # Additional strict checks
                    if ip_info.ip_class == IPClass.PRIVATE and not self._allow_private_ips():
                        confidence = 0.1
                        errors.append('Private IP addresses not allowed')
                        
            return ValidationResult(
                is_valid=len(errors) == 0 or confidence > 0.5,
                id_type=IDType.IP_ADDRESS,
                confidence=confidence,
                errors=errors,
                metadata=validation_metadata
            )
            
        except Exception as e:
            logger.error(f"IP validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                id_type=IDType.IP_ADDRESS,
                confidence=0.0,
                errors=[f'Validation error: {str(e)}'],
                metadata={}
            )
            
    def can_validate(self, value: str) -> bool:
        """Check if value looks like an IP address."""
        try:
            ipaddress.ip_address(value.strip())
            return True
        except ValueError:
            return False
            
    def validate_range(self, ip_range: str) -> ValidationResult:
        """
        Validate IP address range or subnet.
        
        Args:
            ip_range: IP range in CIDR notation (e.g., "192.168.1.0/24")
            
        Returns:
            ValidationResult for the IP range
        """
        try:
            network = ipaddress.ip_network(ip_range, strict=False)
            
            metadata = {
                'network_address': str(network.network_address),
                'broadcast_address': str(network.broadcast_address),
                'num_addresses': network.num_addresses,
                'prefix_length': network.prefixlen,
                'is_private': network.is_private,
                'is_multicast': network.is_multicast,
                'is_reserved': network.is_reserved,
            }
            
            return ValidationResult(
                is_valid=True,
                id_type=IDType.IP_ADDRESS,
                confidence=0.9,
                errors=[],
                metadata=metadata
            )
            
        except ValueError as e:
            return ValidationResult(
                is_valid=False,
                id_type=IDType.IP_ADDRESS,
                confidence=0.0,
                errors=[f'Invalid IP range: {str(e)}'],
                metadata={}
            )
            
    def check_ip_in_range(self, ip_address: str, ip_range: str) -> bool:
        """Check if IP address is within specified range."""
        try:
            ip = ipaddress.ip_address(ip_address)
            network = ipaddress.ip_network(ip_range, strict=False)
            return ip in network
        except ValueError:
            return False
            
    def get_ip_geolocation(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get geolocation information for IP address."""
        if not self._can_geolocate():
            return None
            
        try:
            ip_info = self._parse_ip_address(ip_address)
            if ip_info.is_valid and ip_info.ip_class == IPClass.PUBLIC:
                return self._get_geolocation(ip_info)
        except Exception as e:
            logger.error(f"Geolocation lookup failed: {str(e)}")
            
        return None
        
    def _parse_ip_address(self, ip_address: str) -> IPAddressInfo:
        """Parse and classify IP address."""
        try:
            # Clean the input
            clean_ip = ip_address.strip()
            
            # Parse IP address
            ip_obj = ipaddress.ip_address(clean_ip)
            
            # Determine type
            ip_type = IPType.IPV4 if isinstance(ip_obj, ipaddress.IPv4Address) else IPType.IPV6
            
            # Classify IP address
            ip_class = self._classify_ip(ip_obj)
            
            # Get network information
            if isinstance(ip_obj, ipaddress.IPv4Address):
                if ip_obj.is_private:
                    network = str(ipaddress.ip_network(f"{clean_ip}/24", strict=False))
                else:
                    network = str(ipaddress.ip_network(f"{clean_ip}/16", strict=False))
            else:  # IPv6
                network = str(ipaddress.ip_network(f"{clean_ip}/64", strict=False))
                
            return IPAddressInfo(
                ip_address=clean_ip,
                ip_type=ip_type,
                ip_class=ip_class,
                network=network,
                is_valid=True
            )
            
        except ValueError as e:
            return IPAddressInfo(
                ip_address=ip_address,
                ip_type=IPType.UNKNOWN,
                ip_class=IPClass.RESERVED,
                is_valid=False
            )
            
    def _classify_ip(self, ip_obj: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> IPClass:
        """Classify IP address type."""
        if ip_obj.is_private:
            return IPClass.PRIVATE
        elif ip_obj.is_loopback:
            return IPClass.LOOPBACK
        elif ip_obj.is_multicast:
            return IPClass.MULTICAST
        elif ip_obj.is_reserved:
            return IPClass.RESERVED
        elif ip_obj.is_unspecified:
            return IPClass.UNSPECIFIED
        else:
            return IPClass.PUBLIC
            
    def _perform_security_checks(self, ip_info: IPAddressInfo):
        """Perform security-related checks on IP address."""
        try:
            ip_obj = ipaddress.ip_address(ip_info.ip_address)
            
            # Check against threat ranges
            threat_score = 0.0
            for threat_range in self.threat_ranges:
                if ip_obj in threat_range:
                    threat_score = max(threat_score, 0.8)
                    break
                    
            # Check VPN/Proxy detection
            is_vpn = self._check_vpn_proxy(ip_obj)
            
            # Check Tor exit nodes
            is_tor = ip_info.ip_address in self.tor_exit_nodes
            
            # Calculate reputation score
            reputation_score = 1.0 - threat_score
            if is_tor:
                reputation_score = min(reputation_score, 0.3)
            elif is_vpn:
                reputation_score = min(reputation_score, 0.7)
                
            # Update IP info
            ip_info.threat_score = threat_score
            ip_info.is_vpn = is_vpn
            ip_info.is_proxy = is_vpn  # Simplified - same check for now
            ip_info.is_tor = is_tor
            ip_info.reputation_score = reputation_score
            
        except Exception as e:
            logger.error(f"Security check failed: {str(e)}")
            
    def _check_vpn_proxy(self, ip_obj: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> bool:
        """Check if IP is likely a VPN or proxy."""
        # Simplified VPN/Proxy detection
        # In production, use commercial IP intelligence services
        
        for vpn_range in self.vpn_ranges:
            if ip_obj in vpn_range:
                return True
                
        # Additional heuristics could include:
        # - Checking against known VPN provider ranges
        # - DNS reverse lookup patterns
        # - Port scan behavior analysis
        # - Connection pattern analysis
        
        return False
        
    def _get_geolocation(self, ip_info: IPAddressInfo) -> Dict[str, Any]:
        """Get geolocation information (placeholder implementation)."""
        # In production, integrate with services like MaxMind, IP2Location, etc.
        return {
            'country': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'isp': 'Unknown',
            'latitude': 0.0,
            'longitude': 0.0,
            'timezone': 'UTC'
        }
        
    def _can_geolocate(self) -> bool:
        """Check if geolocation is available."""
        # Check if geolocation service is configured and available
        return hasattr(self.config, 'geolocation_enabled') and self.config.geolocation_enabled
        
    def _allow_private_ips(self) -> bool:
        """Check if private IPs are allowed."""
        return getattr(self.config, 'allow_private_ips', True)
        
    def normalize_ip(self, ip_address: str) -> str:
        """Normalize IP address to standard format."""
        try:
            ip_obj = ipaddress.ip_address(ip_address.strip())
            return str(ip_obj)
        except ValueError:
            return ip_address
            
    def get_supported_types(self) -> List[IDType]:
        """Get supported ID types."""
        return [IDType.IP_ADDRESS]
