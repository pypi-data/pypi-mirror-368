"""
Risk-Based Scoring Validator for PyIDVerify

This module provides comprehensive risk assessment and adaptive scoring for biometric
authentication. Implements intelligent risk calculation, context-aware authentication,
and dynamic security policies based on real-time threat assessment.

Author: PyIDVerify Team
Date: August 7, 2025
Version: 1.0.0
"""

import asyncio
import json
import logging
import numpy as np
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Union, Set, Callable, NamedTuple
import hashlib
import uuid
import statistics
from concurrent.futures import ThreadPoolExecutor
# import geoip2.errors  # Optional dependency for geolocation analysis

from pyidverify.core.types import ValidationLevel, BiometricType, IDType
from pyidverify.core.exceptions import PyIDVerifyError, ValidationError
from pyidverify.validators.biometric import BaseBiometricValidator, BiometricValidationResult, BaseValidator, ValidationResult


class RiskCategory(Enum):
    """Risk assessment categories"""
    IDENTITY_RISK = auto()         # User identity verification risk
    BEHAVIORAL_RISK = auto()       # Behavioral pattern anomalies
    CONTEXTUAL_RISK = auto()       # Environmental and contextual factors
    TEMPORAL_RISK = auto()         # Time-based access patterns
    DEVICE_RISK = auto()           # Device-specific risk factors
    LOCATION_RISK = auto()         # Geographic and network location
    BIOMETRIC_RISK = auto()        # Biometric sample quality and authenticity
    HISTORICAL_RISK = auto()       # Historical usage patterns


class RiskSeverity(Enum):
    """Risk severity levels"""
    NEGLIGIBLE = (0.0, 0.1, "Negligible risk")
    MINIMAL = (0.1, 0.25, "Minimal risk")
    LOW = (0.25, 0.4, "Low risk")
    MODERATE = (0.4, 0.6, "Moderate risk")
    HIGH = (0.6, 0.8, "High risk")
    CRITICAL = (0.8, 0.95, "Critical risk")
    EXTREME = (0.95, 1.0, "Extreme risk")
    
    def __init__(self, min_score: float, max_score: float, description: str):
        self.min_score = min_score
        self.max_score = max_score
        self.description = description


class AuthenticationPolicy(Enum):
    """Authentication policies based on risk levels"""
    ALLOW = auto()                 # Allow access
    REQUIRE_ADDITIONAL_FACTOR = auto()  # Require additional authentication
    STEP_UP_AUTHENTICATION = auto()  # Escalate authentication requirements
    REQUIRE_ADMIN_APPROVAL = auto()  # Require administrator approval
    DENY_ACCESS = auto()           # Deny access completely
    QUARANTINE = auto()            # Quarantine user/session


class RiskFactor(NamedTuple):
    """Individual risk factor"""
    category: RiskCategory
    name: str
    score: float
    weight: float
    confidence: float
    description: str
    evidence: Dict[str, Any]


