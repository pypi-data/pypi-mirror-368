from .molecular_species import *


_molecular_starting_temperatures = {
    MolecularSpecies.h2o: 190,
    MolecularSpecies.h2o_ch4: 190,
    MolecularSpecies.co2: 100,
    MolecularSpecies.co: 60,
}


def get_starting_temperature(species: MolecularSpecies) -> float:
    return _molecular_starting_temperatures[species]
