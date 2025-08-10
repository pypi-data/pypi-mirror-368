"""
FraudGuard: A comprehensive fraud detection package for financial institutions.

This package provides modular, production-ready tools for detecting financial fraud
using machine learning. It includes pre-built feature extractors, model implementations,
and deployment utilities specifically designed for financial fraud detection.
"""

__version__ = "0.1.0"
__author__ = "FraudGuard Team"
__email__ = "contact@fraudguard.io"

from .core.config import FraudGuardConfig
from .pipeline.feature_pipeline import FeaturePipeline
from .pipeline.model_orchestrator import ModelOrchestrator
from .pipeline.scoring_engine import ScoringEngine

# Main pipeline class for easy access
from .pipeline.fraud_detection_pipeline import FraudDetectionPipeline

# Feature extractors
from .features import (
    TransactionFeatures,
    BehavioralFeatures,
    TemporalFeatures,
    VelocityFeatures
)

# Models
from .models import (
    XGBoostModel,
    RandomForestModel,
    EnsembleModel,
    AnomalyModel
)

# Utilities
from .utils.metrics import FraudMetrics
from .utils.preprocessing import FraudPreprocessor

__all__ = [
    "FraudDetectionPipeline",
    "FeaturePipeline", 
    "ModelOrchestrator",
    "ScoringEngine",
    "TransactionFeatures",
    "BehavioralFeatures", 
    "TemporalFeatures",
    "VelocityFeatures",
    "XGBoostModel",
    "RandomForestModel",
    "EnsembleModel", 
    "AnomalyModel",
    "FraudMetrics",
    "FraudPreprocessor",
    "FraudGuardConfig"
]

# Package metadata
__title__ = "fraudguard"
__description__ = "Modular fraud detection for financial institutions"
__url__ = "https://github.com/fraudguard/fraudguard"
__license__ = "MIT"
