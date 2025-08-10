"""
Behavioral feature extraction for fraud detection.

This module creates features based on user behavior patterns,
aggregating historical transaction data to identify anomalies.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from ..core.base import BaseFeatureExtractor
from ..core.config import config
import logging

logger = logging.getLogger(__name__)


class BehavioralFeatures(BaseFeatureExtractor):
    """
    Extracts behavioral features based on user transaction history.
    
    Features include:
    - Transaction frequency patterns
    - Spending behavior analysis
    - Merchant preference patterns  
    - Geographic behavior patterns
    - Deviation from normal behavior
    """
    
    def __init__(self,
                 lookback_days: int = 30,
                 aggregation_functions: List[str] = None,
                 user_id_column: str = 'user_id',
                 timestamp_column: str = 'timestamp'):
        super().__init__()
        
        self.lookback_days = lookback_days
        self.aggregation_functions = aggregation_functions or ['mean', 'std', 'count', 'sum']
        self.user_id_column = user_id_column
        self.timestamp_column = timestamp_column
        
        # Fitted parameters
        self.user_profiles_ = {}
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract behavioral features from transaction data."""
        features = pd.DataFrame(index=data.index)
        
        if self.user_id_column not in data.columns:
            logger.warning(f"User ID column '{self.user_id_column}' not found")
            return features
            
        # Convert timestamp to datetime
        data_copy = data.copy()
        data_copy[self.timestamp_column] = pd.to_datetime(data_copy[self.timestamp_column])
        
        # Extract behavioral features for each transaction
        behavioral_features = []
        
        for idx, row in data_copy.iterrows():
            user_id = row[self.user_id_column]
            current_time = row[self.timestamp_column]
            
            # Get user's behavioral features
            user_features = self._get_user_behavioral_features(
                user_id, current_time, data_copy
            )
            
            behavioral_features.append(user_features)
        
        # Convert to DataFrame
        behavioral_df = pd.DataFrame(behavioral_features, index=data.index)
        features = pd.concat([features, behavioral_df], axis=1)
        
        return features
    
    def _get_user_behavioral_features(self, user_id: str, current_time: pd.Timestamp, 
                                    data: pd.DataFrame) -> Dict[str, Any]:
        """Get behavioral features for a specific user and time."""
        
        # Filter to user's historical transactions (before current time)
        user_history = data[
            (data[self.user_id_column] == user_id) &
            (data[self.timestamp_column] < current_time) &
            (data[self.timestamp_column] >= current_time - pd.Timedelta(days=self.lookback_days))
        ].copy()
        
        features = {}
        
        if len(user_history) == 0:
            # No history - return default features
            return self._get_default_features()
        
        # Transaction frequency features
        features.update(self._extract_frequency_features(user_history, current_time))
        
        # Amount behavior features
        features.update(self._extract_amount_behavior(user_history))
        
        # Merchant behavior features  
        features.update(self._extract_merchant_behavior(user_history))
        
        # Time behavior features
        features.update(self._extract_time_behavior(user_history))
        
        # Geographic behavior features
        features.update(self._extract_geographic_behavior(user_history))
        
        return features
    
    def _extract_frequency_features(self, user_history: pd.DataFrame, 
                                  current_time: pd.Timestamp) -> Dict[str, Any]:
        """Extract transaction frequency features."""
        features = {}
        
        # Basic frequency statistics
        features['txn_count_30d'] = len(user_history)
        
        # Daily transaction patterns
        daily_counts = user_history.groupby(user_history[self.timestamp_column].dt.date).size()
        
        if len(daily_counts) > 0:
            features['avg_txns_per_day'] = daily_counts.mean()
            features['std_txns_per_day'] = daily_counts.std()
            features['max_txns_per_day'] = daily_counts.max()
        else:
            features['avg_txns_per_day'] = 0
            features['std_txns_per_day'] = 0
            features['max_txns_per_day'] = 0
        
        # Time since last transaction
        if len(user_history) > 0:
            last_txn_time = user_history[self.timestamp_column].max()
            features['hours_since_last_txn'] = (current_time - last_txn_time).total_seconds() / 3600
        else:
            features['hours_since_last_txn'] = float('inf')
        
        return features
    
    def _extract_amount_behavior(self, user_history: pd.DataFrame) -> Dict[str, Any]:
        """Extract amount-based behavioral features."""
        features = {}
        
        if 'amount' not in user_history.columns or len(user_history) == 0:
            return {'avg_amount': 0, 'std_amount': 0, 'total_amount': 0}
        
        amounts = user_history['amount']
        
        # Basic amount statistics
        for func in self.aggregation_functions:
            if hasattr(amounts, func):
                features[f'amount_{func}'] = getattr(amounts, func)()
        
        # Amount percentiles
        features['amount_p25'] = amounts.quantile(0.25)
        features['amount_p75'] = amounts.quantile(0.75)
        features['amount_p95'] = amounts.quantile(0.95)
        
        # Amount patterns
        features['amount_range'] = amounts.max() - amounts.min()
        features['amount_cv'] = amounts.std() / amounts.mean() if amounts.mean() > 0 else 0
        
        return features
    
    def _extract_merchant_behavior(self, user_history: pd.DataFrame) -> Dict[str, Any]:
        """Extract merchant behavioral features."""
        features = {}
        
        if 'merchant_category' not in user_history.columns:
            return {}
            
        # Merchant diversity
        unique_merchants = user_history['merchant_category'].nunique()
        total_transactions = len(user_history)
        
        features['merchant_diversity'] = unique_merchants / total_transactions if total_transactions > 0 else 0
        features['unique_merchants'] = unique_merchants
        
        # Most frequent merchant category
        if len(user_history) > 0:
            top_merchant = user_history['merchant_category'].mode()
            if len(top_merchant) > 0:
                features['top_merchant_category'] = top_merchant.iloc[0]
                features['top_merchant_pct'] = (user_history['merchant_category'] == top_merchant.iloc[0]).mean()
        
        return features
    
    def _extract_time_behavior(self, user_history: pd.DataFrame) -> Dict[str, Any]:
        """Extract temporal behavioral features."""
        features = {}
        
        if len(user_history) == 0:
            return {}
        
        # Hour patterns
        hours = user_history[self.timestamp_column].dt.hour
        features['preferred_hour'] = hours.mode().iloc[0] if len(hours.mode()) > 0 else 12
        features['hour_std'] = hours.std()
        
        # Day of week patterns
        days = user_history[self.timestamp_column].dt.dayofweek
        features['weekend_txn_pct'] = (days >= 5).mean()
        
        # Business hours usage
        business_hours = ((hours >= 9) & (hours <= 17))
        features['business_hours_pct'] = business_hours.mean()
        
        return features
    
    def _extract_geographic_behavior(self, user_history: pd.DataFrame) -> Dict[str, Any]:
        """Extract geographic behavioral features."""
        features = {}
        
        # Country diversity
        if 'country' in user_history.columns:
            unique_countries = user_history['country'].nunique()
            features['country_diversity'] = unique_countries
            
            # International transaction percentage
            if len(user_history) > 0:
                # Assume first country is home country
                home_country = user_history['country'].mode()
                if len(home_country) > 0:
                    features['international_txn_pct'] = (
                        user_history['country'] != home_country.iloc[0]
                    ).mean()
        
        return features
    
    def _get_default_features(self) -> Dict[str, Any]:
        """Return default features for users with no history."""
        return {
            'txn_count_30d': 0,
            'avg_txns_per_day': 0,
            'std_txns_per_day': 0,
            'max_txns_per_day': 0,
            'hours_since_last_txn': float('inf'),
            'amount_mean': 0,
            'amount_std': 0,
            'amount_count': 0,
            'amount_sum': 0,
            'merchant_diversity': 0,
            'unique_merchants': 0,
            'weekend_txn_pct': 0,
            'business_hours_pct': 0,
            'country_diversity': 0,
            'international_txn_pct': 0
        }
