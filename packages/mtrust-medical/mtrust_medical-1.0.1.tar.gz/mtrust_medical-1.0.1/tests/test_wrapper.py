import numpy as np
from mtrust.wrappers.medical import MTrustWrapper

class DummyModel:
    def predict(self, x):
        return np.ones(len(x))  # Always predict 1

def test_wrapper_runs():
    model = DummyModel()
    wrapper = MTrustWrapper(model, bias_threshold=0.8)

    images = np.random.rand(5, 224, 224)
    demographics = {"gender": ["M", "F", "M", "F", "F"]}
    results = wrapper.predict(images, demographics)

    assert isinstance(results, dict)
    assert "predictions" in results
    assert "bias_report" in results
