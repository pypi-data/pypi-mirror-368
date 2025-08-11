#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module to help with fitting Gauss Curves to data

@author: hoelken
"""
import warnings
import numpy as np
from scipy.optimize import curve_fit, fminbound
from scipy.signal import find_peaks

from ..base import Logging

logger = Logging.get_logger()


class LineFit:
    """
    ## LineFit
    Helper class to take care of fitting noise data of line profiles.

    Provided a set of `x` and `y` values of same dimension the process will first look for
    peaks in the `y`. Depending on the number of peaks the algorithm will try a single or
    overlapping gauss fit and will compute starting amplitude, mean and sigma from the peak(s)
    found.

    It will first try a lorentzian fit, if this does not work it will try a gaussian fit as fallback.

    The resulting optimized values, covariance and errors can be retrieved directly after the fit was performed.
    Also, the x-location of the maximum (peak) is available.
    """

    def __init__(self, xes, yes, error_threshold=1.1):
        #: x axis
        self.xes = np.array(xes, dtype='float64')
        #: y values to x axis entries
        self.yes = np.array(yes, dtype='float64')
        #: Float to set the max error for gauss (before checking with lorentzian)
        self.error_threshold = error_threshold
        # Initial values
        self.p0_args = []
        # Results
        #: POPT: Optimized values for (amplitude, center, sigma) per peak.
        #:   if more than one peak is detected this will be multiple of 3 values with (a1, c1, s1, a2, s2, c2, ...)
        self.popt = None
        #: The estimated covariance of popt.
        self.pcov = None
        #: The standard deviation errors on (amplitude, center, sigma)
        self.perr = None
        #: the absolute max location (x)
        self.max_location = None
        #: Fit used
        self.fitting_function = None

    def run(self):
        """
        Trigger the fitting process.

        ### Raises
        `RuntimeError` if the fit was not successful
        """
        self._check_input()
        self._initial_values()
        self._fit_line()
        self._find_max()
        return self

    def _check_input(self):
        if len(self.xes) == 0 or len(self.yes) == 0:
            raise RuntimeError('At least one of the given data sets is empty')

    def _fit_line(self):
        self._fit_lorentz()
        if self.perr is not None and np.mean(self.perr) < self.error_threshold:
            return

        self._fit_gauss()
        if self.perr is not None and np.mean(self.perr) < self.error_threshold:
            return

        raise RuntimeError('Could not fit given data. Neither Gauss nor Lorentz function worked.')

    def _initial_values(self):
        peaks, _ = find_peaks(self.yes, distance=len(self.yes)//3, prominence=0.05)
        if len(peaks) == 0:
            peaks = [np.argmax(self.yes)]

        ymin = min(self.yes)
        ysum = sum(self.yes)
        ysum = len(self.yes) if ysum <= 0 else ysum
        for peak in peaks:
            self.p0_args.append(self.yes[peak] - ymin)                                              # amplitude
            self.p0_args.append(self.xes[peak])                                                     # center
            self.p0_args.append(np.sqrt(sum(self.yes * (self.xes - self.xes[peak]) ** 2) / ysum))   # sigma

    def _fit_gauss(self):
        self.fitting_function = 'gaussian'
        self._fit(overlapping_gaussian)

    def _fit_lorentz(self):
        self.fitting_function = 'lorentzian'
        self._fit(overlapping_lorentzian)

    def _find_max(self):
        x0 = min(self.xes)
        x1 = max(self.xes)
        if self.fitting_function == 'lorentzian':
            self.max_location = fminbound(lambda x: -overlapping_lorentzian(x, *self.popt), x0, x1)
        else:
            self.max_location = fminbound(lambda x: -overlapping_gaussian(x, *self.popt), x0, x1)

    def _fit(self, func):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            try:
                self.popt, self.pcov = curve_fit(func, self.xes, self.yes, p0=self.p0_args)
                self.perr = np.sqrt(np.diag(self.pcov))
            except (TypeError, RuntimeWarning, RuntimeError):
                pass


def gaussian(x, amplitude, mean, sigma) -> float:
    """
    Fitting function for [Gaussian normal distribution](https://en.wikipedia.org/wiki/Normal_distribution).

    Signature follows requirements for `scipy.optimize.curve_fit` callable,
    see [curve_fit documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html).
    It takes the independent variable as the first argument and the parameters to fit as separate remaining arguments.

    ### Params
    - `x` The free variable
    - `amplitude` The amplitude
    - `mean` The center of the peak
    - `sigma` The standard deviation (The width of the peak)

    ### Returns
    The y value
    """
    return amplitude * np.exp(-np.power(x - mean, 2.) / (2 * np.power(sigma, 2.)))


def overlapping_gaussian(x, *args):
    """
    Fitting function for data with (potentially) overlapping gaussian shaped peaks.
    Parameters are similar to `gaussian`. Always only one x, but the other params may come in packs of three.

    See `gaussian` for further details
    """
    return sum(gaussian(x, *args[i*3:(i+1)*3]) for i in range(int(len(args) / 3)))


def lorentzian(x, amplitude, center, width) -> float:
    """
    Fitting function for [Cauchy-Lorentzian distribution](https://en.wikipedia.org/wiki/Cauchy_distribution)

    Signature follows requirements for `scipy.optimize.curve_fit` callable,
    see [curve_fit documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html).
    It takes the independent variable as the first argument and the parameters to fit as separate remaining arguments.

    ### Params
    - `x` The free variable
    - `amplitude` The amplitude
    - `center` The center of the peak
    - `width` The width of the peak

    ### Returns
    The y value
    """
    return amplitude * width**2 / ((x-center)**2 + width**2)


def overlapping_lorentzian(x, *args) -> float:
    """
    Fitting function for data with (potentially) overlapping lorentzian shaped peaks.
    Parameters are similar to `lorentzian`. Always only one x, but the other params may come in packs of three.

    See `lorentzian` for further details
    """
    return sum([lorentzian(x, *args[i*3:(i+1)*3]) for i in range(int(len(args)/3))])
