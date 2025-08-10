"""
Anomaly detection models for fraud detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union
import logging

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

try:
    from sklearn.neural_network import MLPRegressor
    NEURAL_NETWORK_AVAILABLE = True
except ImportError:
    NEURAL_NETWORK_AVAILABLE = False

from .base_model import BaseFraudModel
from ..core.exceptions import ModelError

logger = logging.getLogger(__name__)


class AnomalyModel(BaseFraudModel):
    """
    Anomaly detection model for unsupervised fraud detection.
    
    Uses isolation forest, one-class SVM, or autoencoder to detect anomalies
    that may represent fraudulent transactions.
    """
    
    def __init__(self,
                 algorithm: str = 'isolation_forest',
                 contamination: float = 0.1,
                 normalize_features: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        
        self.algorithm = algorithm
        self.contamination = contamination
        self.normalize_features = normalize_features
        self.scaler = StandardScaler() if normalize_features else None
        
        # Validate algorithm choice
        valid_algorithms = ['isolation_forest', 'one_class_svm', 'autoencoder']
        if algorithm not in valid_algorithms:
            raise ValueError(f"Algorithm must be one of {valid_algorithms}")
        
        if algorithm == 'autoencoder' and not NEURAL_NETWORK_AVAILABLE:
            raise ValueError("MLPRegressor not available for autoencoder. Install scikit-learn>=0.24")
    
    def _create_model(self, **kwargs):
        """Create anomaly detection model."""
        
        if self.algorithm == 'isolation_forest':
            return IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_jobs=-1,
                **kwargs
            )
        elif self.algorithm == 'one_class_svm':
            return OneClassSVM(
                nu=self.contamination,
                **kwargs
            )
        elif self.algorithm == 'autoencoder':
            return self._create_autoencoder(**kwargs)
        
    def _create_autoencoder(self, **kwargs):
        """Create a simple autoencoder using MLPRegressor."""
        
        # Default architecture
        default_layers = (50, 20, 50)  # Encoder-bottleneck-decoder
        
        return MLPRegressor(
            hidden_layer_sizes=kwargs.get('hidden_layer_sizes', default_layers),
            activation='relu',
            solver='adam',
            alpha=0.001,
            random_state=42,
            max_iter=500,
            **{k: v for k, v in kwargs.items() if k != 'hidden_layer_sizes'}
        )
    
    def _fit_model(self, X: pd.DataFrame, y: pd.Series = None, 
                   validation_data: Optional[tuple] = None, **kwargs):
        """Fit anomaly detection model."""
        
        # Note: Anomaly detection typically ignores labels for training
        # but we can use them for evaluation
        
        # Normalize features if requested
        if self.normalize_features:
            X_scaled = pd.DataFrame(
                self.scaler.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
        else:
            X_scaled = X
        
        if self.algorithm in ['isolation_forest', 'one_class_svm']:
            self.model.fit(X_scaled)
        elif self.algorithm == 'autoencoder':
            # Train autoencoder to reconstruct input
            self.model.fit(X_scaled, X_scaled)
        
        # Calculate anomaly scores for training data
        train_scores = self.predict_proba(X)
        
        if y is not None:
            # If we have labels, calculate metrics
            self.training_metrics_ = self._calculate_anomaly_metrics(y, train_scores)
            logger.info(f"Training anomaly detection AUC: {self.training_metrics_.get('auc', 'N/A')}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict anomalies (1=anomaly/fraud, -1 or 0=normal)."""
        if not self.is_fitted:
            raise ModelError("Model must be fitted before making predictions")
        
        if self.normalize_features:
            X_scaled = pd.DataFrame(
                self.scaler.transform(X),
                columns=X.columns,
                index=X.index
            )
        else:
            X_scaled = X
        
        if self.algorithm in ['isolation_forest', 'one_class_svm']:
            predictions = self.model.predict(X_scaled)
            # Convert to binary (1=anomaly, 0=normal)
            return (predictions == -1).astype(int)
        elif self.algorithm == 'autoencoder':
            # Use reconstruction error threshold
            reconstruction_errors = self._get_reconstruction_errors(X_scaled)
            threshold = np.percentile(reconstruction_errors, (1 - self.contamination) * 100)
            return (reconstruction_errors > threshold).astype(int)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return anomaly scores (higher = more anomalous)."""
        if not self.is_fitted:
            raise ModelError("Model must be fitted before making predictions")
        
        if self.normalize_features:
            X_scaled = pd.DataFrame(
                self.scaler.transform(X),
                columns=X.columns,
                index=X.index
            )
        else:
            X_scaled = X
        
        if self.algorithm == 'isolation_forest':
            # Isolation forest returns scores between -1 and 1
            # Convert to 0-1 scale (higher = more anomalous)
            scores = self.model.decision_function(X_scaled)
            scores = (scores.max() - scores) / (scores.max() - scores.min())
        elif self.algorithm == 'one_class_svm':
            # One-class SVM decision function (negative = anomaly)
            scores = -self.model.decision_function(X_scaled)
            scores = (scores - scores.min()) / (scores.max() - scores.min())
        elif self.algorithm == 'autoencoder':
            # Use reconstruction error as anomaly score
            scores = self._get_reconstruction_errors(X_scaled)
            scores = (scores - scores.min()) / (scores.max() - scores.min())
        
        return scores
    
    def _get_reconstruction_errors(self, X: pd.DataFrame) -> np.ndarray:
        """Calculate reconstruction errors for autoencoder."""
        if self.algorithm != 'autoencoder':
            raise ValueError("Reconstruction errors only available for autoencoder")
        
        reconstructed = self.model.predict(X)
        errors = np.mean((X.values - reconstructed) ** 2, axis=1)
        return errors
    
    def _calculate_anomaly_metrics(self, y_true: np.ndarray, anomaly_scores: np.ndarray) -> Dict[str, float]:
        """Calculate metrics for anomaly detection."""
        from sklearn.metrics import roc_auc_score, average_precision_score
        
        metrics = {}
        
        try:
            # Assume 1 = fraud/anomaly in ground truth
            metrics['auc'] = roc_auc_score(y_true, anomaly_scores)
            metrics['average_precision'] = average_precision_score(y_true, anomaly_scores)
            
        except Exception as e:
            logger.warning(f"Error calculating anomaly metrics: {e}")
        
        return metrics
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance for anomaly detection.
        Note: Only available for some algorithms.
        """
        if self.algorithm == 'isolation_forest' and hasattr(self.model, 'feature_importances_'):
            return dict(zip(self.feature_names_, self.model.feature_importances_))
        else:
            logger.warning(f"Feature importance not available for {self.algorithm}")
            return {}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get anomaly model information."""
        info = {
            'model_type': 'AnomalyDetection',
            'algorithm': self.algorithm,
            'contamination': self.contamination,
            'normalize_features': self.normalize_features,
            'is_fitted': self.is_fitted,
        }
        
        if self.is_fitted:
            info.update({
                'n_features': len(self.feature_names_),
                'training_metrics': self.training_metrics_
            })
            
            if self.algorithm == 'isolation_forest':
                info['n_estimators'] = getattr(self.model, 'n_estimators', None)
            elif self.algorithm == 'autoencoder':
                info['hidden_layer_sizes'] = getattr(self.model, 'hidden_layer_sizes', None)
                
        return info
