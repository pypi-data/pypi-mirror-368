"""
Transaction-based feature extraction.

This module provides features directly derived from individual transaction
attributes like amount, merchant, location, etc.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from ..core.base import BaseFeatureExtractor
from ..core.config import config
import logging

logger = logging.getLogger(__name__)


class TransactionFeatures(BaseFeatureExtractor):
    """
    Extracts features from individual transaction attributes.
    
    Features include:
    - Amount-based features (bins, log-transform, z-score)
    - Merchant category features
    - Geographic features
    - Time-based features
    - Payment method features
    """
    
    def __init__(self, 
                 amount_bins: Optional[List[float]] = None,
                 include_merchant: bool = True,
                 include_geographic: bool = True,
                 include_time: bool = True,
                 include_payment_method: bool = True):
        super().__init__()
        
        self.amount_bins = amount_bins or config.get('features.transaction.amount_bins')
        self.include_merchant = include_merchant
        self.include_geographic = include_geographic  
        self.include_time = include_time
        self.include_payment_method = include_payment_method
        
        # Fitted parameters
        self.amount_mean_ = None
        self.amount_std_ = None
        self.merchant_encoder_ = None
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract transaction features from data."""
        features = pd.DataFrame(index=data.index)
        
        # Amount features
        if 'amount' in data.columns:
            features = pd.concat([features, self._extract_amount_features(data)], axis=1)
            
        # Merchant features  
        if self.include_merchant and 'merchant_category' in data.columns:
            features = pd.concat([features, self._extract_merchant_features(data)], axis=1)
            
        # Geographic features
        if self.include_geographic:
            features = pd.concat([features, self._extract_geographic_features(data)], axis=1)
            
        # Time features
        if self.include_time and 'timestamp' in data.columns:
            features = pd.concat([features, self._extract_time_features(data)], axis=1)
            
        # Payment method features
        if self.include_payment_method and 'payment_method' in data.columns:
            features = pd.concat([features, self._extract_payment_features(data)], axis=1)
            
        return features
    
    def _extract_amount_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract amount-based features."""
        features = pd.DataFrame(index=data.index)
        amount = data['amount']
        
        # Basic amount features
        features['amount'] = amount
        features['amount_log'] = np.log1p(amount)
        features['amount_sqrt'] = np.sqrt(amount)
        
        # Amount bins
        features['amount_bin'] = pd.cut(amount, bins=self.amount_bins, labels=False)
        
        # Amount statistics (if fitted)
        if self.amount_mean_ is not None and self.amount_std_ is not None:
            features['amount_zscore'] = (amount - self.amount_mean_) / self.amount_std_
            features['amount_high'] = (amount > self.amount_mean_ + 2 * self.amount_std_).astype(int)
            features['amount_low'] = (amount < self.amount_mean_ - 2 * self.amount_std_).astype(int)
        
        # Round number detection
        features['is_round_amount'] = (amount % 1 == 0).astype(int)
        features['is_round_10'] = (amount % 10 == 0).astype(int) 
        features['is_round_100'] = (amount % 100 == 0).astype(int)
        
        return features
    
    def _extract_merchant_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract merchant-based features."""
        features = pd.DataFrame(index=data.index)
        
        # Merchant category encoding
        if 'merchant_category' in data.columns:
            merchant_dummies = pd.get_dummies(data['merchant_category'], prefix='merchant')
            features = pd.concat([features, merchant_dummies], axis=1)
        
        # Merchant risk indicators (common high-risk categories)
        high_risk_categories = ['online_gaming', 'crypto', 'adult_entertainment', 'gambling']
        if 'merchant_category' in data.columns:
            features['high_risk_merchant'] = data['merchant_category'].isin(high_risk_categories).astype(int)
        
        return features
    
    def _extract_geographic_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract geographic features."""
        features = pd.DataFrame(index=data.index)
        
        # Country features
        if 'country' in data.columns:
            country_dummies = pd.get_dummies(data['country'], prefix='country')
            features = pd.concat([features, country_dummies], axis=1)
            
            # High-risk countries (example list)
            high_risk_countries = ['XX', 'YY', 'ZZ']  # Replace with actual risk list
            features['high_risk_country'] = data['country'].isin(high_risk_countries).astype(int)
        
        # Distance features (if lat/lon available)
        if all(col in data.columns for col in ['user_lat', 'user_lon', 'merchant_lat', 'merchant_lon']):
            features['transaction_distance'] = self._calculate_distance(
                data['user_lat'], data['user_lon'],
                data['merchant_lat'], data['merchant_lon']
            )
            
        return features
    
    def _extract_time_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract time-based features."""
        features = pd.DataFrame(index=data.index)
        
        # Convert timestamp to datetime if needed
        timestamp = pd.to_datetime(data['timestamp'])
        
        # Basic time features
        features['hour'] = timestamp.dt.hour
        features['day_of_week'] = timestamp.dt.dayofweek
        features['day_of_month'] = timestamp.dt.day
        features['month'] = timestamp.dt.month
        features['is_weekend'] = (timestamp.dt.dayofweek >= 5).astype(int)
        
        # Business hours
        features['is_business_hours'] = ((timestamp.dt.hour >= 9) & (timestamp.dt.hour <= 17)).astype(int)
        features['is_night_time'] = ((timestamp.dt.hour >= 22) | (timestamp.dt.hour <= 5)).astype(int)
        
        # Cyclical encoding for temporal features
        features['hour_sin'] = np.sin(2 * np.pi * features['hour'] / 24)
        features['hour_cos'] = np.cos(2 * np.pi * features['hour'] / 24)
        features['day_sin'] = np.sin(2 * np.pi * features['day_of_week'] / 7)
        features['day_cos'] = np.cos(2 * np.pi * features['day_of_week'] / 7)
        
        return features
    
    def _extract_payment_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract payment method features."""
        features = pd.DataFrame(index=data.index)
        
        # Payment method dummies
        if 'payment_method' in data.columns:
            payment_dummies = pd.get_dummies(data['payment_method'], prefix='payment')
            features = pd.concat([features, payment_dummies], axis=1)
        
        # Card type features
        if 'card_type' in data.columns:
            card_dummies = pd.get_dummies(data['card_type'], prefix='card')
            features = pd.concat([features, card_dummies], axis=1)
        
        # Digital payment indicators
        if 'payment_method' in data.columns:
            digital_methods = ['paypal', 'apple_pay', 'google_pay', 'venmo']
            features['is_digital_payment'] = data['payment_method'].isin(digital_methods).astype(int)
        
        return features
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate haversine distance between two points."""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Fit the feature extractor to training data."""
        if 'amount' in X.columns:
            self.amount_mean_ = X['amount'].mean()
            self.amount_std_ = X['amount'].std()
            
        return super().fit(X, y)
