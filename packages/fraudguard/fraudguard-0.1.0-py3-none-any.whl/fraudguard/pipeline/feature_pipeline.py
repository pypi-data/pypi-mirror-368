"""
Feature pipeline for combining multiple feature extractors.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Union
import logging

from ..core.base import BaseFeatureExtractor
from ..core.exceptions import FeatureExtractionError

logger = logging.getLogger(__name__)


class FeaturePipeline:
    """
    Pipeline for combining and managing multiple feature extractors.
    
    Allows chaining feature extractors and provides a unified interface
    for feature engineering operations.
    """
    
    def __init__(self, extractors: Optional[List[BaseFeatureExtractor]] = None):
        self.extractors = extractors or []
        self.is_fitted = False
        self.feature_names_ = []
        
    def add_extractor(self, extractor: BaseFeatureExtractor):
        """Add a feature extractor to the pipeline."""
        self.extractors.append(extractor)
        return self
        
    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Fit all feature extractors in the pipeline."""
        try:
            for extractor in self.extractors:
                extractor.fit(X, y)
                
            # Collect all feature names
            self.feature_names_ = []
            for extractor in self.extractors:
                self.feature_names_.extend(extractor.get_feature_names())
                
            self.is_fitted = True
            logger.info(f"Feature pipeline fitted with {len(self.extractors)} extractors")
            return self
            
        except Exception as e:
            raise FeatureExtractionError(f"Error fitting feature pipeline: {str(e)}")
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data using all fitted extractors."""
        if not self.is_fitted:
            raise FeatureExtractionError("Pipeline must be fitted before transform")
            
        try:
            features_list = []
            
            for extractor in self.extractors:
                extracted_features = extractor.transform(X)
                features_list.append(extracted_features)
                
            # Combine all features
            if features_list:
                combined_features = pd.concat(features_list, axis=1)
                return combined_features
            else:
                return pd.DataFrame(index=X.index)
                
        except Exception as e:
            raise FeatureExtractionError(f"Error transforming features: {str(e)}")
    
    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> pd.DataFrame:
        """Fit and transform in one step."""
        return self.fit(X, y).transform(X)
    
    def __add__(self, other: Union[BaseFeatureExtractor, 'FeaturePipeline']) -> 'FeaturePipeline':
        """Allow combining with + operator."""
        if isinstance(other, BaseFeatureExtractor):
            new_extractors = self.extractors + [other]
        elif isinstance(other, FeaturePipeline):
            new_extractors = self.extractors + other.extractors
        else:
            raise TypeError("Can only add FeatureExtractor or FeaturePipeline")
            
        return FeaturePipeline(new_extractors)
    
    def get_feature_names(self) -> List[str]:
        """Get all feature names from the pipeline."""
        return self.feature_names_
