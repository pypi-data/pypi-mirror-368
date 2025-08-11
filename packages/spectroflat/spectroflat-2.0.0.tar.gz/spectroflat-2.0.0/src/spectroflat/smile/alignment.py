from __future__ import annotations

import numpy as np
from scipy.interpolate import interp1d

from .offset_map import OffsetMap
from ..base import Logging
from ..base.config import SmileConfig
from ..utils.line_detection import find_line_cores

log = Logging.get_logger()


class StateAligner:
    """
    The StateAligner uses the already desmiled version of the input flat frames
    to compute the differential position of all selected lines with respect to mod. state 0.
    The delta will then be linear interpolated over the full range and added to the offset map of the
    respective state.
    """

    def __init__(self, desmiled: np.array, omap: OffsetMap, config: SmileConfig):
        self.states = desmiled
        self.config = config
        self.omap = omap
        self.deltas = [{'x': [], 'y': []} for _ in range(desmiled.shape[0])]
        self._nstates = desmiled.shape[0]
        self._range = np.empty(0)
        self._lcores = []

    def run(self) -> StateAligner:
        self._get_range()
        self._find_line_cores_per_state()
        self._get_position_deltas()
        self._adjust_smile_map()
        return self

    def _find_line_cores_per_state(self):
        c = self.states.shape[1] // 2
        peaks, centers = find_line_cores(self.states[0, c], self.config)
        self._lcores.append(centers)
        for s in range(1, self._nstates):
            self._lcores.append(find_line_cores(self.states[s, c], self.config, peaks)[1])

    def _get_range(self):
        end = self.states.shape[2]
        if self.config.roi is not None:
            end = self.config.roi[1].stop - self.config.roi[1].start
        self._range = np.arange(end)

    def _get_position_deltas(self):
        for s in range(1, self._nstates):
            self.deltas[s]['x'].append(0)
            self.deltas[s]['y'].append(0)
            for i in range(len(self._lcores[0])):
                if i >= len(self._lcores[s]):
                    break
                if self._lcores[0][i] is None or self._lcores[s][i] is None:
                    continue
                d = self._lcores[0][i] - self._lcores[s][i]
                if np.abs(d) < self.config.line_distance/2:
                    self.deltas[s]['x'].append(self._lcores[s][i])
                    self.deltas[s]['y'].append(d)
            self.deltas[s]['x'].append(self._range[-1])
            self.deltas[s]['y'].append(0)

    def _adjust_smile_map(self):
        for s in range(1, self._nstates):
            linear_fit = interp1d(self.deltas[s]['x'], self.deltas[s]['y'], fill_value=0, bounds_error=False)
            delta_offsets = linear_fit(self._range)[np.newaxis, :]
            if self.config.roi is None:
                self.omap.map[s] = self.omap.map[s] + delta_offsets
            else:
                self.omap.map[s][self.config.roi] = self.omap.map[s][self.config.roi] + delta_offsets
