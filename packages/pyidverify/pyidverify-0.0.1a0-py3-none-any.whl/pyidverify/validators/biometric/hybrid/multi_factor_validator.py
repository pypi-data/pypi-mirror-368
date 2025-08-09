"""
Multi-Factor Biometric Validator for PyIDVerify

This module provides comprehensive multi-factor biometric authentication combining
multiple biometric modalities for enhanced security and accuracy. Implements advanced
fusion algorithms, risk assessment, and adaptive authentication strategies.

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
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Union, Set, Callable
from threading import Lock
import hashlib
import uuid

from pyidverify.core.types import ValidationLevel, BiometricType, IDType, ValidationStatus, ValidationMetadata
from pyidverify.core.exceptions import PyIDVerifyError, ValidationError
from pyidverify.validators.biometric import BaseBiometricValidator, BiometricValidationResult, BaseValidator, ValidationResult


class FusionStrategy(Enum):
    """Biometric fusion strategies for multi-factor authentication"""
    SCORE_LEVEL = auto()           # Combine similarity scores
    RANK_LEVEL = auto()            # Combine ranking information  
    DECISION_LEVEL = auto()        # Combine binary decisions
    FEATURE_LEVEL = auto()         # Combine feature vectors
    WEIGHTED_MAJORITY = auto()     # Weighted voting system
    BAYESIAN_FUSION = auto()       # Bayesian probability fusion
    NEURAL_FUSION = auto()         # Neural network based fusion
    ADAPTIVE_FUSION = auto()       # Context-adaptive fusion


class AuthenticationMode(Enum):
    """Authentication modes for different security requirements"""
    STANDARD = auto()              # Normal security level
    HIGH_SECURITY = auto()         # Enhanced security requirements
    CONTINUOUS = auto()            # Continuous authentication
    STEP_UP = auto()              # Progressive authentication
    EMERGENCY = auto()             # Emergency access mode
    DEGRADED = auto()             # Fallback mode with reduced modalities


class BiometricWeight(Enum):
    """Weight assignments for different biometric modalities"""
    FINGERPRINT = 0.35
    FACIAL = 0.25
    VOICE = 0.15
    IRIS = 0.40
    KEYSTROKE = 0.10
    MOUSE = 0.05
    SIGNATURE = 0.20
    PALM = 0.30


class RiskLevel(Enum):
    """Risk assessment levels"""
    VERY_LOW = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()
    CRITICAL = auto()


@dataclass
class BiometricModality:
    """Individual biometric modality configuration"""
    biometric_type: BiometricType
    validator: BaseBiometricValidator
    weight: float
    threshold: float
    required: bool = False
    fallback_allowed: bool = True
    max_attempts: int = 3
    timeout_seconds: int = 30
    quality_threshold: float = 0.7


@dataclass
class AuthenticationContext:
    """Context information for authentication session"""
    session_id: str
    user_id: Optional[str]
    device_id: Optional[str]
    location: Optional[str]
    timestamp: datetime
    authentication_mode: AuthenticationMode
    risk_factors: Dict[str, Any]
    previous_attempts: int = 0
    lockout_until: Optional[datetime] = None


@dataclass
class FusionResult:
    """Result of biometric fusion process"""
    final_score: float
    confidence_level: float
    contributing_modalities: Set[BiometricType]
    individual_scores: Dict[BiometricType, float]
    fusion_strategy_used: FusionStrategy
    risk_assessment: RiskLevel
    authentication_strength: float
    decision_reasoning: List[str]


@dataclass
class ContinuousAuthState:
    """State tracking for continuous authentication"""
    session_id: str
    user_profile: Dict[BiometricType, Any]
    baseline_established: bool
    last_verification: datetime
    verification_interval: timedelta
    anomaly_score: float
    trust_level: float
    degradation_events: List[Dict[str, Any]]


class MultiFusionEngine:
    """Advanced fusion engine for combining biometric results"""
    
    def __init__(self):
        self.fusion_models = {}
        self.calibration_data = {}
        self.performance_metrics = {}
        
    def score_level_fusion(self, scores: Dict[BiometricType, float], 
                          weights: Dict[BiometricType, float]) -> float:
        """Weighted score level fusion"""
        if not scores or not weights:
            return 0.0
            
        total_weight = 0.0
        weighted_sum = 0.0
        
        for bio_type, score in scores.items():
            if bio_type in weights:
                weight = weights[bio_type]
                weighted_sum += score * weight
                total_weight += weight
                
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def bayesian_fusion(self, scores: Dict[BiometricType, float],
                       priors: Dict[BiometricType, float]) -> float:
        """Bayesian fusion of biometric scores"""
        if not scores or not priors:
            return 0.0
            
        # Calculate likelihood for each modality
        likelihoods = {}
        for bio_type, score in scores.items():
            if bio_type in priors:
                # Convert score to likelihood using beta distribution
                alpha = score * 10 + 1
                beta = (1 - score) * 10 + 1
                likelihood = (alpha / (alpha + beta))
                likelihoods[bio_type] = likelihood * priors[bio_type]
        
        # Normalize probabilities
        total_likelihood = sum(likelihoods.values())
        if total_likelihood == 0:
            return 0.0
            
        return min(1.0, total_likelihood / len(likelihoods))
    
    def adaptive_fusion(self, scores: Dict[BiometricType, float],
                       context: AuthenticationContext,
                       historical_performance: Dict[BiometricType, float]) -> Tuple[float, str]:
        """Adaptive fusion based on context and historical performance"""
        
        # Adjust weights based on context
        adaptive_weights = self._calculate_adaptive_weights(context, historical_performance)
        
        # Select fusion strategy based on context
        if context.authentication_mode == AuthenticationMode.HIGH_SECURITY:
            strategy = "conservative_fusion"
            # Use more conservative thresholds
            fused_score = self.score_level_fusion(scores, adaptive_weights) * 0.9
        elif context.authentication_mode == AuthenticationMode.CONTINUOUS:
            strategy = "temporal_fusion"
            # Consider temporal consistency
            fused_score = self._temporal_consistency_fusion(scores, adaptive_weights, context)
        else:
            strategy = "standard_fusion"
            fused_score = self.score_level_fusion(scores, adaptive_weights)
            
        return fused_score, strategy
    
    def _calculate_adaptive_weights(self, context: AuthenticationContext,
                                  historical_performance: Dict[BiometricType, float]) -> Dict[BiometricType, float]:
        """Calculate adaptive weights based on context and performance"""
        base_weights = {
            BiometricType.FINGERPRINT: BiometricWeight.FINGERPRINT.value,
            BiometricType.FACIAL: BiometricWeight.FACIAL.value,
            BiometricType.VOICE: BiometricWeight.VOICE.value,
            BiometricType.IRIS: BiometricWeight.IRIS.value,
            BiometricType.BEHAVIORAL_KEYSTROKE: BiometricWeight.KEYSTROKE.value,
            BiometricType.BEHAVIORAL_MOUSE: BiometricWeight.MOUSE.value,
            BiometricType.BEHAVIORAL_SIGNATURE: BiometricWeight.SIGNATURE.value
        }
        
        # Adjust based on historical performance
        for bio_type, performance in historical_performance.items():
            if bio_type in base_weights:
                # Boost weights for well-performing modalities
                adjustment = (performance - 0.5) * 0.2
                base_weights[bio_type] = max(0.1, min(0.8, base_weights[bio_type] + adjustment))
        
        # Context-based adjustments
        if context.authentication_mode == AuthenticationMode.HIGH_SECURITY:
            # Prefer more reliable modalities
            base_weights[BiometricType.FINGERPRINT] *= 1.2
            base_weights[BiometricType.IRIS] *= 1.3
        
        # Normalize weights
        total_weight = sum(base_weights.values())
        return {k: v / total_weight for k, v in base_weights.items()}
    
    def _temporal_consistency_fusion(self, scores: Dict[BiometricType, float],
                                   weights: Dict[BiometricType, float],
                                   context: AuthenticationContext) -> float:
        """Fusion considering temporal consistency"""
        base_score = self.score_level_fusion(scores, weights)
        
        # Apply temporal consistency bonus/penalty
        consistency_factor = 1.0
        
        # Check for unusual patterns in risk factors
        if context.risk_factors.get('location_change', False):
            consistency_factor *= 0.95
        if context.risk_factors.get('device_change', False):
            consistency_factor *= 0.90
        if context.risk_factors.get('time_anomaly', False):
            consistency_factor *= 0.85
            
        return base_score * consistency_factor


class RiskAssessmentEngine:
    """Advanced risk assessment for multi-factor authentication"""
    
    def __init__(self):
        self.risk_models = {}
        self.anomaly_detectors = {}
        self.threat_intelligence = {}
        
    def assess_authentication_risk(self, context: AuthenticationContext,
                                 biometric_results: Dict[BiometricType, BiometricValidationResult],
                                 user_profile: Dict[str, Any]) -> Tuple[RiskLevel, Dict[str, Any]]:
        """Comprehensive risk assessment for authentication attempt"""
        
        risk_factors = {}
        risk_score = 0.0
        
        # Biometric quality assessment
        quality_risk = self._assess_biometric_quality_risk(biometric_results)
        risk_factors['biometric_quality'] = quality_risk
        risk_score += quality_risk * 0.3
        
        # Context anomaly assessment
        context_risk = self._assess_context_anomalies(context, user_profile)
        risk_factors['context_anomalies'] = context_risk
        risk_score += context_risk * 0.25
        
        # Behavioral pattern assessment
        behavioral_risk = self._assess_behavioral_patterns(context, biometric_results)
        risk_factors['behavioral_patterns'] = behavioral_risk
        risk_score += behavioral_risk * 0.20
        
        # Device and location assessment
        device_risk = self._assess_device_location_risk(context, user_profile)
        risk_factors['device_location'] = device_risk
        risk_score += device_risk * 0.15
        
        # Temporal pattern assessment
        temporal_risk = self._assess_temporal_patterns(context, user_profile)
        risk_factors['temporal_patterns'] = temporal_risk
        risk_score += temporal_risk * 0.10
        
        # Determine risk level
        risk_level = self._calculate_risk_level(risk_score)
        
        return risk_level, risk_factors
    
    def _assess_biometric_quality_risk(self, results: Dict[BiometricType, BiometricValidationResult]) -> float:
        """Assess risk based on biometric sample quality"""
        if not results:
            return 1.0  # Maximum risk for no biometric data
            
        quality_scores = []
        for bio_type, result in results.items():
            if hasattr(result, 'quality_score'):
                quality_scores.append(result.quality_score)
            else:
                quality_scores.append(0.5)  # Default medium quality
                
        avg_quality = sum(quality_scores) / len(quality_scores)
        return max(0.0, 1.0 - avg_quality)  # Inverse of quality
    
    def _assess_context_anomalies(self, context: AuthenticationContext, 
                                user_profile: Dict[str, Any]) -> float:
        """Assess risk based on contextual anomalies"""
        risk = 0.0
        
        # Check for location anomalies
        if context.location:
            known_locations = user_profile.get('known_locations', [])
            if context.location not in known_locations:
                risk += 0.3
                
        # Check for time anomalies
        current_hour = context.timestamp.hour
        typical_hours = user_profile.get('typical_access_hours', [])
        if typical_hours and current_hour not in typical_hours:
            risk += 0.2
            
        # Check for device anomalies
        if context.device_id:
            known_devices = user_profile.get('known_devices', [])
            if context.device_id not in known_devices:
                risk += 0.4
                
        return min(1.0, risk)
    
    def _assess_behavioral_patterns(self, context: AuthenticationContext,
                                  results: Dict[BiometricType, BiometricValidationResult]) -> float:
        """Assess risk based on behavioral biometric patterns"""
        risk = 0.0
        
        # Check behavioral biometric anomalies
        behavioral_types = {
            BiometricType.BEHAVIORAL_KEYSTROKE,
            BiometricType.BEHAVIORAL_MOUSE,
            BiometricType.BEHAVIORAL_SIGNATURE
        }
        
        for bio_type in behavioral_types:
            if bio_type in results:
                result = results[bio_type]
                if hasattr(result, 'anomaly_score'):
                    risk += result.anomaly_score * 0.2
                    
        return min(1.0, risk)
    
    def _assess_device_location_risk(self, context: AuthenticationContext,
                                   user_profile: Dict[str, Any]) -> float:
        """Assess device and location based risk"""
        risk = 0.0
        
        # Device reputation
        if context.device_id:
            device_reputation = user_profile.get('device_reputation', {}).get(context.device_id, 0.5)
            risk += (1.0 - device_reputation) * 0.5
            
        # Location risk
        if context.location:
            location_risk = user_profile.get('location_risk', {}).get(context.location, 0.0)
            risk += location_risk * 0.5
            
        return min(1.0, risk)
    
    def _assess_temporal_patterns(self, context: AuthenticationContext,
                                user_profile: Dict[str, Any]) -> float:
        """Assess temporal pattern based risk"""
        risk = 0.0
        
        # Check for rapid successive attempts
        if context.previous_attempts > 2:
            risk += 0.4
            
        # Check for lockout violations
        if context.lockout_until and context.timestamp < context.lockout_until:
            risk += 0.8
            
        return min(1.0, risk)
    
    def _calculate_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if risk_score <= 0.1:
            return RiskLevel.VERY_LOW
        elif risk_score <= 0.3:
            return RiskLevel.LOW
        elif risk_score <= 0.5:
            return RiskLevel.MEDIUM
        elif risk_score <= 0.7:
            return RiskLevel.HIGH
        elif risk_score <= 0.9:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.CRITICAL


class ContinuousAuthenticationEngine:
    """Engine for continuous authentication and monitoring"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ContinuousAuthState] = {}
        self.session_lock = Lock()
        self.monitoring_active = True
        
    async def start_continuous_monitoring(self, session_id: str, 
                                        initial_profile: Dict[BiometricType, Any],
                                        verification_interval: timedelta = timedelta(minutes=5)) -> None:
        """Start continuous authentication monitoring for a session"""
        
        with self.session_lock:
            auth_state = ContinuousAuthState(
                session_id=session_id,
                user_profile=initial_profile,
                baseline_established=True,
                last_verification=datetime.now(),
                verification_interval=verification_interval,
                anomaly_score=0.0,
                trust_level=1.0,
                degradation_events=[]
            )
            self.active_sessions[session_id] = auth_state
            
        # Start background monitoring
        asyncio.create_task(self._monitor_session(session_id))
    
    async def _monitor_session(self, session_id: str) -> None:
        """Background monitoring of authentication session"""
        
        while self.monitoring_active and session_id in self.active_sessions:
            try:
                auth_state = self.active_sessions[session_id]
                current_time = datetime.now()
                
                # Check if verification is due
                if current_time - auth_state.last_verification >= auth_state.verification_interval:
                    await self._perform_background_verification(session_id)
                    
                # Check for anomalies in session behavior
                await self._check_session_anomalies(session_id)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logging.error(f"Error in continuous monitoring for session {session_id}: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _perform_background_verification(self, session_id: str) -> None:
        """Perform background biometric verification"""
        
        if session_id not in self.active_sessions:
            return
            
        auth_state = self.active_sessions[session_id]
        
        # Collect passive biometric samples (e.g., keystroke, mouse patterns)
        passive_samples = await self._collect_passive_biometrics(session_id)
        
        if passive_samples:
            # Compare against user profile
            anomaly_score = await self._calculate_session_anomaly(passive_samples, auth_state.user_profile)
            
            # Update authentication state
            auth_state.anomaly_score = anomaly_score
            auth_state.last_verification = datetime.now()
            
            # Adjust trust level based on anomaly score
            trust_adjustment = (1.0 - anomaly_score) * 0.1
            auth_state.trust_level = max(0.0, min(1.0, auth_state.trust_level + trust_adjustment - 0.05))
            
            # Log significant anomalies
            if anomaly_score > 0.7:
                auth_state.degradation_events.append({
                    'timestamp': datetime.now().isoformat(),
                    'anomaly_score': anomaly_score,
                    'trust_level': auth_state.trust_level,
                    'event_type': 'high_anomaly_detected'
                })
    
    async def _collect_passive_biometrics(self, session_id: str) -> Dict[BiometricType, Any]:
        """Collect passive biometric samples during session"""
        # This would interface with actual biometric collectors
        # For now, return mock data structure
        return {
            BiometricType.BEHAVIORAL_KEYSTROKE: {'typing_rhythm': [], 'dwell_times': []},
            BiometricType.BEHAVIORAL_MOUSE: {'movement_patterns': [], 'click_intervals': []}
        }
    
    async def _calculate_session_anomaly(self, samples: Dict[BiometricType, Any],
                                       baseline_profile: Dict[BiometricType, Any]) -> float:
        """Calculate anomaly score for session samples"""
        if not samples or not baseline_profile:
            return 0.5  # Default medium anomaly
            
        anomaly_scores = []
        
        for bio_type, sample_data in samples.items():
            if bio_type in baseline_profile:
                baseline_data = baseline_profile[bio_type]
                # Calculate similarity/anomaly (simplified)
                anomaly = await self._compare_biometric_patterns(sample_data, baseline_data)
                anomaly_scores.append(anomaly)
        
        return sum(anomaly_scores) / len(anomaly_scores) if anomaly_scores else 0.5
    
    async def _compare_biometric_patterns(self, sample: Any, baseline: Any) -> float:
        """Compare biometric patterns to detect anomalies"""
        # Simplified anomaly detection - in real implementation would use
        # sophisticated pattern matching algorithms
        return 0.2  # Low anomaly for mock implementation
    
    async def _check_session_anomalies(self, session_id: str) -> None:
        """Check for session-level anomalies"""
        if session_id not in self.active_sessions:
            return
            
        auth_state = self.active_sessions[session_id]
        
        # Check trust level degradation
        if auth_state.trust_level < 0.3:
            # Trigger re-authentication
            await self._trigger_step_up_authentication(session_id)
    
    async def _trigger_step_up_authentication(self, session_id: str) -> None:
        """Trigger step-up authentication for degraded session"""
        logging.warning(f"Triggering step-up authentication for session: {session_id}")
        
        # In real implementation, would notify the application to request
        # additional authentication from the user
        if session_id in self.active_sessions:
            auth_state = self.active_sessions[session_id]
            auth_state.degradation_events.append({
                'timestamp': datetime.now().isoformat(),
                'event_type': 'step_up_authentication_triggered',
                'trust_level': auth_state.trust_level,
                'reason': 'trust_level_degradation'
            })


class MultiFactorBiometricValidator(BaseBiometricValidator):
    """
    Advanced Multi-Factor Biometric Validator
    
    Provides comprehensive multi-modal biometric authentication with:
    - Multiple fusion strategies
    - Risk-based authentication
    - Continuous authentication monitoring
    - Adaptive security policies
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.ENHANCED):
        super().__init__(validation_level)
        
        self.fusion_engine = MultiFusionEngine()
        self.risk_engine = RiskAssessmentEngine()
        self.continuous_engine = ContinuousAuthenticationEngine()
        
        self.registered_modalities: Dict[BiometricType, BiometricModality] = {}
        self.authentication_policies: Dict[AuthenticationMode, Dict[str, Any]] = {}
        self.performance_metrics: Dict[str, Any] = {}
        
        self._initialize_default_policies()
        self._setup_logging()
    
    def _initialize_default_policies(self) -> None:
        """Initialize default authentication policies"""
        
        self.authentication_policies = {
            AuthenticationMode.STANDARD: {
                'min_modalities': 2,
                'min_score_threshold': 0.7,
                'required_modalities': {BiometricType.FINGERPRINT},
                'risk_tolerance': RiskLevel.MEDIUM,
                'fusion_strategy': FusionStrategy.WEIGHTED_MAJORITY
            },
            AuthenticationMode.HIGH_SECURITY: {
                'min_modalities': 3,
                'min_score_threshold': 0.85,
                'required_modalities': {BiometricType.FINGERPRINT, BiometricType.FACIAL},
                'risk_tolerance': RiskLevel.LOW,
                'fusion_strategy': FusionStrategy.BAYESIAN_FUSION
            },
            AuthenticationMode.CONTINUOUS: {
                'min_modalities': 1,
                'min_score_threshold': 0.6,
                'required_modalities': set(),
                'risk_tolerance': RiskLevel.MEDIUM,
                'fusion_strategy': FusionStrategy.ADAPTIVE_FUSION,
                'monitoring_interval': timedelta(minutes=3)
            },
            AuthenticationMode.STEP_UP: {
                'min_modalities': 2,
                'min_score_threshold': 0.8,
                'required_modalities': {BiometricType.IRIS},
                'risk_tolerance': RiskLevel.LOW,
                'fusion_strategy': FusionStrategy.NEURAL_FUSION
            }
        }
    
    def _setup_logging(self) -> None:
        """Setup logging for multi-factor authentication"""
        self.logger = logging.getLogger(f"{__name__}.MultiFactorBiometricValidator")
        self.logger.setLevel(logging.INFO)
    
    def register_biometric_modality(self, modality: BiometricModality) -> None:
        """Register a biometric modality for multi-factor authentication"""
        
        if not isinstance(modality.validator, BaseBiometricValidator):
            raise ValidationError(f"Invalid validator type for {modality.biometric_type}")
            
        self.registered_modalities[modality.biometric_type] = modality
        self.logger.info(f"Registered biometric modality: {modality.biometric_type}")
    
    async def validate_multi_factor(self, 
                                  biometric_samples: Dict[BiometricType, Any],
                                  context: AuthenticationContext,
                                  user_templates: Optional[Dict[BiometricType, Any]] = None) -> BiometricValidationResult:
        """
        Perform multi-factor biometric authentication
        
        Args:
            biometric_samples: Dictionary of biometric samples by type
            context: Authentication context information
            user_templates: Pre-enrolled user biometric templates
            
        Returns:
            BiometricValidationResult with fusion results and risk assessment
        """
        
        start_time = time.time()
        session_id = context.session_id
        
        try:
            # Validate input parameters
            if not biometric_samples:
                raise ValidationError("No biometric samples provided")
                
            # Get authentication policy for current mode
            policy = self.authentication_policies.get(context.authentication_mode, 
                                                    self.authentication_policies[AuthenticationMode.STANDARD])
            
            # Check minimum modality requirements
            available_modalities = set(biometric_samples.keys()) & set(self.registered_modalities.keys())
            
            if len(available_modalities) < policy['min_modalities']:
                raise ValidationError(f"Insufficient biometric modalities. Required: {policy['min_modalities']}, "
                                    f"Provided: {len(available_modalities)}")
            
            # Check required modalities
            required_modalities = policy.get('required_modalities', set())
            missing_required = required_modalities - available_modalities
            if missing_required:
                raise ValidationError(f"Missing required biometric modalities: {missing_required}")
            
            # Perform individual biometric validations in parallel
            individual_results = await self._validate_individual_modalities(
                biometric_samples, user_templates, available_modalities
            )
            
            # Perform risk assessment
            risk_level, risk_factors = self.risk_engine.assess_authentication_risk(
                context, individual_results, {}  # User profile would be loaded from DB
            )
            
            # Check if risk level is acceptable
            if risk_level.value > policy['risk_tolerance'].value:
                return BiometricValidationResult(
                    is_valid=False,
                    id_type=IDType.NATIONAL_ID,
                    original_value="multi_modal_sample",
                    normalized_value="multi_modal_sample", 
                    status=ValidationStatus.INVALID,
                    confidence_score=0.0,
                    risk_score=1.0,
                    biometric_type=BiometricType.MULTI_MODAL,
                    errors=[f"Risk level {risk_level} exceeds tolerance {policy['risk_tolerance']}"],
                    metadata=ValidationMetadata(
                        validator_name="MultiFactorBiometricValidator",
                        validator_version="1.0.0",
                        validation_timestamp=datetime.now(),
                        processing_time_ms=1.0,
                        validation_level=ValidationLevel.ENHANCED
                    )
                )
            
            # Perform biometric fusion
            fusion_result = await self._perform_biometric_fusion(
                individual_results, policy, context
            )
            
            # Make final authentication decision
            is_valid = (fusion_result.final_score >= policy['min_score_threshold'] and
                       fusion_result.confidence_level >= 0.5)
            
            # Create validation result
            result = BiometricValidationResult(
                is_valid=is_valid,
                confidence_score=fusion_result.confidence_level,
                biometric_type=BiometricType.MULTI_MODAL,
                quality_score=self._calculate_overall_quality(individual_results),
                match_score=fusion_result.final_score,
                liveness_score=self._calculate_overall_liveness(individual_results),
                validation_level=ValidationLevel.ENHANCED,
                metadata={
                    'fusion_result': asdict(fusion_result),
                    'individual_results': {str(k): asdict(v) for k, v in individual_results.items()},
                    'risk_assessment': {'level': risk_level, 'factors': risk_factors},
                    'session_id': session_id,
                    'authentication_mode': context.authentication_mode,
                    'processing_time_ms': (time.time() - start_time) * 1000
                }
            )
            
            # Start continuous monitoring if enabled
            if context.authentication_mode == AuthenticationMode.CONTINUOUS and is_valid:
                user_profile = self._build_user_profile(individual_results)
                monitoring_interval = policy.get('monitoring_interval', timedelta(minutes=5))
                await self.continuous_engine.start_continuous_monitoring(
                    session_id, user_profile, monitoring_interval
                )
            
            # Log authentication attempt
            self._log_authentication_attempt(context, result, fusion_result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Multi-factor authentication failed for session {session_id}: {e}")
            return BiometricValidationResult(
                is_valid=False,
                id_type=IDType.NATIONAL_ID,
                original_value="multi_modal_sample",
                normalized_value="multi_modal_sample",
                status=ValidationStatus.INVALID,
                confidence_score=0.0,
                risk_score=1.0,
                biometric_type=BiometricType.MULTI_MODAL,
                errors=[f"Authentication error: {str(e)}"],
                metadata=ValidationMetadata(
                    validator_name="MultiFactorBiometricValidator",
                    validator_version="1.0.0",
                    validation_timestamp=datetime.now(),
                    processing_time_ms=1.0,
                    validation_level=ValidationLevel.ENHANCED
                )
            )
    
    async def _validate_individual_modalities(self,
                                            biometric_samples: Dict[BiometricType, Any],
                                            user_templates: Optional[Dict[BiometricType, Any]],
                                            available_modalities: Set[BiometricType]) -> Dict[BiometricType, BiometricValidationResult]:
        """Validate individual biometric modalities in parallel"""
        
        individual_results = {}
        
        # Create validation tasks
        tasks = []
        for bio_type in available_modalities:
            if bio_type in self.registered_modalities and bio_type in biometric_samples:
                modality = self.registered_modalities[bio_type]
                sample = biometric_samples[bio_type]
                template = user_templates.get(bio_type) if user_templates else None
                
                task = asyncio.create_task(
                    self._validate_single_modality(modality, sample, template)
                )
                tasks.append((bio_type, task))
        
        # Execute validations in parallel
        for bio_type, task in tasks:
            try:
                result = await task
                individual_results[bio_type] = result
            except Exception as e:
                self.logger.error(f"Validation failed for {bio_type}: {e}")
                individual_results[bio_type] = BiometricValidationResult(
                    is_valid=False,
                    confidence_score=0.0,
                    biometric_type=bio_type,
                    quality_score=0.0,
                    match_score=0.0,
                    liveness_score=0.0,
                    validation_level=ValidationLevel.ENHANCED,
                    errors=[f"Validation error: {str(e)}"]
                )
        
        return individual_results
    
    async def _validate_single_modality(self,
                                       modality: BiometricModality,
                                       sample: Any,
                                       template: Optional[Any]) -> BiometricValidationResult:
        """Validate a single biometric modality"""
        
        validator = modality.validator
        
        if template:
            # Perform matching against enrolled template
            return await asyncio.get_event_loop().run_in_executor(
                None, validator.validate, sample, template
            )
        else:
            # Perform quality assessment and liveness detection only
            quality_score = await asyncio.get_event_loop().run_in_executor(
                None, validator.assess_quality, sample
            )
            
            liveness_score = await asyncio.get_event_loop().run_in_executor(
                None, validator.detect_liveness, sample
            )
            
            return BiometricValidationResult(
                is_valid=(quality_score >= modality.quality_threshold and 
                         liveness_score >= 0.5),
                confidence_score=min(quality_score, liveness_score),
                biometric_type=modality.biometric_type,
                quality_score=quality_score,
                match_score=0.0,  # No template to match against
                liveness_score=liveness_score,
                validation_level=ValidationLevel.ENHANCED
            )
    
    async def _perform_biometric_fusion(self,
                                      individual_results: Dict[BiometricType, BiometricValidationResult],
                                      policy: Dict[str, Any],
                                      context: AuthenticationContext) -> FusionResult:
        """Perform biometric fusion based on policy and context"""
        
        # Extract scores from individual results
        scores = {}
        for bio_type, result in individual_results.items():
            if result.is_valid:
                scores[bio_type] = result.match_score if result.match_score > 0 else result.confidence_score
        
        if not scores:
            return FusionResult(
                final_score=0.0,
                confidence_level=0.0,
                contributing_modalities=set(),
                individual_scores=scores,
                fusion_strategy_used=FusionStrategy.DECISION_LEVEL,
                risk_assessment=RiskLevel.CRITICAL,
                authentication_strength=0.0,
                decision_reasoning=["No valid biometric samples"]
            )
        
        # Get fusion strategy from policy
        fusion_strategy = policy.get('fusion_strategy', FusionStrategy.WEIGHTED_MAJORITY)
        
        # Calculate weights
        weights = {}
        for bio_type in scores.keys():
            if bio_type in self.registered_modalities:
                weights[bio_type] = self.registered_modalities[bio_type].weight
        
        # Perform fusion based on strategy
        if fusion_strategy == FusionStrategy.SCORE_LEVEL:
            final_score = self.fusion_engine.score_level_fusion(scores, weights)
            strategy_name = "score_level"
        elif fusion_strategy == FusionStrategy.BAYESIAN_FUSION:
            priors = {bio_type: 0.5 for bio_type in scores.keys()}  # Uniform priors
            final_score = self.fusion_engine.bayesian_fusion(scores, priors)
            strategy_name = "bayesian"
        elif fusion_strategy == FusionStrategy.ADAPTIVE_FUSION:
            historical_performance = {}  # Would load from database
            final_score, strategy_name = self.fusion_engine.adaptive_fusion(
                scores, context, historical_performance
            )
        else:  # Default to weighted majority
            final_score = self.fusion_engine.score_level_fusion(scores, weights)
            strategy_name = "weighted_majority"
        
        # Calculate confidence level
        confidence_level = self._calculate_fusion_confidence(scores, weights, final_score)
        
        # Assess authentication strength
        auth_strength = self._calculate_authentication_strength(
            len(scores), final_score, confidence_level
        )
        
        # Generate decision reasoning
        reasoning = self._generate_decision_reasoning(individual_results, final_score, strategy_name)
        
        return FusionResult(
            final_score=final_score,
            confidence_level=confidence_level,
            contributing_modalities=set(scores.keys()),
            individual_scores=scores,
            fusion_strategy_used=fusion_strategy,
            risk_assessment=RiskLevel.LOW,  # Would be calculated based on context
            authentication_strength=auth_strength,
            decision_reasoning=reasoning
        )
    
    def _calculate_overall_quality(self, results: Dict[BiometricType, BiometricValidationResult]) -> float:
        """Calculate overall quality score from individual results"""
        if not results:
            return 0.0
            
        valid_results = [r for r in results.values() if r.is_valid]
        if not valid_results:
            return 0.0
            
        quality_scores = [r.quality_score for r in valid_results]
        return sum(quality_scores) / len(quality_scores)
    
    def _calculate_overall_liveness(self, results: Dict[BiometricType, BiometricValidationResult]) -> float:
        """Calculate overall liveness score from individual results"""
        if not results:
            return 0.0
            
        valid_results = [r for r in results.values() if r.is_valid]
        if not valid_results:
            return 0.0
            
        liveness_scores = [r.liveness_score for r in valid_results]
        return sum(liveness_scores) / len(liveness_scores)
    
    def _calculate_fusion_confidence(self, scores: Dict[BiometricType, float],
                                   weights: Dict[BiometricType, float],
                                   final_score: float) -> float:
        """Calculate confidence level for fusion result"""
        if not scores:
            return 0.0
            
        # Calculate confidence based on:
        # 1. Number of contributing modalities
        # 2. Consistency of individual scores
        # 3. Final fused score
        
        modality_factor = min(1.0, len(scores) / 3.0)  # Up to 3 modalities considered optimal
        
        # Calculate score consistency (lower variance = higher confidence)
        score_values = list(scores.values())
        if len(score_values) > 1:
            variance = np.var(score_values)
            consistency_factor = max(0.0, 1.0 - variance)
        else:
            consistency_factor = 1.0
            
        score_factor = final_score
        
        return (modality_factor * 0.4 + consistency_factor * 0.3 + score_factor * 0.3)
    
    def _calculate_authentication_strength(self, num_modalities: int,
                                         final_score: float, 
                                         confidence: float) -> float:
        """Calculate overall authentication strength"""
        
        # Factors contributing to authentication strength:
        # - Number of modalities (more = stronger)
        # - Final score (higher = stronger) 
        # - Confidence level (higher = stronger)
        
        modality_strength = min(1.0, num_modalities / 4.0)  # Up to 4 modalities
        score_strength = final_score
        confidence_strength = confidence
        
        return (modality_strength * 0.3 + score_strength * 0.4 + confidence_strength * 0.3)
    
    def _generate_decision_reasoning(self, results: Dict[BiometricType, BiometricValidationResult],
                                   final_score: float, strategy: str) -> List[str]:
        """Generate human-readable decision reasoning"""
        
        reasoning = []
        
        valid_modalities = [bio_type for bio_type, result in results.items() if result.is_valid]
        invalid_modalities = [bio_type for bio_type, result in results.items() if not result.is_valid]
        
        reasoning.append(f"Used {strategy} fusion strategy")
        reasoning.append(f"Valid modalities: {len(valid_modalities)} ({', '.join([str(m) for m in valid_modalities])})")
        
        if invalid_modalities:
            reasoning.append(f"Invalid modalities: {len(invalid_modalities)} ({', '.join([str(m) for m in invalid_modalities])})")
        
        reasoning.append(f"Final authentication score: {final_score:.3f}")
        
        # Add modality-specific insights
        for bio_type, result in results.items():
            if result.is_valid:
                score = result.match_score if result.match_score > 0 else result.confidence_score
                reasoning.append(f"{bio_type}: score={score:.3f}, quality={result.quality_score:.3f}")
        
        return reasoning
    
    def _build_user_profile(self, results: Dict[BiometricType, BiometricValidationResult]) -> Dict[BiometricType, Any]:
        """Build user profile for continuous authentication"""
        profile = {}
        
        for bio_type, result in results.items():
            if result.is_valid and hasattr(result, 'metadata'):
                # Extract relevant profile information from validation result
                profile[bio_type] = {
                    'baseline_score': result.match_score,
                    'quality_baseline': result.quality_score,
                    'characteristics': result.metadata.get('characteristics', {}),
                    'patterns': result.metadata.get('patterns', {})
                }
        
        return profile
    
    def _log_authentication_attempt(self, context: AuthenticationContext,
                                  result: BiometricValidationResult,
                                  fusion_result: FusionResult) -> None:
        """Log authentication attempt for audit purposes"""
        
        log_entry = {
            'timestamp': context.timestamp.isoformat(),
            'session_id': context.session_id,
            'user_id': context.user_id,
            'device_id': context.device_id,
            'authentication_mode': context.authentication_mode,
            'success': result.is_valid,
            'final_score': fusion_result.final_score,
            'confidence': fusion_result.confidence_level,
            'modalities_used': [str(m) for m in fusion_result.contributing_modalities],
            'fusion_strategy': fusion_result.fusion_strategy_used,
            'risk_level': fusion_result.risk_assessment,
            'processing_time': result.metadata.get('processing_time_ms', 0)
        }
        
        self.logger.info(f"Authentication attempt: {json.dumps(log_entry)}")
    
    # Override base class methods
    
    def validate(self, data: Any, reference_template: Optional[Any] = None, 
                validation_level: Optional[ValidationLevel] = None) -> BiometricValidationResult:
        """
        Synchronous validation method (delegates to async method)
        
        Args:
            data: Dictionary containing biometric samples and context
            reference_template: User biometric templates
            validation_level: Override validation level
            
        Returns:
            BiometricValidationResult
        """
        
        # Extract biometric samples and context from data
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary containing 'samples' and 'context'")
        
        biometric_samples = data.get('samples', {})
        context_data = data.get('context', {})
        
        # Create authentication context
        context = AuthenticationContext(
            session_id=context_data.get('session_id', str(uuid.uuid4())),
            user_id=context_data.get('user_id'),
            device_id=context_data.get('device_id'),
            location=context_data.get('location'),
            timestamp=datetime.now(),
            authentication_mode=AuthenticationMode(context_data.get('mode', AuthenticationMode.STANDARD.value)),
            risk_factors=context_data.get('risk_factors', {}),
            previous_attempts=context_data.get('previous_attempts', 0)
        )
        
        # Run async validation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.validate_multi_factor(biometric_samples, context, reference_template)
            )
            return result
        finally:
            loop.close()
    
    def extract_features(self, data: Any) -> Dict[str, Any]:
        """Extract features from multi-modal biometric data"""
        
        features = {
            'multi_modal_features': {},
            'fusion_metadata': {},
            'quality_metrics': {}
        }
        
        if isinstance(data, dict) and 'samples' in data:
            biometric_samples = data['samples']
            
            for bio_type, sample in biometric_samples.items():
                if bio_type in self.registered_modalities:
                    modality = self.registered_modalities[bio_type]
                    try:
                        modality_features = modality.validator.extract_features(sample)
                        features['multi_modal_features'][str(bio_type)] = modality_features
                    except Exception as e:
                        self.logger.warning(f"Feature extraction failed for {bio_type}: {e}")
        
        return features
    
    def create_template(self, data: Any) -> Dict[str, Any]:
        """Create multi-modal biometric template"""
        
        template = {
            'template_id': str(uuid.uuid4()),
            'creation_timestamp': datetime.now().isoformat(),
            'modality_templates': {},
            'fusion_parameters': {},
            'version': '1.0'
        }
        
        if isinstance(data, dict) and 'samples' in data:
            biometric_samples = data['samples']
            
            for bio_type, sample in biometric_samples.items():
                if bio_type in self.registered_modalities:
                    modality = self.registered_modalities[bio_type]
                    try:
                        modality_template = modality.validator.create_template(sample)
                        template['modality_templates'][str(bio_type)] = modality_template
                    except Exception as e:
                        self.logger.warning(f"Template creation failed for {bio_type}: {e}")
        
        return template
    
    def match_templates(self, template1: Dict[str, Any], template2: Dict[str, Any]) -> float:
        """Match two multi-modal biometric templates"""
        
        if not template1 or not template2:
            return 0.0
            
        modality_templates1 = template1.get('modality_templates', {})
        modality_templates2 = template2.get('modality_templates', {})
        
        # Find common modalities
        common_modalities = set(modality_templates1.keys()) & set(modality_templates2.keys())
        
        if not common_modalities:
            return 0.0
        
        # Calculate individual modality match scores
        match_scores = {}
        weights = {}
        
        for bio_type_str in common_modalities:
            bio_type = BiometricType[bio_type_str] if bio_type_str in BiometricType.__members__ else None
            if bio_type and bio_type in self.registered_modalities:
                modality = self.registered_modalities[bio_type]
                
                template_1 = modality_templates1[bio_type_str]
                template_2 = modality_templates2[bio_type_str]
                
                match_score = modality.validator.match_templates(template_1, template_2)
                match_scores[bio_type] = match_score
                weights[bio_type] = modality.weight
        
        # Fuse match scores
        if match_scores:
            return self.fusion_engine.score_level_fusion(match_scores, weights)
        
        return 0.0
    
    def assess_quality(self, data: Any) -> float:
        """Assess overall quality of multi-modal biometric data"""
        
        if not isinstance(data, dict) or 'samples' not in data:
            return 0.0
            
        biometric_samples = data['samples']
        quality_scores = []
        
        for bio_type, sample in biometric_samples.items():
            if bio_type in self.registered_modalities:
                modality = self.registered_modalities[bio_type]
                try:
                    quality = modality.validator.assess_quality(sample)
                    quality_scores.append(quality * modality.weight)
                except Exception as e:
                    self.logger.warning(f"Quality assessment failed for {bio_type}: {e}")
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    def detect_liveness(self, data: Any) -> float:
        """Detect liveness across multi-modal biometric data"""
        
        if not isinstance(data, dict) or 'samples' not in data:
            return 0.0
            
        biometric_samples = data['samples']
        liveness_scores = []
        
        for bio_type, sample in biometric_samples.items():
            if bio_type in self.registered_modalities:
                modality = self.registered_modalities[bio_type]
                try:
                    liveness = modality.validator.detect_liveness(sample)
                    liveness_scores.append(liveness)
                except Exception as e:
                    self.logger.warning(f"Liveness detection failed for {bio_type}: {e}")
        
        return sum(liveness_scores) / len(liveness_scores) if liveness_scores else 0.0
    
    # Implement abstract methods from BaseBiometricValidator
    
    def _preprocess_biometric_data(self, raw_data: Union[bytes, Any]) -> Union[bytes, Any]:
        """Preprocess multi-modal biometric data"""
        # Multi-factor validator delegates preprocessing to individual modalities
        return raw_data
    
    def _extract_biometric_features(self, preprocessed_data: Union[bytes, Any]) -> Dict[str, Any]:
        """Extract features from multi-modal biometric data"""
        return self.extract_features(preprocessed_data)
    
    def _assess_biometric_quality(self, raw_data: Union[bytes, Any]) -> float:
        """Assess quality of multi-modal biometric data"""
        return self.assess_quality(raw_data)


# Export main classes
__all__ = [
    'MultiFactorBiometricValidator',
    'FusionStrategy',
    'AuthenticationMode',
    'BiometricModality',
    'AuthenticationContext',
    'FusionResult',
    'ContinuousAuthState',
    'RiskLevel'
]
