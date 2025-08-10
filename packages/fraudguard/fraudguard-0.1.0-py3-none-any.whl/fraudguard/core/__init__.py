"""
Core module containing base classes, configuration, and exceptions.
"""

from .base import BaseFeatureExtractor, BaseModel, BasePipeline
from .config import FraudGuardConfig
from .exceptions import (
    FraudGuardError,
    ConfigurationError,
    FeatureExtractionError,
    ModelError,
    ValidationError
)

__all__ = [
    "BaseFeatureExtractor",
    "BaseModel", 
    "BasePipeline",
    "FraudGuardConfig",
    "FraudGuardError",
    "ConfigurationError",
    "FeatureExtractionError", 
    "ModelError",
    "ValidationError"
]
