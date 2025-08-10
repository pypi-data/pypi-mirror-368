"""
Scoring engine for fraud risk assessment and categorization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Engine for scoring and categorizing fraud risk.
    
    Provides risk categorization, threshold management, and
    decision support for fraud detection systems.
    """
    
    def __init__(self,
                 risk_thresholds: Optional[Dict[str, float]] = None):
        self.risk_thresholds = risk_thresholds or {
            'low': 0.3,
            'medium': 0.7,
            'high': 0.9
        }
        
    def categorize_risk(self, scores: Union[np.ndarray, List[float]]) -> List[str]:
        """Categorize fraud scores into risk levels."""
        if isinstance(scores, list):
            scores = np.array(scores)
            
        categories = []
        
        for score in scores:
            if score < self.risk_thresholds['low']:
                categories.append('low')
            elif score < self.risk_thresholds['medium']:
                categories.append('medium')
            elif score < self.risk_thresholds['high']:
                categories.append('high')
            else:
                categories.append('critical')
                
        return categories
    
    def get_recommendations(self, scores: Union[np.ndarray, List[float]]) -> List[str]:
        """Get recommended actions based on fraud scores."""
        categories = self.categorize_risk(scores)
        
        recommendations = []
        for category in categories:
            if category == 'low':
                recommendations.append('approve')
            elif category == 'medium':
                recommendations.append('review')
            elif category == 'high':
                recommendations.append('manual_review')
            else:  # critical
                recommendations.append('block')
                
        return recommendations
    
    def set_thresholds(self, thresholds: Dict[str, float]):
        """Update risk thresholds."""
        self.risk_thresholds.update(thresholds)
        logger.info(f"Updated risk thresholds: {self.risk_thresholds}")
