"""
Base wrapper class for M-TRUST.
Provides a standard interface for integrating bias detection, mitigation, and metrics.
"""

from abc import ABC, abstractmethod
from mtrust.core.bias_detector import BiasDetector
from mtrust.core.mitigation import BiasMitigator
from mtrust.core.metrics import FairnessMetrics

class BaseWrapper(ABC):
    """
    Abstract base wrapper for models in M-TRUST.
    Handles bias detection, mitigation, and fairness evaluation.
    """

    def __init__(self, model, bias_threshold=0.8):
        """
        Args:
            model: Any model object with a .predict() method.
            bias_threshold (float): Threshold above which bias mitigation is triggered.
        """
        self.model = model
        self.bias_threshold = bias_threshold
        self.detector = BiasDetector()
        self.mitigator = BiasMitigator()
        self.metrics = FairnessMetrics()

    @abstractmethod
    def preprocess(self, inputs):
        """
        Preprocess raw inputs for the model.
        Must be implemented by subclass.
        """
        pass

    @abstractmethod
    def postprocess(self, outputs):
        """
        Postprocess model outputs.
        Must be implemented by subclass.
        """
        pass

    def predict(self, inputs, metadata=None):
        """
        Run prediction, detect and mitigate bias if needed.

        Args:
            inputs: Model inputs.
            metadata (dict): Auxiliary information (e.g., demographics, quality scores).

        Returns:
            dict: {
                "predictions": processed outputs,
                "bias_report": bias analysis results
            }
        """
        processed_inputs = self.preprocess(inputs)
        raw_outputs = self.model.predict(processed_inputs)
        processed_outputs = self.postprocess(raw_outputs)

        bias_report = self._run_bias_pipeline(processed_outputs, metadata)

        return {
            "predictions": processed_outputs,
            "bias_report": bias_report
        }

    def _run_bias_pipeline(self, predictions, metadata):
        """
        Run bias detection and mitigation.

        Args:
            predictions: Model predictions.
            metadata (dict): Additional metadata for bias detection.

        Returns:
            dict: Bias report.
        """
        if metadata is None:
            return {"message": "No metadata provided for bias detection."}

        # Example: demographic bias detection
        bias_results = self.detector.detect_demographic_bias(
            predictions, metadata.get("demographics", {})
        )

        if bias_results.get("bias_score", 0) > self.bias_threshold:
            predictions = self.mitigator.mitigate(predictions, strategy="reweighting")
            bias_results["mitigation_applied"] = True
        else:
            bias_results["mitigation_applied"] = False

        # Add fairness metrics
        metrics = self.metrics.calculate_all(predictions, metadata)
        bias_results["fairness_metrics"] = metrics

        return bias_results
