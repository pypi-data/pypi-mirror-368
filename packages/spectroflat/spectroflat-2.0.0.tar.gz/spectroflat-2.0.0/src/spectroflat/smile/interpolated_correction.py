#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
provides SmileInterpolator

@author: hoelken
"""
import numpy as np
from scipy.interpolate import CubicSpline
from qollib.processing.execution import simultaneous, CPU_LIM

from .smile_correction import SmileCorrector
from ..base import Logging

log = Logging.get_logger()


class SmileInterpolator(SmileCorrector):
    """
    ## SmileInterpolator

    Uses (bi cubic) 2D interpolation to de-skew the given image according to the provided `OffsetMap`.
    """

    def _correct_smile(self):
        rows, cols = self._img.shape
        rows = np.arange(rows)
        xes = np.arange(cols)
        args = [(r, xes, self._smap.get_offsets(r, self._mod_state), self._img[r]) for r in rows]
        res = dict(simultaneous(SmileInterpolator.desmile_row, args, workers=min(CPU_LIM, 7)))
        self._construct_result(res, rows)

    def _construct_result(self, res: dict, rows: np.array):
        self.result = np.array([res[row] for row in rows])
        b = int(np.max(np.abs(self._smap.map))) + 1
        self.result[:, 0:b] = self._img.mean()
        self.result[:, -b:] = self._img.mean()

    @staticmethod
    def desmile_row(args: tuple) -> tuple:
        # 0: row_id, 1: xes, 2: shifts, 3: row values
        # return args[0], np.interp(args[1], args[1] + args[2], args[3])
        try:
            mshifts = SmileInterpolator._monotonic_shifts(args[1], args[2])
            cs = CubicSpline(mshifts, args[3])
            return args[0], cs(args[1])
        except ValueError as e:
            log.error('Row %s: %s', args[0], e)
            raise e

    @staticmethod
    def _monotonic_shifts(xes: np.array, shifts: np.array) -> np.array:
        length = len(shifts)
        mask = shifts != 0
        first_non_zero = np.where(mask.any(), mask.argmax(), 0)
        if first_non_zero != 0:
            shifts[0:first_non_zero] = shifts[first_non_zero]
        val = length - np.flip(mask).argmax() - 1
        last_non_zero = np.where(mask.any(), val, length)
        if last_non_zero != length:
            shifts[last_non_zero:] = np.maximum.accumulate(shifts[last_non_zero:])
        return xes + shifts

    @staticmethod
    def desmile_state(data: tuple) -> tuple:
        """
        Applies the smile correction to all mod states simultaneously.

        ### Params
        data should be a tuple of:
        0 = smap: OffsetMap,
        1 = img: np.array, the image to correct,
        2 = state: Union[int, None]

        ### Returns
        A tuple of (state, corrected_image)
        """
        sc = SmileInterpolator(data[0], data[1], mod_state=data[2]).run()
        return data[2], sc.result
