import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any

class BiasDetector:
    """
    Detects multiple types of bias in medical AI predictions.
    
    Bias Types:
    1. Demographic bias - performance gaps across groups
    2. Quality bias - output quality variations
    3. Annotation bias - label inconsistencies
    4. Amplification bias - bias increase across modalities
    """
    
    def __init__(self, 
                 demographic_threshold: float = 0.05,
                 quality_threshold: float = 0.10,
                 amplification_threshold: float = 1.5):
        """
        Initialize bias detector with thresholds.
        
        Args:
            demographic_threshold: Max acceptable demographic gap
            quality_threshold: Max acceptable quality variation
            amplification_threshold: Max acceptable amplification factor
        """
        self.demographic_threshold = demographic_threshold
        self.quality_threshold = quality_threshold
        self.amplification_threshold = amplification_threshold
        self.bias_history = []
    
    def detect_demographic_bias(self, 
                                predictions: np.ndarray,
                                demographics: pd.DataFrame) -> Dict[str, float]:
        """
        Detect bias across demographic groups.
        
        Args:
            predictions: Model predictions
            demographics: DataFrame with demographic info
            
        Returns:
            Dictionary with bias metrics per group
        """
        bias_metrics = {}
        
        # Group by each demographic factor
        for column in ['race', 'gender', 'age_group']:
            if column in demographics.columns:
                grouped = demographics.groupby(column)
                
                # Calculate performance per group
                group_performance = {}
                for group_name, group_indices in grouped.groups.items():
                    group_preds = predictions[group_indices]
                    group_performance[group_name] = np.mean(group_preds)
                
                # Calculate bias as max difference
                if group_performance:
                    max_perf = max(group_performance.values())
                    min_perf = min(group_performance.values())
                    bias = (max_perf - min_perf) / (max_perf + 1e-8)
                    bias_metrics[f'{column}_bias'] = bias
                    
                    # Check if exceeds threshold
                    if bias > self.demographic_threshold:
                        bias_metrics[f'{column}_biased'] = True
                    else:
                        bias_metrics[f'{column}_biased'] = False
        
        return bias_metrics
    
    def detect_quality_bias(self, 
                           outputs: List[str],
                           demographics: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Detect quality variations in text outputs.
        
        Args:
            outputs: Text outputs (e.g., reports)
            demographics: Optional demographic data
            
        Returns:
            Quality bias metrics
        """
        quality_metrics = {}
        
        # Measure output lengths
        lengths = [len(output) for output in outputs]
        
        # Overall quality metrics
        quality_metrics['mean_length'] = np.mean(lengths)
        quality_metrics['std_length'] = np.std(lengths)
        quality_metrics['cv_length'] = np.std(lengths) / (np.mean(lengths) + 1e-8)
        
        # Check for quality bias
        if quality_metrics['cv_length'] > self.quality_threshold:
            quality_metrics['quality_biased'] = True
        else:
            quality_metrics['quality_biased'] = False
        
        # If demographics provided, check quality by group
        if demographics is not None and 'race' in demographics.columns:
            for group in demographics['race'].unique():
                group_mask = demographics['race'] == group
                group_lengths = [lengths[i] for i in range(len(lengths)) if group_mask.iloc[i]]
                if group_lengths:
                    quality_metrics[f'mean_length_{group}'] = np.mean(group_lengths)
        
        return quality_metrics
    
    def detect_amplification_bias(self,
                                  image_bias: float,
                                  text_bias: float) -> Dict[str, float]:
        """
        Detect bias amplification across modalities.
        
        Args:
            image_bias: Bias in image modality
            text_bias: Bias in text modality
            
        Returns:
            Amplification metrics
        """
        amplification = text_bias / (image_bias + 1e-8)
        
        return {
            'image_bias': image_bias,
            'text_bias': text_bias,
            'amplification_factor': amplification,
            'amplification_biased': amplification > self.amplification_threshold
        }
    
    def detect_all_biases(self,
                         predictions: np.ndarray,
                         outputs: List[str],
                         demographics: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect all types of bias.
        
        Returns:
            Comprehensive bias report
        """
        all_biases = {}
        
        # Demographic bias
        demo_bias = self.detect_demographic_bias(predictions, demographics)
        all_biases.update(demo_bias)
        
        # Quality bias
        quality_bias = self.detect_quality_bias(outputs, demographics)
        all_biases.update(quality_bias)
        
        # Overall bias score
        bias_count = sum(1 for k, v in all_biases.items() if k.endswith('_biased') and v)
        all_biases['total_biases_detected'] = bias_count
        all_biases['bias_severity'] = 'high' if bias_count > 2 else 'medium' if bias_count > 0 else 'low'
        
        # Store in history
        self.bias_history.append(all_biases)
        
        return all_biases