"""
Basic tests for model implementations.
"""

import numpy as np
import pandas as pd
from fraudguard.models.xgboost_model import XGBoostModel

def test_xgboost_fit_predict(processed_transaction_data, dummy_labels):
    """Test XGBoost model with properly processed numeric data."""
    model = XGBoostModel()
    model.fit(processed_transaction_data, dummy_labels)
    preds = model.predict(processed_transaction_data)
    assert len(preds) == len(dummy_labels)
    assert all(pred in [0, 1] for pred in preds)  # Check binary predictions

def test_xgboost_predict_proba(processed_transaction_data, dummy_labels):
    """Test XGBoost probability predictions."""
    model = XGBoostModel()
    model.fit(processed_transaction_data, dummy_labels)
    probas = model.predict_proba(processed_transaction_data)
    assert probas.shape == (len(dummy_labels), 2)  # Two classes
    assert np.allclose(probas.sum(axis=1), 1.0)  # Probabilities sum to 1
