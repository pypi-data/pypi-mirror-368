from __future__ import annotations

import copy

import numpy as np

from ..shift.img_rotation import RotationCorrection
from ..smile import OffsetMap, SmileInterpolator
from ..utils.processing import MP


class ArtificialFlat:

    def __init__(self, img: np.array, roi: tuple = None):
        self._roi = roi if roi is not None else tuple([slice(0, s) for s in img.shape])
        self.artificial = np.ones(img.shape)
        self._input = img

    def create(self) -> ArtificialFlat:
        self._expand_vertical_average()
        return self

    def _expand_vertical_average(self):
        average = np.mean(self._input[self._roi], axis=1)
        states, rows, _ = self.artificial.shape
        for s in range(states):
            for r in range(rows):
                self.artificial[s, r, self._roi[2]] = average[s]

    def resmile(self, offsets: OffsetMap) -> ArtificialFlat:
        b = int(np.max(np.abs(offsets.map))) + 1
        rot = -float(offsets.header['Rotation'])
        omap = copy.deepcopy(offsets)
        omap.header['Rotation'] = 0
        args = []
        for s in range(self.artificial.shape[0]):
            omap.map[s] *= -1
            args.append((omap, self.artificial[s], s))
        result = dict(MP.simultaneous(SmileInterpolator.desmile_state, args))
        img = [RotationCorrection(result[s], rot).bicubic() for s in range(self.artificial.shape[0])]
        self.artificial = np.array(img)
        self.artificial[self._roi][:, :, 0:b] = self._input[self._roi][:, :, 0:b]
        self.artificial[self._roi][:, :, -b:] = self._input[self._roi][:, :, -b:]
        return self

    def pad(self, shape: tuple):
        y = (shape[1] - self.artificial.shape[1]) // 2
        x = (shape[2] - self.artificial.shape[2]) // 2
        self.artificial = np.pad(self.artificial, ((0, 0), (y, y), (x, x)), 'constant', constant_values=1)
        return self

    def remove(self, img: np.array):
        return np.true_divide(img.astype('float32'), self.artificial.astype('float32'),
                              out=img.astype('float32'), where=self.artificial != 0, dtype='float64')
