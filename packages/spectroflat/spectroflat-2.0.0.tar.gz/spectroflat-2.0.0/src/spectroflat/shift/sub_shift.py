#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Util for sub pixel shifting

@author: hoelken
"""
import numpy as np
from scipy import ndimage, signal


class Shifter:
    """
    Helper class to shift images in subpixel amounts using FFT
    """

    @staticmethod
    def d1shift(img: np.array, offset: float) -> np.array:
        """
        Creates a FFTd version of the image and shifts it by the offset amount.

        ## Params
        - `ìmg`: An 1d array object representing the image row
        - `offset`: The amount the center is shifted
        """
        window = signal.windows.kaiser(len(img), 2.5)
        ft_img = np.fft.fft(img * window)
        result = ndimage.fourier_shift(ft_img, shift=-offset)
        return np.fft.ifft(result).real

    @staticmethod
    def d2shift(img, offset):
        """
        Creates a FFTd version of the image and shifts it by the offset amount.

        ## Params
        - `ìmg`: An array object representing the image
        - `offset`: The amount the center is shifted must be float or iterable.
            If float the same offset will be applied to all axes, if iterable an offset for each axis must be provided
        """
        window2d = np.sqrt(np.outer(signal.windows.kaiser(img.shape[0], 2.5),
                                    signal.windows.kaiser(img.shape[1], 2.5)))
        ft_img = np.fft.fft2(img * window2d)
        result = ndimage.fourier_shift(ft_img, shift=-offset)
        return np.fft.ifft2(result).real
