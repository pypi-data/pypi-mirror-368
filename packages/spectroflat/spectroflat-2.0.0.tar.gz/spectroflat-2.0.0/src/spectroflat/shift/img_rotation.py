import numpy as np

from skimage.feature import canny
from skimage.transform import probabilistic_hough_line, rotate

from ..base.exceptions import InsufficientDataException

DEG2RAD = np.pi / 180


class RotationAnalysis:
    """
    This class analyzes the global rotation of a given image.

    First it detects edges via the canny algorithm, and then it uses scikit
    implementation of [Hough Transform](https://en.wikipedia.org/wiki/Hough_transform) to detect
    straight lines. Finally, the angle of all lines is computed and the median of all angles is returned.
    """

    @staticmethod
    def detect_horizontal_rotation(img: np.array) -> float:
        return RotationAnalysis(img.T).run().angle * -1

    @staticmethod
    def detect_vertical_rotation(img: np.array) -> float:
        return RotationAnalysis(img).run().angle

    def __init__(self, img: np.array, deg_range: float = 4):
        #: The image to analyse
        self._orig = img
        #: Max rotation in deg
        self._deg_range = deg_range
        #: The detected rotation angle in degree
        self.angle: float = 0.0

    def run(self):
        """Start the detection algorithm"""
        lines = self._detect_lines()
        if len(lines) == 0:
            raise InsufficientDataException('No lines detected. Cannot determine image rotation.')

        self._detect_rotation(lines)
        return self

    def _detect_lines(self) -> list:
        theta = np.linspace(-self._deg_range * DEG2RAD, self._deg_range * DEG2RAD)
        edges = canny(self._orig, sigma=1.5)
        return probabilistic_hough_line(edges, threshold=50, line_length=150, line_gap=10, theta=theta)

    def _detect_rotation(self, lines: list):
        angles = [np.degrees(np.arctan2(y2 - y1, x2 - x1)) for (x1, y1), (x2, y2) in lines]
        # noinspection PyTypeChecker
        self.angle = RotationAnalysis.minimize(np.median(angles))

    @staticmethod
    def minimize(angle: float) -> float:
        angle = angle % 90
        if angle > 45:
            angle -= 90
        if angle < -45:
            angle += 90
        return angle


class RotationCorrection:

    def __init__(self, img: np.array, angle: float):
        self._img = img
        self._angle = angle

    def _cut_shape(self) -> tuple:
        rad_angle = np.abs(self._angle) * DEG2RAD
        cut0 = int(np.ceil(np.tan(rad_angle) * self._img.shape[1] / 2))
        cut1 = int(np.ceil(np.tan(rad_angle) * self._img.shape[0] / 2))
        return slice(cut0, self._img.shape[0] - cut0), slice(cut1, self._img.shape[1] - cut1)

    def bicubic(self, cut_shape: bool = False, pad_mean: bool = True) -> np.array:
        """
        Rotate the given image by the given angle with a bicubic algorithm
        ### Params
        - cut_shape: If True image will be cropped to square
        - pad_mean: If True the black borders will be filled with the images mean value instead.

        ### Returns
        The rotated image
        """
        if self._angle == 0:
            return self._img
        img = rotate(self._img, self._angle, order=3)
        if cut_shape:
            return img[self._cut_shape()]
        if pad_mean:
            inner = self._cut_shape()
            temp = np.ones(self._img.shape) * img[inner].mean()
            temp[inner] = img[inner]
            img = temp
        return img
