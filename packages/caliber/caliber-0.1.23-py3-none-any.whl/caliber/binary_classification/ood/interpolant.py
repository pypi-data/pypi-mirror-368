import numpy as np
from caliber.binary_classification.base import AbstractBinaryClassificationModel


class OodInterpolantBinaryClassificationModel(AbstractBinaryClassificationModel):
    def predict_proba(self, id_probs: np.ndarray, ood_probs: np.ndarray) -> np.ndarray:
        return id_probs * (1 - ood_probs) + 0.5 * ood_probs
