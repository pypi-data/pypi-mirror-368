import numpy as np


def extract_c2c_comp(img: np.array, shape: tuple) -> np.array:
    """
    Removes the average column2column response comp
    :param img: the mean flat frame
    :param shape: the shape of the pattern to create
    :return: tuple (the cleaned input img, avrg. response diff)
    """
    states = img.shape[0]
    avrg = np.mean(np.mean(img, axis=0), axis=0)
    response = np.mean([avrg[i] / avrg[i + 1] for i in range(0, len(avrg) - 1, 2) if avrg[i + 1] > 1e-3])
    pattern = np.ones(shape)
    for col in range(0, shape[1] - 1, 2):
        pattern[:, col + 1] = response
    return np.array([pattern for _ in range(states)])
