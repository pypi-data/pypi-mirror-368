"""
Hybrid Biometric Validators for PyIDVerify - Phase 4 Advanced Features

This module contains advanced hybrid biometric validators that combine multiple
authentication factors and provide sophisticated risk-based authentication:

1. Multi-Factor Biometric Validator - Combines multiple biometric modalities
2. Continuous Authentication Validator - Ongoing session monitoring
3. Risk-Based Scoring Validator - Comprehensive risk assessment

Phase 4 Advanced Features:
- Multi-factor biometric combinations with intelligent fusion
- Continuous authentication and behavioral monitoring
- Risk-based scoring with adaptive policies
- Performance optimization for enterprise deployment

Author: PyIDVerify Team
Date: August 7, 2025
Version: 1.0.0 - Phase 4 Complete
"""

from typing import List, Dict, Any
import logging

# Multi-Factor Biometric Authentication
from .multi_factor_validator import (
    MultiFactorBiometricValidator,
    FusionStrategy,
    AuthenticationMode,
    BiometricModality,
    AuthenticationContext,
    FusionResult,
    ContinuousAuthState,
    RiskLevel
)

# Continuous Authentication
from .continuous_auth_validator import (
    ContinuousAuthenticationValidator,
    ContinuousAuthMode,
    ThreatLevel,
    SessionState,
    BiometricSample,
    ContinuousSession,
    AnomalyEvent,
    ContinuousAuthResult
)

# Risk-Based Scoring
from .risk_based_validator import (
    RiskBasedScoringValidator,
    RiskCategory,
    RiskSeverity,
    AuthenticationPolicy,
    RiskContext,
    RiskAssessment,
    UserRiskProfile,
    RiskFactor
)

# Configure logging
logger = logging.getLogger(__name__)

# Module version
__version__ = "1.0.0-phase4"

# Phase 4 validator registry
PHASE4_VALIDATORS = {
    'multi_factor': MultiFactorBiometricValidator,
    'continuous_auth': ContinuousAuthenticationValidator,
    'risk_based': RiskBasedScoringValidator
}

# Export all Phase 4 components
__all__ = [
    # Multi-Factor Authentication
    'MultiFactorBiometricValidator',
    'FusionStrategy',
    'AuthenticationMode',
    'BiometricModality',
    'AuthenticationContext',
    'FusionResult',
    'ContinuousAuthState',
    'RiskLevel',
    
    # Continuous Authentication
    'ContinuousAuthenticationValidator',
    'ContinuousAuthMode',
    'ThreatLevel',
    'SessionState',
    'BiometricSample',
    'ContinuousSession',
    'AnomalyEvent',
    'ContinuousAuthResult',
    
    # Risk-Based Scoring
    'RiskBasedScoringValidator',
    'RiskCategory',
    'RiskSeverity',
    'AuthenticationPolicy',
    'RiskContext',
    'RiskAssessment',
    'UserRiskProfile',
    'RiskFactor',
    
    # Validator registry
    'PHASE4_VALIDATORS'
]


def create_multi_factor_validator(validation_level=None):
    """Factory function for multi-factor biometric validator"""
    from pyidverify.core.types import BiometricType
    return MultiFactorBiometricValidator(BiometricType.MULTI_MODAL)


def create_continuous_auth_validator(validation_level=None):
    """Factory function for continuous authentication validator"""
    from pyidverify.core.types import BiometricType
    return ContinuousAuthenticationValidator(BiometricType.CONTINUOUS_AUTH)


def create_risk_based_validator(validation_level=None):
    """Factory function for risk-based scoring validator"""
    from pyidverify.core.types import BiometricType
    return RiskBasedScoringValidator(BiometricType.RISK_ASSESSMENT)


# Factory function registry
VALIDATOR_FACTORIES = {
    'multi_factor': create_multi_factor_validator,
    'continuous_auth': create_continuous_auth_validator,
    'risk_based': create_risk_based_validator
}

logger.info(f"PyIDVerify Phase 4 Hybrid Biometric Validators loaded - Version: {__version__}")
logger.info(f"Available validators: {list(PHASE4_VALIDATORS.keys())}")
