"""
## Fitting

Line detection and line fitting package provides classes to detect lines
in spectrographic images and to find the line center in a given row.

Please refer to the description of the individual modules for more details.
"""

from .line import Line
from .line_fit import LineFit
from .line_detector import LineDetector
from .line_locator import AutoLineLocator