@dataclass
class RiskContext:
    """Comprehensive risk assessment context"""
    user_id: Optional[str]
    session_id: str
    device_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    location: Optional[str]
    timestamp: datetime
    
    # Authentication context
    authentication_method: str
    previous_attempts: int
    lockout_count: int
    
    # Biometric context
    biometric_samples: Dict[BiometricType, Any]
    quality_scores: Dict[BiometricType, float]
    match_scores: Dict[BiometricType, float]
    
    # Historical context
    user_history: Optional[Dict[str, Any]] = None
    device_history: Optional[Dict[str, Any]] = None
    location_history: Optional[List[str]] = None
    
    # External intelligence
    threat_intelligence: Optional[Dict[str, Any]] = None
    security_events: List[Dict[str, Any]] = None


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment result"""
    assessment_id: str
    timestamp: datetime
    context: RiskContext
    
    # Overall risk
    total_risk_score: float
    risk_severity: RiskSeverity
    confidence_level: float
    
    # Category breakdowns
    risk_factors: List[RiskFactor]
    category_scores: Dict[RiskCategory, float]
    
    # Recommendations
    recommended_policy: AuthenticationPolicy
    required_actions: List[str]
    security_recommendations: List[str]
    
    # Additional metadata
    assessment_duration_ms: float
    model_version: str
    risk_model_confidence: float


@dataclass
class UserRiskProfile:
    """User risk profile for historical analysis"""
    user_id: str
    created_at: datetime
    last_updated: datetime
    
    # Behavioral baselines
    typical_locations: List[str]
    typical_devices: List[str]
    typical_access_hours: List[int]
    typical_biometric_quality: Dict[BiometricType, float]
    
    # Risk history
    risk_history: List[float]
    authentication_success_rate: float
    anomaly_frequency: float
    
    # Security events
    security_incidents: List[Dict[str, Any]]
    lockout_history: List[datetime]
    
    # Trust metrics
    trust_score: float
    reliability_index: float


class GeolocationAnalyzer:
    """Analyzes geolocation-based risk factors"""
    
    def __init__(self):
        self.high_risk_countries = {
            'CN', 'RU', 'KP', 'IR'  # Example high-risk country codes
        }
        self.known_vpn_ranges = set()  # Would be populated with known VPN IP ranges
        self.tor_exit_nodes = set()    # Would be populated with Tor exit node IPs
    
    def analyze_location_risk(self, ip_address: str, 
                            known_locations: List[str] = None) -> RiskFactor:
        """Analyze location-based risk factors"""
        
        risk_score = 0.0
        evidence = {}
        description = "Location analysis"
        
        try:
            # Mock geolocation analysis (would use actual GeoIP database)
            country_code = self._get_country_code(ip_address)
            city = self._get_city(ip_address)
            
            evidence['ip_address'] = ip_address
            evidence['country_code'] = country_code
            evidence['city'] = city
            
            # High-risk country check
            if country_code in self.high_risk_countries:
                risk_score += 0.4
                description += f" - High-risk country: {country_code}"
            
            # VPN/Proxy detection
            if self._is_vpn_or_proxy(ip_address):
                risk_score += 0.3
                description += " - VPN/Proxy detected"
                evidence['vpn_detected'] = True
            
            # Tor network detection
            if ip_address in self.tor_exit_nodes:
                risk_score += 0.5
                description += " - Tor exit node detected"
                evidence['tor_detected'] = True
            
            # Location consistency check
            if known_locations:
                current_location = f"{city}, {country_code}"
                if current_location not in known_locations:
                    risk_score += 0.2
                    description += " - New location detected"
                    evidence['location_change'] = True
            
        except Exception as e:
            logging.warning(f"Location analysis failed: {e}")
            risk_score = 0.1  # Default low risk on failure
            evidence['error'] = str(e)
        
        return RiskFactor(
            category=RiskCategory.LOCATION_RISK,
            name="geolocation_analysis",
            score=min(1.0, risk_score),
            weight=0.15,
            confidence=0.8,
            description=description,
            evidence=evidence
        )
    
    def _get_country_code(self, ip_address: str) -> str:
        """Get country code from IP address"""
        # Mock implementation - would use actual GeoIP database
        ip_hash = hash(ip_address) % 100
        if ip_hash < 10:
            return 'CN'
        elif ip_hash < 15:
            return 'RU'
        elif ip_hash < 80:
            return 'US'
        else:
            return 'UK'
    
    def _get_city(self, ip_address: str) -> str:
        """Get city from IP address"""
        # Mock implementation
        country = self._get_country_code(ip_address)
        cities = {
            'US': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
            'UK': ['London', 'Manchester', 'Birmingham'],
            'CN': ['Beijing', 'Shanghai', 'Guangzhou'],
            'RU': ['Moscow', 'Saint Petersburg']
        }
        ip_hash = hash(ip_address) % len(cities.get(country, ['Unknown']))
        return cities.get(country, ['Unknown'])[ip_hash]
    
    def _is_vpn_or_proxy(self, ip_address: str) -> bool:
        """Check if IP address belongs to VPN or proxy service"""
        # Mock implementation - would check against known VPN IP ranges
        return hash(ip_address) % 20 == 0  # 5% chance for demo


class DeviceAnalyzer:
    """Analyzes device-based risk factors"""
    
    def __init__(self):
        self.suspicious_user_agents = {
            'automated_tool', 'bot', 'crawler', 'scanner'
        }
        self.mobile_indicators = {
            'mobile', 'android', 'iphone', 'ipad'
        }
    
    def analyze_device_risk(self, device_id: Optional[str], 
                          user_agent: Optional[str],
                          known_devices: List[str] = None) -> RiskFactor:
        """Analyze device-based risk factors"""
        
        risk_score = 0.0
        evidence = {}
        description = "Device analysis"
        
        # Device fingerprint analysis
        if device_id:
            evidence['device_id'] = device_id
            
            # Check against known devices
            if known_devices and device_id not in known_devices:
                risk_score += 0.3
                description += " - New device detected"
                evidence['new_device'] = True
        else:
            risk_score += 0.1
            description += " - No device fingerprint"
            evidence['no_device_id'] = True
        
        # User agent analysis
        if user_agent:
            evidence['user_agent'] = user_agent
            user_agent_lower = user_agent.lower()
            
            # Check for suspicious user agents
            for suspicious in self.suspicious_user_agents:
                if suspicious in user_agent_lower:
                    risk_score += 0.4
                    description += f" - Suspicious user agent: {suspicious}"
                    evidence['suspicious_user_agent'] = True
                    break
            
            # Check for mobile device
            is_mobile = any(indicator in user_agent_lower for indicator in self.mobile_indicators)
            evidence['is_mobile'] = is_mobile
            
            # Unusual browser characteristics
            if len(user_agent) < 50:  # Very short user agent
                risk_score += 0.2
                description += " - Unusual browser signature"
                evidence['unusual_browser'] = True
        
        return RiskFactor(
            category=RiskCategory.DEVICE_RISK,
            name="device_analysis",
            score=min(1.0, risk_score),
            weight=0.12,
            confidence=0.7,
            description=description,
            evidence=evidence
        )


class BiometricRiskAnalyzer:
    """Analyzes biometric-specific risk factors"""
    
    def __init__(self):
        self.quality_thresholds = {
            BiometricType.FINGERPRINT: 0.8,
            BiometricType.FACIAL: 0.75,
            BiometricType.VOICE: 0.7,
            BiometricType.IRIS: 0.85,
            BiometricType.BEHAVIORAL_KEYSTROKE: 0.6,
            BiometricType.BEHAVIORAL_MOUSE: 0.6,
            BiometricType.BEHAVIORAL_SIGNATURE: 0.7
        }
        
        self.spoofing_indicators = {
            'synthetic_generation', 'replay_attack', 'template_reconstruction',
            'presentation_attack', 'deepfake', 'voice_synthesis'
        }
    
    def analyze_biometric_risk(self, biometric_type: BiometricType,
                             quality_score: float,
                             match_score: float,
                             sample_data: Any,
                             liveness_score: Optional[float] = None) -> RiskFactor:
        """Analyze biometric sample risk factors"""
        
        risk_score = 0.0
        evidence = {}
        description = f"Biometric analysis - {biometric_type}"
        
        # Quality assessment
        threshold = self.quality_thresholds.get(biometric_type, 0.7)
        quality_ratio = quality_score / threshold
        
        if quality_score < threshold * 0.5:
            risk_score += 0.4
            description += " - Very poor quality"
            evidence['poor_quality'] = True
        elif quality_score < threshold * 0.8:
            risk_score += 0.2
            description += " - Below quality threshold"
            evidence['low_quality'] = True
        
        evidence['quality_score'] = quality_score
        evidence['quality_threshold'] = threshold
        
        # Match score analysis
        if match_score < 0.3:
            risk_score += 0.5
            description += " - Very low match score"
            evidence['low_match_score'] = True
        elif match_score < 0.5:
            risk_score += 0.3
            description += " - Below match threshold"
        
        evidence['match_score'] = match_score
        
        # Liveness assessment
        if liveness_score is not None:
            if liveness_score < 0.5:
                risk_score += 0.4
                description += " - Failed liveness check"
                evidence['liveness_failed'] = True
            elif liveness_score < 0.7:
                risk_score += 0.2
                description += " - Low liveness confidence"
                evidence['low_liveness'] = True
            
            evidence['liveness_score'] = liveness_score
        
        # Spoofing detection (mock implementation)
        spoofing_risk = self._detect_spoofing_risk(sample_data)
        if spoofing_risk > 0.3:
            risk_score += spoofing_risk
            description += " - Potential spoofing detected"
            evidence['spoofing_risk'] = spoofing_risk
        
        return RiskFactor(
            category=RiskCategory.BIOMETRIC_RISK,
            name=f"biometric_{biometric_type.name.lower()}",
            score=min(1.0, risk_score),
            weight=0.25,
            confidence=0.85,
            description=description,
            evidence=evidence
        )
    
    def _detect_spoofing_risk(self, sample_data: Any) -> float:
        """Detect potential spoofing in biometric sample"""
        # Mock spoofing detection - would use actual anti-spoofing algorithms
        if isinstance(sample_data, dict):
            # Check for synthetic generation indicators
            if sample_data.get('synthetic_probability', 0) > 0.5:
                return 0.6
            
            # Check for replay attack patterns
            if sample_data.get('replay_indicators', False):
                return 0.7
        
        return 0.1  # Default low spoofing risk


class BehavioralAnalyzer:
    """Analyzes behavioral pattern risks"""
    
    def __init__(self):
        self.anomaly_thresholds = {
            'keystroke_deviation': 2.5,
            'mouse_pattern_change': 2.0,
            'typing_rhythm_anomaly': 3.0,
            'access_pattern_anomaly': 2.0
        }
    
    def analyze_behavioral_risk(self, user_profile: Optional[UserRiskProfile],
                              current_behavior: Dict[str, Any],
                              historical_data: Dict[str, Any] = None) -> List[RiskFactor]:
        """Analyze behavioral pattern risk factors"""
        
        risk_factors = []
        
        # Keystroke dynamics analysis
        if 'keystroke_dynamics' in current_behavior:
            keystroke_risk = self._analyze_keystroke_anomaly(
                current_behavior['keystroke_dynamics'],
                user_profile,
                historical_data
            )
            risk_factors.append(keystroke_risk)
        
        # Access pattern analysis
        if user_profile:
            access_risk = self._analyze_access_patterns(user_profile, current_behavior)
            risk_factors.append(access_risk)
        
        # Temporal behavior analysis
        temporal_risk = self._analyze_temporal_behavior(current_behavior, user_profile)
        risk_factors.append(temporal_risk)
        
        return risk_factors
    
    def _analyze_keystroke_anomaly(self, keystroke_data: Dict[str, Any],
                                 user_profile: Optional[UserRiskProfile],
                                 historical_data: Dict[str, Any] = None) -> RiskFactor:
        """Analyze keystroke dynamics anomalies"""
        
        risk_score = 0.0
        evidence = keystroke_data.copy()
        description = "Keystroke dynamics analysis"
        
        # Compare with user profile if available
        if user_profile and hasattr(user_profile, 'keystroke_baseline'):
            baseline = getattr(user_profile, 'keystroke_baseline', {})
            
            # Analyze dwell time deviation
            if 'dwell_times' in keystroke_data and 'dwell_time_mean' in baseline:
                current_dwell = statistics.mean(keystroke_data['dwell_times'])
                baseline_dwell = baseline['dwell_time_mean']
                baseline_std = baseline.get('dwell_time_std', 50.0)
                
                if baseline_std > 0:
                    deviation = abs(current_dwell - baseline_dwell) / baseline_std
                    if deviation > self.anomaly_thresholds['keystroke_deviation']:
                        risk_score += min(0.4, deviation / 5.0)
                        description += f" - Dwell time anomaly ({deviation:.2f} std dev)"
                        evidence['dwell_time_anomaly'] = deviation
            
            # Analyze typing speed deviation
            if 'typing_speed' in keystroke_data and 'typing_speed_mean' in baseline:
                current_speed = keystroke_data['typing_speed']
                baseline_speed = baseline['typing_speed_mean']
                baseline_std = baseline.get('typing_speed_std', 10.0)
                
                if baseline_std > 0:
                    speed_deviation = abs(current_speed - baseline_speed) / baseline_std
                    if speed_deviation > 2.0:
                        risk_score += min(0.3, speed_deviation / 4.0)
                        description += f" - Typing speed anomaly ({speed_deviation:.2f} std dev)"
                        evidence['typing_speed_anomaly'] = speed_deviation
        
        # General keystroke quality indicators
        if keystroke_data.get('error_rate', 0) > 0.1:  # High error rate
            risk_score += 0.2
            description += " - High error rate detected"
            evidence['high_error_rate'] = True
        
        return RiskFactor(
            category=RiskCategory.BEHAVIORAL_RISK,
            name="keystroke_dynamics",
            score=min(1.0, risk_score),
            weight=0.15,
            confidence=0.7,
            description=description,
            evidence=evidence
        )
    
    def _analyze_access_patterns(self, user_profile: UserRiskProfile,
                               current_behavior: Dict[str, Any]) -> RiskFactor:
        """Analyze access pattern anomalies"""
        
        risk_score = 0.0
        evidence = {}
        description = "Access pattern analysis"
        
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Check typical access hours
        if (hasattr(user_profile, 'typical_access_hours') and 
            user_profile.typical_access_hours):
            if current_hour not in user_profile.typical_access_hours:
                risk_score += 0.3
                description += f" - Unusual access time: {current_hour}:00"
                evidence['unusual_access_time'] = current_hour
        
        # Check access frequency
        if current_behavior.get('session_count_today', 0) > 50:  # Excessive sessions
            risk_score += 0.2
            description += " - Excessive session count"
            evidence['excessive_sessions'] = True
        
        # Check rapid successive access
        last_access = current_behavior.get('last_access_time')
        if last_access:
            time_diff = (current_time - last_access).total_seconds()
            if time_diff < 30:  # Less than 30 seconds
                risk_score += 0.1
                description += " - Rapid successive access"
                evidence['rapid_access'] = time_diff
        
        return RiskFactor(
            category=RiskCategory.BEHAVIORAL_RISK,
            name="access_patterns",
            score=min(1.0, risk_score),
            weight=0.10,
            confidence=0.6,
            description=description,
            evidence=evidence
        )
    
    def _analyze_temporal_behavior(self, current_behavior: Dict[str, Any],
                                 user_profile: Optional[UserRiskProfile]) -> RiskFactor:
        """Analyze temporal behavior patterns"""
        
        risk_score = 0.0
        evidence = {}
        description = "Temporal behavior analysis"
        
        # Check for automation indicators
        if current_behavior.get('consistent_timing', False):
            risk_score += 0.3
            description += " - Automation-like timing patterns"
            evidence['automation_suspected'] = True
        
        # Check session duration anomalies
        session_duration = current_behavior.get('session_duration', 0)
        if session_duration < 60:  # Very short session
            risk_score += 0.1
            description += " - Unusually short session"
            evidence['short_session'] = session_duration
        elif session_duration > 28800:  # Over 8 hours
            risk_score += 0.2
            description += " - Unusually long session"
            evidence['long_session'] = session_duration
        
        return RiskFactor(
            category=RiskCategory.BEHAVIORAL_RISK,
            name="temporal_behavior",
            score=min(1.0, risk_score),
            weight=0.08,
            confidence=0.5,
            description=description,
            evidence=evidence
        )


class RiskScoringEngine:
    """Main risk scoring engine that combines all risk factors"""
    
    def __init__(self):
        self.geolocation_analyzer = GeolocationAnalyzer()
        self.device_analyzer = DeviceAnalyzer()
        self.biometric_analyzer = BiometricRiskAnalyzer()
        self.behavioral_analyzer = BehavioralAnalyzer()
        
        # Risk category weights
        self.category_weights = {
            RiskCategory.IDENTITY_RISK: 0.20,
            RiskCategory.BEHAVIORAL_RISK: 0.18,
            RiskCategory.CONTEXTUAL_RISK: 0.15,
            RiskCategory.TEMPORAL_RISK: 0.10,
            RiskCategory.DEVICE_RISK: 0.12,
            RiskCategory.LOCATION_RISK: 0.10,
            RiskCategory.BIOMETRIC_RISK: 0.25,
            RiskCategory.HISTORICAL_RISK: 0.15
        }
        
        # Policy thresholds
        self.policy_thresholds = {
            0.1: AuthenticationPolicy.ALLOW,
            0.3: AuthenticationPolicy.REQUIRE_ADDITIONAL_FACTOR,
            0.5: AuthenticationPolicy.STEP_UP_AUTHENTICATION,
            0.7: AuthenticationPolicy.REQUIRE_ADMIN_APPROVAL,
            0.9: AuthenticationPolicy.DENY_ACCESS,
            1.0: AuthenticationPolicy.QUARANTINE
        }
    
    def assess_comprehensive_risk(self, context: RiskContext,
                                user_profile: Optional[UserRiskProfile] = None) -> RiskAssessment:
        """Perform comprehensive risk assessment"""
        
        start_time = time.time()
        assessment_id = str(uuid.uuid4())
        
        all_risk_factors = []
        
        # Location risk analysis
        if context.ip_address:
            location_risk = self.geolocation_analyzer.analyze_location_risk(
                context.ip_address,
                user_profile.typical_locations if user_profile else None
            )
            all_risk_factors.append(location_risk)
        
        # Device risk analysis
        device_risk = self.device_analyzer.analyze_device_risk(
            context.device_id,
            context.user_agent,
            user_profile.typical_devices if user_profile else None
        )
        all_risk_factors.append(device_risk)
        
        # Biometric risk analysis
        for biometric_type, sample in context.biometric_samples.items():
            quality_score = context.quality_scores.get(biometric_type, 0.5)
            match_score = context.match_scores.get(biometric_type, 0.5)
            liveness_score = sample.get('liveness_score') if isinstance(sample, dict) else None
            
            biometric_risk = self.biometric_analyzer.analyze_biometric_risk(
                biometric_type, quality_score, match_score, sample, liveness_score
            )
            all_risk_factors.append(biometric_risk)
        
        # Behavioral risk analysis
        current_behavior = {
            'session_count_today': context.previous_attempts,
            'last_access_time': context.timestamp - timedelta(minutes=5),  # Mock
            'session_duration': 1800,  # Mock 30 minutes
        }
        
        # Add biometric behavioral data
        for biometric_type, sample in context.biometric_samples.items():
            if biometric_type in [BiometricType.BEHAVIORAL_KEYSTROKE, 
                                BiometricType.BEHAVIORAL_MOUSE, 
                                BiometricType.BEHAVIORAL_SIGNATURE]:
                if isinstance(sample, dict):
                    current_behavior[f'{biometric_type.name.lower()}_dynamics'] = sample
        
        behavioral_risks = self.behavioral_analyzer.analyze_behavioral_risk(
            user_profile, current_behavior
        )
        all_risk_factors.extend(behavioral_risks)
        
        # Historical risk analysis
        if user_profile:
            historical_risk = self._analyze_historical_risk(user_profile, context)
            all_risk_factors.append(historical_risk)
        
        # Authentication context risk
        auth_risk = self._analyze_authentication_context_risk(context)
        all_risk_factors.append(auth_risk)
        
        # Calculate category scores
        category_scores = self._calculate_category_scores(all_risk_factors)
        
        # Calculate total weighted risk score
        total_risk_score = self._calculate_total_risk_score(category_scores)
        
        # Determine risk severity
        risk_severity = self._determine_risk_severity(total_risk_score)
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(all_risk_factors)
        
        # Determine recommended policy
        recommended_policy = self._determine_authentication_policy(total_risk_score, context)
        
        # Generate recommendations
        required_actions, security_recommendations = self._generate_recommendations(
            total_risk_score, risk_severity, all_risk_factors, context
        )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        return RiskAssessment(
            assessment_id=assessment_id,
            timestamp=datetime.now(),
            context=context,
            total_risk_score=total_risk_score,
            risk_severity=risk_severity,
            confidence_level=confidence_level,
            risk_factors=all_risk_factors,
            category_scores=category_scores,
            recommended_policy=recommended_policy,
            required_actions=required_actions,
            security_recommendations=security_recommendations,
            assessment_duration_ms=processing_time,
            model_version="1.0.0",
            risk_model_confidence=confidence_level
        )
    
    def _analyze_historical_risk(self, user_profile: UserRiskProfile,
                               context: RiskContext) -> RiskFactor:
        """Analyze historical risk patterns"""
        
        risk_score = 0.0
        evidence = {}
        description = "Historical risk analysis"
        
        # Check authentication success rate
        if user_profile.authentication_success_rate < 0.8:
            risk_score += 0.2
            description += f" - Low success rate: {user_profile.authentication_success_rate:.2f}"
            evidence['low_success_rate'] = user_profile.authentication_success_rate
        
        # Check recent lockouts
        recent_lockouts = [
            lockout for lockout in user_profile.lockout_history
            if lockout > datetime.now() - timedelta(days=7)
        ]
        if len(recent_lockouts) > 2:
            risk_score += 0.3
            description += f" - Recent lockouts: {len(recent_lockouts)}"
            evidence['recent_lockouts'] = len(recent_lockouts)
        
        # Check security incidents
        if user_profile.security_incidents:
            recent_incidents = [
                incident for incident in user_profile.security_incidents
                if datetime.fromisoformat(incident['timestamp']) > datetime.now() - timedelta(days=30)
            ]
            if recent_incidents:
                risk_score += 0.4
                description += f" - Recent security incidents: {len(recent_incidents)}"
                evidence['security_incidents'] = len(recent_incidents)
        
        # Check trust score
        if user_profile.trust_score < 0.5:
            risk_score += 0.3
            description += f" - Low trust score: {user_profile.trust_score:.2f}"
            evidence['low_trust_score'] = user_profile.trust_score
        
        return RiskFactor(
            category=RiskCategory.HISTORICAL_RISK,
            name="historical_analysis",
            score=min(1.0, risk_score),
            weight=0.15,
            confidence=0.8,
            description=description,
            evidence=evidence
        )
    
    def _analyze_authentication_context_risk(self, context: RiskContext) -> RiskFactor:
        """Analyze authentication context risk"""
        
        risk_score = 0.0
        evidence = {}
        description = "Authentication context analysis"
        
        # Check previous failed attempts
        if context.previous_attempts > 3:
            risk_score += 0.4
            description += f" - Multiple failed attempts: {context.previous_attempts}"
            evidence['failed_attempts'] = context.previous_attempts
        
        # Check lockout count
        if context.lockout_count > 0:
            risk_score += 0.3
            description += f" - Previous lockouts: {context.lockout_count}"
            evidence['lockout_count'] = context.lockout_count
        
        # Check authentication method
        if context.authentication_method.lower() in ['basic', 'password_only']:
            risk_score += 0.2
            description += " - Weak authentication method"
            evidence['weak_auth_method'] = context.authentication_method
        
        # Check for security events
        if context.security_events:
            recent_events = len([
                event for event in context.security_events
                if datetime.fromisoformat(event.get('timestamp', '2000-01-01')) > 
                   datetime.now() - timedelta(hours=24)
            ])
            if recent_events > 0:
                risk_score += 0.2
                description += f" - Recent security events: {recent_events}"
                evidence['recent_security_events'] = recent_events
        
        return RiskFactor(
            category=RiskCategory.CONTEXTUAL_RISK,
            name="authentication_context",
            score=min(1.0, risk_score),
            weight=0.15,
            confidence=0.7,
            description=description,
            evidence=evidence
        )
    
    def _calculate_category_scores(self, risk_factors: List[RiskFactor]) -> Dict[RiskCategory, float]:
        """Calculate risk scores by category"""
        
        category_scores = defaultdict(list)
        
        # Group risk factors by category
        for factor in risk_factors:
            weighted_score = factor.score * factor.weight * factor.confidence
            category_scores[factor.category].append(weighted_score)
        
        # Calculate average score per category
        final_scores = {}
        for category, scores in category_scores.items():
            final_scores[category] = statistics.mean(scores) if scores else 0.0
        
        return final_scores
    
    def _calculate_total_risk_score(self, category_scores: Dict[RiskCategory, float]) -> float:
        """Calculate total weighted risk score"""
        
        total_score = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 0.1)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_risk_severity(self, total_risk_score: float) -> RiskSeverity:
        """Determine risk severity from total score"""
        
        for severity in RiskSeverity:
            if severity.min_score <= total_risk_score <= severity.max_score:
                return severity
        
        return RiskSeverity.EXTREME  # Default to highest risk
    
    def _calculate_confidence_level(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate overall confidence in risk assessment"""
        
        if not risk_factors:
            return 0.0
        
        confidence_scores = [factor.confidence for factor in risk_factors]
        return statistics.mean(confidence_scores)
    
    def _determine_authentication_policy(self, total_risk_score: float,
                                       context: RiskContext) -> AuthenticationPolicy:
        """Determine appropriate authentication policy"""
        
        # Find the appropriate policy based on thresholds
        for threshold in sorted(self.policy_thresholds.keys()):
            if total_risk_score <= threshold:
                return self.policy_thresholds[threshold]
        
        return AuthenticationPolicy.QUARANTINE  # Highest risk action
    
    def _generate_recommendations(self, total_risk_score: float,
                                risk_severity: RiskSeverity,
                                risk_factors: List[RiskFactor],
                                context: RiskContext) -> Tuple[List[str], List[str]]:
        """Generate required actions and security recommendations"""
        
        required_actions = []
        security_recommendations = []
        
        # General recommendations based on risk severity
        if risk_severity == RiskSeverity.EXTREME:
            required_actions.append("IMMEDIATE: Block access and investigate")
            required_actions.append("IMMEDIATE: Alert security team")
            security_recommendations.append("Conduct full security audit")
            
        elif risk_severity == RiskSeverity.CRITICAL:
            required_actions.append("Require administrator approval")
            required_actions.append("Implement additional monitoring")
            security_recommendations.append("Review user account for compromise")
            
        elif risk_severity == RiskSeverity.HIGH:
            required_actions.append("Require step-up authentication")
            required_actions.append("Increase session monitoring")
            security_recommendations.append("Verify user through alternative channel")
            
        elif risk_severity == RiskSeverity.MODERATE:
            required_actions.append("Require additional authentication factor")
            security_recommendations.append("Monitor session for anomalies")
            
        # Factor-specific recommendations
        for factor in risk_factors:
            if factor.score > 0.7:  # High-risk factors
                if factor.category == RiskCategory.LOCATION_RISK:
                    required_actions.append("Verify location through alternate method")
                    security_recommendations.append("Update trusted location list")
                    
                elif factor.category == RiskCategory.DEVICE_RISK:
                    required_actions.append("Device verification required")
                    security_recommendations.append("Register device if legitimate")
                    
                elif factor.category == RiskCategory.BIOMETRIC_RISK:
                    required_actions.append("Require alternative biometric")
                    security_recommendations.append("Check biometric sensor quality")
                    
                elif factor.category == RiskCategory.BEHAVIORAL_RISK:
                    required_actions.append("Behavioral verification required")
                    security_recommendations.append("Update behavioral baseline")
        
        return required_actions, security_recommendations


