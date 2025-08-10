"""
Unit tests for feature extractors.
"""

import pandas as pd
import numpy as np
from fraudguard.features.transaction import TransactionFeatures
from fraudguard.features.behavioral import BehavioralFeatures

def test_transaction_features(dummy_transaction_data):
    """Test transaction feature extraction."""
    features = TransactionFeatures()
    processed = features.fit_transform(dummy_transaction_data)
    
    # Check that we have numeric features
    assert 'amount' in processed.columns
    assert 'amount_log' in processed.columns
    assert processed.shape[0] == dummy_transaction_data.shape[0]
    
    # Verify numeric data types
    numeric_cols = processed.select_dtypes(include=[np.number]).columns
    assert len(numeric_cols) > 0, "Should produce numeric features"

def test_behavioral_features(dummy_transaction_data):
    """Test behavioral feature extraction."""
    features = BehavioralFeatures()
    processed = features.fit_transform(dummy_transaction_data) 
    
    # Should have behavioral features
    assert 'txn_count_30d' in processed.columns
    assert processed.shape[0] == dummy_transaction_data.shape[0]
    
    # Check for numeric outputs
    assert processed.dtypes.apply(lambda x: pd.api.types.is_numeric_dtype(x)).all()
