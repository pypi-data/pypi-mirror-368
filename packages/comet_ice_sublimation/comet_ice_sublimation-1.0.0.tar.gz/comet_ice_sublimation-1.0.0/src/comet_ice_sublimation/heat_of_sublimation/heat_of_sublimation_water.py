from .heat_of_sublimation_result import *
from ..physical_constants import *


# "Vaporization of Comet Nuclei: Light Curves and Life Times", Cowan & A'Hearn, 1979
# DOI: 10.1007/BF00897085
def heat_of_sublimation_water(t_K: float) -> HeatOfSublimationResult:
    """
    Calculates the latent heat of sublimation and the vapor pressure of the
    solid for given ice, and the derivatives thereof.

    from Marti & Mauersberger (1993 GRL 20, 363), valid between 170K and 250K
    DOI: 10.1029/93GL00105
    """

    t_K2 = t_K**2

    # in calories/mole
    latent_heat_of_vaporization = 12420.0 - 4.8 * t_K
    latent_heat_of_vaporization_prime = -4.8
    # convert to ergs/molecule
    latent_heat_of_vaporization *= cal_per_mol_to_ergs_per_molecule
    latent_heat_of_vaporization_prime *= cal_per_mol_to_ergs_per_molecule

    pressure_pascals = -2663.5 / t_K + 12.537
    pressure_dynecm2 = 10.0 * 10.0**pressure_pascals
    pressure_dynecm2_prime = (2663.5 / t_K2) * pressure_dynecm2

    # atomic mass units to grams
    mass = 18.0 * amu_to_grams

    return HeatOfSublimationResult(
        mass_g=mass,
        latent_heat_of_vaporization=latent_heat_of_vaporization,
        latent_heat_of_vaporization_prime=latent_heat_of_vaporization_prime,
        pressure=pressure_dynecm2,
        pressure_prime=pressure_dynecm2_prime,
    )
