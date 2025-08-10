"""
Base classes for all FraudGuard components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import logging

logger = logging.getLogger(__name__)


class BaseFeatureExtractor(ABC, BaseEstimator, TransformerMixin):
    """
    Base class for all feature extractors in FraudGuard.
    
    Feature extractors are responsible for transforming raw transaction data
    into machine learning features suitable for fraud detection.
    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.is_fitted = False
        self.feature_names_ = []
        
    @abstractmethod
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from the input data.
        
        Args:
            data: Input transaction data
            
        Returns:
            DataFrame with extracted features
        """
        pass
    
    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Fit the feature extractor to the training data."""
        self.feature_names_ = self.extract_features(X).columns.tolist()
        self.is_fitted = True
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform input data using fitted feature extractor."""
        if not self.is_fitted:
            raise ValueError(f"{self.name} must be fitted before transform")
        return self.extract_features(X)
    
    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> pd.DataFrame:
        """Fit and transform in one step."""
        return self.fit(X, y).transform(X)
    
    def __add__(self, other: 'BaseFeatureExtractor') -> 'FeaturePipeline':
        """Allow combining feature extractors with + operator."""
        from ..pipeline.feature_pipeline import FeaturePipeline
        return FeaturePipeline([self, other])
    
    def get_feature_names(self) -> List[str]:
        """Get names of extracted features."""
        return self.feature_names_


class BaseModel(ABC, BaseEstimator):
    """
    Base class for all machine learning models in FraudGuard.
    """
    
    def __init__(self, name: Optional[str] = None, **kwargs):
        self.name = name or self.__class__.__name__
        self.model = None
        self.is_fitted = False
        self.feature_names_ = []
        self.classes_ = []
        
    @abstractmethod
    def _create_model(self, **kwargs):
        """Create the underlying ML model."""
        pass
    
    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs):
        """Train the model on the given data."""
        pass
    
    @abstractmethod 
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions on new data."""
        pass
    
    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return prediction probabilities."""
        pass
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores if available."""
        if hasattr(self.model, 'feature_importances_'):
            return dict(zip(self.feature_names_, self.model.feature_importances_))
        return {}


class BasePipeline(ABC):
    """
    Base class for fraud detection pipelines.
    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self.is_fitted = False
        
    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs):
        """Fit the pipeline to training data."""
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make fraud predictions."""
        pass
    
    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return fraud probability scores."""
        pass
