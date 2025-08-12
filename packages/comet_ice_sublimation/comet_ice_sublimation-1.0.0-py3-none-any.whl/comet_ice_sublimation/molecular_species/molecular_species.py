from enum import StrEnum


# supported molecules
class MolecularSpecies(StrEnum):
    h2o = "H2O"
    h2o_ch4 = "H2O_CH4"
    co2 = "CO2"
    co = "CO"

    @classmethod
    def all_species(cls):
        return [x.value for x in cls]
