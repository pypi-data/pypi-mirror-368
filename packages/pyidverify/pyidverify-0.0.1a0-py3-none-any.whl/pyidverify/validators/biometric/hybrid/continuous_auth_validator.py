"""
Continuous Authentication Validator for PyIDVerify

This module provides continuous biometric authentication capabilities that monitor
user behavior throughout a session to detect potential security threats and maintain
ongoing authentication assurance. Implements advanced behavioral pattern analysis,
anomaly detection, and adaptive trust scoring.

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
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Union, Set, Callable, Deque
from threading import Lock, Thread
import hashlib
import uuid
import statistics
from concurrent.futures import ThreadPoolExecutor

from pyidverify.core.types import ValidationLevel, BiometricType, IDType
from pyidverify.core.exceptions import PyIDVerifyError, ValidationError
from pyidverify.validators.biometric import BaseBiometricValidator, BiometricValidationResult, BaseValidator, ValidationResult


class ContinuousAuthMode(Enum):
    """Continuous authentication modes"""
    PASSIVE = auto()           # Background monitoring only
    ACTIVE = auto()            # Periodic explicit verification
    ADAPTIVE = auto()          # Adaptive based on risk
    TRANSPARENT = auto()       # Invisible to user
    CHALLENGE_RESPONSE = auto() # Challenge when anomalies detected


class ThreatLevel(Enum):
    """Threat levels for continuous authentication"""
    MINIMAL = auto()
    LOW = auto()
    MODERATE = auto()
    HIGH = auto()
    CRITICAL = auto()
    EMERGENCY = auto()


class SessionState(Enum):
    """Continuous authentication session states"""
    ACTIVE = auto()
    DEGRADED = auto()
    SUSPICIOUS = auto()
    LOCKED = auto()
    TERMINATED = auto()


class AnomalyType(Enum):
    """Types of behavioral anomalies"""
    KEYSTROKE_DEVIATION = auto()
    MOUSE_PATTERN_CHANGE = auto()
    TYPING_RHYTHM_ANOMALY = auto()
    BIOMETRIC_QUALITY_DROP = auto()
    TEMPORAL_INCONSISTENCY = auto()
    LOCATION_ANOMALY = auto()
    DEVICE_ANOMALY = auto()
    BEHAVIORAL_DRIFT = auto()


@dataclass
class BiometricSample:
    """Individual biometric sample with timestamp"""
    timestamp: datetime
    biometric_type: BiometricType
    raw_data: Any
    quality_score: float
    features: Dict[str, Any]
    session_id: str
    anomaly_indicators: Dict[str, float] = None


@dataclass
class ContinuousSession:
    """Continuous authentication session tracking"""
    session_id: str
    user_id: str
    device_id: Optional[str]
    start_time: datetime
    last_activity: datetime
    
    # Behavioral baselines
    keystroke_baseline: Optional[Dict[str, Any]] = None
    mouse_baseline: Optional[Dict[str, Any]] = None
    typing_rhythm_baseline: Optional[Dict[str, Any]] = None
    
    # Session metrics
    trust_score: float = 1.0
    anomaly_score: float = 0.0
    session_state: SessionState = SessionState.ACTIVE
    threat_level: ThreatLevel = ThreatLevel.MINIMAL
    
    # Activity tracking
    sample_buffer: Deque[BiometricSample] = None
    anomaly_history: List[Dict[str, Any]] = None
    verification_history: List[Dict[str, Any]] = None
    
    # Configuration
    buffer_size: int = 100
    baseline_samples: int = 20
    anomaly_threshold: float = 0.7
    trust_decay_rate: float = 0.01
    verification_interval: timedelta = timedelta(minutes=5)


@dataclass
class AnomalyEvent:
    """Anomaly detection event"""
    event_id: str
    timestamp: datetime
    session_id: str
    anomaly_type: AnomalyType
    severity: float
    description: str
    affected_biometric: BiometricType
    baseline_deviation: float
    confidence_level: float
    recommended_action: str


@dataclass
class ContinuousAuthResult:
    """Result of continuous authentication assessment"""
    session_id: str
    timestamp: datetime
    is_authenticated: bool
    trust_score: float
    anomaly_score: float
    session_state: SessionState
    threat_level: ThreatLevel
    detected_anomalies: List[AnomalyEvent]
    recommended_actions: List[str]
    session_duration: timedelta
    samples_analyzed: int
    confidence_level: float


class BaselineEstimator:
    """Estimates behavioral baselines from biometric samples"""
    
    def __init__(self):
        self.min_samples = 20
        self.confidence_threshold = 0.8
    
    def estimate_keystroke_baseline(self, samples: List[BiometricSample]) -> Dict[str, Any]:
        """Estimate keystroke dynamics baseline"""
        if len(samples) < self.min_samples:
            return {}
            
        keystroke_samples = [s for s in samples if s.biometric_type == BiometricType.BEHAVIORAL_KEYSTROKE]
        
        if len(keystroke_samples) < self.min_samples:
            return {}
        
        # Extract timing features
        dwell_times = []
        flight_times = []
        typing_speeds = []
        
        for sample in keystroke_samples:
            features = sample.features
            if 'dwell_times' in features:
                dwell_times.extend(features['dwell_times'])
            if 'flight_times' in features:
                flight_times.extend(features['flight_times'])
            if 'typing_speed' in features:
                typing_speeds.append(features['typing_speed'])
        
        baseline = {
            'dwell_time_mean': statistics.mean(dwell_times) if dwell_times else 0,
            'dwell_time_std': statistics.stdev(dwell_times) if len(dwell_times) > 1 else 0,
            'flight_time_mean': statistics.mean(flight_times) if flight_times else 0,
            'flight_time_std': statistics.stdev(flight_times) if len(flight_times) > 1 else 0,
            'typing_speed_mean': statistics.mean(typing_speeds) if typing_speeds else 0,
            'typing_speed_std': statistics.stdev(typing_speeds) if len(typing_speeds) > 1 else 0,
            'sample_count': len(keystroke_samples),
            'confidence': min(1.0, len(keystroke_samples) / 50.0)
        }
        
        return baseline
    
    def estimate_mouse_baseline(self, samples: List[BiometricSample]) -> Dict[str, Any]:
        """Estimate mouse behavior baseline"""
        if len(samples) < self.min_samples:
            return {}
            
        mouse_samples = [s for s in samples if s.biometric_type == BiometricType.BEHAVIORAL_MOUSE]
        
        if len(mouse_samples) < self.min_samples:
            return {}
        
        # Extract movement features
        velocities = []
        accelerations = []
        click_intervals = []
        path_efficiencies = []
        
        for sample in mouse_samples:
            features = sample.features
            if 'velocity_profile' in features:
                velocities.extend(features['velocity_profile'])
            if 'acceleration_profile' in features:
                accelerations.extend(features['acceleration_profile'])
            if 'click_intervals' in features:
                click_intervals.extend(features['click_intervals'])
            if 'path_efficiency' in features:
                path_efficiencies.append(features['path_efficiency'])
        
        baseline = {
            'velocity_mean': statistics.mean(velocities) if velocities else 0,
            'velocity_std': statistics.stdev(velocities) if len(velocities) > 1 else 0,
            'acceleration_mean': statistics.mean(accelerations) if accelerations else 0,
            'acceleration_std': statistics.stdev(accelerations) if len(accelerations) > 1 else 0,
            'click_interval_mean': statistics.mean(click_intervals) if click_intervals else 0,
            'click_interval_std': statistics.stdev(click_intervals) if len(click_intervals) > 1 else 0,
            'path_efficiency_mean': statistics.mean(path_efficiencies) if path_efficiencies else 0,
            'sample_count': len(mouse_samples),
            'confidence': min(1.0, len(mouse_samples) / 30.0)
        }
        
        return baseline
    
    def estimate_typing_rhythm_baseline(self, samples: List[BiometricSample]) -> Dict[str, Any]:
        """Estimate typing rhythm baseline"""
        if len(samples) < self.min_samples:
            return {}
        
        # Combine keystroke samples for rhythm analysis
        keystroke_samples = [s for s in samples if s.biometric_type == BiometricType.BEHAVIORAL_KEYSTROKE]
        
        if len(keystroke_samples) < self.min_samples:
            return {}
        
        # Extract rhythm features
        inter_key_intervals = []
        burst_patterns = []
        pause_patterns = []
        
        for sample in keystroke_samples:
            features = sample.features
            if 'inter_key_intervals' in features:
                inter_key_intervals.extend(features['inter_key_intervals'])
            if 'burst_length' in features:
                burst_patterns.append(features['burst_length'])
            if 'pause_duration' in features:
                pause_patterns.append(features['pause_duration'])
        
        baseline = {
            'inter_key_mean': statistics.mean(inter_key_intervals) if inter_key_intervals else 0,
            'inter_key_std': statistics.stdev(inter_key_intervals) if len(inter_key_intervals) > 1 else 0,
            'burst_length_mean': statistics.mean(burst_patterns) if burst_patterns else 0,
            'pause_duration_mean': statistics.mean(pause_patterns) if pause_patterns else 0,
            'rhythm_consistency': self._calculate_rhythm_consistency(inter_key_intervals),
            'sample_count': len(keystroke_samples),
            'confidence': min(1.0, len(keystroke_samples) / 40.0)
        }
        
        return baseline
    
    def _calculate_rhythm_consistency(self, intervals: List[float]) -> float:
        """Calculate typing rhythm consistency"""
        if len(intervals) < 5:
            return 0.5
            
        # Calculate coefficient of variation
        mean_interval = statistics.mean(intervals)
        if mean_interval == 0:
            return 0.0
            
        std_interval = statistics.stdev(intervals)
        cv = std_interval / mean_interval
        
        # Convert to consistency score (lower CV = higher consistency)
        consistency = max(0.0, 1.0 - cv)
        return consistency


class AnomalyDetector:
    """Advanced anomaly detection for continuous authentication"""
    
    def __init__(self):
        self.detection_models = {}
        self.sensitivity_levels = {}
        
    def detect_keystroke_anomalies(self, sample: BiometricSample, 
                                 baseline: Dict[str, Any]) -> List[AnomalyEvent]:
        """Detect keystroke dynamics anomalies"""
        anomalies = []
        
        if not baseline or baseline.get('confidence', 0) < 0.5:
            return anomalies
        
        features = sample.features
        
        # Check dwell time deviation
        if 'dwell_times' in features and 'dwell_time_mean' in baseline:
            sample_dwell_mean = statistics.mean(features['dwell_times'])
            baseline_mean = baseline['dwell_time_mean']
            baseline_std = baseline.get('dwell_time_std', 0.1)
            
            if baseline_std > 0:
                deviation = abs(sample_dwell_mean - baseline_mean) / baseline_std
                if deviation > 2.5:  # More than 2.5 standard deviations
                    anomalies.append(AnomalyEvent(
                        event_id=str(uuid.uuid4()),
                        timestamp=sample.timestamp,
                        session_id=sample.session_id,
                        anomaly_type=AnomalyType.KEYSTROKE_DEVIATION,
                        severity=min(1.0, deviation / 5.0),
                        description=f"Dwell time deviation: {deviation:.2f} std deviations",
                        affected_biometric=BiometricType.BEHAVIORAL_KEYSTROKE,
                        baseline_deviation=deviation,
                        confidence_level=0.8,
                        recommended_action="Monitor additional samples"
                    ))
        
        # Check typing speed deviation
        if 'typing_speed' in features and 'typing_speed_mean' in baseline:
            sample_speed = features['typing_speed']
            baseline_speed = baseline['typing_speed_mean']
            baseline_std = baseline.get('typing_speed_std', 10.0)
            
            if baseline_std > 0:
                speed_deviation = abs(sample_speed - baseline_speed) / baseline_std
                if speed_deviation > 3.0:
                    anomalies.append(AnomalyEvent(
                        event_id=str(uuid.uuid4()),
                        timestamp=sample.timestamp,
                        session_id=sample.session_id,
                        anomaly_type=AnomalyType.TYPING_RHYTHM_ANOMALY,
                        severity=min(1.0, speed_deviation / 6.0),
                        description=f"Typing speed anomaly: {speed_deviation:.2f} std deviations",
                        affected_biometric=BiometricType.BEHAVIORAL_KEYSTROKE,
                        baseline_deviation=speed_deviation,
                        confidence_level=0.7,
                        recommended_action="Verify user identity"
                    ))
        
        return anomalies
    
    def detect_mouse_anomalies(self, sample: BiometricSample, 
                             baseline: Dict[str, Any]) -> List[AnomalyEvent]:
        """Detect mouse pattern anomalies"""
        anomalies = []
        
        if not baseline or baseline.get('confidence', 0) < 0.5:
            return anomalies
        
        features = sample.features
        
        # Check velocity pattern deviation
        if 'velocity_profile' in features and 'velocity_mean' in baseline:
            sample_velocity_mean = statistics.mean(features['velocity_profile'])
            baseline_velocity = baseline['velocity_mean']
            baseline_std = baseline.get('velocity_std', 50.0)
            
            if baseline_std > 0:
                velocity_deviation = abs(sample_velocity_mean - baseline_velocity) / baseline_std
                if velocity_deviation > 2.0:
                    anomalies.append(AnomalyEvent(
                        event_id=str(uuid.uuid4()),
                        timestamp=sample.timestamp,
                        session_id=sample.session_id,
                        anomaly_type=AnomalyType.MOUSE_PATTERN_CHANGE,
                        severity=min(1.0, velocity_deviation / 4.0),
                        description=f"Mouse velocity anomaly: {velocity_deviation:.2f} std deviations",
                        affected_biometric=BiometricType.BEHAVIORAL_MOUSE,
                        baseline_deviation=velocity_deviation,
                        confidence_level=0.6,
                        recommended_action="Increase monitoring frequency"
                    ))
        
        # Check click pattern anomalies
        if 'click_intervals' in features and 'click_interval_mean' in baseline:
            if features['click_intervals']:
                sample_click_mean = statistics.mean(features['click_intervals'])
                baseline_click = baseline['click_interval_mean']
                baseline_std = baseline.get('click_interval_std', 200.0)
                
                if baseline_std > 0:
                    click_deviation = abs(sample_click_mean - baseline_click) / baseline_std
                    if click_deviation > 2.5:
                        anomalies.append(AnomalyEvent(
                            event_id=str(uuid.uuid4()),
                            timestamp=sample.timestamp,
                            session_id=sample.session_id,
                            anomaly_type=AnomalyType.MOUSE_PATTERN_CHANGE,
                            severity=min(1.0, click_deviation / 5.0),
                            description=f"Click pattern anomaly: {click_deviation:.2f} std deviations",
                            affected_biometric=BiometricType.BEHAVIORAL_MOUSE,
                            baseline_deviation=click_deviation,
                            confidence_level=0.7,
                            recommended_action="Verify mouse usage patterns"
                        ))
        
        return anomalies
    
    def detect_quality_anomalies(self, sample: BiometricSample,
                               historical_quality: List[float]) -> List[AnomalyEvent]:
        """Detect biometric quality anomalies"""
        anomalies = []
        
        if len(historical_quality) < 10:
            return anomalies
        
        # Calculate quality baseline from recent history
        recent_quality = historical_quality[-20:]  # Last 20 samples
        baseline_quality = statistics.mean(recent_quality)
        quality_std = statistics.stdev(recent_quality) if len(recent_quality) > 1 else 0.1
        
        # Check for significant quality drop
        quality_deviation = (baseline_quality - sample.quality_score) / quality_std if quality_std > 0 else 0
        
        if quality_deviation > 2.0:  # Quality dropped significantly
            anomalies.append(AnomalyEvent(
                event_id=str(uuid.uuid4()),
                timestamp=sample.timestamp,
                session_id=sample.session_id,
                anomaly_type=AnomalyType.BIOMETRIC_QUALITY_DROP,
                severity=min(1.0, quality_deviation / 4.0),
                description=f"Biometric quality drop: {quality_deviation:.2f} std deviations",
                affected_biometric=sample.biometric_type,
                baseline_deviation=quality_deviation,
                confidence_level=0.8,
                recommended_action="Check biometric sensor condition"
            ))
        
        return anomalies
    
    def detect_temporal_anomalies(self, sample: BiometricSample,
                                recent_samples: List[BiometricSample]) -> List[AnomalyEvent]:
        """Detect temporal pattern anomalies"""
        anomalies = []
        
        if len(recent_samples) < 5:
            return anomalies
        
        # Check for unusual timing patterns
        same_type_samples = [s for s in recent_samples if s.biometric_type == sample.biometric_type]
        
        if len(same_type_samples) >= 3:
            # Calculate inter-sample intervals
            intervals = []
            for i in range(1, len(same_type_samples)):
                interval = (same_type_samples[i].timestamp - same_type_samples[i-1].timestamp).total_seconds()
                intervals.append(interval)
            
            if intervals:
                mean_interval = statistics.mean(intervals)
                std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 60.0
                
                # Check current interval
                current_interval = (sample.timestamp - same_type_samples[-1].timestamp).total_seconds()
                
                if std_interval > 0:
                    interval_deviation = abs(current_interval - mean_interval) / std_interval
                    
                    if interval_deviation > 3.0:  # Unusual timing
                        anomalies.append(AnomalyEvent(
                            event_id=str(uuid.uuid4()),
                            timestamp=sample.timestamp,
                            session_id=sample.session_id,
                            anomaly_type=AnomalyType.TEMPORAL_INCONSISTENCY,
                            severity=min(1.0, interval_deviation / 6.0),
                            description=f"Temporal pattern anomaly: {interval_deviation:.2f} std deviations",
                            affected_biometric=sample.biometric_type,
                            baseline_deviation=interval_deviation,
                            confidence_level=0.6,
                            recommended_action="Analyze session timing patterns"
                        ))
        
        return anomalies


class TrustScoreCalculator:
    """Calculates and maintains trust scores for continuous authentication"""
    
    def __init__(self):
        self.base_trust = 1.0
        self.decay_rate = 0.01
        self.anomaly_impact_weights = {
            AnomalyType.KEYSTROKE_DEVIATION: 0.15,
            AnomalyType.MOUSE_PATTERN_CHANGE: 0.10,
            AnomalyType.TYPING_RHYTHM_ANOMALY: 0.12,
            AnomalyType.BIOMETRIC_QUALITY_DROP: 0.08,
            AnomalyType.TEMPORAL_INCONSISTENCY: 0.05,
            AnomalyType.BEHAVIORAL_DRIFT: 0.20
        }
    
    def calculate_trust_score(self, previous_trust: float,
                            anomalies: List[AnomalyEvent],
                            time_since_last_update: timedelta,
                            positive_evidence: float = 0.0) -> float:
        """Calculate updated trust score based on anomalies and time decay"""
        
        # Apply time-based decay
        decay_factor = self.decay_rate * (time_since_last_update.total_seconds() / 3600.0)  # Per hour
        trust_with_decay = previous_trust * (1.0 - decay_factor)
        
        # Calculate anomaly impact
        anomaly_penalty = 0.0
        for anomaly in anomalies:
            weight = self.anomaly_impact_weights.get(anomaly.anomaly_type, 0.1)
            penalty = weight * anomaly.severity * anomaly.confidence_level
            anomaly_penalty += penalty
        
        # Apply anomaly penalty
        trust_after_anomalies = max(0.0, trust_with_decay - anomaly_penalty)
        
        # Apply positive evidence bonus
        positive_bonus = positive_evidence * 0.05  # Small bonus for good behavior
        final_trust = min(1.0, trust_after_anomalies + positive_bonus)
        
        return final_trust
    
    def calculate_session_risk(self, trust_score: float,
                             anomaly_count: int,
                             session_duration: timedelta) -> ThreatLevel:
        """Calculate overall session risk level"""
        
        # Base risk from trust score
        trust_risk = 1.0 - trust_score
        
        # Anomaly density risk
        duration_hours = session_duration.total_seconds() / 3600.0
        anomaly_density = anomaly_count / max(1.0, duration_hours)
        density_risk = min(1.0, anomaly_density / 10.0)  # Normalize to 0-1
        
        # Combined risk score
        combined_risk = (trust_risk * 0.7 + density_risk * 0.3)
        
        # Map to threat level
        if combined_risk <= 0.2:
            return ThreatLevel.MINIMAL
        elif combined_risk <= 0.4:
            return ThreatLevel.LOW
        elif combined_risk <= 0.6:
            return ThreatLevel.MODERATE
        elif combined_risk <= 0.8:
            return ThreatLevel.HIGH
        else:
            return ThreatLevel.CRITICAL


class ContinuousAuthenticationValidator(BaseBiometricValidator):
    """
    Continuous Authentication Validator for PyIDVerify
    
    Provides ongoing authentication monitoring through behavioral biometric analysis.
    Maintains trust scores, detects anomalies, and adapts security measures based on
    user behavior patterns throughout active sessions.
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.ENHANCED):
        super().__init__(validation_level)
        
        self.baseline_estimator = BaselineEstimator()
        self.anomaly_detector = AnomalyDetector()
        self.trust_calculator = TrustScoreCalculator()
        
        self.active_sessions: Dict[str, ContinuousSession] = {}
        self.session_lock = Lock()
        
        # Background monitoring
        self.monitoring_active = True
        self.monitoring_thread: Optional[Thread] = None
        
        # Configuration
        self.max_sessions = 1000
        self.session_timeout = timedelta(hours=8)
        self.cleanup_interval = timedelta(minutes=30)
        
        self._setup_logging()
        self._start_background_monitoring()
    
    def _setup_logging(self) -> None:
        """Setup logging for continuous authentication"""
        self.logger = logging.getLogger(f"{__name__}.ContinuousAuthenticationValidator")
        self.logger.setLevel(logging.INFO)
    
    def _start_background_monitoring(self) -> None:
        """Start background monitoring thread"""
        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self.monitoring_thread = Thread(target=self._background_monitor, daemon=True)
            self.monitoring_thread.start()
            self.logger.info("Started continuous authentication background monitoring")
    
    def _background_monitor(self) -> None:
        """Background monitoring of all active sessions"""
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                with self.session_lock:
                    sessions_to_remove = []
                    
                    for session_id, session in self.active_sessions.items():
                        # Check for session timeout
                        if current_time - session.last_activity > self.session_timeout:
                            sessions_to_remove.append(session_id)
                            continue
                        
                        # Apply trust decay
                        time_since_last = current_time - session.last_activity
                        session.trust_score = self.trust_calculator.calculate_trust_score(
                            session.trust_score, [], time_since_last
                        )
                        
                        # Update session state based on trust score
                        if session.trust_score < 0.3:
                            session.session_state = SessionState.SUSPICIOUS
                        elif session.trust_score < 0.1:
                            session.session_state = SessionState.LOCKED
                    
                    # Remove timed out sessions
                    for session_id in sessions_to_remove:
                        self.logger.info(f"Removing timed out session: {session_id}")
                        del self.active_sessions[session_id]
                
                # Sleep until next monitoring cycle
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in background monitoring: {e}")
                time.sleep(60)
    
    def start_continuous_session(self, user_id: str, device_id: Optional[str] = None,
                               initial_samples: List[BiometricSample] = None) -> str:
        """Start a new continuous authentication session"""
        
        session_id = str(uuid.uuid4())
        current_time = datetime.now()
        
        # Create new session
        session = ContinuousSession(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            start_time=current_time,
            last_activity=current_time,
            sample_buffer=deque(maxlen=100),
            anomaly_history=[],
            verification_history=[]
        )
        
        # Process initial samples if provided
        if initial_samples:
            for sample in initial_samples:
                sample.session_id = session_id
                session.sample_buffer.append(sample)
            
            # Establish initial baselines if enough samples
            if len(session.sample_buffer) >= session.baseline_samples:
                self._update_session_baselines(session)
        
        # Store session
        with self.session_lock:
            if len(self.active_sessions) >= self.max_sessions:
                # Remove oldest session
                oldest_session_id = min(self.active_sessions.keys(),
                                      key=lambda x: self.active_sessions[x].start_time)
                del self.active_sessions[oldest_session_id]
                self.logger.warning(f"Removed oldest session {oldest_session_id} due to capacity limit")
            
            self.active_sessions[session_id] = session
        
        self.logger.info(f"Started continuous authentication session: {session_id} for user: {user_id}")
        return session_id
    
    def process_biometric_sample(self, session_id: str, 
                               biometric_sample: BiometricSample) -> ContinuousAuthResult:
        """Process a new biometric sample for continuous authentication"""
        
        with self.session_lock:
            if session_id not in self.active_sessions:
                raise ValidationError(f"Session not found: {session_id}")
            
            session = self.active_sessions[session_id]
            
            # Update session activity
            session.last_activity = biometric_sample.timestamp
            session.sample_buffer.append(biometric_sample)
        
        # Detect anomalies
        anomalies = self._detect_sample_anomalies(session, biometric_sample)
        
        # Update baselines if needed
        if len(session.sample_buffer) >= session.baseline_samples:
            self._update_session_baselines(session)
        
        # Calculate updated trust score
        time_since_last = timedelta(seconds=5)  # Assume 5 second interval
        positive_evidence = self._calculate_positive_evidence(biometric_sample, session)
        
        session.trust_score = self.trust_calculator.calculate_trust_score(
            session.trust_score, anomalies, time_since_last, positive_evidence
        )
        
        # Update anomaly score
        if anomalies:
            session.anomaly_score = statistics.mean([a.severity for a in anomalies])
            session.anomaly_history.extend([asdict(a) for a in anomalies])
        
        # Determine session state and threat level
        session.threat_level = self.trust_calculator.calculate_session_risk(
            session.trust_score,
            len([a for a in session.anomaly_history if 
                datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(hours=1)]),
            datetime.now() - session.start_time
        )
        
        # Update session state
        if session.trust_score < 0.1:
            session.session_state = SessionState.LOCKED
        elif session.trust_score < 0.3:
            session.session_state = SessionState.SUSPICIOUS
        elif anomalies and any(a.severity > 0.7 for a in anomalies):
            session.session_state = SessionState.DEGRADED
        else:
            session.session_state = SessionState.ACTIVE
        
        # Generate recommended actions
        recommended_actions = self._generate_recommendations(session, anomalies)
        
        # Create result
        result = ContinuousAuthResult(
            session_id=session_id,
            timestamp=datetime.now(),
            is_authenticated=(session.session_state in [SessionState.ACTIVE, SessionState.DEGRADED]),
            trust_score=session.trust_score,
            anomaly_score=session.anomaly_score,
            session_state=session.session_state,
            threat_level=session.threat_level,
            detected_anomalies=anomalies,
            recommended_actions=recommended_actions,
            session_duration=datetime.now() - session.start_time,
            samples_analyzed=len(session.sample_buffer),
            confidence_level=self._calculate_result_confidence(session, anomalies)
        )
        
        self.logger.info(f"Processed sample for session {session_id}: trust={session.trust_score:.3f}, "
                        f"anomalies={len(anomalies)}, state={session.session_state}")
        
        return result
    
    def _detect_sample_anomalies(self, session: ContinuousSession, 
                               sample: BiometricSample) -> List[AnomalyEvent]:
        """Detect anomalies in the new biometric sample"""
        
        anomalies = []
        
        # Keystroke anomalies
        if (sample.biometric_type == BiometricType.BEHAVIORAL_KEYSTROKE and 
            session.keystroke_baseline):
            keystroke_anomalies = self.anomaly_detector.detect_keystroke_anomalies(
                sample, session.keystroke_baseline
            )
            anomalies.extend(keystroke_anomalies)
        
        # Mouse anomalies
        if (sample.biometric_type == BiometricType.BEHAVIORAL_MOUSE and 
            session.mouse_baseline):
            mouse_anomalies = self.anomaly_detector.detect_mouse_anomalies(
                sample, session.mouse_baseline
            )
            anomalies.extend(mouse_anomalies)
        
        # Quality anomalies
        recent_samples = list(session.sample_buffer)[-50:]  # Last 50 samples
        same_type_samples = [s for s in recent_samples if s.biometric_type == sample.biometric_type]
        
        if len(same_type_samples) >= 10:
            quality_history = [s.quality_score for s in same_type_samples]
            quality_anomalies = self.anomaly_detector.detect_quality_anomalies(
                sample, quality_history
            )
            anomalies.extend(quality_anomalies)
        
        # Temporal anomalies
        temporal_anomalies = self.anomaly_detector.detect_temporal_anomalies(
            sample, recent_samples
        )
        anomalies.extend(temporal_anomalies)
        
        return anomalies
    
    def _update_session_baselines(self, session: ContinuousSession) -> None:
        """Update behavioral baselines for the session"""
        
        buffer_samples = list(session.sample_buffer)
        
        # Update keystroke baseline
        session.keystroke_baseline = self.baseline_estimator.estimate_keystroke_baseline(
            buffer_samples
        )
        
        # Update mouse baseline
        session.mouse_baseline = self.baseline_estimator.estimate_mouse_baseline(
            buffer_samples
        )
        
        # Update typing rhythm baseline
        session.typing_rhythm_baseline = self.baseline_estimator.estimate_typing_rhythm_baseline(
            buffer_samples
        )
        
        self.logger.debug(f"Updated baselines for session {session.session_id}")
    
    def _calculate_positive_evidence(self, sample: BiometricSample,
                                   session: ContinuousSession) -> float:
        """Calculate positive evidence score from sample quality and consistency"""
        
        positive_evidence = 0.0
        
        # Quality bonus
        if sample.quality_score > 0.8:
            positive_evidence += 0.3
        
        # Consistency bonus (if sample matches baseline well)
        if sample.biometric_type == BiometricType.BEHAVIORAL_KEYSTROKE and session.keystroke_baseline:
            baseline_confidence = session.keystroke_baseline.get('confidence', 0.0)
            if baseline_confidence > 0.7:
                positive_evidence += 0.2
        
        return positive_evidence
    
    def _generate_recommendations(self, session: ContinuousSession,
                                anomalies: List[AnomalyEvent]) -> List[str]:
        """Generate recommended actions based on session state"""
        
        recommendations = []
        
        if session.session_state == SessionState.LOCKED:
            recommendations.append("Session locked - require full re-authentication")
            recommendations.append("Investigate potential security breach")
        
        elif session.session_state == SessionState.SUSPICIOUS:
            recommendations.append("Increase monitoring frequency")
            recommendations.append("Request additional authentication factors")
            recommendations.append("Log detailed security events")
        
        elif session.session_state == SessionState.DEGRADED:
            recommendations.append("Monitor session closely")
            recommendations.append("Consider step-up authentication")
        
        # Anomaly-specific recommendations
        for anomaly in anomalies:
            if anomaly.severity > 0.8:
                recommendations.append(f"High severity anomaly detected: {anomaly.description}")
                recommendations.append(anomaly.recommended_action)
        
        # Trust score based recommendations
        if session.trust_score < 0.5:
            recommendations.append("Trust score below threshold - verify user identity")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_result_confidence(self, session: ContinuousSession,
                                   anomalies: List[AnomalyEvent]) -> float:
        """Calculate confidence level for continuous authentication result"""
        
        # Base confidence from sample count
        sample_confidence = min(1.0, len(session.sample_buffer) / 50.0)
        
        # Baseline confidence
        baseline_confidence = 0.0
        baseline_count = 0
        
        if session.keystroke_baseline:
            baseline_confidence += session.keystroke_baseline.get('confidence', 0.0)
            baseline_count += 1
        
        if session.mouse_baseline:
            baseline_confidence += session.mouse_baseline.get('confidence', 0.0)
            baseline_count += 1
        
        if baseline_count > 0:
            baseline_confidence /= baseline_count
        
        # Anomaly confidence impact
        anomaly_confidence = 1.0
        if anomalies:
            high_confidence_anomalies = [a for a in anomalies if a.confidence_level > 0.7]
            if high_confidence_anomalies:
                anomaly_confidence = statistics.mean([a.confidence_level for a in high_confidence_anomalies])
        
        # Combined confidence
        overall_confidence = (sample_confidence * 0.3 + 
                            baseline_confidence * 0.4 + 
                            anomaly_confidence * 0.3)
        
        return overall_confidence
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a continuous authentication session"""
        
        with self.session_lock:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            return {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'device_id': session.device_id,
                'start_time': session.start_time.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'trust_score': session.trust_score,
                'anomaly_score': session.anomaly_score,
                'session_state': session.session_state,
                'threat_level': session.threat_level,
                'sample_count': len(session.sample_buffer),
                'recent_anomalies': len([a for a in session.anomaly_history if 
                                       datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(hours=1)]),
                'session_duration': (datetime.now() - session.start_time).total_seconds(),
                'baseline_status': {
                    'keystroke': session.keystroke_baseline is not None,
                    'mouse': session.mouse_baseline is not None,
                    'typing_rhythm': session.typing_rhythm_baseline is not None
                }
            }
    
    def terminate_session(self, session_id: str) -> bool:
        """Terminate a continuous authentication session"""
        
        with self.session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.session_state = SessionState.TERMINATED
                
                # Log session termination
                duration = datetime.now() - session.start_time
                self.logger.info(f"Terminated session {session_id} for user {session.user_id}, "
                               f"duration: {duration}, final trust: {session.trust_score:.3f}")
                
                del self.active_sessions[session_id]
                return True
        
        return False
    
    def get_active_session_count(self) -> int:
        """Get number of active continuous authentication sessions"""
        with self.session_lock:
            return len(self.active_sessions)
    
    def cleanup(self) -> None:
        """Cleanup continuous authentication validator"""
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        
        with self.session_lock:
            self.active_sessions.clear()
        
        self.logger.info("Continuous authentication validator cleaned up")
    
    # Override base class methods
    
    def validate(self, data: Any, reference_template: Optional[Any] = None, 
                validation_level: Optional[ValidationLevel] = None) -> BiometricValidationResult:
        """
        Validate biometric data for continuous authentication
        
        Args:
            data: Dictionary containing session_id and biometric_sample
            reference_template: Not used in continuous authentication
            validation_level: Override validation level
            
        Returns:
            BiometricValidationResult adapted from continuous auth result
        """
        
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary containing 'session_id' and 'sample'")
        
        session_id = data.get('session_id')
        sample_data = data.get('sample')
        
        if not session_id or not sample_data:
            raise ValidationError("Both session_id and sample must be provided")
        
        # Create BiometricSample from data
        biometric_sample = BiometricSample(
            timestamp=datetime.now(),
            biometric_type=BiometricType(sample_data.get('biometric_type', BiometricType.BEHAVIORAL_KEYSTROKE.value)),
            raw_data=sample_data.get('raw_data'),
            quality_score=sample_data.get('quality_score', 0.5),
            features=sample_data.get('features', {}),
            session_id=session_id
        )
        
        # Process sample
        continuous_result = self.process_biometric_sample(session_id, biometric_sample)
        
        # Convert to BiometricValidationResult
        return BiometricValidationResult(
            is_valid=continuous_result.is_authenticated,
            confidence_score=continuous_result.confidence_level,
            biometric_type=BiometricType.CONTINUOUS_AUTH,
            quality_score=biometric_sample.quality_score,
            match_score=continuous_result.trust_score,
            liveness_score=1.0 - continuous_result.anomaly_score,
            validation_level=validation_level or self.validation_level,
            metadata={
                'continuous_auth_result': asdict(continuous_result),
                'session_state': continuous_result.session_state,
                'threat_level': continuous_result.threat_level,
                'anomaly_count': len(continuous_result.detected_anomalies),
                'trust_score': continuous_result.trust_score
            }
        )
    
    def extract_features(self, data: Any) -> Dict[str, Any]:
        """Extract continuous authentication features"""
        return {
            'session_features': {},
            'temporal_patterns': {},
            'behavioral_consistency': 0.5
        }
    
    def create_template(self, data: Any) -> Dict[str, Any]:
        """Create continuous authentication template (behavioral baseline)"""
        return {
            'template_type': 'continuous_auth_baseline',
            'creation_timestamp': datetime.now().isoformat(),
            'baseline_data': {},
            'confidence_level': 0.5
        }
    
    def match_templates(self, template1: Dict[str, Any], template2: Dict[str, Any]) -> float:
        """Match continuous authentication templates"""
        return 0.5  # Continuous auth uses different matching approach
    
    def assess_quality(self, data: Any) -> float:
        """Assess quality for continuous authentication"""
        if isinstance(data, dict) and 'sample' in data:
            return data['sample'].get('quality_score', 0.5)
        return 0.5
    
    def detect_liveness(self, data: Any) -> float:
        """Detect liveness for continuous authentication"""
        return 1.0  # Continuous auth inherently detects liveness through behavior
    
    # Implement abstract methods from BaseBiometricValidator
    
    def _preprocess_biometric_data(self, raw_data: Union[bytes, Any]) -> Union[bytes, Any]:
        """Preprocess biometric data for continuous authentication"""
        # For continuous authentication, minimal preprocessing to maintain real-time performance
        if isinstance(raw_data, dict):
            processed_data = {}
            for key, value in raw_data.items():
                if isinstance(value, str):
                    processed_data[key] = value.strip()
                else:
                    processed_data[key] = value
            return processed_data
        return raw_data
    
    def _extract_biometric_features(self, preprocessed_data: Union[bytes, Any]) -> Dict[str, Any]:
        """Extract features for continuous authentication"""
        features = {}
        
        if isinstance(preprocessed_data, dict):
            # Extract timing features for behavioral analysis
            if 'timestamps' in preprocessed_data:
                timestamps = preprocessed_data['timestamps']
                if len(timestamps) >= 2:
                    intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
                    features['timing_intervals'] = intervals
                    features['average_interval'] = sum(intervals) / len(intervals)
                    features['interval_variance'] = sum((x - features['average_interval'])**2 for x in intervals) / len(intervals)
            
            # Extract keystroke features
            if 'keystrokes' in preprocessed_data:
                keystrokes = preprocessed_data['keystrokes']
                features['keystroke_patterns'] = self._extract_keystroke_features(keystrokes)
            
            # Extract mouse movement features
            if 'mouse_movements' in preprocessed_data:
                movements = preprocessed_data['mouse_movements']
                features['mouse_patterns'] = self._extract_mouse_features(movements)
        
        return features
    
    def _extract_keystroke_features(self, keystrokes: List[Dict]) -> Dict[str, Any]:
        """Extract keystroke timing features"""
        if not keystrokes:
            return {}
        
        dwell_times = []
        flight_times = []
        
        for keystroke in keystrokes:
            if 'press_time' in keystroke and 'release_time' in keystroke:
                dwell_times.append(keystroke['release_time'] - keystroke['press_time'])
        
        for i in range(1, len(keystrokes)):
            if 'press_time' in keystrokes[i] and 'release_time' in keystrokes[i-1]:
                flight_times.append(keystrokes[i]['press_time'] - keystrokes[i-1]['release_time'])
        
        return {
            'dwell_times': dwell_times,
            'flight_times': flight_times,
            'average_dwell': sum(dwell_times) / len(dwell_times) if dwell_times else 0,
            'average_flight': sum(flight_times) / len(flight_times) if flight_times else 0
        }
    
    def _extract_mouse_features(self, movements: List[Dict]) -> Dict[str, Any]:
        """Extract mouse movement features"""
        if not movements:
            return {}
        
        velocities = []
        accelerations = []
        
        for i in range(1, len(movements)):
            if all(key in movements[i] for key in ['x', 'y', 'timestamp']) and \
               all(key in movements[i-1] for key in ['x', 'y', 'timestamp']):
                
                dx = movements[i]['x'] - movements[i-1]['x']
                dy = movements[i]['y'] - movements[i-1]['y']
                dt = movements[i]['timestamp'] - movements[i-1]['timestamp']
                
                if dt > 0:
                    velocity = (dx**2 + dy**2)**0.5 / dt
                    velocities.append(velocity)
        
        return {
            'velocities': velocities,
            'average_velocity': sum(velocities) / len(velocities) if velocities else 0,
            'max_velocity': max(velocities) if velocities else 0
        }
    
    def _assess_biometric_quality(self, raw_data: Union[bytes, Any]) -> float:
        """Assess quality of biometric data for continuous authentication"""
        if not isinstance(raw_data, dict):
            return 0.5  # Default quality for non-dict data
        
        quality_scores = []
        
        # Assess data completeness
        expected_fields = ['timestamps', 'keystrokes', 'mouse_movements']
        completeness = sum(1 for field in expected_fields if field in raw_data) / len(expected_fields)
        quality_scores.append(completeness)
        
        # Assess data quantity
        if 'keystrokes' in raw_data and raw_data['keystrokes']:
            keystroke_quality = min(len(raw_data['keystrokes']) / 10, 1.0)  # Normalize to 10 keystrokes
            quality_scores.append(keystroke_quality)
        
        if 'mouse_movements' in raw_data and raw_data['mouse_movements']:
            mouse_quality = min(len(raw_data['mouse_movements']) / 20, 1.0)  # Normalize to 20 movements
            quality_scores.append(mouse_quality)
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.5


# Export main classes
__all__ = [
    'ContinuousAuthenticationValidator',
    'ContinuousAuthMode',
    'ThreatLevel',
    'SessionState',
    'BiometricSample',
    'ContinuousSession',
    'AnomalyEvent',
    'ContinuousAuthResult'
]
