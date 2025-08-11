import numpy as np


def save_divide(a: np.array, b: np.array) -> np.array:
    """
    Method to safely divide one array by the other.
    Avoids division by zero and improves numerical precision.
    """
    return np.true_divide(a.astype('float32'), b.astype('float32'), out=a.astype('float32'),
                          where=b != 0, dtype='float64')
