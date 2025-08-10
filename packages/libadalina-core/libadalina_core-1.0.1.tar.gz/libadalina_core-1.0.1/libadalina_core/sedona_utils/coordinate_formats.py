from enum import Enum

class EPSGFormats(Enum):
    """
    Enum representing common EPSG formats used in geospatial data.
    """
    EPSG4326 = 4326  # WGS84
    EPSG32632 = 32632  # UTM zone 32N

    @staticmethod
    def from_code(code: int) -> 'EPSGFormats':
        for f in EPSGFormats:
            if f.value == code:
                return f
        raise ValueError(f"No EPSG format found for code {code}")

"""
Default EPSG format used in libadalina.

All DataFrame are converted upon reading and writing to this format.
"""
DEFAULT_EPSG = EPSGFormats.EPSG4326