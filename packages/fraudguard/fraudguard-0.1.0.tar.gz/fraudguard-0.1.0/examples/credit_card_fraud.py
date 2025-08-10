from fraudguard.features import TransactionFeatures, BehavioralFeatures
from fraudguard.models import XGBoostModel
from fraudguard.pipeline import FraudDetectionPipeline

# Load example data
import pandas as pd
data = pd.read_csv("credit_card_transactions.csv")
labels = data.pop("is_fraud")

features = TransactionFeatures() + BehavioralFeatures()
model = XGBoostModel()

pipeline = FraudDetectionPipeline(features=features, model=model)
pipeline.fit(data, labels)

scores = pipeline.score_transactions(data)
print(scores)
