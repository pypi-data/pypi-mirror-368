"""
Biometric-Specific Core Types

Extended type definitions specifically for biometric validation operations.
Complements the main types module with biometric-focused enumerations,
data structures, and utility functions.

Features:
- Biometric processing pipeline stages
- Performance measurement types
- Security classification for biometric data
- Template storage and management types
- Multi-modal fusion data structures

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for biometric data handling
"""

from enum import Enum, IntEnum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Set, Tuple, TYPE_CHECKING
from datetime import datetime, timezone
import uuid

from .types import BiometricType, BiometricQuality, BiometricTemplate, LivenessDetectionResult

if TYPE_CHECKING:
    from .types import BiometricValidationResult


class BiometricProcessingStage(Enum):
    """
    Enumeration of biometric processing pipeline stages.
    
    Tracks the current stage of biometric validation processing
    for monitoring, debugging, and performance optimization.
    """
    
    INITIALIZATION = "initialization"
    PREPROCESSING = "preprocessing"
    QUALITY_ASSESSMENT = "quality_assessment"
    LIVENESS_DETECTION = "liveness_detection"
    FEATURE_EXTRACTION = "feature_extraction"
    TEMPLATE_GENERATION = "template_generation"
    TEMPLATE_MATCHING = "template_matching"
    RESULT_GENERATION = "result_generation"
    COMPLETION = "completion"
    ERROR_HANDLING = "error_handling"


class BiometricSecurityLevel(IntEnum):
    """
    Security levels for biometric operations.
    
    Defines the security rigor applied to biometric processing
    with corresponding computational and accuracy requirements.
    """
    
    BASIC = 1          # Basic security, faster processing
    STANDARD = 2       # Standard security for most applications  
    HIGH = 3          # High security for sensitive applications
    MAXIMUM = 4       # Maximum security for critical applications
    
    @property
    def description(self) -> str:
        """Get description of this security level."""
        descriptions = {
            self.BASIC: "Basic security - optimized for speed",
            self.STANDARD: "Standard security - balanced approach",
            self.HIGH: "High security - enhanced protection",
            self.MAXIMUM: "Maximum security - maximum protection"
        }
        return descriptions[self]
    
    @property
    def min_quality_threshold(self) -> BiometricQuality:
        """Minimum quality threshold for this security level."""
        thresholds = {
            self.BASIC: BiometricQuality.FAIR,
            self.STANDARD: BiometricQuality.GOOD,
            self.HIGH: BiometricQuality.VERY_GOOD,
            self.MAXIMUM: BiometricQuality.EXCELLENT
        }
        return thresholds[self]
    
    @property
    def requires_liveness_detection(self) -> bool:
        """Whether this security level requires liveness detection."""
        return self >= self.STANDARD


class BiometricMatchingAlgorithm(Enum):
    """
    Available biometric matching algorithms.
    
    Defines the algorithms available for template comparison
    and matching operations across different biometric modalities.
    """
    
    # General algorithms
    EUCLIDEAN_DISTANCE = "euclidean_distance"
    COSINE_SIMILARITY = "cosine_similarity"
    HAMMING_DISTANCE = "hamming_distance"
    
    # Fingerprint-specific
    MINUTIAE_MATCHING = "minutiae_matching"
    RIDGE_PATTERN_MATCHING = "ridge_pattern_matching"
    
    # Facial recognition-specific
    EIGENFACES = "eigenfaces"
    FISHERFACES = "fisherfaces"
    LBPH = "lbph"
    DEEP_NEURAL_NETWORK = "deep_neural_network"
    
    # Voice-specific
    MEL_FREQUENCY_CEPSTRAL = "mel_frequency_cepstral"
    FORMANT_ANALYSIS = "formant_analysis"
    
    # Behavioral-specific
    DYNAMIC_TIME_WARPING = "dynamic_time_warping"
    STATISTICAL_MODELING = "statistical_modeling"


