import itertools
import logging
import operator
import sys

from .heat_of_sublimation_result import *
from ..physical_constants import *


# "Vaporization of Comet Nuclei: Light Curves and Life Times", Cowan & A'Hearn, 1979
# DOI: 10.1007/BF00897085
def heat_of_sublimation_carbon_monoxide(t_K: float) -> HeatOfSublimationResult:

    # generate powers of the temperature
    t_K2, t_K3, t_K4, t_K5, t_K6 = list(
        itertools.accumulate([t_K] * 4, operator.mul, initial=t_K**2)
    )

    if t_K > 68.127:
        latent_heat_of_vaporization = 0
        latent_heat_of_vaporization_prime = 0
        pressure_dynecm2 = 0
        pressure_dynecm2_prime = 0
        sys.exit(f"error in CO temp, T = {t_K}")
    elif t_K > 61.544:
        latent_heat_of_vaporization = 1855 + 3.253 * t_K - 0.06833 * t_K2
        latent_heat_of_vaporization_prime = 3.253 - 0.13666 * t_K
        pressure_dynecm2 = (
            16.8655152e0
            - 748.151471e0 / t_K
            - 5.84330795e0 / t_K2
            + 3.93853859e0 / t_K3
        )
        pressure_dynecm2_prime = (
            748.15147e0 / t_K2 + 11.6866159e0 / t_K3 - 11.81561577e0 / t_K4
        )
    elif t_K >= 14.0:
        latent_heat_of_vaporization = (
            1893
            + 7.331 * t_K
            + 0.01096 * t_K2
            - 0.0060658 * t_K3
            + 1.166e-4 * t_K4
            - 7.8957e-7 * t_K5
        )
        latent_heat_of_vaporization_prime = (
            7.331
            + 0.02192 * t_K
            - 0.0181974 * t_K2
            + 4.664e-4 * t_K3
            - 3.94785e-6 * t_K4
        )
        pressure_torr = (
            18.0741183e0
            - 769.842078e0 / t_K
            - 12148.7759e0 / t_K2
            + 2.7350095e5 / t_K3
            - 2.9087467e6 / t_K4
            + 1.20319418e7 / t_K5
        )
        pressure_torr_prime = (
            769.842078e0 / t_K2
            + 24297.5518 / t_K3
            - 820502.85e0 / t_K4
            + 11634986.8e0 / t_K5
            - 60159709.0e0 / t_K6
        )
        pressure_dynecm2 = torr_to_dyne_per_cm2 * 10.0**pressure_torr
        pressure_dynecm2_prime = pressure_torr_prime * pressure_dynecm2
    else:
        logging.warn("CO temperature < 14 K")
        latent_heat_of_vaporization = (
            1893
            + 7.331 * t_K
            + 0.01096 * t_K2
            - 0.0060658 * t_K3
            + 1.166e-4 * t_K4
            - 7.8957e-7 * t_K5
        )
        latent_heat_of_vaporization_prime = (
            7.331
            + 0.02192 * t_K
            - 0.0181974 * t_K2
            + 4.664e-4 * t_K3
            - 3.94785e-6 * t_K4
        )
        pressure_dynecm2 = 0
        pressure_dynecm2_prime = 0

    # convert to ergs/molecule
    latent_heat_of_vaporization *= cal_per_mol_to_ergs_per_molecule
    latent_heat_of_vaporization_prime *= cal_per_mol_to_ergs_per_molecule

    # atomic mass units to grams
    mass = 28.0 * amu_to_grams

    return HeatOfSublimationResult(
        mass_g=mass,
        latent_heat_of_vaporization=latent_heat_of_vaporization,
        latent_heat_of_vaporization_prime=latent_heat_of_vaporization_prime,
        pressure=pressure_dynecm2,
        pressure_prime=pressure_dynecm2_prime,
    )
