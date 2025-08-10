"""
XGBoost model implementation for fraud detection.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Union
import logging

try:
    import xgboost as xgb
except ImportError:
    raise ImportError("XGBoost not installed. Install with: pip install xgboost")

from .base_model import BaseFraudModel
from ..core.config import config
from ..core.exceptions import ModelError

logger = logging.getLogger(__name__)


class XGBoostModel(BaseFraudModel):
    """
    XGBoost implementation optimized for fraud detection.
    
    Features:
    - Handles class imbalance automatically
    - Early stopping to prevent overfitting
    - Feature importance calculation
    - Hyperparameter optimization ready
    """
    
    def __init__(self, 
                 n_estimators: int = 100,
                 max_depth: int = 6,
                 learning_rate: float = 0.1,
                 subsample: float = 0.8,
                 colsample_bytree: float = 0.8,
                 scale_pos_weight: Optional[float] = None,
                 early_stopping_rounds: int = 10,
                 **kwargs):
        super().__init__(**kwargs)
        
        # Get default parameters from config
        default_params = config.get('models.xgboost', {})
        
        self.n_estimators = n_estimators or default_params.get('n_estimators', 100)
        self.max_depth = max_depth or default_params.get('max_depth', 6)
        self.learning_rate = learning_rate or default_params.get('learning_rate', 0.1)
        self.subsample = subsample or default_params.get('subsample', 0.8)
        self.colsample_bytree = colsample_bytree or default_params.get('colsample_bytree', 0.8)
        self.scale_pos_weight = scale_pos_weight
        self.early_stopping_rounds = early_stopping_rounds
        
    def _create_model(self, **kwargs) -> xgb.XGBClassifier:
        """Create XGBoost classifier with fraud detection optimizations."""
        
        model_params = {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'subsample': self.subsample,
            'colsample_bytree': self.colsample_bytree,
            'random_state': config.get('pipeline.random_state', 42),
            'n_jobs': -1,
            'eval_metric': 'auc',
            'use_label_encoder': False
        }
        
        # Handle class imbalance with scale_pos_weight
        if self.scale_pos_weight is not None:
            model_params['scale_pos_weight'] = self.scale_pos_weight
        elif not self.handle_imbalance:
            # Auto-calculate scale_pos_weight if not handling imbalance with sampling
            model_params['scale_pos_weight'] = 'auto'
            
        # Override with any provided kwargs
        model_params.update(kwargs)
        
        return xgb.XGBClassifier(**model_params)
    
    def _fit_model(self, X: pd.DataFrame, y: pd.Series, 
                   validation_data: Optional[tuple] = None, **kwargs):
        """Fit XGBoost model with early stopping."""
        
        fit_params = {}
        
        # Setup validation for early stopping
        if validation_data is not None:
            X_val, y_val = validation_data
            fit_params['eval_set'] = [(X, y), (X_val, y_val)]
            fit_params['early_stopping_rounds'] = self.early_stopping_rounds
            fit_params['verbose'] = False
        
        # Fit the model, ensuring the model is initialized before fitting
        if not hasattr(self, 'model') or self.model is None:
            self.model = self._create_model()
        self.model.fit(X, y, **fit_params)
        
        # Log training info
        if hasattr(self.model, 'evals_result_'):
            evals_result = self.model.evals_result_
            if 'validation_1' in evals_result:
                best_score = max(evals_result['validation_1']['auc'])
                logger.info(f"Best validation AUC: {best_score:.4f}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make fraud predictions (0=legitimate, 1=fraud)."""
        if not self.is_fitted:
            raise ModelError("Model must be fitted before making predictions")
            
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return prediction probabilities."""
        if not self.is_fitted:
            raise ModelError("Model must be fitted before making predictions")
            
        return self.model.predict_proba(X)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get XGBoost feature importance scores."""
        if not self.is_fitted:
            return {}
            
        importance_scores = self.model.feature_importances_
        return dict(zip(self.feature_names_, importance_scores))
    
    def plot_feature_importance(self, top_n: int = 20, figsize: tuple = (10, 8)):
        """Plot feature importance."""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
        except ImportError:
            raise ImportError("matplotlib and seaborn required for plotting")
        
        importance_df = self.get_feature_importance_df().head(top_n)
        
        plt.figure(figsize=figsize)
        sns.barplot(data=importance_df, x='importance', y='feature')
        plt.title(f'Top {top_n} Feature Importance - {self.name}')
        plt.xlabel('Importance Score')
        plt.tight_layout()
        plt.show()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model configuration and performance info."""
        info = {
            'model_type': 'XGBoost',
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'is_fitted': self.is_fitted,
        }
        
        if self.is_fitted:
            info.update({
                'n_features': len(self.feature_names_),
                'training_metrics': self.training_metrics_,
                'best_iteration': getattr(self.model, 'best_iteration', None)
            })
            
        return info

    
