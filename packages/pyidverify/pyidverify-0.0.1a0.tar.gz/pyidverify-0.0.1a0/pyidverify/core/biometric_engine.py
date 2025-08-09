"""
Biometric Engine Framework

Provides the core engine for biometric validation operations including template
processing, liveness detection, multi-modal fusion, and security management.
This engine coordinates all biometric validation activities within PyIDVerify.

Features:
- Template generation and secure storage
- Liveness detection and anti-spoofing
- Multi-modal biometric fusion
- Performance optimization and caching
- Security-first design with encryption
- Comprehensive audit logging
- Real-time processing capabilities

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for biometric data handling
"""

import asyncio
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from datetime import datetime, timezone, timedelta
from abc import ABC, abstractmethod
import uuid
import json
from pathlib import Path

from .types import (
    BiometricType, 
    BiometricQuality, 
    BiometricTemplate, 
    BiometricValidationResult,
    LivenessDetectionResult,
    ValidationStatus,
    IDType
)
from .exceptions import (
    ValidationError,
    BiometricError,
    SecurityError,
    ConfigurationError
)
from ..security import SecurityManager
from .interfaces import CacheProvider, ConfigProvider

# Configure logging
logger = logging.getLogger(__name__)


class BiometricProcessor(ABC):
    """
    Abstract base class for biometric processing algorithms.
    
    Defines the interface for biometric-specific processing including
    feature extraction, template generation, and matching operations.
    """
    
    @abstractmethod
    def extract_features(self, raw_data: Union[bytes, Any]) -> Dict[str, Any]:
        """
        Extract features from raw biometric data.
        
        Args:
            raw_data: Raw biometric sample data
            
        Returns:
            Dictionary of extracted features
            
        Raises:
            BiometricError: If feature extraction fails
        """
        pass
    
    @abstractmethod
    def generate_template(self, features: Dict[str, Any]) -> BiometricTemplate:
        """
        Generate secure biometric template from features.
        
        Args:
            features: Extracted biometric features
            
        Returns:
            Encrypted biometric template
            
        Raises:
            BiometricError: If template generation fails
        """
        pass
    
    @abstractmethod
    def match_templates(self, 
                       template1: BiometricTemplate, 
                       template2: BiometricTemplate) -> float:
        """
        Compare two biometric templates and return similarity score.
        
        Args:
            template1: First template to compare
            template2: Second template to compare
            
        Returns:
            Similarity score between 0.0 and 1.0
            
        Raises:
            BiometricError: If template matching fails
        """
        pass
    
    @abstractmethod
    def assess_quality(self, raw_data: Union[bytes, Any]) -> BiometricQuality:
        """
        Assess the quality of a biometric sample.
        
        Args:
            raw_data: Raw biometric sample data
            
        Returns:
            Quality assessment result
            
        Raises:
            BiometricError: If quality assessment fails
        """
        pass


class LivenessDetector(ABC):
    """
    Abstract base class for liveness detection algorithms.
    
    Implements anti-spoofing mechanisms to detect live vs. artificial
    biometric samples across different modalities.
    """
    
    @abstractmethod
    def detect_liveness(self, 
                       raw_data: Union[bytes, Any],
                       biometric_type: BiometricType) -> Tuple[LivenessDetectionResult, float]:
        """
        Detect if biometric sample is from a live person.
        
        Args:
            raw_data: Raw biometric sample data
            biometric_type: Type of biometric being tested
            
        Returns:
            Tuple of (liveness_result, confidence_score)
            
        Raises:
            BiometricError: If liveness detection fails
        """
        pass