@dataclass
class BiometricProcessingMetrics:
    """
    Metrics collected during biometric processing.
    
    Tracks performance, accuracy, and security metrics
    for biometric validation operations.
    """
    
    processing_stage: BiometricProcessingStage = BiometricProcessingStage.INITIALIZATION
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    processing_time_ms: Optional[float] = None
    
    # Quality metrics
    input_quality: Optional[BiometricQuality] = None
    quality_assessment_time_ms: Optional[float] = None
    
    # Liveness detection metrics
    liveness_detection_performed: bool = False
    liveness_result: Optional[LivenessDetectionResult] = None
    liveness_score: Optional[float] = None
    liveness_detection_time_ms: Optional[float] = None
    
    # Feature extraction metrics
    features_extracted: Optional[int] = None
    feature_extraction_time_ms: Optional[float] = None
    feature_dimensions: Optional[int] = None
    
    # Template metrics
    template_generation_time_ms: Optional[float] = None
    template_size_bytes: Optional[int] = None
    
    # Matching metrics (if performed)
    template_matching_performed: bool = False
    matching_algorithm: Optional[BiometricMatchingAlgorithm] = None
    matching_score: Optional[float] = None
    matching_threshold: Optional[float] = None
    matching_time_ms: Optional[float] = None
    
    # Security metrics
    security_level: BiometricSecurityLevel = BiometricSecurityLevel.STANDARD
    encryption_performed: bool = False
    audit_logged: bool = False
    
    # Error tracking
    errors_encountered: List[str] = field(default_factory=list)
    warnings_generated: List[str] = field(default_factory=list)
    
    def mark_completion(self) -> None:
        """Mark processing as completed and calculate total time."""
        self.end_time = datetime.now(timezone.utc)
        self.processing_stage = BiometricProcessingStage.COMPLETION
        
        if self.start_time and self.end_time:
            time_delta = self.end_time - self.start_time
            self.processing_time_ms = time_delta.total_seconds() * 1000
    
    def add_error(self, error_message: str) -> None:
        """Add an error to the metrics."""
        self.errors_encountered.append(error_message)
        self.processing_stage = BiometricProcessingStage.ERROR_HANDLING
    
    def add_warning(self, warning_message: str) -> None:
        """Add a warning to the metrics."""
        self.warnings_generated.append(warning_message)
    
    @property
    def is_successful(self) -> bool:
        """Whether processing completed successfully."""
        return (self.processing_stage == BiometricProcessingStage.COMPLETION 
                and len(self.errors_encountered) == 0)
    
    @property
    def performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        return {
            'total_processing_time_ms': self.processing_time_ms,
            'quality_assessment_time_ms': self.quality_assessment_time_ms,
            'liveness_detection_time_ms': self.liveness_detection_time_ms,
            'feature_extraction_time_ms': self.feature_extraction_time_ms,
            'template_generation_time_ms': self.template_generation_time_ms,
            'matching_time_ms': self.matching_time_ms,
            'is_successful': self.is_successful,
            'errors_count': len(self.errors_encountered),
            'warnings_count': len(self.warnings_generated)
        }


@dataclass
class BiometricTemplateMetadata:
    """
    Extended metadata for biometric templates.
    
    Stores comprehensive information about template creation,
    processing parameters, and quality metrics.
    """
    
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    biometric_type: Optional[BiometricType] = None
    creation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Processing metadata
    processing_version: str = "1.0.0"
    algorithm_version: str = "1.0.0"
    processing_stage_metrics: Optional[BiometricProcessingMetrics] = None
    
    # Quality and security metadata
    quality_score: Optional[BiometricQuality] = None
    security_level: BiometricSecurityLevel = BiometricSecurityLevel.STANDARD
    liveness_verified: bool = False
    
    # Template characteristics
    feature_count: Optional[int] = None
    template_size_bytes: Optional[int] = None
    compression_ratio: Optional[float] = None
    
    # Validation metadata
    validation_count: int = 0
    last_validation_timestamp: Optional[datetime] = None
    successful_validations: int = 0
    failed_validations: int = 0
    
    # Expiration and maintenance
    expiration_date: Optional[datetime] = None
    maintenance_required: bool = False
    
    def record_validation(self, success: bool) -> None:
        """Record a validation attempt."""
        self.validation_count += 1
        self.last_validation_timestamp = datetime.now(timezone.utc)
        
        if success:
            self.successful_validations += 1
        else:
            self.failed_validations += 1
    
    @property
    def success_rate(self) -> float:
        """Calculate validation success rate."""
        if self.validation_count == 0:
            return 0.0
        return self.successful_validations / self.validation_count
    
    @property
    def is_expired(self) -> bool:
        """Check if template has expired."""
        if not self.expiration_date:
            return False
        return datetime.now(timezone.utc) > self.expiration_date
    
    @property
    def age_days(self) -> int:
        """Get template age in days."""
        age = datetime.now(timezone.utc) - self.creation_timestamp
        return age.days


