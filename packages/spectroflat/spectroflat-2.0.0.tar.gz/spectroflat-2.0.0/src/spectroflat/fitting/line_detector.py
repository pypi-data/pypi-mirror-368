from typing import Union

import numpy as np
from qollib.processing import simultaneous
from qollib.ui import progress

from .line import Line
from .line_fit import LineFit
from ..base import Logging

logger = Logging.get_logger()


class LineDetector:
    """
    This class aims to detect absorption (or emission) lines in an image.

    It first bins all rows and looks for peaks to detect the approx line center.
    This reduces noise and allows for a good first estimate where to expect line(s).

    Then, for each anchor row, the area around the estimated center is fitted with a gaussian
    to detect the actual peak. A map of those detected peaks is available via the `lines` variable
    at the end of the process.
    """

    def __init__(self, image, line_centers: Union[list, np.array], anchors: int = 170, line_distance: int = 80):
        #: number of anchor points to take for each line
        self.anchors = anchors
        #: Integer > 1 to define the minimum distance of two lines.
        self.line_centers = np.array(line_centers)
        #: Float to set the max error for gauss (before trying with lorentzian)
        self.line_distance = line_distance
        #: The image data as 2-dim matrix
        self.image = np.array(image)
        # list of cols to check
        self.check_cols = []
        #: resulting list of lines detected
        self.lines = []

    def run(self):
        """
        Detect lines at anchor points
        """
        self._normalize()
        self._create_lines()
        self._determine_cols_to_check()
        self._detect_lines_per_col()

    def _normalize(self):
        self.image = self.image / np.std(self.image)
        self.image = self.image - np.min(self.image)

    def _create_lines(self) -> None:
        self.lines = [self._create_line(peak) for peak in self.line_centers]

    def _create_line(self, peak: int) -> Line:
        return Line(peak, self.image.shape[0], rot_anker=0, line_distance=self.line_distance)

    def _determine_cols_to_check(self) -> None:
        dist = int(np.ceil(self.image.shape[1] / self.anchors))
        logger.debug('Creating anchors every %s rows', dist)
        self.check_cols = np.array([min(self.image.shape[1] - 1, dist * i) for i in range(1, self.anchors)], dtype=int)
        self.check_cols = np.unique(self.check_cols)

    def _detect_lines_per_col(self):
        data = [self._line_args(line) for line in self.lines]
        self.lines = simultaneous(_detect_line, data)
        progress.dot(flush=True)

    def _line_args(self, line):
        return {'line': line, 'cols': self.check_cols, 'data': self.image, 'error': 2.1}


def _detect_line(args):
    """
    Method on module level to allow parallelization.

    :param args: Tuple with (Line, [cols to check], data)
    """
    error_cols = []
    for col in args['cols']:
        fitter = LineFit(args['line'].area(col), np.transpose(args['data'])[col][args['line'].area(col)],
                         error_threshold=args['error'])
        try:
            fitter.run()
            args['line'].add((fitter.max_location, col))
        except RuntimeError:
            error_cols.append(col)
    success = False if not args['line'].map else len(args['cols']) / len(args['line'].map) > 0.65
    progress.dot(success=success)
    return args['line']
