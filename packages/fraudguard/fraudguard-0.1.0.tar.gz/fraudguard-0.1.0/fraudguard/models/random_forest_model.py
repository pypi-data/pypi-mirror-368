"""
Random Forest model implementation for fraud detection.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import logging

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from .base_model import BaseFraudModel
from ..core.config import config
from ..core.exceptions import ModelError

logger = logging.getLogger(__name__)


class RandomForestModel(BaseFraudModel):
    """
    Random Forest implementation for fraud detection.
    
    Features:
    - Robust to overfitting
    - Handles mixed data types well
    - Built-in feature importance
    - Good baseline performance
    """
    
    def __init__(self,
                 n_estimators: int = 100,
                 max_depth: Optional[int] = 10,
                 min_samples_split: int = 2,
                 min_samples_leaf: int = 1,
                 max_features: str = 'sqrt',
                 bootstrap: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        
        # Get default parameters from config
        default_params = config.get('models.random_forest', {})
        
        self.n_estimators = n_estimators or default_params.get('n_estimators', 100)
        self.max_depth = max_depth or default_params.get('max_depth', 10)
        self.min_samples_split = min_samples_split or default_params.get('min_samples_split', 2)
        self.min_samples_leaf = min_samples_leaf or default_params.get('min_samples_leaf', 1)
        self.max_features = max_features
        self.bootstrap = bootstrap
        
    def _create_model(self, **kwargs) -> RandomForestClassifier:
        """Create Random Forest classifier."""
        
        model_params = {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'max_features': self.max_features,
            'bootstrap': self.bootstrap,
            'random_state': config.get('pipeline.random_state', 42),
            'n_jobs': -1
        }
        
        # Handle class imbalance
        if self.class_weight:
            model_params['class_weight'] = self.class_weight
        
        # Override with any provided kwargs
        model_params.update(kwargs)
        
        return RandomForestClassifier(**model_params)
    
    def _fit_model(self, X: pd.DataFrame, y: pd.Series, 
                   validation_data: Optional[tuple] = None, **kwargs):
        """Fit Random Forest model."""
        
        # Fit the model
        self.model.fit(X, y)
        
        # Perform cross-validation if no validation set provided
        if validation_data is None:
            cv_scores = cross_val_score(
                self.model, X, y, 
                cv=5, 
                scoring='roc_auc', 
                n_jobs=-1
            )
            logger.info(f"Cross-validation AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        else:
            X_val, y_val = validation_data
            val_proba = self.model.predict_proba(X_val)[:, 1]
            val_metrics = self._calculate_metrics(y_val, val_proba)
            logger.info(f"Validation AUC: {val_metrics.get('auc', 'N/A'):.4f}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make fraud predictions."""
        if not self.is_fitted:
            raise ModelError("Model must be fitted before making predictions")
            
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return prediction probabilities."""
        if not self.is_fitted:
            raise ModelError("Model must be fitted before making predictions")
            
        return self.model.predict_proba(X)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get Random Forest feature importance scores."""
        if not self.is_fitted:
            return {}
            
        importance_scores = self.model.feature_importances_
        return dict(zip(self.feature_names_, importance_scores))
    
    def get_tree_info(self) -> Dict[str, Any]:
        """Get information about the trees in the forest."""
        if not self.is_fitted:
            return {}
        
        trees = self.model.estimators_
        
        return {
            'n_trees': len(trees),
            'avg_tree_depth': np.mean([tree.tree_.max_depth for tree in trees]),
            'avg_tree_leaves': np.mean([tree.tree_.n_leaves for tree in trees]),
            'avg_tree_nodes': np.mean([tree.tree_.node_count for tree in trees])
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model configuration and performance info."""
        info = {
            'model_type': 'RandomForest',
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'is_fitted': self.is_fitted,
        }
        
        if self.is_fitted:
            info.update({
                'n_features': len(self.feature_names_),
                'training_metrics': self.training_metrics_,
                'tree_info': self.get_tree_info()
            })
            
        return info
