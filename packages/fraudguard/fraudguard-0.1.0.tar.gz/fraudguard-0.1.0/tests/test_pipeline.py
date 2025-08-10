"""
End-to-end pipeline tests.
"""

import pandas as pd
import numpy as np
from fraudguard.features import TransactionFeatures, BehavioralFeatures
from fraudguard.models.xgboost_model import XGBoostModel
from fraudguard.pipeline.fraud_detection_pipeline import FraudDetectionPipeline

def test_pipeline_fit_predict(dummy_transaction_data, dummy_labels):
    """Test complete pipeline with proper data types."""
    features = TransactionFeatures() + BehavioralFeatures()
    model = XGBoostModel()
    pipeline = FraudDetectionPipeline(features=features, model=model)
    
    # Use pandas Series for labels (not Python list)
    pipeline.fit(dummy_transaction_data, dummy_labels)
    preds = pipeline.predict(dummy_transaction_data)
    assert len(preds) == len(dummy_labels)

def test_pipeline_feature_processing(dummy_transaction_data):
    """Test that features are properly processed."""
    features = TransactionFeatures()
    processed_features = features.fit_transform(dummy_transaction_data)
    
    # Should have numeric columns that XGBoost can handle
    numeric_cols = processed_features.select_dtypes(include=[np.number]).columns
    assert len(numeric_cols) > 0, "Should have numeric features for ML models"