class RiskBasedScoringValidator(BaseBiometricValidator):
    """
    Risk-Based Scoring Validator for PyIDVerify
    
    Provides comprehensive risk assessment and adaptive scoring for biometric
    authentication based on multiple risk factors including behavioral patterns,
    contextual information, and historical data.
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.ENHANCED):
        super().__init__(validation_level)
        
        self.risk_engine = RiskScoringEngine()
        self.user_profiles: Dict[str, UserRiskProfile] = {}
        
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging for risk-based scoring"""
        self.logger = logging.getLogger(f"{__name__}.RiskBasedScoringValidator")
        self.logger.setLevel(logging.INFO)
    
    def assess_authentication_risk(self, user_id: Optional[str],
                                 session_id: str,
                                 biometric_data: Dict[BiometricType, Any],
                                 context_data: Dict[str, Any]) -> RiskAssessment:
        """
        Assess comprehensive authentication risk
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            biometric_data: Biometric samples and scores
            context_data: Environmental and contextual information
            
        Returns:
            RiskAssessment with comprehensive risk analysis
        """
        
        # Build risk context
        context = RiskContext(
            user_id=user_id,
            session_id=session_id,
            device_id=context_data.get('device_id'),
            ip_address=context_data.get('ip_address'),
            user_agent=context_data.get('user_agent'),
            location=context_data.get('location'),
            timestamp=datetime.now(),
            authentication_method=context_data.get('auth_method', 'biometric'),
            previous_attempts=context_data.get('previous_attempts', 0),
            lockout_count=context_data.get('lockout_count', 0),
            biometric_samples=biometric_data.get('samples', {}),
            quality_scores=biometric_data.get('quality_scores', {}),
            match_scores=biometric_data.get('match_scores', {}),
            threat_intelligence=context_data.get('threat_intel'),
            security_events=context_data.get('security_events', [])
        )
        
        # Get user profile
        user_profile = self.user_profiles.get(user_id) if user_id else None
        
        # Perform comprehensive risk assessment
        assessment = self.risk_engine.assess_comprehensive_risk(context, user_profile)
        
        # Log assessment
        self.logger.info(f"Risk assessment completed: session={session_id}, "
                        f"risk_score={assessment.total_risk_score:.3f}, "
                        f"severity={assessment.risk_severity}, "
                        f"policy={assessment.recommended_policy}")
        
        return assessment
    
    def create_user_risk_profile(self, user_id: str, 
                               historical_data: Dict[str, Any]) -> UserRiskProfile:
        """Create risk profile for a user"""
        
        profile = UserRiskProfile(
            user_id=user_id,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            typical_locations=historical_data.get('locations', []),
            typical_devices=historical_data.get('devices', []),
            typical_access_hours=historical_data.get('access_hours', []),
            typical_biometric_quality=historical_data.get('biometric_quality', {}),
            risk_history=historical_data.get('risk_scores', []),
            authentication_success_rate=historical_data.get('success_rate', 0.9),
            anomaly_frequency=historical_data.get('anomaly_frequency', 0.1),
            security_incidents=historical_data.get('security_incidents', []),
            lockout_history=historical_data.get('lockout_history', []),
            trust_score=historical_data.get('trust_score', 0.8),
            reliability_index=historical_data.get('reliability_index', 0.7)
        )
        
        self.user_profiles[user_id] = profile
        
        self.logger.info(f"Created risk profile for user: {user_id}")
        return profile
    
    def update_user_risk_profile(self, user_id: str, 
                               new_data: Dict[str, Any]) -> Optional[UserRiskProfile]:
        """Update existing user risk profile"""
        
        if user_id not in self.user_profiles:
            return None
        
        profile = self.user_profiles[user_id]
        profile.last_updated = datetime.now()
        
        # Update various profile fields
        if 'locations' in new_data:
            profile.typical_locations = list(set(profile.typical_locations + new_data['locations']))
        
        if 'devices' in new_data:
            profile.typical_devices = list(set(profile.typical_devices + new_data['devices']))
        
        if 'access_hours' in new_data:
            profile.typical_access_hours = list(set(profile.typical_access_hours + new_data['access_hours']))
        
        if 'risk_score' in new_data:
            profile.risk_history.append(new_data['risk_score'])
            # Keep only last 100 scores
            profile.risk_history = profile.risk_history[-100:]
        
        if 'success_rate' in new_data:
            # Update with weighted average
            profile.authentication_success_rate = (
                profile.authentication_success_rate * 0.8 + new_data['success_rate'] * 0.2
            )
        
        if 'security_incident' in new_data:
            profile.security_incidents.append(new_data['security_incident'])
        
        if 'lockout' in new_data:
            profile.lockout_history.append(datetime.now())
        
        self.logger.info(f"Updated risk profile for user: {user_id}")
        return profile
    
    def get_risk_threshold_recommendations(self, risk_score: float) -> Dict[str, Any]:
        """Get recommendations based on risk score thresholds"""
        
        recommendations = {
            'authentication_policy': AuthenticationPolicy.ALLOW,
            'additional_factors_required': [],
            'monitoring_level': 'standard',
            'session_restrictions': [],
            'administrative_actions': []
        }
        
        if risk_score >= 0.9:
            recommendations.update({
                'authentication_policy': AuthenticationPolicy.QUARANTINE,
                'additional_factors_required': ['admin_approval', 'phone_verification'],
                'monitoring_level': 'critical',
                'session_restrictions': ['block_access', 'immediate_investigation'],
                'administrative_actions': ['security_alert', 'account_review']
            })
        elif risk_score >= 0.7:
            recommendations.update({
                'authentication_policy': AuthenticationPolicy.REQUIRE_ADMIN_APPROVAL,
                'additional_factors_required': ['phone_verification', 'email_confirmation'],
                'monitoring_level': 'high',
                'session_restrictions': ['limited_access', 'enhanced_logging'],
                'administrative_actions': ['security_review']
            })
        elif risk_score >= 0.5:
            recommendations.update({
                'authentication_policy': AuthenticationPolicy.STEP_UP_AUTHENTICATION,
                'additional_factors_required': ['sms_code', 'email_token'],
                'monitoring_level': 'elevated',
                'session_restrictions': ['time_limited', 'activity_monitoring'],
                'administrative_actions': []
            })
        elif risk_score >= 0.3:
            recommendations.update({
                'authentication_policy': AuthenticationPolicy.REQUIRE_ADDITIONAL_FACTOR,
                'additional_factors_required': ['totp_code'],
                'monitoring_level': 'standard',
                'session_restrictions': ['standard_monitoring'],
                'administrative_actions': []
            })
        
        return recommendations
    
    # Override base class methods
    
    def validate(self, data: Any, reference_template: Optional[Any] = None, 
                validation_level: Optional[ValidationLevel] = None) -> BiometricValidationResult:
        """
        Validate with comprehensive risk scoring
        
        Args:
            data: Dictionary containing biometric data and context information
            reference_template: User templates and profiles
            validation_level: Override validation level
            
        Returns:
            BiometricValidationResult with risk assessment integrated
        """
        
        if not isinstance(data, dict):
            raise ValidationError("Data must be dictionary with biometric_data and context_data")
        
        # Extract components
        biometric_data = data.get('biometric_data', {})
        context_data = data.get('context_data', {})
        user_id = context_data.get('user_id')
        session_id = context_data.get('session_id', str(uuid.uuid4()))
        
        # Perform risk assessment
        risk_assessment = self.assess_authentication_risk(
            user_id, session_id, biometric_data, context_data
        )
        
        # Determine validation result based on risk
        is_valid = (risk_assessment.recommended_policy in [
            AuthenticationPolicy.ALLOW,
            AuthenticationPolicy.REQUIRE_ADDITIONAL_FACTOR
        ])
        
        confidence_score = max(0.0, 1.0 - risk_assessment.total_risk_score)
        
        return BiometricValidationResult(
            is_valid=is_valid,
            confidence_score=confidence_score,
            biometric_type=BiometricType.RISK_ASSESSMENT,
            quality_score=1.0 - risk_assessment.total_risk_score,
            match_score=confidence_score,
            liveness_score=1.0,  # Risk assessment doesn't directly assess liveness
            validation_level=validation_level or self.validation_level,
            metadata={
                'risk_assessment': asdict(risk_assessment),
                'policy_recommendation': risk_assessment.recommended_policy,
                'risk_severity': risk_assessment.risk_severity,
                'required_actions': risk_assessment.required_actions,
                'security_recommendations': risk_assessment.security_recommendations,
                'total_risk_score': risk_assessment.total_risk_score,
                'confidence_level': risk_assessment.confidence_level
            }
        )
    
    def extract_features(self, data: Any) -> Dict[str, Any]:
        """Extract risk-relevant features"""
        return {
            'risk_features': {},
            'contextual_features': {},
            'behavioral_patterns': {}
        }
    
    def create_template(self, data: Any) -> Dict[str, Any]:
        """Create risk-based template (user profile)"""
        return {
            'template_type': 'risk_profile',
            'creation_timestamp': datetime.now().isoformat(),
            'profile_data': {},
            'risk_baselines': {}
        }
    
    def match_templates(self, template1: Dict[str, Any], template2: Dict[str, Any]) -> float:
        """Match risk profiles"""
        return 0.5  # Risk profiles use different comparison methods
    
    def assess_quality(self, data: Any) -> float:
        """Assess quality of risk assessment data"""
        if isinstance(data, dict):
            completeness = len(data.get('biometric_data', {})) / 10.0  # Normalize
            context_completeness = len(data.get('context_data', {})) / 15.0
            return min(1.0, (completeness + context_completeness) / 2.0)
        return 0.0
    
    def detect_liveness(self, data: Any) -> float:
        """Risk assessment inherently detects suspicious behavior"""
        if isinstance(data, dict):
            risk_indicators = data.get('context_data', {}).get('risk_indicators', [])
            return max(0.0, 1.0 - len(risk_indicators) / 10.0)
        return 1.0
    
    # Implement abstract methods from BaseBiometricValidator
    
    def _preprocess_biometric_data(self, raw_data: Union[bytes, Any]) -> Union[bytes, Any]:
        """Preprocess data for risk-based assessment"""
        if isinstance(raw_data, dict):
            processed_data = {}
            for key, value in raw_data.items():
                if isinstance(value, str):
                    processed_data[key] = value.strip().lower()
                elif isinstance(value, (int, float)):
                    processed_data[key] = value
                elif isinstance(value, dict):
                    processed_data[key] = self._preprocess_biometric_data(value)
                else:
                    processed_data[key] = value
            return processed_data
        return raw_data
    
    def _extract_biometric_features(self, preprocessed_data: Union[bytes, Any]) -> Dict[str, Any]:
        """Extract features for risk assessment"""
        features = {}
        
        if isinstance(preprocessed_data, dict):
            # Extract context features
            if 'context_data' in preprocessed_data:
                context = preprocessed_data['context_data']
                features['context_features'] = self._extract_context_features(context)
            
            # Extract biometric data features
            if 'biometric_data' in preprocessed_data:
                bio_data = preprocessed_data['biometric_data']
                features['biometric_features'] = self._extract_biometric_risk_features(bio_data)
            
            # Extract temporal features
            if 'timestamp' in preprocessed_data:
                features['temporal_features'] = self._extract_temporal_features(preprocessed_data['timestamp'])
        
        return features
    
    def _extract_context_features(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context-based risk features"""
        features = {}
        
        # Device features
        if 'device_info' in context_data:
            device = context_data['device_info']
            features['device_type'] = device.get('type', 'unknown')
            features['device_os'] = device.get('os', 'unknown')
            features['device_browser'] = device.get('browser', 'unknown')
        
        # Location features
        if 'location' in context_data:
            location = context_data['location']
            features['country'] = location.get('country', 'unknown')
            features['city'] = location.get('city', 'unknown')
            features['coordinates'] = location.get('coordinates', [0, 0])
        
        # Network features
        if 'network' in context_data:
            network = context_data['network']
            features['ip_address'] = network.get('ip_address', '')
            features['isp'] = network.get('isp', 'unknown')
            features['is_vpn'] = network.get('is_vpn', False)
        
        return features
    
    def _extract_biometric_risk_features(self, biometric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract biometric risk assessment features"""
        features = {}
        
        # Quality indicators
        quality_scores = []
        for bio_type, data in biometric_data.items():
            if isinstance(data, dict) and 'quality_score' in data:
                quality_scores.append(data['quality_score'])
        
        features['average_quality'] = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        features['min_quality'] = min(quality_scores) if quality_scores else 0
        features['quality_variance'] = sum((x - features['average_quality'])**2 for x in quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Template matching scores
        match_scores = []
        for bio_type, data in biometric_data.items():
            if isinstance(data, dict) and 'match_score' in data:
                match_scores.append(data['match_score'])
        
        features['average_match'] = sum(match_scores) / len(match_scores) if match_scores else 0
        features['min_match'] = min(match_scores) if match_scores else 0
        
        return features
    
    def _extract_temporal_features(self, timestamp: float) -> Dict[str, Any]:
        """Extract temporal risk features"""
        import datetime
        
        dt = datetime.datetime.fromtimestamp(timestamp)
        
        return {
            'hour_of_day': dt.hour,
            'day_of_week': dt.weekday(),
            'is_weekend': dt.weekday() >= 5,
            'is_night': dt.hour < 6 or dt.hour > 22
        }
    
    def _assess_biometric_quality(self, raw_data: Union[bytes, Any]) -> float:
        """Assess quality of data for risk assessment"""
        if not isinstance(raw_data, dict):
            return 0.3  # Low quality for non-dict data
        
        quality_factors = []
        
        # Assess context data completeness
        if 'context_data' in raw_data:
            context = raw_data['context_data']
            expected_context = ['device_info', 'location', 'network', 'timestamp']
            context_completeness = sum(1 for field in expected_context if field in context) / len(expected_context)
            quality_factors.append(context_completeness)
        
        # Assess biometric data quality
        if 'biometric_data' in raw_data:
            bio_data = raw_data['biometric_data']
            if isinstance(bio_data, dict):
                bio_quality_scores = []
                for bio_type, data in bio_data.items():
                    if isinstance(data, dict) and 'quality_score' in data:
                        bio_quality_scores.append(data['quality_score'])
                
                if bio_quality_scores:
                    avg_bio_quality = sum(bio_quality_scores) / len(bio_quality_scores)
                    quality_factors.append(avg_bio_quality)
        
        # Assess data freshness
        if 'timestamp' in raw_data:
            import time
            current_time = time.time()
            data_age = current_time - raw_data['timestamp']
            freshness = max(0.0, 1.0 - data_age / 3600)  # Decay over 1 hour
            quality_factors.append(freshness)
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.3


# Export main classes
__all__ = [
    'RiskBasedScoringValidator',
    'RiskCategory',
    'RiskSeverity',
    'AuthenticationPolicy',
    'RiskContext',
    'RiskAssessment',
    'UserRiskProfile',
    'RiskFactor'
]
