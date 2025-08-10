from fraudguard.features import TransactionFeatures, VelocityFeatures
from fraudguard.models import RandomForestModel
from fraudguard.pipeline import FraudDetectionPipeline

import pandas as pd
data = pd.read_csv("digital_payments.csv")
labels = data.pop("fraud_label")

features = TransactionFeatures() + VelocityFeatures()
model = RandomForestModel()

pipeline = FraudDetectionPipeline(features=features, model=model)
pipeline.fit(data, labels)

preds = pipeline.predict(data)
print(preds)
