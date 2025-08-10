import numpy as np
import pytest
from mtrust.core.bias_detector import BiasDetector

def test_detects_demographic_bias():
    detector = BiasDetector()
    preds = np.array([1, 0, 1, 1, 0])
    demographics = {"gender": ["M", "F", "M", "F", "F"]}

    results = detector.detect_demographic_bias(preds, demographics)
    assert isinstance(results, dict)
    assert "bias_score" in results
    assert 0 <= results["bias_score"] <= 1

def test_detects_quality_bias():
    detector = BiasDetector()
    preds = np.array([0.1, 0.9, 0.4])
    quality_scores = [0.8, 0.2, 0.9]

    results = detector.detect_quality_bias(preds, quality_scores)
    assert "bias_score" in results
    assert 0 <= results["bias_score"] <= 1
