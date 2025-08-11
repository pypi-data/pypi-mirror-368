from __future__ import annotations

import warnings

import numpy as np
from scipy import signal as sig
from scipy.ndimage import gaussian_filter
from skimage.filters import gaussian

from ..utils import Collections


class LineRemover:
    """
    class removes the vertical features (i.e. absorption/emission lines) from the flat field image.
    The input datacube must be de-smiled.
    """

    def __init__(self, cube: np.array):
        #: The original datacube
        self.cube = cube
        #: The resulting Flat Field
        self.result = []

    def run(self) -> LineRemover:
        """
        Iterates over all mod states in the image cube and removes the vertical features
        while maintaining the vertical gradient.
        """
        self.result = np.array([self.__remove_lines(s) for s in range(self.cube.shape[0])])
        return self

    def __remove_lines(self, state) -> np.array:
        img = self.cube[state]
        mean_spec = np.repeat(np.mean(img, axis=0, keepdims=True), img.shape[0], axis=0)
        return img / mean_spec


class ResidualsRemover:
    """
    Helper to remove vertical 1px wide line residuals by interpolating over the
    left and right border of the peak.

    The Residual is detected by finding peaks in the horizontal average of the
    central region of the image.
    """

    def __init__(self, img: np.array, peak_threshold: float = 0.5):
        self.img = img
        self._threshold = peak_threshold
        self._peaks = None

    def run(self) -> ResidualsRemover:
        self._smooth_outliers()
        self._smooth_global_vertical_residuals()
        self._smooth_local_vertical_residuals()
        self._smooth_outliers()
        self._re_normalize()
        return self

    def _smooth_outliers(self):
        self.img = Collections.replace_sigma_outliers(self.img, s=2.8)

    def _smooth_local_vertical_residuals(self):
        self._find_local_vertical_reseduals()
        self._smooth_vertical_residuals()

    def _smooth_global_vertical_residuals(self):
        self._find_global_vertical_reseduals()
        self._smooth_vertical_residuals()

    def _find_local_vertical_reseduals(self):
        quarter = self.img.shape[0] // 4
        one_dim = np.mean(self.img[quarter:-quarter, :], axis=0)
        pos, _ = sig.find_peaks(one_dim, prominence=self._threshold)
        neg, _ = sig.find_peaks(-one_dim, prominence=self._threshold)
        self._peaks = np.concatenate([pos, neg])

    def _find_global_vertical_reseduals(self):
        one_dim = np.mean(self.img, axis=0)
        pos, _ = sig.find_peaks(one_dim, prominence=self._threshold)
        neg, _ = sig.find_peaks(-one_dim, prominence=self._threshold)
        self._peaks = np.concatenate([pos, neg])

    def _smooth_vertical_residuals(self):
        for peak in self._peaks:
            left = np.mean(self.img[:, peak - 4:peak], axis=1) / 2
            right = np.mean(self.img[:, peak + 1:peak + 5], axis=1) / 2
            self.img[:, peak - 1:peak + 2] = np.array([left + right for _ in range(3)]).T

    def _re_normalize(self):
        self.img = self.img / np.mean(self.img)


class GlobalSmudger:
    """
    ## GlobalSmudger

    This class is to be applied after the absorption lines have been removed from the
    spectral image. As main residuals are vertically, we first generate a polynomial in
    horizontal direction to get the remaining global gradients of the image.
    Then, we do the same in horizontal direction. Finally, a gaussian filter is applied
    to create a smooth gain table

    Polynomial degree and the sigma value to ignore outliers are configurable.
    """

    def __init__(self, img: np.array, deg: int = 11, sigma_mask: float = 0.9):
        self._orig = img
        self._deg = deg
        self._sigma_mask = sigma_mask
        self.gain = np.empty(img.shape)

    def run(self) -> GlobalSmudger:
        self._setup()
        self._fit_cols()
        self._fit_rows()
        self._blur()
        return self

    def _setup(self):
        self._cols = range(self._orig.shape[1])
        self._rows = range(self._orig.shape[0])
        self.gain = Collections.replace_sigma_outliers(self._orig, self._sigma_mask)

    def _fit_rows(self):
        for r in self._rows:
            self._fit_row(r, self._cols)

    def _fit_cols(self):
        self.gain = self.gain.T
        for c in self._cols:
            self._fit_row(c, self._rows)
        self.gain = self.gain.T

    def _fit_row(self, r: int, xes: range):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', np.RankWarning)
            poly = np.poly1d(np.polyfit(xes, self.gain[r], self._deg))
        self.gain[r] = np.array([poly(xes)])

    def _blur(self):
        self.gain = gaussian(self.gain)


class GaussianBlur:

    def __init__(self, img: np.array, kernel: int = 250, truncate: float = 1.5):
        self._orig = img
        self._kernel = kernel
        self._truncate = truncate
        self.gain = np.empty(img.shape)

    def run(self):
        self.gain = gaussian_filter(self._orig, sigma=self._kernel, truncate=self._truncate)
        return self
