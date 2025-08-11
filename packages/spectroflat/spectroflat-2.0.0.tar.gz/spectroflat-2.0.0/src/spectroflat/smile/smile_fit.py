import copy
import warnings
from dataclasses import dataclass

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brute
from scipy.signal import detrend
from qollib.ui.progress import msg

from ..base.config import SmileConfig
from ..base.logging import Logging
from ..utils.line_detection import find_line_cores
from ..utils.processing import MP

log = Logging.get_logger()


@dataclass
class FitRef:
    values: np.array
    cores: np.array = None
    peaks: list = None

    def detrend(self):
        self.values = detrend(self.values) + self.values.mean()
        return self


class SmileFit:

    def __init__(self, img: np.array, config: SmileConfig):
        self._img = img
        self._conf = config
        self._state = -1
        self._current = None
        self.shift_map = []
        self.chi2_map = []

    def run(self):
        while self._get_state():
            log.info('Processing state %s', self._state)
            self._process_state()
        self._post_process_results()

    def _get_state(self) -> bool:
        self._state += 1
        if len(self._img.shape) <= 2:
            self._current = self._img
            return True if self._state == 0 else False

        if self._img.shape[0] > self._state:
            self._current = self._img[self._state]
            return True
        return False

    def _process_state(self):
        sif = _SmileImgFit(self._current, self._conf).run()
        self.shift_map.append(sif.shifts)
        self.chi2_map.append(sif.errors)

    def _post_process_results(self):
        self.shift_map = np.array(self.shift_map)
        self.chi2_map = np.array(self.chi2_map)


class _SmileImgFit:

    def __init__(self, img: np.array, config: SmileConfig):
        self._img = img
        self._conf = config
        self.shifts = []
        self.errors = []
        self._ref = None

    def run(self):
        self._select_reference()
        self._fit_rows()
        self._smooth()
        return self

    def _fit_rows(self):
        rows = range(self._img.shape[0])
        res = dict(MP.simultaneous(_fit_row, [(r, self._img[r], self._ref, self._conf) for r in rows]))
        msg(flush=True)
        for r in rows:
            self.shifts.append(res[r].shifts)
            self.errors.append(res[r].error)

    def _select_reference(self):
        center = self._img.shape[0] // 2
        self._ref = FitRef(values=np.average(self._img[center - 3: center + 3], axis=0))
        if self._conf.detrend:
            self._ref.detrend()
        peaks, cores = find_line_cores(self._ref.values, self._conf)
        nix = [i for i, v in enumerate(cores) if v is None]
        if nix:
            peaks = np.delete(peaks, nix).astype(float)
            cores = np.delete(cores, nix).astype(float)
        self._ref.values = self._ref.values / np.mean(self._ref.values)
        self._ref.cores = cores
        self._ref.peaks = peaks

    def _smooth(self):
        if self._conf.smile_deg < 1:
            return
        self.shifts = np.array(self.shifts)
        yes = np.arange(self._img.shape[0])
        for col in range(self._img.shape[1]):
            poly = np.polynomial.Polynomial.fit(yes, self.shifts[:, col], deg=self._conf.smile_deg)
            self.shifts[:, col] = poly(yes)


class _RowFit:

    def __init__(self, row: np.array, ref: FitRef, config: SmileConfig):
        self._row = row
        self._ref = copy.copy(ref)
        self._conf = config
        self._xes = np.arange(len(self._row))
        self._lines = []
        self.shifts = []
        self.error = []

    def run(self):
        self._detrend()
        self._find_lines()
        self._find_fit()
        return self

    def _detrend(self):
        if self._conf.detrend:
            self._row = detrend(self._row) + self._row.max()

    def _find_lines(self):
        peaks, cores = find_line_cores(self._row, self._conf, self._ref.peaks)
        self._lines = np.array(cores)

    def _find_fit(self):
        with warnings.catch_warnings():
            # We do a brute force approach for the best deg. Thus, we can safely ignore RankWarnings.
            warnings.filterwarnings('ignore', message='.*The fit may.*')
            res = brute(self._chi2_error, (slice(self._conf.min_dispersion_deg, self._conf.max_dispersion_deg + 1, 1),))
            self._chi2_error(res)

    def _chi2_error(self, deg: tuple) -> float:
        self._fit_shifts(int(np.round(deg)))
        self._compute_chi2_error()
        return float(np.sum(self.error))

    def _fit_shifts(self, deg: int):
        uspl = np.polynomial.Polynomial.fit(self._lines, self._ref.cores, deg)
        # Enforce monotony here by stepping through the values and
        # using always the maximum seen so far.
        dispersion = np.maximum.accumulate(uspl(self._xes))
        self.shifts = dispersion - self._xes

    def _compute_chi2_error(self):
        try:
            cs = CubicSpline(self.shifts + self._xes, self._row)
            current = cs(self._xes)
            current = current / np.mean(current)
            self.error = (current - self._ref.values) ** 2 / self._ref.values ** 2
        except ValueError:
            self.error = np.infty


def _fit_row(args: tuple) -> tuple:
    fr = _RowFit(args[1], args[2], args[3]).run()
    msg(f'row {args[0]}')
    return args[0], fr
