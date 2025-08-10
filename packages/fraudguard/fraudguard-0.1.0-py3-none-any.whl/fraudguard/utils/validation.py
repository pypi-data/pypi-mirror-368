"""
Data validation utilities for fraud detection.
"""

import pandas as pd
import numpy as np
from typing import List, Optional
import logging

from ..core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class FraudValidator:
    """
    Validator for fraud detection data and models.
    """
    
    def validate_training_data(self, X: pd.DataFrame, y: pd.Series):
        """Validate training data for fraud detection."""
        if X.empty:
            raise ValidationError("Training features cannot be empty")
            
        if y.empty:
            raise ValidationError("Training labels cannot be empty")
            
        if len(X) != len(y):
            raise ValidationError("Features and labels must have same length")
            
        # Check for reasonable fraud rate
        fraud_rate = y.mean()
        if fraud_rate == 0:
            raise ValidationError("No fraud cases in training data")
        if fraud_rate == 1:
            raise ValidationError("No legitimate cases in training data")
            
        logger.info(f"Training data validation passed. Fraud rate: {fraud_rate:.3f}")
    
    def validate_prediction_data(self, X: pd.DataFrame):
        """Validate prediction data."""
        if X.empty:
            raise ValidationError("Prediction data cannot be empty")
            
        logger.debug(f"Prediction data validation passed. Shape: {X.shape}")
