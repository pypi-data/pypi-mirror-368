from dataclasses import dataclass
import math

import numpy as np

from comet_ice_sublimation.heat_of_sublimation import *
from comet_ice_sublimation.model_input import *
from comet_ice_sublimation.physical_constants import *


@dataclass
class SublimationRateIterationResult:
    # sublimation rate for the model, molecules per cm^2 per second
    z: float
    # if model converges, the resulting surface temperature
    # if not converged, suggested next temperature to try
    t_K: float
    # if energy balances succeeds, the model is converged and this is set to True
    converged: bool


def converge_energy_balance(
    smi: SublimationModelInput,
    average_projection_factor: float,
    t_init_K: float,
    num_iterations_max: int = 100000,
) -> SublimationRateIterationResult:

    niter = 0
    cur_temp_K = t_init_K

    # compute the incident solar flux
    incident_solar_flux = (
        solar_flux_1au_erg_per_cm2_per_second
        * average_projection_factor
        * (1.0 - smi.visual_albedo)
        / smi.rh_au**2
    )

    if average_projection_factor > 0:
        while niter < num_iterations_max:
            niter += 1
            srir = energy_balance(
                smi=smi,
                incident_solar_flux=incident_solar_flux,
                t_K=cur_temp_K,
            )
            if srir.converged:
                break
            cur_temp_K = srir.t_K
        else:
            raise RuntimeError("Energy balance iteration did not converge.")
    else:
        return SublimationRateIterationResult(z=0.0, t_K=np.nan, converged=True)

    return srir


def energy_balance(
    smi: SublimationModelInput,
    incident_solar_flux: float,
    t_K: float,
) -> SublimationRateIterationResult:
    # Calculate temperature and sublimation rate, and whether or not this converged

    heat_of_sub = heat_of_sublimation(species=smi.species, t_K=t_K)

    root = 1 / math.sqrt(heat_of_sub.mass_g * 2 * math.pi * boltzmann_ergs_per_kelvin)
    root_t = math.sqrt(t_K)

    thermal_radiated_flux = (
        (1 - smi.infrared_albedo)
        * stefan_boltzmann_sigma_ergs_percm2_per_kelvin4
        * t_K**4
    )

    evaporation_loss_flux = (
        root / root_t * heat_of_sub.pressure * heat_of_sub.latent_heat_of_vaporization
    )

    energy_balance_flux = (
        thermal_radiated_flux + evaporation_loss_flux - incident_solar_flux
    )

    z = max(evaporation_loss_flux / heat_of_sub.latent_heat_of_vaporization, 1e-30)

    # temperature derivative
    radiated_flux_derivative = 4 * thermal_radiated_flux / t_K

    x1 = heat_of_sub.pressure_prime * heat_of_sub.latent_heat_of_vaporization
    x2 = heat_of_sub.pressure * heat_of_sub.latent_heat_of_vaporization_prime

    evaporation_flux_derivative = root / root_t * (x1 + x2)
    energy_balance_derivative = radiated_flux_derivative + evaporation_flux_derivative

    dt = math.copysign(
        min(10, abs(energy_balance_flux / energy_balance_derivative / 2)),
        energy_balance_flux / energy_balance_derivative,
    )
    t_K -= dt

    convergence_threshold = 1e-6
    converged = (
        abs(energy_balance_flux / incident_solar_flux) < convergence_threshold
        or abs(energy_balance_flux) < convergence_threshold
    )

    return SublimationRateIterationResult(z=z, t_K=t_K, converged=converged)
