"""
Metrics and evaluation utilities for fraud detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging

from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_recall_curve,
    confusion_matrix, classification_report, roc_curve, auc,
    precision_score, recall_score, f1_score, accuracy_score
)

logger = logging.getLogger(__name__)


class FraudMetrics:
    """
    Comprehensive fraud detection metrics calculator.
    
    Provides financial fraud-specific metrics like precision at K%,
    false alert rates, and cost-benefit analysis.
    """
    
    def __init__(self):
        self.metrics_cache = {}
    
    def calculate_all_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                             y_scores: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive fraud detection metrics.
        
        Args:
            y_true: True labels (0=legitimate, 1=fraud)
            y_pred: Predicted labels
            y_scores: Prediction probabilities/scores
            
        Returns:
            Dictionary containing all calculated metrics
        """
        metrics = {}
        
        # Basic classification metrics
        metrics.update(self._calculate_basic_metrics(y_true, y_pred))
        
        # Fraud-specific metrics
        if y_scores is not None:
            metrics.update(self._calculate_fraud_metrics(y_true, y_scores))
            metrics.update(self._calculate_precision_at_k(y_true, y_scores))
            metrics.update(self._calculate_financial_metrics(y_true, y_scores))
        
        # Confusion matrix details
        metrics.update(self._calculate_confusion_metrics(y_true, y_pred))
        
        return metrics
    
    def _calculate_basic_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate basic classification metrics."""
        try:
            return {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, zero_division=0),
                'recall': recall_score(y_true, y_pred, zero_division=0),
                'f1_score': f1_score(y_true, y_pred, zero_division=0)
            }
        except Exception as e:
            logger.warning(f"Error calculating basic metrics: {e}")
            return {}
    
    def _calculate_fraud_metrics(self, y_true: np.ndarray, y_scores: np.ndarray) -> Dict[str, float]:
        """Calculate fraud-specific metrics."""
        metrics = {}
        
        try:
            # AUC metrics
            metrics['auc'] = roc_auc_score(y_true, y_scores)
            metrics['average_precision'] = average_precision_score(y_true, y_scores)
            
            # ROC curve details
            fpr, tpr, _ = roc_curve(y_true, y_scores)
            metrics['auc_roc'] = auc(fpr, tpr)
            
            # Find optimal threshold (Youden's J statistic)
            optimal_idx = np.argmax(tpr - fpr)
            metrics['optimal_threshold'] = _[optimal_idx] if len(_) > optimal_idx else 0.5
            
        except Exception as e:
            logger.warning(f"Error calculating fraud metrics: {e}")
        
        return metrics
    
    def _calculate_precision_at_k(self, y_true: np.ndarray, y_scores: np.ndarray, 
                                 k_values: List[float] = None) -> Dict[str, float]:
        """Calculate precision at top K% of scores."""
        if k_values is None:
            k_values = [1, 2, 5, 10, 20]
        
        metrics = {}
        
        try:
            # Sort by score descending
            sorted_indices = np.argsort(-y_scores)
            y_true_sorted = y_true[sorted_indices]
            
            for k in k_values:
                # Calculate how many samples to consider for top k%
                n_samples = int(len(y_true) * k / 100)
                if n_samples == 0:
                    continue
                
                # Calculate precision at top k%
                top_k_true = y_true_sorted[:n_samples]
                precision_at_k = np.sum(top_k_true) / len(top_k_true) if len(top_k_true) > 0 else 0
                metrics[f'precision_at_{k}_percent'] = precision_at_k
                
                # Calculate detection rate at top k% (recall)
                total_frauds = np.sum(y_true)
                if total_frauds > 0:
                    detection_rate = np.sum(top_k_true) / total_frauds
                    metrics[f'detection_rate_at_{k}_percent'] = detection_rate
        
        except Exception as e:
            logger.warning(f"Error calculating precision at K: {e}")
        
        return metrics
    
    def _calculate_financial_metrics(self, y_true: np.ndarray, y_scores: np.ndarray,
                                   avg_fraud_amount: float = 1000,
                                   investigation_cost: float = 50,
                                   false_positive_cost: float = 10) -> Dict[str, float]:
        """Calculate financial impact metrics."""
        metrics = {}
        
        try:
            # Use a threshold that balances precision and recall
            threshold = 0.5
            y_pred = (y_scores >= threshold).astype(int)
            
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            
            # Financial calculations
            fraud_prevented = tp * avg_fraud_amount
            investigation_costs = (tp + fp) * investigation_cost
            false_positive_costs = fp * false_positive_cost
            fraud_losses = fn * avg_fraud_amount
            
            total_savings = fraud_prevented - investigation_costs - false_positive_costs
            total_possible_fraud = np.sum(y_true) * avg_fraud_amount
            
            metrics['estimated_fraud_prevented'] = fraud_prevented
            metrics['investigation_costs'] = investigation_costs
            metrics['false_positive_costs'] = false_positive_costs
            metrics['fraud_losses'] = fraud_losses
            metrics['net_savings'] = total_savings
            metrics['savings_rate'] = total_savings / total_possible_fraud if total_possible_fraud > 0 else 0
            
        except Exception as e:
            logger.warning(f"Error calculating financial metrics: {e}")
        
        return metrics
    
    def _calculate_confusion_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """Calculate confusion matrix and derived metrics."""
        metrics = {}
        
        try:
            cm = confusion_matrix(y_true, y_pred)
            
            if cm.shape == (2, 2):
                tn, fp, fn, tp = cm.ravel()
                
                metrics['true_negatives'] = int(tn)
                metrics['false_positives'] = int(fp)
                metrics['false_negatives'] = int(fn)
                metrics['true_positives'] = int(tp)
                
                # Rates
                metrics['false_positive_rate'] = fp / (fp + tn) if (fp + tn) > 0 else 0
                metrics['false_negative_rate'] = fn / (fn + tp) if (fn + tp) > 0 else 0
                metrics['true_positive_rate'] = tp / (tp + fn) if (tp + fn) > 0 else 0
                metrics['true_negative_rate'] = tn / (tn + fp) if (tn + fp) > 0 else 0
                
                # False alert rate (important for fraud detection)
                total_alerts = tp + fp
                metrics['false_alert_rate'] = fp / total_alerts if total_alerts > 0 else 0
                metrics['total_alerts'] = int(total_alerts)
                
            # Store confusion matrix for later use
            metrics['confusion_matrix'] = cm.tolist()
            
        except Exception as e:
            logger.warning(f"Error calculating confusion metrics: {e}")
        
        return metrics
    
    def generate_classification_report(self, y_true: np.ndarray, y_pred: np.ndarray) -> str:
        """Generate detailed classification report."""
        try:
            return classification_report(
                y_true, y_pred,
                target_names=['Legitimate', 'Fraud'],
                zero_division=0
            )
        except Exception as e:
            logger.warning(f"Error generating classification report: {e}")
            return "Error generating report"
    
    def calculate_threshold_metrics(self, y_true: np.ndarray, y_scores: np.ndarray, 
                                   thresholds: Optional[List[float]] = None) -> pd.DataFrame:
        """Calculate metrics across different thresholds."""
        if thresholds is None:
            # Use precision-recall curve thresholds
            _, _, thresholds = precision_recall_curve(y_true, y_scores)
            # Limit to reasonable number of thresholds
            if len(thresholds) > 100:
                indices = np.linspace(0, len(thresholds)-1, 100, dtype=int)
                thresholds = thresholds[indices]
        
        results = []
        
        for threshold in thresholds:
            y_pred = (y_scores >= threshold).astype(int)
            
            try:
                metrics = {
                    'threshold': threshold,
                    'precision': precision_score(y_true, y_pred, zero_division=0),
                    'recall': recall_score(y_true, y_pred, zero_division=0),
                    'f1_score': f1_score(y_true, y_pred, zero_division=0),
                }
                
                # Add confusion matrix metrics
                if len(np.unique(y_pred)) > 1:  # Avoid errors when all predictions are same
                    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
                    metrics.update({
                        'true_positives': tp,
                        'false_positives': fp,
                        'false_negatives': fn,
                        'true_negatives': tn,
                        'false_alert_rate': fp / (tp + fp) if (tp + fp) > 0 else 0
                    })
                
                results.append(metrics)
                
            except Exception as e:
                logger.warning(f"Error calculating metrics for threshold {threshold}: {e}")
                continue
        
        return pd.DataFrame(results)
    
    def plot_metrics(self, y_true: np.ndarray, y_scores: np.ndarray, 
                    figsize: Tuple[int, int] = (15, 10)):
        """Plot comprehensive fraud detection metrics."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.gridspec import GridSpec
        except ImportError:
            raise ImportError("matplotlib required for plotting")
        
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(2, 3, figure=fig)
        
        # ROC Curve
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_roc_curve(y_true, y_scores, ax1)
        
        # Precision-Recall Curve
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_precision_recall_curve(y_true, y_scores, ax2)
        
        # Precision at K
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_precision_at_k(y_true, y_scores, ax3)
        
        # Score Distribution
        ax4 = fig.add_subplot(gs[1, 0])
        self._plot_score_distribution(y_true, y_scores, ax4)
        
        # Threshold Analysis
        ax5 = fig.add_subplot(gs[1, 1:])
        self._plot_threshold_analysis(y_true, y_scores, ax5)
        
        plt.tight_layout()
        plt.show()
    
    def _plot_roc_curve(self, y_true, y_scores, ax):
        """Plot ROC curve."""
        fpr, tpr, _ = roc_curve(y_true, y_scores)
        roc_auc = auc(fpr, tpr)
        
        ax.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.3f})')
        ax.plot([0, 1], [0, 1], 'k--', label='Random')
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('ROC Curve')
        ax.legend()
        ax.grid(True)
    
    def _plot_precision_recall_curve(self, y_true, y_scores, ax):
        """Plot Precision-Recall curve."""
        precision, recall, _ = precision_recall_curve(y_true, y_scores)
        pr_auc = auc(recall, precision)
        
        ax.plot(recall, precision, label=f'PR Curve (AUC = {pr_auc:.3f})')
        ax.set_xlabel('Recall')
        ax.set_ylabel('Precision')
        ax.set_title('Precision-Recall Curve')
        ax.legend()
        ax.grid(True)
    
    def _plot_precision_at_k(self, y_true, y_scores, ax):
        """Plot precision at different K values."""
        k_values = range(1, 21)  # 1% to 20%
        precisions = []
        
        sorted_indices = np.argsort(-y_scores)
        y_true_sorted = y_true[sorted_indices]
        
        for k in k_values:
            n_samples = int(len(y_true) * k / 100)
            if n_samples > 0:
                precision = np.sum(y_true_sorted[:n_samples]) / n_samples
                precisions.append(precision)
            else:
                precisions.append(0)
        
        ax.plot(k_values, precisions, 'o-')
        ax.set_xlabel('Top K%')
        ax.set_ylabel('Precision')
        ax.set_title('Precision at Top K%')
        ax.grid(True)
    
    def _plot_score_distribution(self, y_true, y_scores, ax):
        """Plot score distributions for legitimate and fraud."""
        legitimate_scores = y_scores[y_true == 0]
        fraud_scores = y_scores[y_true == 1]
        
        ax.hist(legitimate_scores, bins=50, alpha=0.7, label='Legitimate', density=True)
        ax.hist(fraud_scores, bins=50, alpha=0.7, label='Fraud', density=True)
        ax.set_xlabel('Fraud Score')
        ax.set_ylabel('Density')
        ax.set_title('Score Distribution')
        ax.legend()
        ax.grid(True)
    
    def _plot_threshold_analysis(self, y_true, y_scores, ax):
        """Plot precision, recall, and F1 vs threshold."""
        df = self.calculate_threshold_metrics(y_true, y_scores)
        
        ax.plot(df['threshold'], df['precision'], label='Precision', linewidth=2)
        ax.plot(df['threshold'], df['recall'], label='Recall', linewidth=2)
        ax.plot(df['threshold'], df['f1_score'], label='F1 Score', linewidth=2)
        
        ax.set_xlabel('Threshold')
        ax.set_ylabel('Score')
        ax.set_title('Metrics vs Threshold')
        ax.legend()
        ax.grid(True)
