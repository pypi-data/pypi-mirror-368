from dataclasses import dataclass


@dataclass
class HeatOfSublimationResult:
    # mass of molecule, grams
    mass_g: float

    # ergs per molecule
    latent_heat_of_vaporization: float
    latent_heat_of_vaporization_prime: float

    # in dyne/cm2
    pressure: float
    pressure_prime: float