@dataclass
class MultiModalBiometricResult:
    """
    Result structure for multi-modal biometric validation.
    
    Aggregates results from multiple biometric modalities
    and provides fusion-based confidence scoring.
    """
    
    modality_results: Dict[BiometricType, 'BiometricValidationResult'] = field(default_factory=dict)
    fusion_algorithm: str = "weighted_average"
    fusion_confidence: float = 0.0
    fusion_decision: bool = False
    
    # Individual modality contributions
    modality_weights: Dict[BiometricType, float] = field(default_factory=dict)
    modality_scores: Dict[BiometricType, float] = field(default_factory=dict)
    
    # Quality and security metrics
    overall_quality: Optional[BiometricQuality] = None
    security_level: BiometricSecurityLevel = BiometricSecurityLevel.STANDARD
    liveness_results: Dict[BiometricType, LivenessDetectionResult] = field(default_factory=dict)
    
    # Processing metadata
    processing_time_ms: Optional[float] = None
    fusion_processing_time_ms: Optional[float] = None
    
    def add_modality_result(self, 
                          biometric_type: BiometricType, 
                          result: 'BiometricValidationResult',
                          weight: float = 1.0) -> None:
        """
        Add result from a biometric modality.
        
        Args:
            biometric_type: Type of biometric modality
            result: Validation result for this modality
            weight: Weight for fusion calculation
        """
        self.modality_results[biometric_type] = result
        self.modality_weights[biometric_type] = weight
        self.modality_scores[biometric_type] = result.confidence_score
    
    def calculate_fusion_score(self) -> float:
        """
        Calculate fused confidence score from all modalities.
        
        Returns:
            Fused confidence score between 0.0 and 1.0
        """
        if not self.modality_scores:
            return 0.0
        
        # Weighted average fusion
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for biometric_type, score in self.modality_scores.items():
            weight = self.modality_weights.get(biometric_type, 1.0)
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        self.fusion_confidence = total_weighted_score / total_weight
        return self.fusion_confidence
    
    @property
    def successful_modalities(self) -> List[BiometricType]:
        """Get list of modalities that passed validation."""
        return [
            biometric_type 
            for biometric_type, result in self.modality_results.items()
            if result.is_valid
        ]
    
    @property
    def failed_modalities(self) -> List[BiometricType]:
        """Get list of modalities that failed validation.""" 
        return [
            biometric_type
            for biometric_type, result in self.modality_results.items()
            if not result.is_valid
        ]


# Utility functions for biometric type handling

