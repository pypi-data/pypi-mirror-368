#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
provides SmileCorrector, RowCorrector

@author: hoelken
"""
import numpy as np

from .offset_map import OffsetMap
from ..base import Logging
from ..shift.img_rotation import RotationCorrection

logger = Logging.get_logger()


class SmileCorrector:
    """
    ## SmileCorrector

    Smile correction super class
    """

    def __init__(self, smap: OffsetMap, img: np.array, mod_state: int = None):
        #: The `SmileMap` to apply
        self._smap = smap
        #: The `Fits` object of the image to correct
        self._img = img
        #: The modulation state to apply. Set to None to apply squashed map
        self._mod_state = mod_state
        #: The smile corrected image data
        self.result = None

    def run(self):
        self._derotate()
        self._squash_smap()
        self._correct_smile()
        return self

    def _derotate(self):
        if 'Rotation' not in self._smap.header:
            return

        angle = float(self._smap.header['Rotation'])
        if angle == 0:
            return

        logger.debug('De-rotating by %0.5f [deg]', angle)
        self._img = RotationCorrection(self._img, angle).bicubic()

    def _squash_smap(self):
        if self._mod_state is not None:
            return
        self._smap.squash()

    def _correct_smile(self):
        raise NotImplemented('Please use derived class!')