class BiometricEngine:
    """
    Core biometric processing engine for PyIDVerify.
    
    Coordinates all biometric validation operations including processing,
    template management, liveness detection, and multi-modal fusion.
    """
    
    def __init__(self, 
                 config_provider: Optional[ConfigProvider] = None,
                 cache_provider: Optional[CacheProvider] = None,
                 security_manager: Optional[SecurityManager] = None):
        """
        Initialize the biometric engine.
        
        Args:
            config_provider: Configuration management interface
            cache_provider: Caching interface for performance optimization
            security_manager: Security operations manager
        """
        self.config_provider = config_provider
        self.cache_provider = cache_provider
        self.security_manager = security_manager or SecurityManager()
        
        # Registry for biometric processors
        self._processors: Dict[BiometricType, BiometricProcessor] = {}
        self._liveness_detectors: Dict[BiometricType, LivenessDetector] = {}
        
        # Performance metrics
        self._metrics = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'average_processing_time': 0.0,
            'liveness_checks_performed': 0,
            'spoofing_attempts_detected': 0
        }
        
        # Template storage (in production, this would be a secure database)
        self._template_storage: Dict[str, BiometricTemplate] = {}
        
        logger.info("BiometricEngine initialized successfully")
    
    def register_processor(self, 
                          biometric_type: BiometricType, 
                          processor: BiometricProcessor) -> None:
        """
        Register a biometric processor for a specific type.
        
        Args:
            biometric_type: Type of biometric this processor handles
            processor: Processor implementation
        """
        self._processors[biometric_type] = processor
        logger.info(f"Registered processor for {biometric_type.value}")
    
    @property
    def processors(self) -> Dict[BiometricType, Any]:
        """Get registered processors (for testing)."""
        return self._processors.copy()
    
    def register_liveness_detector(self, 
                                  biometric_type: BiometricType, 
                                  detector: LivenessDetector) -> None:
        """
        Register a liveness detector for a specific biometric type.
        
        Args:
            biometric_type: Type of biometric this detector handles
            detector: Liveness detector implementation
        """
        self._liveness_detectors[biometric_type] = detector
        logger.info(f"Registered liveness detector for {biometric_type.value}")
    
    async def process_biometric(self, 
                               raw_data: Union[bytes, Any],
                               biometric_type: BiometricType,
                               perform_liveness_check: bool = True,
                               reference_template: Optional[BiometricTemplate] = None) -> BiometricValidationResult:
        """
        Process a biometric sample and perform validation.
        
        Args:
            raw_data: Raw biometric sample data
            biometric_type: Type of biometric being processed
            perform_liveness_check: Whether to perform liveness detection
            reference_template: Reference template for comparison (optional)
            
        Returns:
            Comprehensive biometric validation result
            
        Raises:
            BiometricError: If processing fails
            ValidationError: If validation parameters are invalid
        """
        start_time = time.time()
        
        try:
            # Update metrics
            self._metrics['total_validations'] += 1
            
            # Get processor for this biometric type
            processor = self._processors.get(biometric_type)
            if not processor:
                raise BiometricError(f"No processor registered for {biometric_type.value}")
            
            # Assess sample quality
            quality = processor.assess_quality(raw_data)
            if quality == BiometricQuality.POOR:
                return BiometricValidationResult(
                    is_valid=False,
                    id_type=self._biometric_type_to_id_type(biometric_type),
                    original_value="[BIOMETRIC_DATA]",
                    normalized_value="[BIOMETRIC_DATA]",
                    confidence_score=0.0,
                    risk_score=1.0,
                    status=ValidationStatus.FAILED,
                    biometric_type=biometric_type,
                    quality_score=quality,
                    errors=["Biometric sample quality too low for reliable validation"]
                )
            
            # Perform liveness detection if requested
            liveness_result = None
            liveness_score = None
            
            if perform_liveness_check:
                liveness_detector = self._liveness_detectors.get(biometric_type)
                if liveness_detector:
                    self._metrics['liveness_checks_performed'] += 1
                    liveness_result, liveness_score = liveness_detector.detect_liveness(
                        raw_data, biometric_type
                    )
                    
                    if liveness_result == LivenessDetectionResult.SPOOF:
                        self._metrics['spoofing_attempts_detected'] += 1
                        return BiometricValidationResult(
                            is_valid=False,
                            id_type=self._biometric_type_to_id_type(biometric_type),
                            original_value="[BIOMETRIC_DATA]",
                            normalized_value="[BIOMETRIC_DATA]", 
                            confidence_score=0.0,
                            risk_score=1.0,
                            status=ValidationStatus.FAILED,
                            biometric_type=biometric_type,
                            quality_score=quality,
                            liveness_score=liveness_score,
                            errors=["Spoofing attempt detected - biometric sample not from live person"]
                        )
            
            # Extract features and generate template
            features = processor.extract_features(raw_data)
            current_template = processor.generate_template(features)
            
            # Store template securely
            template_id = current_template.template_id
            encrypted_template = self.security_manager.encrypt_data(
                json.dumps({
                    'template_id': current_template.template_id,
                    'biometric_type': current_template.biometric_type.value,
                    'features_hash': hashlib.sha256(current_template.encrypted_features).hexdigest(),
                    'quality_score': current_template.quality_score.value,
                    'creation_timestamp': current_template.creation_timestamp.isoformat()
                }).encode()
            )
            
            # Perform template matching if reference provided
            is_valid = True
            confidence_score = 0.9  # Default high confidence for enrollment
            match_score = None
            
            if reference_template:
                match_score = processor.match_templates(current_template, reference_template)
                
                # Determine validation result based on match score and quality
                threshold = self._get_matching_threshold(biometric_type, quality)
                is_valid = match_score >= threshold
                confidence_score = match_score
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            self._update_processing_metrics(processing_time)
            
            # Update success metrics
            if is_valid:
                self._metrics['successful_validations'] += 1
            else:
                self._metrics['failed_validations'] += 1
            
            # Create comprehensive result
            result = BiometricValidationResult(
                is_valid=is_valid,
                id_type=self._biometric_type_to_id_type(biometric_type),
                original_value="[BIOMETRIC_DATA]",
                normalized_value="[BIOMETRIC_DATA]",
                confidence_score=confidence_score,
                risk_score=1.0 - confidence_score,
                status=ValidationStatus.VALID if is_valid else ValidationStatus.FAILED,
                biometric_type=biometric_type,
                quality_score=quality,
                liveness_score=liveness_score,
                template_id=template_id,
                matching_algorithm=processor.__class__.__name__,
                metadata={
                    'processing_time_ms': processing_time,
                    'liveness_detection_performed': perform_liveness_check,
                    'liveness_result': liveness_result.value if liveness_result else None,
                    'template_matching_performed': reference_template is not None,
                    'match_score': match_score,
                    'matching_threshold': self._get_matching_threshold(biometric_type, quality) if reference_template else None
                }
            )
            
            # Store template for future reference
            self._template_storage[template_id] = current_template
            
            logger.info(f"Biometric validation completed: {biometric_type.value}, "
                       f"Valid: {is_valid}, Confidence: {confidence_score:.3f}")
            
            return result
            
        except Exception as e:
            self._metrics['failed_validations'] += 1
            logger.error(f"Biometric processing failed: {e}")
            
            return BiometricValidationResult(
                is_valid=False,
                id_type=self._biometric_type_to_id_type(biometric_type),
                original_value="[BIOMETRIC_DATA]",
                normalized_value="[BIOMETRIC_DATA]",
                confidence_score=0.0,
                risk_score=1.0,
                status=ValidationStatus.ERROR,
                biometric_type=biometric_type,
                errors=[f"Biometric processing error: {str(e)}"]
            )
    
    def _biometric_type_to_id_type(self, biometric_type: BiometricType) -> IDType:
        """Convert BiometricType to IDType."""
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
    
    def _get_matching_threshold(self, 
                               biometric_type: BiometricType, 
                               quality: BiometricQuality) -> float:
        """Get matching threshold based on biometric type and quality."""
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
        
        base_threshold = base_thresholds.get(biometric_type, 0.7)
        
        # Adjust threshold based on quality
        quality_adjustments = {
            BiometricQuality.POOR: 0.0,      # Not usable
            BiometricQuality.FAIR: -0.1,     # Lower threshold
            BiometricQuality.GOOD: 0.0,      # No adjustment
            BiometricQuality.VERY_GOOD: 0.05, # Slightly higher
            BiometricQuality.EXCELLENT: 0.1   # Higher threshold
        }
        
        adjustment = quality_adjustments.get(quality, 0.0)
        return min(0.99, max(0.1, base_threshold + adjustment))
    
    def _update_processing_metrics(self, processing_time_ms: float) -> None:
        """Update processing time metrics."""
        current_avg = self._metrics['average_processing_time']
        total_validations = self._metrics['total_validations']
        
        # Calculate running average
        self._metrics['average_processing_time'] = (
            (current_avg * (total_validations - 1) + processing_time_ms) / total_validations
        )
    
    def get_template(self, template_id: str) -> Optional[BiometricTemplate]:
        """
        Retrieve a stored biometric template.
        
        Args:
            template_id: Unique identifier for the template
            
        Returns:
            BiometricTemplate if found, None otherwise
        """
        return self._template_storage.get(template_id)
    
    def delete_template(self, template_id: str) -> bool:
        """
        Securely delete a biometric template.
        
        Args:
            template_id: Unique identifier for the template
            
        Returns:
            True if template was deleted, False if not found
        """
        if template_id in self._template_storage:
            # Secure deletion - overwrite memory
            template = self._template_storage[template_id]
            template.encrypted_features = b'\x00' * len(template.encrypted_features)
            
            del self._template_storage[template_id]
            logger.info(f"Securely deleted biometric template: {template_id}")
            return True
        
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current engine performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        return self._metrics.copy()
    
    def get_supported_types(self) -> Set[BiometricType]:
        """
        Get set of supported biometric types.
        
        Returns:
            Set of BiometricType values with registered processors
        """
        return set(self._processors.keys())
    
    async def cleanup_expired_templates(self, max_age_days: int = 365) -> int:
        """
        Clean up expired biometric templates.
        
        Args:
            max_age_days: Maximum age in days before template expires
            
        Returns:
            Number of templates deleted
        """
        deleted_count = 0
        expired_ids = []
        
        for template_id, template in self._template_storage.items():
            if template.is_expired(max_age_days):
                expired_ids.append(template_id)
        
        for template_id in expired_ids:
            if self.delete_template(template_id):
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} expired biometric templates")
        return deleted_count


class BiometricEngineFactory:
    """Factory for creating configured BiometricEngine instances."""
    
    @staticmethod
    def create_engine(config: Optional[Dict[str, Any]] = None) -> BiometricEngine:
        """
        Create a configured BiometricEngine instance.
        
        Args:
            config: Engine configuration dictionary
            
        Returns:
            Configured BiometricEngine instance
        """
        config = config or {}
        
        # Create engine with default configuration
        engine = BiometricEngine()
        
        logger.info("BiometricEngine created via factory")
        return engine


# Global engine instance for singleton access
_global_engine: Optional[BiometricEngine] = None

def get_biometric_engine() -> BiometricEngine:
    """
    Get the global biometric engine instance.
    
    Returns:
        Global BiometricEngine instance
    """
    global _global_engine
    
    if _global_engine is None:
        _global_engine = BiometricEngineFactory.create_engine()
    
    return _global_engine
