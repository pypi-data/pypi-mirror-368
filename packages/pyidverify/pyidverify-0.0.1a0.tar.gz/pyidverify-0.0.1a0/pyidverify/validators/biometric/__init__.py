"""
Base Biometric Validator

Provides the foundational validator class specifically for biometric validation
operations. Extends the core BaseValidator with biometric-specific functionality
including template management, liveness detection, and anti-spoofing measures.

Features:
- Biometric template processing and storage
- Liveness detection integration
- Multi-modal biometric support
- Quality assessment and thresholding
- Anti-spoofing security measures
- Performance optimization for real-time processing
- Comprehensive audit logging for biometric operations

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for biometric data handling
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from abc import abstractmethod
from datetime import datetime, timezone
import uuid

from ...core.base_validator import BaseValidator
from ...core.interfaces import ValidatorInfo, ValidatorCapability, create_validator_info
from ...core.types import (
    IDType,
    ValidationLevel,
    ValidationResult,
    ValidationStatus,
    ValidationMetadata,
    BiometricType,
    BiometricQuality,
    BiometricTemplate,
    BiometricValidationResult,
    LivenessDetectionResult
)
from ...core.exceptions import ValidationError, BiometricError, SecurityError
from ...core.biometric_engine import BiometricEngine, get_biometric_engine
from ...security import SecurityManager

# Configure logging
logger = logging.getLogger(__name__)


class BaseBiometricValidator(BaseValidator):
    """
    Abstract base class for all biometric validators in PyIDVerify.
    
    Extends BaseValidator with biometric-specific functionality including
    template management, liveness detection, quality assessment, and
    security measures specific to biometric data processing.
    """
    
    def __init__(self, 
                 biometric_type: BiometricType,
                 enable_liveness_detection: bool = True,
                 quality_threshold: BiometricQuality = BiometricQuality.FAIR,
                 **kwargs):
        """
        Initialize biometric validator.
        
        Args:
            biometric_type: Type of biometric this validator handles
            enable_liveness_detection: Whether to perform liveness detection
            quality_threshold: Minimum quality threshold for validation
            **kwargs: Additional arguments passed to BaseValidator
        """
        # Set biometric_type FIRST - needed by _create_validator_info() during parent initialization
        self.biometric_type = biometric_type
        self.enable_liveness_detection = enable_liveness_detection
        self.quality_threshold = quality_threshold
        
        # Initialize base validator with biometric-specific ID type
        id_type = self._biometric_type_to_id_type(biometric_type)
        super().__init__(id_type=id_type, **kwargs)
        
        # Get biometric engine instance
        self.biometric_engine = get_biometric_engine()
        
        # Security manager for biometric data protection
        self.security_manager = SecurityManager()
        
        # Biometric-specific metrics
        self._biometric_metrics = {
            'total_biometric_validations': 0,
            'liveness_checks_performed': 0,
            'spoofing_attempts_detected': 0,
            'quality_rejections': 0,
            'template_matches': 0,
            'template_mismatches': 0,
            'average_quality_score': 0.0
        }
        
        logger.info(f"BaseBiometricValidator initialized for {biometric_type.value}")
    
    def _biometric_type_to_id_type(self, biometric_type: BiometricType) -> IDType:
        """Convert BiometricType to IDType for base validator."""
        mapping = {
            BiometricType.FINGERPRINT: IDType.FINGERPRINT,
            BiometricType.FACIAL: IDType.FACIAL_RECOGNITION,
            BiometricType.IRIS: IDType.IRIS_SCAN,
            BiometricType.RETINAL: IDType.RETINAL_SCAN,
            BiometricType.VOICE: IDType.VOICE_PATTERN,
            BiometricType.PALM_PRINT: IDType.PALM_PRINT,
            BiometricType.DNA: IDType.DNA_PATTERN,
            BiometricType.KEYSTROKE: IDType.KEYSTROKE_DYNAMICS,
            BiometricType.MOUSE_DYNAMICS: IDType.MOUSE_PATTERNS,
            BiometricType.GAIT: IDType.GAIT_ANALYSIS,
            BiometricType.SIGNATURE: IDType.SIGNATURE_DYNAMICS,
            BiometricType.TYPING_RHYTHM: IDType.TYPING_RHYTHM,
            BiometricType.MULTI_MODAL: IDType.MULTI_BIOMETRIC,
            BiometricType.CONTINUOUS: IDType.CONTINUOUS_AUTH,
            BiometricType.RISK_BASED: IDType.BIOMETRIC_RISK_SCORE
        }
        return mapping.get(biometric_type, IDType.CUSTOM)
    
    @abstractmethod
    def _preprocess_biometric_data(self, raw_data: Union[bytes, Any]) -> Union[bytes, Any]:
        """
        Preprocess raw biometric data before validation.
        
        Subclasses must implement this method to handle biometric-specific
        preprocessing such as image normalization, audio filtering, etc.
        
        Args:
            raw_data: Raw biometric sample data
            
        Returns:
            Preprocessed biometric data
            
        Raises:
            BiometricError: If preprocessing fails
        """
        pass
    
    @abstractmethod
    def _extract_biometric_features(self, preprocessed_data: Union[bytes, Any]) -> Dict[str, Any]:
        """
        Extract biometric features from preprocessed data.
        
        Subclasses must implement this method to extract the specific
        features relevant to their biometric modality.
        
        Args:
            preprocessed_data: Preprocessed biometric data
            
        Returns:
            Dictionary of extracted features
            
        Raises:
            BiometricError: If feature extraction fails
        """
        pass
    
    @abstractmethod
    def _assess_biometric_quality(self, raw_data: Union[bytes, Any]) -> BiometricQuality:
        """
        Assess the quality of a biometric sample.
        
        Subclasses must implement quality assessment specific to their
        biometric modality (e.g., image clarity, audio SNR, etc.).
        
        Args:
            raw_data: Raw biometric sample data
            
        Returns:
            Quality assessment result
            
        Raises:
            BiometricError: If quality assessment fails
        """
        pass
    
    def _perform_liveness_detection(self, raw_data: Union[bytes, Any]) -> Tuple[LivenessDetectionResult, float]:
        """
        Perform liveness detection on biometric sample.
        
        Default implementation returns INCONCLUSIVE. Subclasses should
        override this method to implement modality-specific liveness detection.
        
        Args:
            raw_data: Raw biometric sample data
            
        Returns:
            Tuple of (liveness_result, confidence_score)
        """
        logger.warning(f"Liveness detection not implemented for {self.biometric_type.value}")
        return LivenessDetectionResult.INCONCLUSIVE, 0.5
    
    async def validate_biometric(self, 
                                raw_data: Union[bytes, Any],
                                reference_template: Optional[BiometricTemplate] = None,
                                validation_level: ValidationLevel = ValidationLevel.STANDARD) -> BiometricValidationResult:
        """
        Perform comprehensive biometric validation.
        
        Args:
            raw_data: Raw biometric sample data
            reference_template: Reference template for comparison (optional)
            validation_level: Level of validation rigor to apply
            
        Returns:
            Comprehensive biometric validation result
            
        Raises:
            BiometricError: If validation fails due to biometric processing issues
            ValidationError: If validation parameters are invalid
        """
        start_time = time.time()
        
        try:
            # Update metrics
            self._biometric_metrics['total_biometric_validations'] += 1
            
            # Log security event
            self.security_manager.log_security_event(
                "biometric_validation_started", 
                {
                    'biometric_type': self.biometric_type.value,
                    'has_reference_template': reference_template is not None,
                    'validation_level': validation_level.value if hasattr(validation_level, 'value') else str(validation_level)
                }
            )
            
            # Step 1: Preprocess biometric data
            preprocessed_data = self._preprocess_biometric_data(raw_data)
            
            # Step 2: Assess quality
            quality = self._assess_biometric_quality(raw_data)
            self._update_quality_metrics(quality)
            
            if quality.value < self.quality_threshold.value:
                self._biometric_metrics['quality_rejections'] += 1
                return BiometricValidationResult(
                    is_valid=False,
                    id_type=self.id_type,
                    original_value="[BIOMETRIC_DATA]",
                    normalized_value="[BIOMETRIC_DATA]",
                    confidence_score=0.0,
                    risk_score=1.0,
                    status=ValidationStatus.FAILED,
                    biometric_type=self.biometric_type,
                    quality_score=quality,
                    errors=[f"Biometric quality ({quality.name}) below threshold ({self.quality_threshold.name})"]
                )
            
            # Step 3: Liveness detection (if enabled)
            liveness_result = None
            liveness_score = None
            
            if self.enable_liveness_detection:
                self._biometric_metrics['liveness_checks_performed'] += 1
                liveness_result, liveness_score = self._perform_liveness_detection(raw_data)
                
                if liveness_result == LivenessDetectionResult.SPOOF:
                    self._biometric_metrics['spoofing_attempts_detected'] += 1
                    self.security_manager.log_security_event(
                        "spoofing_attempt_detected",
                        {
                            'biometric_type': self.biometric_type.value,
                            'liveness_score': liveness_score
                        }
                    )
                    
                    return BiometricValidationResult(
                        is_valid=False,
                        id_type=self.id_type,
                        original_value="[BIOMETRIC_DATA]",
                        normalized_value="[BIOMETRIC_DATA]",
                        confidence_score=0.0,
                        risk_score=1.0,
                        status=ValidationStatus.FAILED,
                        biometric_type=self.biometric_type,
                        quality_score=quality,
                        liveness_score=liveness_score,
                        errors=["Spoofing attempt detected - biometric sample not from live person"]
                    )
            
            # Step 4: Feature extraction
            features = self._extract_biometric_features(preprocessed_data)
            
            # Step 5: Template generation
            current_template = BiometricTemplate(
                biometric_type=self.biometric_type,
                encrypted_features=self.security_manager.encrypt_data(str(features).encode()),
                quality_score=quality,
                metadata={
                    'validator_type': self.__class__.__name__,
                    'processing_version': '1.0.0',
                    'feature_count': len(features),
                    'liveness_checked': self.enable_liveness_detection,
                    'liveness_result': liveness_result.value if liveness_result else None
                }
            )
            
            # Step 6: Template matching (if reference provided)
            is_valid = True
            confidence_score = 0.9  # Default high confidence for enrollment
            match_score = None
            
            if reference_template:
                match_score = await self._match_biometric_templates(current_template, reference_template)
                threshold = self._get_matching_threshold(quality, validation_level)
                is_valid = match_score >= threshold
                confidence_score = match_score
                
                if is_valid:
                    self._biometric_metrics['template_matches'] += 1
                else:
                    self._biometric_metrics['template_mismatches'] += 1
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Create comprehensive validation result
            result = BiometricValidationResult(
                is_valid=is_valid,
                id_type=self.id_type,
                original_value="[BIOMETRIC_DATA]",
                normalized_value="[BIOMETRIC_DATA]",
                confidence_score=confidence_score,
                risk_score=1.0 - confidence_score,
                status=ValidationStatus.VALID if is_valid else ValidationStatus.FAILED,
                biometric_type=self.biometric_type,
                quality_score=quality,
                liveness_score=liveness_score,
                template_id=current_template.template_id,
                matching_algorithm=self.__class__.__name__,
                metadata={
                    'processing_time_ms': processing_time,
                    'validation_level': validation_level.value if hasattr(validation_level, 'value') else str(validation_level),
                    'liveness_detection_enabled': self.enable_liveness_detection,
                    'liveness_result': liveness_result.value if liveness_result else None,
                    'template_matching_performed': reference_template is not None,
                    'match_score': match_score,
                    'matching_threshold': threshold if reference_template else None,
                    'quality_threshold_used': self.quality_threshold.value,
                    'feature_extraction_successful': True
                }
            )
            
            # Log successful validation
            self.security_manager.log_security_event(
                "biometric_validation_completed",
                {
                    'biometric_type': self.biometric_type.value,
                    'is_valid': is_valid,
                    'confidence_score': confidence_score,
                    'processing_time_ms': processing_time
                }
            )
            
            logger.info(f"Biometric validation completed: {self.biometric_type.value}, "
                       f"Valid: {is_valid}, Confidence: {confidence_score:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Biometric validation failed: {e}")
            self.security_manager.log_security_event(
                "biometric_validation_error",
                {
                    'biometric_type': self.biometric_type.value,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            
            return BiometricValidationResult(
                is_valid=False,
                id_type=self.id_type,
                original_value="[BIOMETRIC_DATA]",
                normalized_value="[BIOMETRIC_DATA]",
                confidence_score=0.0,
                risk_score=1.0,
                status=ValidationStatus.ERROR,
                biometric_type=self.biometric_type,
                errors=[f"Biometric validation error: {str(e)}"]
            )
    
    async def _match_biometric_templates(self, 
                                        template1: BiometricTemplate, 
                                        template2: BiometricTemplate) -> float:
        """
        Match two biometric templates and return similarity score.
        
        Default implementation provides basic template comparison.
        Subclasses should override for modality-specific matching.
        
        Args:
            template1: First template to compare
            template2: Second template to compare
            
        Returns:
            Similarity score between 0.0 and 1.0
            
        Raises:
            BiometricError: If template matching fails
        """
        if template1.biometric_type != template2.biometric_type:
            raise BiometricError("Cannot match templates of different biometric types")
        
        # Basic template comparison (subclasses should override)
        # This is a placeholder implementation
        features1_hash = self.security_manager.hash_data(template1.encrypted_features)
        features2_hash = self.security_manager.hash_data(template2.encrypted_features)
        
        # Simple hash-based comparison (not suitable for production)
        if features1_hash == features2_hash:
            return 1.0
        else:
            # Use quality scores to estimate similarity
            quality_similarity = 1.0 - abs(template1.quality_score.value - template2.quality_score.value) / 5.0
            return max(0.0, quality_similarity * 0.7)  # Conservative estimate
    
    def _get_matching_threshold(self, 
                               quality: BiometricQuality, 
                               validation_level: ValidationLevel) -> float:
        """
        Get matching threshold based on quality and validation level.
        
        Args:
            quality: Sample quality
            validation_level: Validation rigor level
            
        Returns:
            Matching threshold between 0.0 and 1.0
        """
        base_thresholds = {
            BiometricType.FINGERPRINT: 0.8,
            BiometricType.FACIAL: 0.75,
            BiometricType.IRIS: 0.9,
            BiometricType.RETINAL: 0.95,
            BiometricType.VOICE: 0.7,
            BiometricType.PALM_PRINT: 0.8,
            BiometricType.DNA: 0.99,
            BiometricType.KEYSTROKE: 0.6,
            BiometricType.MOUSE_DYNAMICS: 0.6,
            BiometricType.GAIT: 0.65,
            BiometricType.SIGNATURE: 0.7,
            BiometricType.TYPING_RHYTHM: 0.6
        }
        
        base_threshold = base_thresholds.get(self.biometric_type, 0.7)
        
        # Adjust based on quality
        quality_adjustments = {
            BiometricQuality.POOR: -0.2,
            BiometricQuality.FAIR: -0.1,
            BiometricQuality.GOOD: 0.0,
            BiometricQuality.VERY_GOOD: 0.05,
            BiometricQuality.EXCELLENT: 0.1
        }
        
        # Adjust based on validation level
        level_adjustments = {
            ValidationLevel.BASIC: -0.1,
            ValidationLevel.STANDARD: 0.0,
            ValidationLevel.STRICT: 0.1,
            ValidationLevel.MAXIMUM: 0.2
        }
        
        quality_adj = quality_adjustments.get(quality, 0.0)
        level_adj = level_adjustments.get(validation_level, 0.0)
        
        final_threshold = base_threshold + quality_adj + level_adj
        return max(0.1, min(0.99, final_threshold))
    
    def _update_quality_metrics(self, quality: BiometricQuality) -> None:
        """Update running quality metrics."""
        current_avg = self._biometric_metrics['average_quality_score']
        total_validations = self._biometric_metrics['total_biometric_validations']
        
        new_avg = ((current_avg * (total_validations - 1)) + quality.value) / total_validations
        self._biometric_metrics['average_quality_score'] = new_avg
    
    # Override base validator methods to use biometric-specific logic
    
    def _validate_internal(self, value: str, validation_level: ValidationLevel = None) -> ValidationResult:
        """
        Internal validation method - not used for biometric validation.
        
        Biometric validators should use validate_biometric() instead.
        This method is implemented to satisfy the BaseValidator interface.
        """
        logger.warning(f"_validate_internal called on biometric validator - use validate_biometric() instead")
        return ValidationResult(
            is_valid=False,
            id_type=self.id_type,
            original_value=value,
            normalized_value=value,
            confidence_score=0.0,
            risk_score=1.0,
            status=ValidationStatus.ERROR,
            errors=["Use validate_biometric() method for biometric validation"]
        )
    
    def _create_validator_info(self) -> ValidatorInfo:
        """Create validator information for this biometric validator."""
        # Handle case where attributes might not be set yet during initialization
        biometric_type = getattr(self, 'biometric_type', None)
        id_type = getattr(self, 'id_type', None) 
        enable_liveness_detection = getattr(self, 'enable_liveness_detection', True)
        quality_threshold = getattr(self, 'quality_threshold', 0.5)
        
        # Use defaults if attributes aren't available yet
        if biometric_type is None:
            biometric_type_value = "unknown"
            biometric_display_name = "Unknown Biometric"
            biometric_category = "unknown"
        else:
            biometric_type_value = biometric_type.value
            biometric_display_name = getattr(biometric_type, 'display_name', biometric_type.value)
            biometric_category = getattr(biometric_type, 'category', 'unknown')
            
        if quality_threshold is None:
            quality_threshold = 0.5
            quality_threshold_name = "MEDIUM"
        else:
            quality_threshold_name = getattr(quality_threshold, 'name', str(quality_threshold))
        
        capabilities = [
            ValidatorCapability.BATCH_PROCESSING,
            ValidatorCapability.ASYNC_PROCESSING,
            ValidatorCapability.CACHING,
            ValidatorCapability.SECURITY_SCANNING,
            ValidatorCapability.COMPLIANCE_CHECKING,
            # Biometric-specific capabilities
            "LIVENESS_DETECTION",
            "QUALITY_ASSESSMENT",
            "TEMPLATE_MATCHING",
            "ANTI_SPOOFING"
        ]
        
        return create_validator_info(
            name=f"{biometric_type_value.title()}BiometricValidator",
            version="1.0.0",
            description=f"Biometric validator for {biometric_display_name}",
            supported_types={id_type} if id_type else set(),
            capabilities=set(capabilities)
        )
    
    def get_biometric_metrics(self) -> Dict[str, Any]:
        """
        Get biometric-specific performance metrics.
        
        Returns:
            Dictionary of biometric validation metrics
        """
        return self._biometric_metrics.copy()
    
    def reset_biometric_metrics(self) -> None:
        """Reset biometric performance metrics."""
        self._biometric_metrics = {
            'total_biometric_validations': 0,
            'liveness_checks_performed': 0,
            'spoofing_attempts_detected': 0,
            'quality_rejections': 0,
            'template_matches': 0,
            'template_mismatches': 0,
            'average_quality_score': 0.0
        }
        logger.info(f"Biometric metrics reset for {self.biometric_type.value}")
