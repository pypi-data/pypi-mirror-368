#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
provides SmileMapGenerator, SmileDetector, LineSmileFitter

@author: hoelken
"""
from datetime import datetime

import numpy as np

from .offset_map import OffsetMap
from .smile_fit import SmileFit
from ..base import Logging
from ..base.smile_config import SmileConfig

logger = Logging.get_logger()


class SmileMapGenerator:
    """
    ##SmileMapGenerator
    This class generates a `OffsetMap` from a set of input files.
    For each state: In every row lines are detected and line cores fitted.
    Then the cores are shifted wrt to the central row until the chi² error
    between current and central row is minimal

    The `OffsetMap` can be saved to a fits file.
    Metadata in the smile map with keywords similar to the FITS images will help to test
    the applicability of the map for an image to correct.
    """

    def __init__(self, smile_config: SmileConfig, cube: np.array):
        #: or for emission lines (thus the image is inverted)
        self._config = smile_config
        #: The image cube to process
        self._cube = cube
        #: Result: The generated OffsetMap
        self.omap = OffsetMap()

    def run(self, out_file=None):
        self._collect_metadata()
        self._configure_builder()
        self._detect_smile()
        self._write_to_disk(out_file)
        return self

    def _collect_metadata(self):
        self.omap.header['Type'] = 'OffsetMap'
        self.omap.header['GenTime'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.omap.header['DIMS'] = repr(['state', 'y', 'lambda'])
        self.omap.header['Shape'] = repr(self._cube.shape)
        self.omap.header['Rotation'] = repr(self._config.rotation_correction)
        if self._config.roi is not None:
            self.omap.header['ROI'] = repr(self._config.roi)

    def _configure_builder(self):
        if self._config.roi is None:
            self._config.total_rows = self._cube.shape[-2]
            self._config.total_cols = self._cube.shape[-1]
        else:
            self._config.total_rows = self._config.roi[0].stop - self._config.roi[0].start
            self._config.total_cols = self._config.roi[1].stop - self._config.roi[1].stop

    def _detect_smile(self):
        if self._config.roi is None:
            sf = SmileFit(self._cube, self._config)
        else:
            roi = (slice(0, self._cube.shape[0]), self._config.roi[0], self._config.roi[1])
            sf = SmileFit(self._cube[roi], self._config)
        sf.run()
        if self._config.roi is None:
            self.omap.map = sf.shift_map
            self.omap.error = sf.chi2_map
        else:
            y0 = roi[1].start
            y1 = self._cube.shape[1] - roi[1].stop
            x0 = roi[2].start
            x1 = self._cube.shape[2] - roi[2].stop
            self.omap.map = np.pad(sf.shift_map, ((0, 0), (y0, y1), (x0, x1)),
                                   'constant', constant_values=(0, 0))
            self.omap.error = np.pad(sf.chi2_map, ((0, 0), (y0, y1), (x0, x1)),
                                     'constant', constant_values=(0, 0))

    def _write_to_disk(self, out_file):
        if out_file is None:
            return

        logger.info('Writing OffsetMap to %s', out_file)
        self.omap.dump(out_file)
