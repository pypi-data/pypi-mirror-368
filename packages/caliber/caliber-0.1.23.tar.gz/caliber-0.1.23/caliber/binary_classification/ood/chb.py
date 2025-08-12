import numpy as np
from scipy.stats import expon

from caliber.binary_classification.base import AbstractBinaryClassificationModel


class CautiousHistogramBinningBinaryClassificationModel(
    AbstractBinaryClassificationModel
):
    def __init__(
        self,
        n_prob_bins: int = 10,
        n_discrim_bins: int = 10,
        min_prob_bin: float = 0.0,
    ):
        super().__init__()
        self._n_prob_bins = n_prob_bins
        self._n_discrim_bins = n_discrim_bins
        self._min_prob_bin = min_prob_bin
        self._prob_bin_edges = None
        self._discrim_bin_edges = None

    def fit(self, probs: np.ndarray, targets: np.ndarray, discrim_probs: np.ndarray, discrim_targets: np.ndarray) -> None:
        self._prob_bin_edges = self._get_prob_bin_edges()
        self._discrim_bin_edges = self._get_discrim_prob_bin_edges()

        prob_bin_indices = np.digitize(probs, self._prob_bin_edges)
        discrim_bin_indices = np.digitize(discrim_probs, self._discrim_bin_edges)
        cautious_probs = self._get_cautious_proba(probs, discrim_probs)

        self._params = np.empty((self.n_prob_bins + 1, self.n_discrim_bins + 1))

        for i in range(1, self._n_prob_bins + 2):
            for j in range(1, self._n_discrim_bins + 2):
                mask = self._get_mask(i, j, prob_bin_indices, discrim_bin_indices)
                self._fit_bin(i, j, mask, cautious_probs, targets, discrim_targets)

    def predict_proba(self, probs: np.ndarray, discrim_probs: np.ndarray) -> np.ndarray:
        if self._prob_bin_edges is None:
            raise ValueError("Run `fit` first.")

        prob_bin_indices = np.digitize(probs, self._prob_bin_edges)
        discrim_bin_indices = np.digitize(discrim_probs, self._discrim_bin_edges)
        cautious_probs = self._get_cautious_proba(probs, discrim_probs)

        for i in range(1, self._n_prob_bins + 2):
            for j in range(1, self._n_discrim_bins + 2):
                mask = self._get_mask(i, j, prob_bin_indices, discrim_bin_indices)
                if not np.isnan(self._params[i - 1, j - 1]):
                    cautious_probs[mask] = cautious_probs[mask] + self._params[i - 1, j - 1]

        return cautious_probs
    
    def _get_cautious_proba(self, probs: np.ndarray, discrim_probs: np.ndarray) -> np.ndarray:
        return probs * (1 - discrim_probs) + 0.5 * discrim_probs
    
    @staticmethod
    def _get_cautious_target_mean(targets: np.ndarray, discrim_targets: np.ndarray) -> float:
        discrim_target_mean = np.mean(discrim_targets)
        return np.mean(targets) * (1 - discrim_target_mean) + 0.5 * discrim_target_mean

    def predict(self, probs: np.ndarray, discrim_probs: np.ndarray) -> np.ndarray:
        return (self.predict_proba(probs, discrim_probs) >= 0.5).astype(int)

    def _get_prob_bin_edges(self) -> np.ndarray:
        return np.linspace(0, 1, self._n_prob_bins + 1)

    def _get_discrim_prob_bin_edges(self) -> np.ndarray:
        return np.linspace(0, self._max_distance, self._n_dist_bins + 1)

    def _fit_bin(self, i: int, j: int, mask: np.ndarray, cautious_probs: np.ndarray, targets: np.ndarray, discrim_targets: np.ndarray) -> None:
        prob_bin = np.mean(mask)
        if prob_bin > self._min_prob_bin:
            self._params[i - 1, j - 1] = self._get_cautious_target_mean(targets[mask], discrim_targets[mask]) - cautious_probs[mask]
        else:
            self._params[i - 1, j - 1] = np.nan

    @staticmethod
    def _get_mask(
        prob_bin_idx: int,
        discrim_bin_idx: int,
        prob_bin_indices: np.ndarray,
        discrim_bin_indices: np.ndarray,
    ) -> np.ndarray:
        return (prob_bin_indices == prob_bin_idx) & (discrim_bin_indices == discrim_bin_idx)
