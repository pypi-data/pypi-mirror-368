import math
from functools import cache


# "Vaporization of Comet Nuclei: Light Curves and Life Times", Cowan & A'Hearn, 1979
# DOI: 10.1007/BF00897085


# this is purely geometric, depending on only the arctic latitude and the choice of latitude grid
@cache
def average_projection_factor(
    arctic_latitude_rad: float,
    latitude_rad: float,
    sin_lat: float,
    cos_lat: float,
    tan_lat: float,
) -> float:
    """
    Computes the average cosine of incident sunlight at the latitude given by latitude_rad in radians.
    The variable arctic_latitude_rad is the latitude at which the 'arctic circle' of the comet begins -
        by our adopted convention, the latitude above which has permanent sunlight in the northern hemisphere,
        and permanent darkness in the southern hemisphere at latitudes less than -arctic_latitude_rad.
    """

    # The average projection factor represents the average cosine of the angle of incident sunlight on a certain latitude
    # over the course of a day on the comet (one rotation)
    # Average projection factor of 1 means <cos theta> = 1, therefore sunlight normal to the surface all day

    # equation 5 of Cowan & A'Hearn 1979
    if latitude_rad <= -arctic_latitude_rad:
        apf = 0
    elif latitude_rad > arctic_latitude_rad:
        apf = sin_lat * math.cos(arctic_latitude_rad)
    else:
        x1 = (
            math.cos(arctic_latitude_rad)
            * sin_lat
            * math.acos(-tan_lat * (1 / math.tan(arctic_latitude_rad)))
            / math.pi
        )
        x2 = (
            math.sin(arctic_latitude_rad)
            * cos_lat
            * math.sin(math.acos(-tan_lat / math.tan(arctic_latitude_rad)))
            / math.pi
        )
        apf = x1 + x2

    return apf
