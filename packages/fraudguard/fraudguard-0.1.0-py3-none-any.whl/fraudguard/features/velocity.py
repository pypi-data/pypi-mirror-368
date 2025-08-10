"""
Velocity-based feature extraction for fraud detection.

This module creates features based on transaction velocity and frequency
patterns that are commonly used in fraud detection systems.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union
from ..core.base import BaseFeatureExtractor
import logging

logger = logging.getLogger(__name__)


class VelocityFeatures(BaseFeatureExtractor):
    """
    Extracts velocity-based features for fraud detection.
    
    Velocity features measure the frequency and intensity of transactions
    across different time windows and dimensions (user, merchant, location, etc.).
    """
    
    def __init__(self,
                 time_windows: List[str] = None,
                 user_id_column: str = 'user_id',
                 timestamp_column: str = 'timestamp',
                 amount_column: str = 'amount'):
        super().__init__()
        
        self.time_windows = time_windows or ['1H', '1D', '7D', '30D']
        self.user_id_column = user_id_column
        self.timestamp_column = timestamp_column  
        self.amount_column = amount_column
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract velocity features from transaction data."""
        features = pd.DataFrame(index=data.index)
        
        # Validate required columns
        required_cols = [self.user_id_column, self.timestamp_column]
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            logger.warning(f"Missing required columns: {missing_cols}")
            return features
        
        # Convert timestamp to datetime
        data_copy = data.copy()
        data_copy[self.timestamp_column] = pd.to_datetime(data_copy[self.timestamp_column])
        
        # Sort by timestamp for efficient processing
        data_copy = data_copy.sort_values(self.timestamp_column)
        
        # Extract velocity features
        velocity_features = []
        
        for idx, row in data_copy.iterrows():
            row_features = self._extract_row_velocity_features(row, data_copy)
            velocity_features.append(row_features)
        
        # Convert to DataFrame
        velocity_df = pd.DataFrame(velocity_features, index=data.index)
        features = pd.concat([features, velocity_df], axis=1)
        
        return features
    
    def _extract_row_velocity_features(self, current_row: pd.Series, 
                                     full_data: pd.DataFrame) -> Dict[str, float]:
        """Extract velocity features for a single transaction."""
        features = {}
        current_time = current_row[self.timestamp_column]
        user_id = current_row[self.user_id_column]
        
        # User-based velocity features
        features.update(
            self._get_user_velocity_features(user_id, current_time, full_data)
        )
        
        # Global velocity features (if needed)
        features.update(
            self._get_global_velocity_features(current_time, full_data)
        )
        
        # Merchant velocity features (if available)
        if 'merchant_id' in current_row.index:
            features.update(
                self._get_merchant_velocity_features(
                    current_row['merchant_id'], current_time, full_data
                )
            )
        
        # Location velocity features (if available) 
        if 'country' in current_row.index:
            features.update(
                self._get_location_velocity_features(
                    current_row['country'], current_time, full_data
                )
            )
        
        return features
    
    def _get_user_velocity_features(self, user_id: str, current_time: pd.Timestamp,
                                  data: pd.DataFrame) -> Dict[str, float]:
        """Get user-specific velocity features."""
        features = {}
        
        # Filter to user's past transactions (before current time)
        user_data = data[
            (data[self.user_id_column] == user_id) &
            (data[self.timestamp_column] < current_time)
        ]
        
        if len(user_data) == 0:
            return self._get_zero_velocity_features('user')
        
        # Calculate velocity for each time window
        for window in self.time_windows:
            window_start = current_time - pd.Timedelta(window)
            window_data = user_data[user_data[self.timestamp_column] >= window_start]
            
            # Transaction count velocity
            features[f'user_txn_count_{window}'] = len(window_data)
            
            # Amount velocity (if amount column exists)
            if self.amount_column in data.columns:
                total_amount = window_data[self.amount_column].sum()
                features[f'user_amount_sum_{window}'] = total_amount
                features[f'user_amount_mean_{window}'] = window_data[self.amount_column].mean()
        
        # Transaction frequency patterns
        if len(user_data) >= 2:
            time_diffs = user_data[self.timestamp_column].diff().dropna()
            
            # Time since last transaction
            features['user_time_since_last_txn'] = (
                current_time - user_data[self.timestamp_column].max()
            ).total_seconds() / 3600  # in hours
            
            # Average time between transactions
            features['user_avg_time_between_txns'] = time_diffs.mean().total_seconds() / 3600
            features['user_min_time_between_txns'] = time_diffs.min().total_seconds() / 3600
        
        return features
    
    def _get_global_velocity_features(self, current_time: pd.Timestamp,
                                    data: pd.DataFrame) -> Dict[str, float]:
        """Get global velocity features (across all users)."""
        features = {}
        
        # Filter to past transactions
        past_data = data[data[self.timestamp_column] < current_time]
        
        if len(past_data) == 0:
            return {}
        
        # Calculate global velocity for shorter windows only (to avoid memory issues)
        short_windows = ['1H', '1D']
        
        for window in [w for w in self.time_windows if w in short_windows]:
            window_start = current_time - pd.Timedelta(window)
            window_data = past_data[past_data[self.timestamp_column] >= window_start]
            
            features[f'global_txn_count_{window}'] = len(window_data)
            
            if self.amount_column in data.columns:
                features[f'global_amount_sum_{window}'] = window_data[self.amount_column].sum()
        
        return features
    
    def _get_merchant_velocity_features(self, merchant_id: str, current_time: pd.Timestamp,
                                      data: pd.DataFrame) -> Dict[str, float]:
        """Get merchant-specific velocity features."""
        features = {}
        
        if 'merchant_id' not in data.columns:
            return features
        
        # Filter to merchant's past transactions
        merchant_data = data[
            (data['merchant_id'] == merchant_id) &
            (data[self.timestamp_column] < current_time)
        ]
        
        if len(merchant_data) == 0:
            return self._get_zero_velocity_features('merchant')
        
        # Calculate merchant velocity for selected windows
        for window in ['1H', '1D']:  # Limit to avoid performance issues
            if window in self.time_windows:
                window_start = current_time - pd.Timedelta(window)
                window_data = merchant_data[merchant_data[self.timestamp_column] >= window_start]
                
                features[f'merchant_txn_count_{window}'] = len(window_data)
                features[f'merchant_unique_users_{window}'] = window_data[self.user_id_column].nunique()
        
        return features
    
    def _get_location_velocity_features(self, country: str, current_time: pd.Timestamp,
                                      data: pd.DataFrame) -> Dict[str, float]:
        """Get location-specific velocity features.""" 
        features = {}
        
        if 'country' not in data.columns:
            return features
        
        # Filter to country's past transactions
        country_data = data[
            (data['country'] == country) &
            (data[self.timestamp_column] < current_time)
        ]
        
        if len(country_data) == 0:
            return {}
        
        # Calculate location velocity for 1 hour window only
        window_start = current_time - pd.Timedelta('1H')
        window_data = country_data[country_data[self.timestamp_column] >= window_start]
        
        features['country_txn_count_1H'] = len(window_data)
        features['country_unique_users_1H'] = window_data[self.user_id_column].nunique()
        
        return features
    
    def _get_zero_velocity_features(self, prefix: str) -> Dict[str, float]:
        """Return zero velocity features for new entities."""
        features = {}
        
        for window in self.time_windows:
            features[f'{prefix}_txn_count_{window}'] = 0
            if self.amount_column:
                features[f'{prefix}_amount_sum_{window}'] = 0
                features[f'{prefix}_amount_mean_{window}'] = 0
        
        if prefix == 'user':
            features['user_time_since_last_txn'] = float('inf')
            features['user_avg_time_between_txns'] = 0
            features['user_min_time_between_txns'] = 0
        
        return features
