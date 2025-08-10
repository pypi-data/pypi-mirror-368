"""
Temporal feature extraction for fraud detection.

This module creates time-based features that capture temporal patterns
and seasonal behaviors in transaction data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from ..core.base import BaseFeatureExtractor
import logging

logger = logging.getLogger(__name__)


class TemporalFeatures(BaseFeatureExtractor):
    """
    Extracts temporal features from transaction timestamps.
    
    Features include:
    - Cyclical time encodings
    - Holiday and special date indicators
    - Time-based aggregations
    - Temporal anomaly scores
    """
    
    def __init__(self,
                 timestamp_column: str = 'timestamp',
                 include_holidays: bool = True,
                 holiday_country: str = 'US'):
        super().__init__()
        
        self.timestamp_column = timestamp_column
        self.include_holidays = include_holidays
        self.holiday_country = holiday_country
        
        # Holiday calendar (simplified - in production use holidays library)
        self.holidays = self._get_holiday_calendar()
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract temporal features from timestamp data."""
        features = pd.DataFrame(index=data.index)
        
        if self.timestamp_column not in data.columns:
            logger.warning(f"Timestamp column '{self.timestamp_column}' not found")
            return features
        
        # Convert to datetime
        timestamp = pd.to_datetime(data[self.timestamp_column])
        
        # Basic time features
        features.update(self._extract_basic_time_features(timestamp))
        
        # Cyclical encodings
        features.update(self._extract_cyclical_features(timestamp))
        
        # Holiday features
        if self.include_holidays:
            features.update(self._extract_holiday_features(timestamp))
        
        # Time-based anomaly features
        features.update(self._extract_temporal_anomalies(timestamp))
        
        return pd.DataFrame(features, index=data.index)
    
    def _extract_basic_time_features(self, timestamp: pd.Series) -> Dict[str, np.ndarray]:
        """Extract basic time components."""
        features = {}
        
        # Basic components
        features['hour'] = timestamp.dt.hour.values
        features['day'] = timestamp.dt.day.values
        features['month'] = timestamp.dt.month.values
        features['year'] = timestamp.dt.year.values
        features['dayofweek'] = timestamp.dt.dayofweek.values
        features['dayofyear'] = timestamp.dt.dayofyear.values
        features['quarter'] = timestamp.dt.quarter.values
        
        # Week features
        features['week'] = timestamp.dt.isocalendar().week.values
        features['is_month_start'] = timestamp.dt.is_month_start.astype(int).values
        features['is_month_end'] = timestamp.dt.is_month_end.astype(int).values
        features['is_quarter_start'] = timestamp.dt.is_quarter_start.astype(int).values
        features['is_quarter_end'] = timestamp.dt.is_quarter_end.astype(int).values
        
        return features
    
    def _extract_cyclical_features(self, timestamp: pd.Series) -> Dict[str, np.ndarray]:
        """Extract cyclical encodings for temporal features."""
        features = {}
        
        # Hour cyclical (24 hours)
        hour_radians = 2 * np.pi * timestamp.dt.hour / 24
        features['hour_sin'] = np.sin(hour_radians).values
        features['hour_cos'] = np.cos(hour_radians).values
        
        # Day of week cyclical (7 days)
        dow_radians = 2 * np.pi * timestamp.dt.dayofweek / 7
        features['dayofweek_sin'] = np.sin(dow_radians).values
        features['dayofweek_cos'] = np.cos(dow_radians).values
        
        # Day of month cyclical (31 days)
        dom_radians = 2 * np.pi * (timestamp.dt.day - 1) / 31
        features['dayofmonth_sin'] = np.sin(dom_radians).values
        features['dayofmonth_cos'] = np.cos(dom_radians).values
        
        # Month cyclical (12 months)
        month_radians = 2 * np.pi * (timestamp.dt.month - 1) / 12
        features['month_sin'] = np.sin(month_radians).values
        features['month_cos'] = np.cos(month_radians).values
        
        # Day of year cyclical (365 days)
        doy_radians = 2 * np.pi * (timestamp.dt.dayofyear - 1) / 365
        features['dayofyear_sin'] = np.sin(doy_radians).values
        features['dayofyear_cos'] = np.cos(doy_radians).values
        
        return features
    
    def _extract_holiday_features(self, timestamp: pd.Series) -> Dict[str, np.ndarray]:
        """Extract holiday-related features."""
        features = {}
        
        # Convert to date for comparison
        dates = timestamp.dt.date
        
        # Holiday indicators
        features['is_holiday'] = dates.isin(self.holidays).astype(int).values
        
        # Days before/after holidays
        features['days_to_next_holiday'] = self._days_to_next_holiday(dates)
        features['days_from_last_holiday'] = self._days_from_last_holiday(dates)
        
        # Holiday season indicators (simplified)
        features['is_holiday_season'] = (
            (timestamp.dt.month == 12) | 
            ((timestamp.dt.month == 11) & (timestamp.dt.day >= 15))
        ).astype(int).values
        
        # Weekend indicators
        features['is_weekend'] = (timestamp.dt.dayofweek >= 5).astype(int).values
        features['is_friday'] = (timestamp.dt.dayofweek == 4).astype(int).values
        features['is_monday'] = (timestamp.dt.dayofweek == 0).astype(int).values
        
        return features
    
    def _extract_temporal_anomalies(self, timestamp: pd.Series) -> Dict[str, np.ndarray]:
        """Extract temporal anomaly indicators."""
        features = {}
        
        # Unusual time indicators
        features['is_late_night'] = ((timestamp.dt.hour >= 23) | (timestamp.dt.hour <= 5)).astype(int).values
        features['is_early_morning'] = (timestamp.dt.hour <= 6).astype(int).values
        features['is_business_hours'] = ((timestamp.dt.hour >= 9) & (timestamp.dt.hour <= 17)).astype(int).values
        
        # Weekend + late night combinations (higher fraud risk)
        is_weekend = timestamp.dt.dayofweek >= 5
        is_late = (timestamp.dt.hour >= 22) | (timestamp.dt.hour <= 4)
        features['weekend_late_night'] = (is_weekend & is_late).astype(int).values
        
        # First/last day of month (payday patterns)
        features['is_payday'] = (
            (timestamp.dt.day <= 2) | 
            (timestamp.dt.day >= 28)
        ).astype(int).values
        
        return features
    
    def _get_holiday_calendar(self) -> List[pd.Timestamp]:
        """Get list of major holidays (simplified version)."""
        # In production, use the 'holidays' library for comprehensive coverage
        holidays_2024 = [
            pd.Timestamp('2024-01-01'),  # New Year's Day
            pd.Timestamp('2024-07-04'),  # Independence Day  
            pd.Timestamp('2024-12-25'),  # Christmas Day
            # Add more holidays as needed
        ]
        
        return holidays_2024
    
    def _days_to_next_holiday(self, dates: pd.Series) -> np.ndarray:
        """Calculate days until next holiday for each date."""
        days_to_holiday = []
        
        for date in dates:
            future_holidays = [h for h in self.holidays if h.date() > date]
            if future_holidays:
                next_holiday = min(future_holidays)
                days_to_holiday.append((next_holiday.date() - date).days)
            else:
                days_to_holiday.append(365)  # No holiday in next year
        
        return np.array(days_to_holiday)
    
    def _days_from_last_holiday(self, dates: pd.Series) -> np.ndarray:
        """Calculate days since last holiday for each date."""
        days_from_holiday = []
        
        for date in dates:
            past_holidays = [h for h in self.holidays if h.date() <= date]
            if past_holidays:
                last_holiday = max(past_holidays)
                days_from_holiday.append((date - last_holiday.date()).days)
            else:
                days_from_holiday.append(365)  # No recent holiday
        
        return np.array(days_from_holiday)
