#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilities for (multi) processing

@author: hoelken
"""

from qollib.processing import simultaneous


class MP:
    @staticmethod
    def simultaneous(func, args, workers: int = None, raise_exception: bool = True):
        return simultaneous(func, args, workers, raise_exception)
