"""
Physiological Biometric Validators

This module contains validators for physiological biometric identifiers including
fingerprint, facial recognition, iris scan, voice pattern, and other physical
biometric modalities.

Physiological biometrics are based on physical characteristics that are relatively
stable over time and unique to individuals.

Available Validators:
- FingerprintValidator: Fingerprint pattern validation
- FacialRecognitionValidator: Facial feature validation  
- IrisScanValidator: Iris pattern validation
- RetinalScanValidator: Retinal pattern validation
- VoicePatternValidator: Voice biometric validation
- PalmPrintValidator: Palm print pattern validation
- DNAPatternValidator: DNA sequence validation (high-security applications)

Copyright (c) 2024 PyIDVerify Contributors
Licensed under MIT License with additional terms for biometric data handling
"""

from typing import List, Dict, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Module version
__version__ = "1.0.0-dev"

# Available validator classes (to be imported when implemented)
__all__ = [
    # Will be populated as validators are implemented
    # 'FingerprintValidator',
    # 'FacialRecognitionValidator', 
    # 'IrisScanValidator',
    # 'RetinalScanValidator',
    # 'VoicePatternValidator',
    # 'PalmPrintValidator',
    # 'DNAPatternValidator'
]

logger.info(f"PyIDVerify Physiological Biometric Validators module loaded - Version: {__version__}")
