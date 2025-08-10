"""
Ensemble model implementations for fraud detection.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
import logging

from sklearn.ensemble import VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

from .base_model import BaseFraudModel
from ..core.exceptions import ModelError

logger = logging.getLogger(__name__)


class EnsembleModel(BaseFraudModel):
    """
    Ensemble model that combines multiple fraud detection models.
    
    Supports both voting and stacking ensemble methods.
    """
    
    def __init__(self,
                 models: List[BaseFraudModel],
                 ensemble_method: str = 'voting',
                 voting: str = 'soft',
                 meta_model: Optional[Any] = None,
                 **kwargs):
        super().__init__(**kwargs)
        
        if not models:
            raise ValueError("Must provide at least one model for ensemble")
        
        self.base_models = models
        self.ensemble_method = ensemble_method
        self.voting = voting
        self.meta_model = meta_model or LogisticRegression(random_state=42)
        
        # Create ensemble
        self.ensemble = self._create_ensemble()
        
    def _create_ensemble(self):
        """Create the ensemble classifier."""
        
        # Prepare model list for sklearn ensemble
        estimators = [
            (f'model_{i}', model.model if hasattr(model, 'model') else model)
            for i, model in enumerate(self.base_models)
        ]
        
        if self.ensemble_method == 'voting':
            return VotingClassifier(
                estimators=estimators,
                voting=self.voting,
                n_jobs=-1
            )
        elif self.ensemble_method == 'stacking':
            return StackingClassifier(
                estimators=estimators,
                final_estimator=self.meta_model,
                cv=5,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown ensemble method: {self.ensemble_method}")
    
    def _create_model(self, **kwargs):
        """Return the ensemble classifier."""
        return self.ensemble
    
    def _fit_model(self, X: pd.DataFrame, y: pd.Series, 
                   validation_data: Optional[tuple] = None, **kwargs):
        """Fit ensemble model."""
        
        # Fit individual models first (if not already fitted)
        for i, model in enumerate(self.base_models):
            if not hasattr(model, 'is_fitted') or not model.is_fitted:
                logger.info(f"Fitting base model {i+1}/{len(self.base_models)}")
                model.fit(X, y, validation_data=validation_data)
        
        # Fit ensemble
        self.model.fit(X, y)
        
        # Evaluate ensemble performance
        if validation_data is None:
            cv_scores = cross_val_score(
                self.model, X, y,
                cv=5,
                scoring='roc_auc',
                n_jobs=-1
            )
            logger.info(f"Ensemble CV AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        else:
            X_val, y_val = validation_data
            val_proba = self.predict_proba(X_val)[:, 1]
            val_metrics = self._calculate_metrics(y_val, val_proba)
            logger.info(f"Ensemble Validation AUC: {val_metrics.get('auc', 'N/A'):.4f}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make ensemble predictions."""
        if not self.is_fitted:
            raise ModelError("Ensemble must be fitted before making predictions")
            
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return ensemble prediction probabilities."""
        if not self.is_fitted:
            raise ModelError("Ensemble must be fitted before making predictions")
            
        return self.model.predict_proba(X)
    
    def get_individual_predictions(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Get predictions from each base model."""
        predictions = {}
        
        for i, model in enumerate(self.base_models):
            model_name = getattr(model, 'name', f'model_{i}')
            if hasattr(model, 'predict_proba'):
                predictions[model_name] = model.predict_proba(X)[:, 1]
            else:
                predictions[model_name] = model.predict(X)
                
        return predictions
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get averaged feature importance from base models."""
        if not self.is_fitted:
            return {}
        
        all_importances = {}
        valid_models = 0
        
        for model in self.base_models:
            if hasattr(model, 'get_feature_importance'):
                model_importance = model.get_feature_importance()
                if model_importance:
                    valid_models += 1
                    for feature, importance in model_importance.items():
                        if feature not in all_importances:
                            all_importances[feature] = 0
                        all_importances[feature] += importance
        
        # Average the importances
        if valid_models > 0:
            for feature in all_importances:
                all_importances[feature] /= valid_models
                
        return all_importances
    
    def get_model_weights(self) -> Dict[str, float]:
        """Get model weights for voting ensemble."""
        if self.ensemble_method != 'voting':
            return {}
        
        # For equal weights (default)
        n_models = len(self.base_models)
        return {
            f'model_{i}': 1.0 / n_models
            for i in range(n_models)
        }
    
    def compare_models(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Compare performance of base models vs ensemble."""
        results = []
        
        # Evaluate each base model
        for i, model in enumerate(self.base_models):
            model_name = getattr(model, 'name', f'model_{i}')
            
            if hasattr(model, 'predict_proba'):
                y_scores = model.predict_proba(X)[:, 1]
            else:
                y_scores = model.predict(X)
                
            metrics = self._calculate_metrics(y, y_scores)
            metrics['model'] = model_name
            metrics['type'] = 'base'
            results.append(metrics)
        
        # Evaluate ensemble
        ensemble_scores = self.predict_proba(X)[:, 1]
        ensemble_metrics = self._calculate_metrics(y, ensemble_scores)
        ensemble_metrics['model'] = f'{self.ensemble_method}_ensemble'
        ensemble_metrics['type'] = 'ensemble'
        results.append(ensemble_metrics)
        
        return pd.DataFrame(results)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get ensemble model information."""
        base_model_info = []
        
        for i, model in enumerate(self.base_models):
            model_name = getattr(model, 'name', f'model_{i}')
            if hasattr(model, 'get_model_info'):
                info = model.get_model_info()
            else:
                info = {'model_type': type(model).__name__}
            info['name'] = model_name
            base_model_info.append(info)
        
        return {
            'model_type': f'{self.ensemble_method.title()}Ensemble',
            'n_base_models': len(self.base_models),
            'ensemble_method': self.ensemble_method,
            'voting': self.voting if self.ensemble_method == 'voting' else None,
            'base_models': base_model_info,
            'is_fitted': self.is_fitted,
            'training_metrics': self.training_metrics_ if self.is_fitted else {}
        }
