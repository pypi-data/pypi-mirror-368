#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Definitions for custom exceptions go here

@author: hoelken
"""


class IllegalStateException(RuntimeError):
    """
    Exception to be raised if the current class is asked to
        perform an operation where the state conditions are not
        satisfied (yet). E.g. no data loaded.
    """
    pass


class DataMissMatchException(RuntimeError):
    """
    Exception to be raised if the data do not fit together.
        I.e. if a dark image from another cam is used, or if the
        integration times don't match.
    """
    pass


class InsufficientDataException(RuntimeError):
    """
    Exception to be raised if the data does not suffice processing.
        I.e. not enough frames to detect polarimetric state
    """
    pass


class IllegalArgumentException(RuntimeError):
    """
    Exception to be raised if the current class is asked to
        perform an operation where the state conditions are not
        satisfied (yet). E.g. no data loaded.
    """
    pass


class MissConfigurationException(RuntimeError):
    """
    Exception to be raised if the given configuration has internal
        conflicts or is missing mandatory information
    """
    pass
