#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The `Collections` utility provides methods to deal with Collections (lists, dictionaries, arrays, ...)

@author: hoelken
"""

from typing import Callable

import numpy as np
from scipy import signal
from scipy.interpolate import interp1d


class Collections:
    """
    Static utility for handling collections.
    """

    @staticmethod
    def as_float_array(orig) -> np.array:
        """
        Creates a copy of the orig and converts all values to `float32`

        ### Params
        - orig: an object that can be converted to a list

        ### Params
        Array with float values converted from the orig
        """
        return np.array(list(orig), dtype=np.float32)

    @staticmethod
    def as_int_array(orig) -> np.array:
        """
        Creates a copy of the orig and converts all values to `int`

        ### Params
        - orig: an object that can be converted to a list

        ### Params
        Array with int values converted from the orig
        """
        return np.array(list(orig), dtype=int)

    @staticmethod
    def bin(orig: np.array, binning: list, method: Callable = np.mean) -> np.array:
        """
        Bins along a given set of axis.

        ### Params
        - orig: The original numpy array
        - binning: A list of binning values.
            - Length of the list must match the number of axis (i.e. the length of the `orig.shape`).
            - Per axis set `1` for no binning, `-1` for bin all and any positive number
                  to specify the bin size along the axis.
        - method: The function to apply to the bin (e.g. np.max for max pooling, np.mean for average)
        ### Returns
        The binned array
        """
        if np.all(np.array(binning) == 1):
            # no binning whatsoever, return original
            return orig

        if len(orig.shape) != len(binning):
            raise Exception(f"Shape {orig.shape} and number of binning axis {binning} don't match.")

        data = orig
        for ax in range(len(binning)):
            data = Collections.bin_axis(data, binning[ax], axis=ax, method=method)
        return data

    @staticmethod
    def bin_axis(data: np.array, binsize: int, axis: int = 0, method: Callable = np.mean):
        """
       Bins an array along a given axis.

       ### Params
       - data: The original numpy array
       - axis: The axis to bin along
       - binsize: The size of each bin
       - method: The function to apply to the bin (e.g. np.max for max pooling, np.mean for average)

       ### Returns
       The binned array
       """
        if binsize < 0:
            return np.array([method(data, axis=axis)])

        dims = np.array(data.shape)
        argdims = np.arange(data.ndim)
        argdims[0], argdims[axis] = argdims[axis], argdims[0]
        data = data.transpose(argdims)
        data = [method(np.take(data, np.arange(int(i * binsize), int(i * binsize + binsize)), 0), 0)
                for i in np.arange(dims[axis] // binsize)]
        data = np.array(data).transpose(argdims)
        return data

    @staticmethod
    def replace_sigma_outliers(data: np.array, s: float = 5) -> np.array:
        """
        Replaces outliers from the data set with the mean.

        :param data: The data to clean
        :param s: the factor of sigma to clean for. Default is 5 Sigma (99.99994%)
        :return: A cleaned copy of the dataset
        """
        copy = data.copy()
        mean_val = np.mean(data)
        sigma = s * np.std(data)
        copy[np.where(np.abs(data - mean_val) > sigma)] = mean_val
        return copy

    @staticmethod
    def interpolate_sigma_outliers(data: np.array, sigma: float = 5, filter_ones: bool = False) -> np.array:
        """Interpolate pixels/areas in 1D(!) arrays that are below or above a given sigma range"""
        outliers = np.where(data <= 1)[0] if filter_ones else np.array([])

        dtr = np.array(signal.detrend(data))
        m, s = dtr.mean(), dtr.std()
        outliers = np.concatenate((outliers, np.where(dtr < m - sigma * s)[0]))
        outliers = np.concatenate((outliers, np.where(dtr > m + sigma * s)[0]))
        outliers = np.array(list(set(outliers)))
        outliers = np.sort(outliers)
        if len(outliers) == 0:
            return data

        xes = np.arange(len(data))
        interp_func = interp1d(np.delete(xes, outliers), np.delete(data, outliers), bounds_error=False)
        corrected_data = interp_func(xes)

        # For regions at the start or end of the data where the interpolation won't work,
        # we fill with the original data
        nans = np.isnan(corrected_data)
        corrected_data[nans] = data[nans]
        return corrected_data
