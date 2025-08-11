from dataclasses import dataclass, field

from qollib.strings import parse_shape

from .sensor_flat_config import SensorFlatConfig
from .smile_config import SmileConfig


@dataclass
class Config:
    """
    Configuration DataItem
    """

    #: Flag to indicate if the pre-flat shall be applied.
    apply_sensor_flat: bool = True

    #: [y0:y1,x0:x1] Region of interest in numpy notation (everything outside will be ignored)
    roi: tuple = None

    #: refine hard flat by iterating it to become self-consistent
    iterations: int = 2

    #: The specific configuration for the pre-flat.
    sensor_flat: SensorFlatConfig = field(default_factory=SensorFlatConfig)

    #: The configuration for the smile detection.
    smile: SmileConfig = field(default_factory=SmileConfig)

    @staticmethod
    def from_dict(data: dict):
        """
        Create a config from a dictionary.

        All instance variable names are supported as keywords.
        All keywords are optional, if the keyword is not present the default will be used.

        """
        sc = data.pop('smile') if 'smile' in data.keys() else None
        sfc = data.pop('sensor_flat') if 'sensor_flat' in data.keys() else None
        data['roi'] = parse_shape(data['roi']) if 'roi' in data else None

        c = Config(**data)
        if sc is not None:
            c.smile = SmileConfig.from_dict(sc)
        if sfc is not None:
            c.sensor_flat = SensorFlatConfig.from_dict(sfc)
        if c.roi is not None:
            c.smile.roi = c.roi
            c.sensor_flat.roi = c.roi
        return c
