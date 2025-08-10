"""
M-TRUST: Multimodal Trustworthy Healthcare AI
A bias detection and mitigation framework for medical AI systems.
"""

from .core.bias_detector import BiasDetector
from .core.mitigation import BiasMitigator
from .core.metrics import FairnessMetrics
from .wrappers.medical import MTrustWrapper
from .__version__ import __version__

__all__ = [
    "BiasDetector",
    "BiasMitigator", 
    "FairnessMetrics",
    "MTrustWrapper",
    "__version__"
]

# Convenience function
def wrap_model(model, **kwargs):
    """Quick wrapper function to make any model fair"""
    return MTrustWrapper(model, **kwargs)