#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
provides OffsetMap

@author: hoelken
"""
from __future__ import annotations

import os

import numpy as np
from astropy.io import fits

from ..base import Logging

log = Logging.get_logger()


class OffsetMap:
    """
    ## Offset Map
    This class holds the map of offsets by the smile per line.
    """

    @staticmethod
    def from_file(path) -> OffsetMap:
        with fits.open(path) as hdul:
            hdul[0].verify('silentfix')
            om = OffsetMap()
            om.header = hdul[0].header
            om.map = hdul[0].data
            om.error = hdul[1].data
            om.path = path
            if len(hdul) == 3:
                om.wl = hdul[2].data
        return om

    def __init__(self, header: dict = None):
        #: The map holds a numpy array with the shifts per mod state.
        #: If the map was squashed the map has shape y,x, else state,y,x
        self.map = np.zeros((0, 0, 0))
        #: The error is the per pixel chi² error from the central line.
        #: If the map was squashed the map has shape y,x, else state,y,x
        self.error = np.zeros((0, 0, 0))
        self.wl = None
        self.header = None
        self.path = None
        header = header if header is not None else {}
        header['squashed'] = False
        self.set_header(header)

    def is_empty(self) -> bool:
        return self.map.shape == (0, 0, 0)

    def set_header(self, header: dict) -> None:
        self.header = fits.Header()
        for key, value in header.items():
            self.header[key] = str(value)

    def get_offsets(self, row: int, state: int = 0) -> np.array:
        img = self.map[state] if self.is_squashed else self.map
        return img[int(row)]

    def get_map(self, state: int = 0) -> np.array:
        return self.map[state] if self.is_squashed() else self.map

    def get_mean_errors(self):
        if self.is_squashed():
            return [np.mean(self.error)]
        return [np.mean(self.error[s]) for s in range(self.map.shape[0])]

    def get_max_errors(self):
        if self.is_squashed():
            return [np.max(self.error)]
        return [np.max(self.error[s]) for s in range(self.map.shape[0])]

    def dump(self, out_file, overwrite: bool = True):
        """
        Dump  a SmileMap to a `fits` file.
        HDU 0: shifts + header
        HDU 1: chi2 error map

        :param out_file: The file to write to
        :param overwrite: Overwrite existing file with same name?
        """
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        hdul = fits.HDUList()
        phdu = fits.PrimaryHDU(self.map, header=self.header)
        hdul.append(phdu)
        hdul.append(fits.ImageHDU(data=self.error))
        if self.wl is not None:
            wlhdu = fits.ImageHDU(data=self.wl)
            wlhdu.header.append(('WLSAMP', f'{(max(self.wl) - min(self.wl))/len(self.wl):.8e}'), 'average sampling')
            wlhdu.header.append(('NWL', len(self.wl)), 'WL-points')
            wlhdu.header.append(('HIERARCH MIN_WL_NM', min(self.wl)), '')
            wlhdu.header.append(('HIERARCH MAX_WL_NM', max(self.wl)), '')
            hdul.append(wlhdu)
        log.info('Write OffsetMap to "%s"...', out_file)
        hdul.writeto(out_file, overwrite=overwrite)
        self.path = out_file

    def is_squashed(self) -> bool:
        return self.header['squashed'] in ['True', True]

    def squash(self) -> None:
        if self.is_squashed():
            return

        self.header['squashed'] = True
        s = self.map.shape[0]
        self.map = np.repeat(self.map.mean(axis=0, keepdims=True), s, axis=0)
        self.error = np.repeat(self.error.mean(axis=0, keepdims=True), s, axis=0)

    def enforce_same_offsets_on_all_states(self):
        states = self.map.shape[0]
        self.map = np.repeat(np.mean(self.map, axis=0, keepdims=True, dtype='float32'), states, axis=0)
        self.error = np.repeat(np.mean(self.error, axis=0, keepdims=True), states, axis=0)

    def __repr__(self) -> str:
        text = f'{self.__class__.__name__}\n'
        for k, v in self.header.items():
            text += f'{k}:\t {v}\n'
        text += f'Shape:\t\t {self.map.shape}\n'
        text += f'Mean Error:\t{np.mean(self.error)}'
        return text
