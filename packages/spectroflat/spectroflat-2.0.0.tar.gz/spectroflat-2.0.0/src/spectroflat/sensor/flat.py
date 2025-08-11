import numpy as np

from .smooth_model import SmoothModel
from ..base.sensor_flat_config import SensorFlatConfig
from ..utils.operations import save_divide


class Flat:
    """
    The `SensorFlat` class is a pre-flat field that contains most of the hard flat field features.
    Most prominently the following is corrected:
        - Sensor features (e.g. dust on the sensor itself)
        - Slit features (e.g. dust on the slit resulting in line features in the spectral direction)
        - (Some of) polarimetric fringes.

    Note 1: The `SensorFlat` is not a full flat and does not correct for gradients nor all fringes.

    Note 2: This class expects 2D data. It is a good idea to have such a flat per modulation state.
    """

    @staticmethod
    def from_frame(flat_frame: np.array, config: SensorFlatConfig):
        """
        Create a `SensorFlat` from an average flat frame.
        Please note that this method expects a 2d image.
        """
        model = SmoothModel(flat_frame, config).create()
        if config.roi is None:
            flat = Flat.save_divide(flat_frame, model.img)
            flat = flat / np.mean(flat)
        else:
            temp = Flat.save_divide(flat_frame[config.roi], model.img[config.roi])
            temp = temp / np.mean(temp)
            flat = np.ones(flat_frame.shape)
            flat[config.roi] = temp
        # import matplotlib.pyplot as plt
        # fig, ax = plt.subplots(nrows=3)
        # ax[0].imshow(model.img)
        # ax[1].imshow(flat_frame)
        # ax[2].imshow(flat)
        # plt.show()
        return Flat(flat)

    def __init__(self, flat: np.array):
        self.flat = flat

    def correct(self, img: np.array):
        return Flat.save_divide(img, self.flat)

    @staticmethod
    def save_divide(a: np.array, b: np.array) -> np.array:
        return save_divide(a, b)
