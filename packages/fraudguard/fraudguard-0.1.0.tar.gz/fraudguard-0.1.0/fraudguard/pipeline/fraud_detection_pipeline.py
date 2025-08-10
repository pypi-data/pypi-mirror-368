"""
Main fraud detection pipeline that combines all components.
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import joblib

from ..core.base import BasePipeline
from ..core.exceptions import ModelError, ValidationError
from .feature_pipeline import FeaturePipeline
from .model_orchestrator import ModelOrchestrator
from .scoring_engine import ScoringEngine
from ..utils.validation import FraudValidator
from ..utils.metrics import FraudMetrics

logger = logging.getLogger(__name__)


class FraudDetectionPipeline(BasePipeline):
    """
    Complete fraud detection pipeline.
    
    Combines feature engineering, model training/prediction, and scoring
    into a unified interface for fraud detection.
    """
    
    def __init__(self,
                 features: Optional[FeaturePipeline] = None,
                 model: Optional[Any] = None,
                 validator: Optional[FraudValidator] = None,
                 name: str = "FraudDetectionPipeline"):
        super().__init__(name)
        
        self.feature_pipeline = features
        self.model_orchestrator = ModelOrchestrator()
        self.scoring_engine = ScoringEngine()
        self.validator = validator or FraudValidator()
        self.metrics_calculator = FraudMetrics()
        
        if model:
            self.model_orchestrator.add_model('primary', model)
    
    def fit(self, X: pd.DataFrame, y: pd.Series, 
            validation_split: float = 0.2,
            **kwargs) -> 'FraudDetectionPipeline':
        """
        Fit the complete fraud detection pipeline.
        
        Args:
            X: Training data
            y: Training labels (0=legitimate, 1=fraud)
            validation_split: Fraction of data for validation
            **kwargs: Additional arguments
        """
        logger.info("Starting fraud detection pipeline training...")
        
        try:
            # Validate input data
            self.validator.validate_training_data(X, y)
            
            # Split data for validation
            if validation_split > 0:
                X_train, X_val, y_train, y_val = self._train_test_split(
                    X, y, validation_split
                )
                validation_data = (X_val, y_val)
            else:
                X_train, y_train = X, y
                validation_data = None
            
            # Fit feature pipeline
            if self.feature_pipeline:
                logger.info("Fitting feature pipeline...")
                X_train_features = self.feature_pipeline.fit_transform(X_train)
                
                if validation_data:
                    X_val_features = self.feature_pipeline.transform(X_val)
                    validation_data = (X_val_features, y_val)
            else:
                X_train_features = X_train
                logger.warning("No feature pipeline provided")
            
            # Fit models
            if self.model_orchestrator.has_models():
                logger.info("Training models...")
                self.model_orchestrator.fit(
                    X_train_features, y_train,
                    validation_data=validation_data,
                    **kwargs
                )
            else:
                raise ModelError("No models configured for training")
            
            self.is_fitted = True
            logger.info("Pipeline training completed successfully")
            
            return self
            
        except Exception as e:
            logger.error(f"Pipeline training failed: {str(e)}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make fraud predictions.
        
        Args:
            X: Input data
            
        Returns:
            Binary predictions (0=legitimate, 1=fraud)
        """
        if not self.is_fitted:
            raise ModelError("Pipeline must be fitted before making predictions")
        
        # Validate input data
        self.validator.validate_prediction_data(X)
        
        # Apply feature engineering
        if self.feature_pipeline:
            X_features = self.feature_pipeline.transform(X)
        else:
            X_features = X
        
        # Get predictions from model orchestrator
        predictions = self.model_orchestrator.predict(X_features)
        
        return predictions
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get fraud probability scores.
        
        Args:
            X: Input data
            
        Returns:
            Probability scores for each class [legitimate_prob, fraud_prob]
        """
        if not self.is_fitted:
            raise ModelError("Pipeline must be fitted before making predictions")
        
        # Validate input data
        self.validator.validate_prediction_data(X)
        
        # Apply feature engineering
        if self.feature_pipeline:
            X_features = self.feature_pipeline.transform(X)
        else:
            X_features = X
        
        # Get probability scores
        probabilities = self.model_orchestrator.predict_proba(X_features)
        
        return probabilities
    
    def score_transactions(self, X: pd.DataFrame, 
                          return_details: bool = False) -> Union[np.ndarray, Dict[str, Any]]:
        """
        Score transactions for fraud risk.
        
        Args:
            X: Transaction data
            return_details: If True, return detailed scoring information
            
        Returns:
            Fraud risk scores or detailed scoring results
        """
        fraud_probabilities = self.predict_proba(X)[:, 1]  # Get fraud probabilities
        
        if return_details:
            predictions = self.predict(X)
            
            results = {
                'fraud_scores': fraud_probabilities,
                'fraud_predictions': predictions,
                'risk_categories': self.scoring_engine.categorize_risk(fraud_probabilities),
                'timestamp': pd.Timestamp.now()
            }
            
            # Add feature importance if available
            if hasattr(self.model_orchestrator, 'get_feature_importance'):
                results['feature_importance'] = self.model_orchestrator.get_feature_importance()
            
            return results
        else:
            return fraud_probabilities
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Evaluate pipeline performance on test data.
        
        Args:
            X: Test features
            y: Test labels
            
        Returns:
            Performance metrics
        """
        if not self.is_fitted:
            raise ModelError("Pipeline must be fitted before evaluation")
        
        # Get predictions and probabilities
        y_pred = self.predict(X)
        y_proba = self.predict_proba(X)[:, 1]
        
        # Calculate comprehensive metrics with y converted to a NumPy array
        metrics = self.metrics_calculator.calculate_all_metrics(np.array(y), y_pred, y_proba)
        
        # Add pipeline-specific info
        metrics['pipeline_info'] = self.get_pipeline_info()
        
        logger.info(f"Pipeline evaluation - AUC: {metrics.get('auc', 'N/A'):.3f}, "
                   f"Precision: {metrics.get('precision', 'N/A'):.3f}, "
                   f"Recall: {metrics.get('recall', 'N/A'):.3f}")
        
        return metrics
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained models."""
        if not self.is_fitted:
            return {}
        
        return self.model_orchestrator.get_feature_importance()
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get comprehensive pipeline information."""
        info = {
            'name': self.name,
            'is_fitted': self.is_fitted,
            'feature_pipeline': None,
            'models': {},
            'components': []
        }
        
        # Feature pipeline info
        if self.feature_pipeline:
            info['feature_pipeline'] = {
                'n_extractors': len(self.feature_pipeline.extractors),
                'extractor_names': [e.name for e in self.feature_pipeline.extractors]
            }
            info['components'].append('feature_engineering')
        
        # Model info
        if self.model_orchestrator.has_models():
            info['models'] = self.model_orchestrator.get_models_info()
            info['components'].append('model_orchestrator')
        
        # Other components
        info['components'].extend(['scoring_engine', 'validator', 'metrics_calculator'])
        
        return info
    
    def save_pipeline(self, filepath: Union[str, Path]):
        """Save the complete pipeline to disk."""
        if not self.is_fitted:
            raise ModelError("Cannot save unfitted pipeline")
        
        try:
            pipeline_path = Path(filepath)
            pipeline_path.parent.mkdir(parents=True, exist_ok=True)
            
            joblib.dump(self, pipeline_path)
            logger.info(f"Pipeline saved to {pipeline_path}")
            
        except Exception as e:
            raise ModelError(f"Error saving pipeline: {str(e)}")
    
    @classmethod
    def load_pipeline(cls, filepath: Union[str, Path]) -> 'FraudDetectionPipeline':
        """Load a saved pipeline from disk."""
        try:
            pipeline = joblib.load(filepath)
            logger.info(f"Pipeline loaded from {filepath}")
            return pipeline
            
        except Exception as e:
            raise ModelError(f"Error loading pipeline: {str(e)}")
    
    def _train_test_split(self, X: pd.DataFrame, y: pd.Series, 
                         validation_split: float) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split data for training and validation."""
        from sklearn.model_selection import train_test_split
        
        return tuple(train_test_split(
            X, y,
            test_size=validation_split,
            random_state=42,
            stratify=y  # Maintain class distribution
        ))
    
    def __repr__(self):
        status = "fitted" if self.is_fitted else "not fitted"
        n_models = len(self.model_orchestrator.models) if self.model_orchestrator else 0
        n_extractors = len(self.feature_pipeline.extractors) if self.feature_pipeline else 0
        
        return (f"FraudDetectionPipeline(status={status}, "
                f"models={n_models}, extractors={n_extractors})")
        
    
