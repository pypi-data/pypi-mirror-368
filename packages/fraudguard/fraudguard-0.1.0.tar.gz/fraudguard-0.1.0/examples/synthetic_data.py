from fraudguard.features import TransactionFeatures
from fraudguard.models import XGBoostModel
from fraudguard.pipeline import FraudDetectionPipeline

import pandas as pd
import numpy as np

# Create simple synthetic data
data = pd.DataFrame({
    "user_id": ["U1", "U2", "U3", "U4"],
    "amount": np.random.uniform(20, 5000, size=4),
    "merchant_category": ["retail", "entertainment", "crypto", "retail"],
    "country": ["US", "UK", "XX", "US"],
    "timestamp": pd.date_range("2024-08-05", periods=4, freq="H"),
    "payment_method": ["card", "paypal", "card", "apple_pay"],
    "card_type": ["credit", "debit", "credit", "debit"]
})
labels = pd.Series([0, 1, 0, 1])
features = TransactionFeatures()
model = XGBoostModel()

pipeline = FraudDetectionPipeline(features=features, model=model)  # type: ignore
pipeline.fit(data, labels)
probas = pipeline.predict_proba(data)
print(probas)
