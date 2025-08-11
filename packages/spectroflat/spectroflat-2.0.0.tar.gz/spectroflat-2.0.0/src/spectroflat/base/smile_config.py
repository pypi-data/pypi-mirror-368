from dataclasses import dataclass
from typing import Union


@dataclass
class SmileConfig:
    """
    DataItem for smile detection configuration.

    This class holds all the tiny little configuration details
    used during smile detection.
    """

    # --- Smoothing and Filtering ----

    #: En-/disable post line removal smoothing of the gain-table
    smooth: bool = True

    # The polynomial degree for the global smudging
    smoothing_degree: int = 11

    # Sigma filter do remove outliers and only take the background variation
    smoothing_filter: float = 1.5

    align_states: bool = True

    # --- Line Detection ---

    detrend: bool = False

    #: List of line centers to use for processing.
    #: If none is given automatic detection will be used.
    line_centers: list = None

    #: Flag if the peaks are downwards (absorption lines, default) or upwards (emission lines, inverted)
    emission_spectrum: bool = False

    #: Maximum allowed error threshold allowed when fitting a line with a Gaussian or Lorentzian profile
    error_threshold: float = 0.32

    # --- Global Smile ---

    #: Integer > 1 to define the minimum distance of two lines in pixels.
    line_distance: int = 13

    #: Minimal prominence factor of the lines to be regarded.
    #:   Especially useful in noisy data
    line_prominence: float = 0

    #: Minimum sigma * std deviation from mean to be regarded as line
    height_sigma: float = 0.42

    #: Minimum degree to allow in the minimization of the dispersion difference in the rows.
    min_dispersion_deg: int = 1

    #: Maximum degree to allow in the minimization of the dispersion difference in the rows.
    max_dispersion_deg: int = 11

    #: Expected smile degree in vertical (slit) direction.
    smile_deg: int = 7

    # -- rotation --

    #: Rotation correction:
    #   - None (default): No correction
    #   - 'horizontal': Auto detect rotation angle to correct for based on horizontal lines
    #   - 'vertical': Auto detect rotation angle to correct for based on vertical lines
    #   - Number (float): Rotate by the given angle
    rotation_correction: Union[float, str] = None

    # -- general --

    #: Flag to determine if all mod states shall have their own offset map or if the same
    #:    offsets shall be used for all.
    state_aware: bool = False

    # -- values below are detected by the algorithm --

    # roi
    roi: tuple = None

    # Total rows
    total_rows: int = 2048
    # Total cols
    total_cols: int = 2048

    @staticmethod
    def from_dict(data: dict):
        """
        Create a smile config from a dictionary.

        All instance variable names are supported as keywords.
        All keywords are optional, if the keyword is not present the default will be used.

        ### Params
        - data: the dictionary to parse

        ### Returns
        The created SmileConfig
        """
        return SmileConfig(**data)
