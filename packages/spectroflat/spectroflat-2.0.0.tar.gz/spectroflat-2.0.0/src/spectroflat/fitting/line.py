#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
provides Line dataclass

@author: hoelken
"""
import numpy as np

from ..base.exceptions import IllegalStateException

DER2RAD = np.pi / 180


class Line:
    """
    Container to store a map of line points
    """

    def __init__(self, center, max_length, rot_anker: int = 2048 // 2, line_distance: int = 25, rotation: float = 0.0):
        #: The averaged line center
        self.center = center
        #: rotation point (i.e. central row (center of y-axis))
        self.rot_anker = rot_anker
        # The tangent based on the rotation in degree
        self.tan_alpha = np.tan(rotation*DER2RAD)
        # The start of the lookup area on the x-axis to search for peaks
        self.start = self.center - line_distance
        # The stop of the lookup area on the x-axis to search for peaks
        self.stop = self.center + line_distance
        # The max length ot the inspected row
        self.max_length = max_length
        #: The resulting list of `[(x1,y1), (x2,y2), ...]` points with the line centers
        self.map = []

    def add(self, point) -> None:
        """
        Add a point to the `Line`.

        :param point: The point to add as (x,y) tuple
        """
        self.map.append(point)

    def gaps(self, coord=1) -> list:
        """Compute distance between the `coord` coordinates of the line points"""
        self.map.sort(key=lambda tup: tup[coord])
        gaps = [self.map[0][coord]]
        for i in range(len(self.map) - 1):
            gaps.append(abs(self.map[i+1][coord] - self.map[i][coord]))
        return gaps

    def area(self, row: int) -> range:
        """The lookup area for the line in a given row."""
        shift = self.shift(row)
        return range(max(0, self.start + shift), min(self.stop + shift, self.max_length))

    def shift(self, row: int) -> int:
        distance = row - self.rot_anker
        if self.tan_alpha == 0.0 or distance == 0:
            return 0

        return int(np.round(distance * self.tan_alpha)) * -1
