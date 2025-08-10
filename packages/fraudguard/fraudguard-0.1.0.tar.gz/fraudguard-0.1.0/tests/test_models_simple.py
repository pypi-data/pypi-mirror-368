# tests/test_models_simple.py
"""
Simplified model tests with numeric data only.
"""

import numpy as np
import pandas as pd
from fraudguard.models.xgboost_model import XGBoostModel

def test_xgboost_simple():
    """Test XGBoost with simple numeric data."""
    # Create simple numeric data
    X = pd.DataFrame({
        'feature1': [1.0, 2.0, 3.0, 4.0],
        'feature2': [0.5, 1.5, 2.5, 3.5],
        'feature3': [10, 20, 30, 40]
    })
    y = pd.Series([0, 1, 0, 1])
    
    model = XGBoostModel(handle_imbalance=False)  # Disable sampling for small dataset
    model.fit(X, y)
    
    preds = model.predict(X)
    probas = model.predict_proba(X)
    
    assert len(preds) == len(y)
    assert probas.shape == (len(y), 2)
