import numpy as np
from scipy.signal import find_peaks

from ..base.config import SmileConfig
from ..fitting.line_fit import LineFit


def find_line_cores(row: np.array, conf: SmileConfig, peaks: list = None) -> tuple:
    allow_shift = False if peaks is None else True
    if not conf.emission_spectrum:
        row = row * -1
    row, peaks = _find_peaks(row, conf, peaks)
    return peaks, _find_minima(peaks, row, conf.line_distance // 2, allow_shift, conf.error_threshold)


def _find_peaks(row: np.array, conf: SmileConfig, peaks: list = None) -> np.array:
    row = row / np.abs(row.mean())
    row = row - row.min()
    h = row.mean() + conf.height_sigma * row.std()
    if peaks is None:
        peaks, _ = find_peaks(row, height=h, prominence=conf.line_prominence, distance=conf.line_distance)
    return row, peaks


def _find_minima(peaks: np.array, row: np.array, win: int, allow_shift: bool = False, max_error: float = 0.5) -> list:
    return [_fit_peak(p, row, win, allow_shift, max_error) for p in peaks]


def _fit_peak(peak: int, row: np.array, win: int, allow_shift: bool, max_error: float) -> float:
    thresholds = [0.25, 0.5, 0.75, 1, 1.5, 2, max_error] if allow_shift else [0.3, max_error]
    thresholds = sorted(thresholds)
    if allow_shift:
        a, b = _get_borders(peak, row, win)
        alt = np.argmax(row[a:b])
        peaks = [peak, a + alt]
    else:
        peaks = [peak]
    for t in thresholds:
        for p in peaks:
            a, b = _get_borders(p, row, win)
            lf = LineFit(np.arange(a, b), row[a:b], error_threshold=t)
            try:
                return lf.run().max_location
            except RuntimeError:
                pass

    return peaks[1] if allow_shift else None


def _get_borders(peak: int, row: np.array, win: int):
    return int(max(0, peak - win)), int(min(len(row), peak + win))
