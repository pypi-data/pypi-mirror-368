"""
Behavioral Biometric Validators

This module contains validators for behavioral biometric identifiers including
keystroke dynamics, mouse patterns, gait analysis, signature dynamics, and
other behavioral biometric modalities.

Behavioral biometrics are based on patterns in human behavior that can be
measured and used for authentication.

Available Validators:
- KeystrokeDynamicsValidator: Typing pattern validation
- MousePatternsValidator: Mouse movement pattern validation
- GaitAnalysisValidator: Walking pattern validation  
- SignatureDynamicsValidator: Signature pattern validation
- TypingRhythmValidator: Typing rhythm pattern validation

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
    # 'KeystrokeDynamicsValidator',
    # 'MousePatternsValidator',
    # 'GaitAnalysisValidator', 
    # 'SignatureDynamicsValidator',
    # 'TypingRhythmValidator'
]

logger.info(f"PyIDVerify Behavioral Biometric Validators module loaded - Version: {__version__}")
