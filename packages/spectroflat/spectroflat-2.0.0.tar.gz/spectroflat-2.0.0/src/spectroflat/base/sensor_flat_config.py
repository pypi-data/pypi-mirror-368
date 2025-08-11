from dataclasses import dataclass


@dataclass
class SensorFlatConfig:
    """
    DataItem for sensor flat extraction configuration.

    This class holds all the tiny little configuration details
    used during the extraction of the sensor flat.
    """

    #: Degree of the polynomial fit in spectral direction (along y-axis)
    spacial_degree: int = 6

    #: Sigma factor for outliers to mask (e.g. pixel that deviate more than `sigma_mask * std`).
    sigma_mask: float = 3.5

    #: Flag to toggle if a column wise response map should be average
    average_column_response_map: bool = False

    #: Number of pixels to ignore on the upper and lower border of the ROI
    fit_border: int = 25

    #: Flag to toggle if the spacial gradient shall be ignored or not
    ignore_gradient: bool = True

    # -- values below are detected by the algorithm

    # roi
    roi: tuple = None

    # Total rows
    total_rows: int = 2048
    # Total cols
    total_cols: int = 2048

    @staticmethod
    def from_dict(data: dict):
        """
        Create a sensor flat config from a dictionary.

        All instance variable names are supported as keywords.
        All keywords are optional, if the keyword is not present the default will be used.

        ### Params
        - data: the dictionary to parse

        ### Returns
        The created SensorFlatConfig
        """
        return SensorFlatConfig(**data)
