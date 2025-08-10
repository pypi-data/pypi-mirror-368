"""
Model orchestrator for managing multiple ML models.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, cast
import logging

from ..models.base_model import BaseFraudModel
from ..core.exceptions import ModelError

logger = logging.getLogger(__name__)


class ModelOrchestrator:
    """
    Orchestrates multiple fraud detection models.
    
    Manages training, prediction, and evaluation of multiple models,
    supporting both individual model access and ensemble operations.
    """
    
    def __init__(self):
        self.models: Dict[str, BaseFraudModel] = {}
        self.is_fitted = False
        
    def add_model(self, name: str, model: BaseFraudModel):
        """Add a model to the orchestrator."""
        self.models[name] = model
        logger.info(f"Added model '{name}' to orchestrator")
        
    def remove_model(self, name: str):
        """Remove a model from the orchestrator."""
        if name in self.models:
            del self.models[name]
            logger.info(f"Removed model '{name}' from orchestrator")
        else:
            logger.warning(f"Model '{name}' not found")
            
    def has_models(self) -> bool:
        """Check if orchestrator has any models."""
        return len(self.models) > 0
    
    def fit(self, X: pd.DataFrame, y: pd.Series, 
            validation_data: Optional[tuple] = None, **kwargs):
        """Fit all models in the orchestrator."""
        if not self.has_models():
            raise ModelError("No models to train")
            
        try:
            for name, model in self.models.items():
                logger.info(f"Training model: {name}")
                model.fit(X, y, validation_data=validation_data, **kwargs)
                
            self.is_fitted = True
            logger.info(f"Successfully trained {len(self.models)} models")
            
        except Exception as e:
            raise ModelError(f"Error training models: {str(e)}")
    
    def predict(self, X: pd.DataFrame, model_name: Optional[str] = None) -> np.ndarray:
        """Make predictions using specified model or primary model."""
        if not self.is_fitted:
            raise ModelError("Models must be fitted before prediction")
            
        if model_name:
            if model_name not in self.models:
                raise ModelError(f"Model '{model_name}' not found")
            return self.models[model_name].predict(X)
        else:
            # Use first model as default
            first_model = next(iter(self.models.values()))
            return first_model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame, model_name: Optional[str] = None) -> np.ndarray:
        """Get prediction probabilities from specified model or primary model."""
        if not self.is_fitted:
            raise ModelError("Models must be fitted before prediction")
            
        if model_name:
            if model_name not in self.models:
                raise ModelError(f"Model '{model_name}' not found")
            return self.models[model_name].predict_proba(X)
        else:
            # Use first model as default
            first_model = next(iter(self.models.values()))
            return first_model.predict_proba(X)
    
    def predict_all(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Get predictions from all models."""
        if not self.is_fitted:
            raise ModelError("Models must be fitted before prediction")
            
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict_proba(X)[:, 1]  # Fraud probability
            
        return predictions
    
    def get_feature_importance(self, model_name: Optional[str] = None) -> Dict[str, float]:
        """Get feature importance from specified model or combined importance."""
        if not self.is_fitted:
            return {}
            
        if model_name:
            if model_name not in self.models:
                raise ModelError(f"Model '{model_name}' not found")
            return self.models[model_name].get_feature_importance()
        else:
            # Combine importance from all models
            combined_importance = {}
            valid_models = 0
            
            for model in self.models.values():
                importance = model.get_feature_importance()
                if importance:
                    valid_models += 1
                    for feature, score in importance.items():
                        if feature not in combined_importance:
                            combined_importance[feature] = 0
                        combined_importance[feature] += score
            
            # Average the importance scores
            if valid_models > 0:
                for feature in combined_importance:
                    combined_importance[feature] /= valid_models
                    
            return combined_importance
    
    def get_models_info(self) -> Dict[str, Any]:
        """Get information about all models."""
        models_info = {}
        
        for name, model in self.models.items():
            get_info = getattr(model, 'get_model_info', None)
            if callable(get_info):
                models_info[name] = cast(Callable[[], Dict[str, Any]], get_info)()
            else:
                models_info[name] = {
                    'model_type': type(model).__name__,
                    'is_fitted': getattr(model, 'is_fitted', False)
                }
                
        return models_info
