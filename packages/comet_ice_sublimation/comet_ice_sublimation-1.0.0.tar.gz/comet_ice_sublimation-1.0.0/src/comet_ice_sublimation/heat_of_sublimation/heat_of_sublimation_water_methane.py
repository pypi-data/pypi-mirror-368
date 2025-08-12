from .heat_of_sublimation_result import *
from ..physical_constants import *


# "Vaporization of Comet Nuclei: Light Curves and Life Times", Cowan & A'Hearn, 1979
# DOI: 10.1007/BF00897085
def heat_of_sublimation_water_methane(t_K: float) -> HeatOfSublimationResult:
    t_K2 = t_K**2

    # in calories/mole
    latent_heat_of_vaporization = 12160.0 + 0.5 * t_K - 0.033 * t_K2
    latent_heat_of_vaporization_prime = 0.5 - 0.066 * t_K
    # convert to ergs/molecule
    latent_heat_of_vaporization *= cal_per_mol_to_ergs_per_molecule
    latent_heat_of_vaporization_prime *= cal_per_mol_to_ergs_per_molecule

    # from Marti & Mauersberger (1993 GRL 20, 363)
    pressure_pascals = -2663.5 / t_K + 12.537
    pressure_dynecm2 = 10.0 * 10.0**pressure_pascals
    pressure_dynecm2_prime = (2663.5 / t_K2) * pressure_dynecm2

    # atomic mass units to grams
    # mass = (18.0 * u.u).to_value(u.g)  # type: ignore
    mass = 18.0 * amu_to_grams

    return HeatOfSublimationResult(
        mass_g=mass,
        latent_heat_of_vaporization=latent_heat_of_vaporization,
        latent_heat_of_vaporization_prime=latent_heat_of_vaporization_prime,
        pressure=pressure_dynecm2,
        pressure_prime=pressure_dynecm2_prime,
    )