def get_compatible_biometric_types(primary_type: BiometricType) -> Set[BiometricType]:
    """
    Get biometric types that are compatible for multi-modal fusion.
    
    Args:
        primary_type: Primary biometric type
        
    Returns:
        Set of compatible biometric types
    """
    compatibility_map = {
        # Physiological combinations
        BiometricType.FINGERPRINT: {BiometricType.FACIAL, BiometricType.IRIS, BiometricType.VOICE},
        BiometricType.FACIAL: {BiometricType.FINGERPRINT, BiometricType.IRIS, BiometricType.VOICE},
        BiometricType.IRIS: {BiometricType.FINGERPRINT, BiometricType.FACIAL, BiometricType.RETINAL},
        BiometricType.RETINAL: {BiometricType.IRIS, BiometricType.FACIAL},
        BiometricType.VOICE: {BiometricType.FINGERPRINT, BiometricType.FACIAL, BiometricType.KEYSTROKE},
        BiometricType.PALM_PRINT: {BiometricType.FINGERPRINT, BiometricType.FACIAL},
        
        # Behavioral combinations
        BiometricType.KEYSTROKE: {BiometricType.MOUSE_DYNAMICS, BiometricType.TYPING_RHYTHM, BiometricType.VOICE},
        BiometricType.MOUSE_DYNAMICS: {BiometricType.KEYSTROKE, BiometricType.TYPING_RHYTHM},
        BiometricType.GAIT: {BiometricType.FACIAL, BiometricType.VOICE},
        BiometricType.SIGNATURE: {BiometricType.KEYSTROKE, BiometricType.MOUSE_DYNAMICS},
        BiometricType.TYPING_RHYTHM: {BiometricType.KEYSTROKE, BiometricType.MOUSE_DYNAMICS},
    }
    
    return compatibility_map.get(primary_type, set())


def calculate_biometric_entropy(biometric_type: BiometricType) -> float:
    """
    Calculate theoretical entropy (in bits) for a biometric type.
    
    Args:
        biometric_type: Biometric type to calculate entropy for
        
    Returns:
        Entropy in bits
    """
    entropy_map = {
        # High entropy (very unique)
        BiometricType.DNA: 64.0,
        BiometricType.IRIS: 40.0,
        BiometricType.RETINAL: 35.0,
        
        # Medium-high entropy
        BiometricType.FINGERPRINT: 25.0,
        BiometricType.PALM_PRINT: 20.0,
        BiometricType.FACIAL: 18.0,
        
        # Medium entropy
        BiometricType.VOICE: 15.0,
        BiometricType.SIGNATURE: 12.0,
        
        # Lower entropy (behavioral)
        BiometricType.KEYSTROKE: 8.0,
        BiometricType.GAIT: 7.0,
        BiometricType.MOUSE_DYNAMICS: 6.0,
        BiometricType.TYPING_RHYTHM: 5.0,
    }
    
    return entropy_map.get(biometric_type, 10.0)  # Default entropy


def get_recommended_quality_threshold(biometric_type: BiometricType, 
                                    security_level: BiometricSecurityLevel) -> BiometricQuality:
    """
    Get recommended quality threshold for biometric type and security level.
    
    Args:
        biometric_type: Type of biometric
        security_level: Required security level
        
    Returns:
        Recommended quality threshold
    """
    # Base quality thresholds by biometric type
    base_thresholds = {
        BiometricType.FINGERPRINT: BiometricQuality.GOOD,
        BiometricType.FACIAL: BiometricQuality.GOOD,
        BiometricType.IRIS: BiometricQuality.VERY_GOOD,
        BiometricType.RETINAL: BiometricQuality.VERY_GOOD,
        BiometricType.VOICE: BiometricQuality.FAIR,
        BiometricType.PALM_PRINT: BiometricQuality.GOOD,
        BiometricType.DNA: BiometricQuality.EXCELLENT,
        BiometricType.KEYSTROKE: BiometricQuality.FAIR,
        BiometricType.MOUSE_DYNAMICS: BiometricQuality.FAIR,
        BiometricType.GAIT: BiometricQuality.FAIR,
        BiometricType.SIGNATURE: BiometricQuality.GOOD,
        BiometricType.TYPING_RHYTHM: BiometricQuality.FAIR,
    }
    
    base_quality = base_thresholds.get(biometric_type, BiometricQuality.GOOD)
    
    # Adjust based on security level
    if security_level >= BiometricSecurityLevel.HIGH:
        if base_quality == BiometricQuality.FAIR:
            return BiometricQuality.GOOD
        elif base_quality == BiometricQuality.GOOD:
            return BiometricQuality.VERY_GOOD
        elif base_quality == BiometricQuality.VERY_GOOD:
            return BiometricQuality.EXCELLENT
    
    if security_level == BiometricSecurityLevel.MAXIMUM:
        return BiometricQuality.EXCELLENT
    
    return base_quality
