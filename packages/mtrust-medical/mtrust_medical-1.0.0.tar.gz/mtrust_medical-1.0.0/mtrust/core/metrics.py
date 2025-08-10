import numpy as np
from typing import Dict, List, Any

class FairnessMetrics:
    """Calculate fairness metrics for medical AI."""
    
    def __init__(self):
        self.predictions_by_group = {}
        self.total_predictions = 0
    
    def update(self, prediction: Any, demographics: Dict):
        """Update metrics with new prediction."""
        group_key = f"{demographics.get('race', 'unknown')}_{demographics.get('gender', 'unknown')}"
        
        if group_key not in self.predictions_by_group:
            self.predictions_by_group[group_key] = []
        
        self.predictions_by_group[group_key].append(prediction)
        self.total_predictions += 1
    
    def get_fairness_score(self) -> float:
        """Calculate overall fairness score (0-1)."""
        if len(self.predictions_by_group) < 2:
            return 1.0  # Perfect fairness if only one group
        
        # Calculate mean performance per group
        group_means = []
        for group, preds in self.predictions_by_group.items():
            if preds:
                group_means.append(np.mean(preds))
        
        if not group_means:
            return 1.0
        
        # Calculate fairness as inverse of coefficient of variation
        cv = np.std(group_means) / (np.mean(group_means) + 1e-8)
        fairness = max(0, 1 - cv)
        
        return fairness
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of fairness metrics."""
        return {
            'total_predictions': self.total_predictions,
            'groups_analyzed': len(self.predictions_by_group),
            'fairness_score': self.get_fairness_score()
        }