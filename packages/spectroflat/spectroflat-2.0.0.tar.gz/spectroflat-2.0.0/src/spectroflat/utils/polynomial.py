from typing import Optional

import numpy as np

# Epsilon as threshold
EPS = 1e-5


def min_value(poly, interval: tuple = (None, None)) -> Optional[float]:
    """
    Return the minimum value of the polynomial within the given range
    (or globally, if no range is given)
    """
    xes, yes = _locally_extreme_values(poly, interval)
    if len(yes) > 1:
        return min(yes)
    if poly(xes[0] - EPS) > yes[0] and poly(xes[0] + EPS) > yes[0]:
        return yes[0]
    return None


def min_pos(poly, interval: tuple = (None, None)) -> Optional[float]:
    """
    Return the position of the minimum of the polynomial within the given range
    (or globally, if no range is given)
    """
    xes, yes = _locally_extreme_values(poly, interval)
    if len(yes) > 1:
        return xes[np.argmin(yes)]
    if poly(xes[0] - EPS) > yes[0] and poly(xes[0] + EPS) > yes[0]:
        return xes[0]
    return None


def max_value(poly, interval: tuple = (None, None)) -> Optional[float]:
    """
    Return the maximum value of the polynomial within the given range
    (or globally, if no range is given)
    """
    xes, yes = _locally_extreme_values(poly, interval)
    if len(yes) > 1:
        return max(yes)
    if poly(xes[0] - EPS) < yes[0] and poly(xes[0] + EPS) < yes[0]:
        return yes[0]
    return None


def max_pos(poly, interval: tuple = (None, None)) -> Optional[float]:
    """
    Return the position of the maximum of the polynomial within the given range
    (or globally, if no range is given)
    """
    xes, yes = _locally_extreme_values(poly, interval)
    if len(yes) > 1:
        return xes[np.argmax(yes)]
    if poly(xes[0] - EPS) < yes[0] and poly(xes[0] + EPS) < yes[0]:
        return xes[0]
    return None


def abs_max_value(poly, interval: tuple = (None, None)) -> float:
    """
    Return the maximum of the absolute extreme values within the given range
    (or globally, if no range is given)
    """
    xes, yes = _locally_extreme_values(poly, interval)
    if len(yes) > 1:
        return max(np.abs(yes))
    if poly(xes[0] - EPS) > yes[0] and poly(xes[0] + EPS) > yes[0]:
        return np.abs(yes[0])
    return 0


def _locally_extreme_values(poly, interval: tuple = (None, None)) -> tuple:
    points = []
    if interval[0] is not None:
        points.append(interval[0])
    d = poly.deriv()
    roots = d.roots() if callable(d.roots) else d.roots
    for x in roots:
        if interval[0] is not None and x < interval[0]:
            continue
        if interval[1] is not None and x > interval[1]:
            continue
        points.append(x)
    if interval[1] is not None:
        points.append(interval[1])
    points.sort()
    values = [poly(x) for x in points]
    return points, values
