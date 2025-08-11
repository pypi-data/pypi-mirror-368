import numpy as np
from scipy import signal as sig

from ..base import Logging

log = Logging.get_logger()


class AutoLineLocator:

    def __init__(self, image: np.array, line_distance: int = 100, sigma: float = 0.6, line_prominence=0):
        self.img = image
        self.sigma = sigma
        self.line_distance = line_distance
        self.line_prominence = line_prominence

    def detect_centers(self) -> np.array:
        self._normalize()
        return self._detect_peaks()

    def _normalize(self):
        self.img = self.img / self.img.std()
        self.img = self.img - self.img.min()

    def _detect_peaks(self) -> np.array:
        row_means = self.img.mean(axis=0)
        h = np.mean(row_means) + self.sigma * np.std(row_means)
        peaks, _ = sig.find_peaks(row_means, height=h, distance=self.line_distance, prominence=self.line_prominence)
        log.info('Detected %s lines at:\n%s', len(peaks), peaks)
        return peaks
