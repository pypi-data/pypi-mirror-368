"""
FastAPI server for real-time fraud scoring and pipeline deployment.
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
import logging

from ..pipeline.fraud_detection_pipeline import FraudDetectionPipeline
from ..core.config import config

logger = logging.getLogger(__name__)

app = FastAPI(title='FraudGuard API', description='Real-time financial fraud detection')

# Assume globally loaded pipeline object
global_pipeline = None

class TransactionRequest(BaseModel):
    data: dict

@app.post("/predict/")
async def predict(request: TransactionRequest):
    if global_pipeline is None or not global_pipeline.is_fitted:
        return {"error": "Pipeline is not loaded or not fitted."}
    try:
        df = pd.DataFrame([request.data])
        scores = global_pipeline.predict_proba(df)
        pred = global_pipeline.predict(df)
        return {"fraud_score": float(scores[0][1]), "is_fraud": int(pred[0])}
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return {"error": str(e)}

@app.post("/evaluate/")
async def evaluate(request: TransactionRequest):
    if global_pipeline is None or not global_pipeline.is_fitted:
        return {"error": "Pipeline is not loaded or not fitted."}
    try:
        df = pd.DataFrame([request.data])
        # Dummy label; replace with actual in production
        metrics = global_pipeline.evaluate(df, pd.Series([1]))
        return {"metrics": metrics}
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return {"error": str(e)}
