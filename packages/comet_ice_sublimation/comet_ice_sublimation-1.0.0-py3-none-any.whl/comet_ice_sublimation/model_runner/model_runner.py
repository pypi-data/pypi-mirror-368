import logging
import math

from comet_ice_sublimation.comet_ice_sublimation import *
from comet_ice_sublimation.energy_balance.energy_balance import *
from comet_ice_sublimation.model_input.sublimation_model_input import *
from comet_ice_sublimation.model_output.sublimation_model_output import *
from comet_ice_sublimation.surface_geometry.surface_geometry import *


def run_sublimation_model(smi: SublimationModelInput) -> SublimationModelResult:

    # sub_solar_latitude = 0  ---> equator along sun-comet axis, north pole of comet perpendicular to sun-comet axis
    # sub_solar_latitude = 90 ---> equator perpendicular to sun-comet axis, north pole of comet pointed at sun

    # marks the 'arctic circle' latitude (in radians) of the comet:
    #  above this latitude, permanent sunlight during a rotation
    #  below this negative latitude, permanent darkness during a rotation
    arctic_latitude_rad = (90 - smi.sub_solar_latitude) * math.pi / 180

    # We are using a spherical coordinate system with the z-axis rotated so that the sub_solar_latitude falls on the sun-comet axis.
    # Positive latitudes are taken by convention to be in the hemisphere pointed toward the sun.

    # sample the latitudes by creating a linear space [-1, 1] and mapping that to latitudes
    # this samples the equator more than the poles
    sin_latitudes, delta_sin_latitude = np.linspace(
        start=-1, stop=1, num=smi.num_latitude_gridpoints, endpoint=True, retstep=True
    )
    # latitudes in radians
    latitudes = np.arcsin(sin_latitudes)
    cos_latitudes = np.cos(latitudes)
    tan_latitudes = np.tan(latitudes)

    # see average_projection_factor function for explanation of these values
    average_projection_factors = [
        average_projection_factor(arctic_latitude_rad, lat, sin_lat, cos_lat, tan_lat)
        for lat, sin_lat, cos_lat, tan_lat in zip(
            latitudes, sin_latitudes, cos_latitudes, tan_latitudes
        )
    ]

    t_init_K = smi.t_init_K
    assert t_init_K is not None

    sublimation_results = [
        converge_energy_balance(
            smi=smi, average_projection_factor=apf, t_init_K=t_init_K
        )
        for apf in average_projection_factors
    ]

    # sublimation rate as a function of latitude
    z = np.array([x.z for x in sublimation_results])

    temperatures = np.array([x.t_K for x in sublimation_results])

    for l, ti in zip(latitudes, temperatures):
        logging.info(f"Lat: {l*180/np.pi:6.4f}\tT (K): {ti:6.4f}")

    # integrate over the sine-of-latitude space from -1 to 1 - so divide by the length of the interval, 2,
    # for the average value
    zbar = np.float64(np.trapezoid(z, dx=np.float64(delta_sin_latitude)) / 2.0)
    zlog = np.log10(zbar)

    # Set these to None if the user isn't interested in them
    if not smi.return_profile:
        latitudes = None
        z = None
        temperatures = None

    return SublimationModelResult(
        z_bar=zbar,
        log10_z_bar=zlog,
        latitudes_rad=latitudes,
        zs=z,
        temps_K=temperatures,
    )
