from .heat_of_sublimation_water import *
from .heat_of_sublimation_water_methane import *
from .heat_of_sublimation_carbon_dioxide import *
from .heat_of_sublimation_carbon_monoxide import *
from ..molecular_species import *


def heat_of_sublimation(
    species: MolecularSpecies, t_K: float
) -> HeatOfSublimationResult:
    if species == MolecularSpecies.h2o:
        return heat_of_sublimation_water(t_K=t_K)
    elif species == MolecularSpecies.h2o_ch4:
        return heat_of_sublimation_water_methane(t_K=t_K)
    elif species == MolecularSpecies.co2:
        return heat_of_sublimation_carbon_dioxide(t_K=t_K)
    elif species == MolecularSpecies.co:
        return heat_of_sublimation_carbon_monoxide(t_K=t_K)
