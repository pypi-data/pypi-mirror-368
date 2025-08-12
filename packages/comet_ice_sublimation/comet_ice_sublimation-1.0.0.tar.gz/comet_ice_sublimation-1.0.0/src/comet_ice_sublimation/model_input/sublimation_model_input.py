from dataclasses import dataclass

from ..molecular_species import *


@dataclass
class SublimationModelInput:
    species: MolecularSpecies
    visual_albedo: float
    infrared_albedo: float
    rh_au: float
    sub_solar_latitude: float
    num_latitude_gridpoints: int
    t_init_K: float | None
    return_profile: bool

    def __str__(self):
        if self.t_init_K is not None:
            temperature_str = f"{self.t_init_K:6.2f} K"
        else:
            temperature_str = "None"

        return (
            f"Species: {self.species.value}\n"
            + f"Visual albedo:\t\t{self.visual_albedo:>6.2f}\t\tInfrared albedo:\t{self.infrared_albedo:<6.2f}\n"
            + f"Heliocentric distance:\t{self.rh_au:>6.2f} AU\tSubsolar latitude:\t{self.sub_solar_latitude:<6.2f} degrees\n"
            + f"Latitude gridpoints:\t{self.num_latitude_gridpoints:>5d}\t\tInitial temperature:\t{temperature_str:<}"
        )
