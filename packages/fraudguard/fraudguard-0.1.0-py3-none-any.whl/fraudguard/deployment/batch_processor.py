"""
Batch processing for bulk transaction fraud scoring.
"""

import pandas as pd
from typing import Union, Optional
from pathlib import Path
import logging

from ..pipeline.fraud_detection_pipeline import FraudDetectionPipeline

logger = logging.getLogger(__name__)

class BatchFraudProcessor:
    """
    Batch scoring engine for fraud detection pipelines.
    """
    def __init__(self, pipeline: FraudDetectionPipeline):
        if not pipeline.is_fitted:
            raise ValueError("Pipeline must be fitted before batch processing.")
        self.pipeline = pipeline
        
    def score_file(self, input_file: Union[str, Path], output_file: Optional[Union[str, Path]] = None):
        df = pd.read_csv(input_file)
        scores = self.pipeline.score_transactions(df)
        df['fraud_score'] = scores
        if output_file:
            df.to_csv(output_file, index=False)
        return df

    def score_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        scores = self.pipeline.score_transactions(df)
        df['fraud_score'] = scores
        return df
