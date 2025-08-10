"""
Pytest configuration and fixtures for FraudGuard tests.
"""

import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def dummy_transaction_data():
    """Create dummy transaction data with proper feature engineering."""
    # Create raw transaction data
    raw_data = pd.DataFrame({
        'user_id': ['A1', 'A2'],
        'amount': [120.0, 2500.0],
        'merchant_category': ['retail', 'crypto'],
        'country': ['US', 'XX'],
        'timestamp': ['2024-08-09T08:00:00', '2024-08-10T23:15:00'],
        'payment_method': ['card', 'paypal'],
        'card_type': ['credit', 'debit']
    })
    
    # Convert timestamp to datetime
    raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'])
    
    return raw_data

@pytest.fixture
def processed_transaction_data():
    """Create processed transaction data suitable for ML models."""
    # Create numeric-only data that XGBoost can handle
    return pd.DataFrame({
        'amount': [120.0, 2500.0],
        'amount_log': [np.log1p(120.0), np.log1p(2500.0)],
        'hour': [8, 23],
        'day_of_week': [4, 5],  # Friday, Saturday
        'is_weekend': [0, 1],
        'is_high_risk_country': [0, 1],
        'is_high_risk_merchant': [0, 1],
        'is_digital_payment': [0, 1],
        'user_txn_count_30d': [5, 2],
        'amount_zscore': [-0.5, 2.1]
    })

@pytest.fixture 
def dummy_labels():
    """Create dummy labels as pandas Series."""
    return pd.Series([0, 1], name='is_fraud')
