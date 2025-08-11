
import numpy as np
from ..shift.img_rotation import RotationCorrection
from ..sensor.flat import Flat


def split_sensor_slit_flat(dust_flat: np.array, rotation: float = 0) -> tuple:
    """
    Splits the given dust flat into the sensor and slit contribution parts.
    :param dust_flat: the dust flat to split
    :param rotation: The rotation of the dust flat (see offset map header)
    :return: tuple(sensor, slit)
    """
    slit_flat = np.ones_like(dust_flat)
    sensor_flat = np.ones_like(dust_flat)
    for s in range(dust_flat.shape[0]):
        df = RotationCorrection(dust_flat[s].astype('float32'), -rotation).bicubic()
        slf = np.repeat(np.mean(df, axis=1, keepdims=True), dust_flat.shape[2], axis=1)
        slit_flat[s] = RotationCorrection(slf, rotation).bicubic()
        slf = slf / slf.mean()
        snf = Flat.save_divide(df, slf)
        snf = snf / snf.mean()
        sensor_flat[s] = RotationCorrection(snf, rotation).bicubic()
    return sensor_flat, slit_flat
