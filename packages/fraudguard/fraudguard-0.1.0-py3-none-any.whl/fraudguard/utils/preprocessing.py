"""
Data preprocessing utilities for fraud detection.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging

from ..core.exceptions import DataError

logger = logging.getLogger(__name__)


class FraudPreprocessor:
    """
    Preprocessing utilities for fraud detection data.
    
    Handles common data cleaning, transformation, and preparation
    tasks specific to fraud detection workflows.
    """
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.is_fitted = False
        
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare fraud detection data."""
        cleaned_data = data.copy()
        
        # Handle missing values
        cleaned_data = self._handle_missing_values(cleaned_data)
        
        # Remove duplicates
        initial_rows = len(cleaned_data)
        cleaned_data = cleaned_data.drop_duplicates()
        removed_rows = initial_rows - len(cleaned_data)
        
        if removed_rows > 0:
            logger.info(f"Removed {removed_rows} duplicate rows")
            
        return cleaned_data
    
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset."""
        # Fill numeric columns with median
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if data[col].isnull().any():
                median_value = data[col].median()
                data[col].fillna(median_value, inplace=True)
                
        # Fill categorical columns with mode
        categorical_columns = data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if data[col].isnull().any():
                mode_value = data[col].mode().iloc[0] if not data[col].mode().empty else 'unknown'
                data[col].fillna(mode_value, inplace=True)
                
        return data
    
    def validate_data(self, data: pd.DataFrame, required_columns: Optional[List[str]] = None):
        """Validate input data for fraud detection."""
        if data.empty:
            raise DataError("Input data is empty")
            
        if required_columns:
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise DataError(f"Missing required columns: {missing_columns}")
                
        # Check for reasonable data types
        if 'amount' in data.columns:
            if not pd.api.types.is_numeric_dtype(data['amount']):
                raise DataError("Amount column must be numeric")
            if (data['amount'] < 0).any():
                raise DataError("Amount column contains negative values")
