import itertools
import logging
import operator

from .heat_of_sublimation_result import *
from ..physical_constants import *


# "Vaporization of Comet Nuclei: Light Curves and Life Times", Cowan & A'Hearn, 1979
# DOI: 10.1007/BF00897085
def heat_of_sublimation_carbon_dioxide(t_K: float) -> HeatOfSublimationResult:

    # generate powers of the temperature
    t_K2, t_K3, t_K4, t_K5, t_K6 = list(
        itertools.accumulate([t_K] * 4, operator.mul, initial=t_K**2)
    )

    # in calories/mole
    latent_heat_of_vaporization = (
        6269.0 + 9.877 * t_K - 0.130997 * t_K2 + 6.2735e-4 * t_K3 - 1.2699e-6 * t_K4
    )
    latent_heat_of_vaporization_prime = (
        9.877 - 0.261994 * t_K + 1.88205e-3 * t_K2 - 5.0796e-6 * t_K3
    )
    # convert to ergs/molecule
    latent_heat_of_vaporization *= cal_per_mol_to_ergs_per_molecule
    latent_heat_of_vaporization_prime *= cal_per_mol_to_ergs_per_molecule

    if t_K <= 20:
        logging.warn("CO2 temperature < 20 K")
        pressure_dynecm2 = 0
        pressure_dynecm2_prime = 0
    else:
        pressure_torr = (
            21.3807649e0
            - 2570.647e0 / t_K
            - 7.78129489e4 / t_K2
            + 4.32506256e6 / t_K3
            - 1.20671368e8 / t_K4
            + 1.34966306e9 / t_K5
        )
        pressure_torr_prime = (
            2570.647e0 / t_K2
            + 1.556258978e5 / t_K3
            - 12.97518768e6 / t_K4
            + 4.82685472e8 / t_K5
            - 6.7483153e9 / t_K6
        )
        pressure_dynecm2 = torr_to_dyne_per_cm2 * 10.0**pressure_torr
        pressure_dynecm2_prime = pressure_torr_prime * pressure_dynecm2

    # atomic mass units to grams
    mass = 44.0 * amu_to_grams

    return HeatOfSublimationResult(
        mass_g=mass,
        latent_heat_of_vaporization=latent_heat_of_vaporization,
        latent_heat_of_vaporization_prime=latent_heat_of_vaporization_prime,
        pressure=pressure_dynecm2,
        pressure_prime=pressure_dynecm2_prime,
    )
