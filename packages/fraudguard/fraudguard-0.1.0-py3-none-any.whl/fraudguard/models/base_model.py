"""
Base model class for fraud detection models.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import logging

from ..core.base import BaseModel
from ..core.exceptions import ModelError

logger = logging.getLogger(__name__)


class BaseFraudModel(BaseModel):
    """
    Enhanced base class for fraud detection models.
    
    Provides common functionality for fraud detection including
    class imbalance handling, feature importance, and model persistence.
    """
    
    def __init__(self, 
                 name: Optional[str] = None,
                 handle_imbalance: bool = True,
                 class_weight: Optional[Union[str, Dict]] = 'balanced',
                 **kwargs):
        super().__init__(name, **kwargs)
        
        self.handle_imbalance = handle_imbalance
        self.class_weight = class_weight
        self.training_metrics_ = {}
        
    def fit(self, X: pd.DataFrame, y: pd.Series, 
            validation_data: Optional[tuple] = None, **kwargs):
        """
        Fit the fraud detection model.
        
        Args:
            X: Training features
            y: Training labels (0=legitimate, 1=fraud)
            validation_data: Optional (X_val, y_val) for validation
            **kwargs: Additional arguments passed to model
        """
        try:
            # Store feature names
            self.feature_names_ = list(X.columns)
            self.classes_ = np.unique(y)
            
            # Handle class imbalance if enabled
            if self.handle_imbalance:
                X, y = self._handle_imbalance(X, y)
            
            # Create and train model
            self.model = self._create_model(**kwargs)
            self._fit_model(X, y, validation_data, **kwargs)
            
            # Calculate training metrics
            train_pred = self.predict_proba(X)[:, 1]
            self.training_metrics_ = self._calculate_metrics(y, train_pred)
            
            self.is_fitted = True
            logger.info(f"{self.name} training completed. AUC: {self.training_metrics_.get('auc', 'N/A')}")
            
            return self
            
        except Exception as e:
            raise ModelError(f"Error fitting {self.name}: {str(e)}")
    
    @abstractmethod
    def _fit_model(self, X: pd.DataFrame, y: pd.Series, 
                   validation_data: Optional[tuple], **kwargs):
        """Implement model-specific fitting logic."""
        pass
    
    def _handle_imbalance(self, X: pd.DataFrame, y: pd.Series) -> tuple:
        """Handle class imbalance using sampling techniques."""
        from imblearn.over_sampling import SMOTE
        from imblearn.combine import SMOTEENN
        
        fraud_rate = y.mean()
        logger.info(f"Original fraud rate: {fraud_rate:.3f}")
        
        if fraud_rate < 0.01:  # Very imbalanced
            sampler = SMOTEENN(random_state=42)
        elif fraud_rate < 0.1:  # Moderately imbalanced  
            sampler = SMOTE(random_state=42)
        else:
            return X, y  # Not too imbalanced
            
        X_resampled, y_resampled = sampler.fit_resample(X, y)
        
        logger.info(f"After resampling fraud rate: {y_resampled.mean():.3f}")
        return pd.DataFrame(X_resampled, columns=X.columns), pd.Series(y_resampled)
    
    def _calculate_metrics(self, y_true: np.ndarray, y_scores: np.ndarray) -> Dict[str, float]:
        """Calculate fraud detection metrics."""
        from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve
        
        metrics = {}
        
        try:
            metrics['auc'] = roc_auc_score(y_true, y_scores)
            metrics['average_precision'] = average_precision_score(y_true, y_scores)
            
            # Precision at different recall levels
            precision, recall, _ = precision_recall_curve(y_true, y_scores)
            
            # Find precision at 50% recall (common fraud detection metric)
            recall_50_idx = np.argmax(recall >= 0.5)
            if recall_50_idx > 0:
                metrics['precision_at_50_recall'] = precision[recall_50_idx]
            
            # Find precision at 80% recall
            recall_80_idx = np.argmax(recall >= 0.8)  
            if recall_80_idx > 0:
                metrics['precision_at_80_recall'] = precision[recall_80_idx]
                
        except Exception as e:
            logger.warning(f"Error calculating metrics: {e}")
            
        return metrics
    
    def get_training_metrics(self) -> Dict[str, float]:
        """Get training performance metrics."""
        return self.training_metrics_
    
    def save_model(self, filepath: Union[str, Path]):
        """Save model to disk."""
        if not self.is_fitted:
            raise ModelError("Cannot save unfitted model")
            
        try:
            joblib.dump(self, filepath)
            logger.info(f"Model saved to {filepath}")
        except Exception as e:
            raise ModelError(f"Error saving model: {str(e)}")
    
    @classmethod
    def load_model(cls, filepath: Union[str, Path]):
        """Load model from disk."""
        try:
            model = joblib.load(filepath)
            logger.info(f"Model loaded from {filepath}")
            return model
        except Exception as e:
            raise ModelError(f"Error loading model: {str(e)}")
    
    def get_feature_importance_df(self) -> pd.DataFrame:
        """Get feature importance as DataFrame."""
        importance_dict = self.get_feature_importance()
        
        if not importance_dict:
            return pd.DataFrame()
            
        df = pd.DataFrame([
            {'feature': feature, 'importance': importance}
            for feature, importance in importance_dict.items()
        ])
        
        return df.sort_values('importance', ascending=False)
