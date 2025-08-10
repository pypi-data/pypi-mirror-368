import numpy as np
import pandas as pd
from typing import Any, Dict, Optional, List
from ..core.bias_detector import BiasDetector
from ..core.mitigation import BiasMitigator
from ..core.metrics import FairnessMetrics
import sys
print(sys.executable)
print(sys.path)
class MTrustWrapper:
    """
    Main wrapper to make any medical AI model fair and trustworthy.
    
    Usage:
        model = YourMedicalModel()
        fair_model = MTrustWrapper(model)
        result = fair_model.predict(image, demographics)
    """
    
    def __init__(self,
                 model: Any,
                 bias_threshold: float = 0.85,
                 mitigation_strength: str = 'balanced',
                 track_metrics: bool = True):
        """
        Initialize M-TRUST wrapper.
        
        Args:
            model: Any medical AI model with predict method
            bias_threshold: Fairness threshold (0-1)
            mitigation_strength: 'conservative', 'balanced', or 'aggressive'
            track_metrics: Whether to track fairness metrics
        """
        self.model = model
        self.bias_threshold = bias_threshold
        self.mitigation_strength = mitigation_strength
        self.track_metrics = track_metrics
        
        # Initialize components
        self.bias_detector = BiasDetector()
        self.mitigator = BiasMitigator(mitigation_strength=mitigation_strength)
        self.metrics = FairnessMetrics() if track_metrics else None
        
        # History tracking
        self.prediction_history = []
    
    def predict(self,
                input_data: Any,
                demographics: Optional[Dict] = None,
                return_bias_info: bool = False) -> Dict[str, Any]:
        """
        Make fair predictions with bias detection and mitigation.
        
        Args:
            input_data: Input for the model (image, text, etc.)
            demographics: Optional demographic information
            return_bias_info: Whether to return bias analysis
            
        Returns:
            Dictionary with predictions and optional bias information
        """
        # Get original prediction
        original_pred = self.model.predict(input_data)
        
        # Convert demographics to DataFrame if provided
        if demographics:
            demo_df = pd.DataFrame([demographics])
        else:
            demo_df = pd.DataFrame()
        
        # Detect bias
        bias_detected = False
        bias_info = {}
        
        if not demo_df.empty:
            # For simplicity, assume predictions are numeric
            if isinstance(original_pred, (list, np.ndarray)):
                pred_array = np.array(original_pred).reshape(-1)
            else:
                pred_array = np.array([original_pred])
            
            # Detect demographic bias
            bias_metrics = self.bias_detector.detect_demographic_bias(
                pred_array, demo_df
            )
            
            # Check if bias exceeds threshold
            for key, value in bias_metrics.items():
                if key.endswith('_biased') and value:
                    bias_detected = True
                    break
            
            bias_info = bias_metrics
        
        # Apply mitigation if bias detected
        if bias_detected:
            if isinstance(original_pred, (list, np.ndarray)):
                mitigated = self.mitigator.mitigate_demographic_bias(
                    np.array(original_pred).reshape(-1),
                    demo_df,
                    bias_info
                )
                final_pred = mitigated.tolist()
            else:
                final_pred = original_pred * 1.05  # Simple boost
        else:
            final_pred = original_pred
        
        # Prepare result
        result = {
            'prediction': final_pred,
            'original_prediction': original_pred,
            'bias_detected': bias_detected,
            'mitigation_applied': bias_detected
        }
        
        if return_bias_info:
            result['bias_info'] = bias_info
        
        # Track metrics if enabled
        if self.track_metrics and demographics:
            self.metrics.update(final_pred, demographics)
            result['fairness_score'] = self.metrics.get_fairness_score()
        
        # Store in history
        self.prediction_history.append(result)
        
        return result
    
    def predict_batch(self,
                     inputs: List[Any],
                     demographics: Optional[pd.DataFrame] = None) -> List[Dict]:
        """
        Make batch predictions with bias mitigation.
        
        Args:
            inputs: List of inputs
            demographics: DataFrame with demographic info
            
        Returns:
            List of prediction results
        """
        results = []
        
        for i, input_data in enumerate(inputs):
            demo = demographics.iloc[i].to_dict() if demographics is not None and i < len(demographics) else None
            result = self.predict(input_data, demo)
            results.append(result)
        
        return results
    
    def get_bias_report(self) -> Dict[str, Any]:
        """
        Get comprehensive bias report from history.
        
        Returns:
            Bias analysis report
        """
        if not self.prediction_history:
            return {"message": "No predictions made yet"}
        
        total_predictions = len(self.prediction_history)
        biased_predictions = sum(1 for p in self.prediction_history if p['bias_detected'])
        
        report = {
            'total_predictions': total_predictions,
            'biased_predictions': biased_predictions,
            'bias_rate': biased_predictions / total_predictions if total_predictions > 0 else 0,
            'mitigation_strength': self.mitigation_strength,
            'bias_threshold': self.bias_threshold
        }
        
        if self.metrics:
            report['fairness_metrics'] = self.metrics.get_summary()
        
        return report
    
    def __call__(self, *args, **kwargs):
        """Allow wrapper to be called like the original model."""
        return self.predict(*args, **kwargs)