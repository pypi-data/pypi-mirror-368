import numpy as np

from ..base.sensor_flat_config import SensorFlatConfig
from ..utils import Collections


class SmoothModel:
    """
    The `SmoothModel` is a smoothed version of the actual flat image.

    It is created by fitting a polynomial of configured degree (usually 2 to 6)
    to each spectral position along the spatial resolution.
    As the Image typically suffers from the spectrographic curvature effect and
    optical aberrations the  fitted version is an ideal representation of the
    flat field frame without these.
    """

    def __init__(self, img: np.array, config: SensorFlatConfig):
        self._orig = img
        self._config = config
        self._current_poly = None
        self.img = None

    def create(self):
        self._configure()
        for x in self._cols:
            self._fit_column(x)
            self._model_column(x)
        self._transpose()
        self._remove_spacial_gradient()
        self._finalize()
        return self

    def _configure(self):
        self._config.total_rows = self._orig.shape[0]
        self._config.total_cols = self._orig.shape[1]
        if self._config.roi is None:
            self.img = np.empty(self._orig.shape).T
            self._rows = range(self._config.total_rows)
            self._cols = range(self._config.total_cols)
            self._offset = 0
        else:
            shape = (self._config.roi[0].stop - self._config.roi[0].start,
                     self._config.roi[1].stop - self._config.roi[1].start)
            self.img = np.empty(shape).T
            self._offset = self._config.roi[1].start
            self._rows = np.arange(self._config.roi[0].start, self._config.roi[0].stop)
            self._cols = range(self._config.roi[1].start, self._config.roi[1].stop)

    def _fit_column(self, x: int):
        b = self._config.fit_border
        if self._config.roi is None:
            col = self._orig[:, x][b:-b]
        else:
            col = self._orig[self._config.roi[0], x][b:-b]
        col = Collections.interpolate_sigma_outliers(col, self._config.sigma_mask, filter_ones=True)
        self._current_poly = np.poly1d(np.polyfit(self._rows[b:-b], col, self._config.spacial_degree))

    def _model_column(self, x: int):
        self.img[x - self._offset] = np.array([self._current_poly(self._rows)])

    def _remove_spacial_gradient(self):
        if self._config.ignore_gradient:
            grad = np.average(self.img, axis=1)
            self.img = np.array([self.img[i] / grad[i] for i in range(len(grad))])

    def _transpose(self):
        self.img = self.img.T

    def _finalize(self):
        if self._config.roi is None:
            return

        img = np.ones(self._orig.shape)
        img[self._config.roi] = self.img
        self.img = img
