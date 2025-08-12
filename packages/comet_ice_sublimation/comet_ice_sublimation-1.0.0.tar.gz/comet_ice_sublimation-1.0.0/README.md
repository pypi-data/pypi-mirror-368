# comet_ice_sublimation
Based on "Vaporization of Comet Nuclei: Light Curves and Life Times", Cowan & A'Hearn, 1979, DOI: 10.1007/BF00897085
Modular rewrite based on https://github.com/Small-Bodies-Node/ice-sublimation for easy inclusion in other projects.

This module uses the rapid rotator model of ice sublimation for comet nuclei where parallels of latitude are isothermal.
Used for estimating molecular sublimation rate per unit area of various ices.
It integrates the energy balance equation to find equilibrium temperatures, then computes sublimation rates as a function of latitude, and reports the total molecular sublimation rate.



# Comet Ice Sublimation Model — Argument Parser
---
- Supports multiple molecular ice species (H₂O, CO₂, CO, mixed ices, etc.).
- Configurable visual and infrared albedos.
- Adjustable latitude grid resolution.
- Optional initial temperature override.
- Returns average sublimation rate or full latitude profiles.
- Output in CSV or JSON format.
- Command-line and Python API usage.
---

## End-user CLI usage

### Manual Installation via Poetry
Clone the repository and install dependencies:
```bash
git clone https://github.com/sjoset/comet-ice-sublimation.git
cd comet-ice-sublimation
poetry install
```

### Manual installation via pip
```
pip install comet_ice_sublimation
```

### Command-line Arguments
| Argument | Required | Description | Default |
|----------|----------|-------------|---------|
| `species` | ✅ | Ice species to consider (choices: see `MolecularSpecies.all_species()`). | — |
| `--Av` | ✅ | Visual albedo (0.0–1.0). | — |
| `--Air` | ✅ | Infrared albedo (0.0–1.0). | — |
| `--rh` | ✅ | Heliocentric distance (AU). | — |
| `--ssl` | ✅ | Sub-solar latitude (degrees, -90 to +90). | — |
| `--nlat` | ❌ | Number of latitude steps. | `181` |
| `--temp` | ❌ | Initial temperature (K). If omitted, uses species defaults: H₂O=190, H₂O–CH₄=190, CO₂=100, CO=60. | `None` |
| `--profiles` | ❌ | Return temperatures & sublimation rates as a function of latitude. | `False` |
| `-o` | ❌ | Output filename for results. | None |
| `--format` | ❌ | Output format (`json` or `csv`). | `json` |
| `-v`, `--verbosity` | ❌ | Verbosity level (0 = final result only, 1 = include logs). | `0` |

### Example Commands
Run a sublimation calculation for water ice at 1 AU:
```bash
comet_ice.py H2O --Av 0.04 --Air 0.5 --rh 1.0 --ssl 0
```

Return full latitude profiles, saving results to CSV:
```bash
comet_ice.py CO2 --Av 0.06 --Air 0.5 --rh 2.0 --ssl 20 --profiles True -o results.csv --format csv
```

---

## Module Integration

You can also import this module and use it in your own projects.

### Construct a SublimationModelInput
To run the sublimation model we need to specify some details of the comet:
- Molecular species of ice
- Visual and infrared albedos (note: not emissivity!) of the surface
- Heliocentric distance
- The sub-solar latitude: For +90, the north pole is pointed at the sun.  For 0, the north pole is perpendicular to the comet-sun axis.
- The number of latitudes to use for integration over the comet surface.
- The initial 'guess' for the temperature of the surface.  Adjust if model fails to converge.

For example, if we wanted a water ice model with visual albedo of 0.05 and infrared albedo of 0.0:
```python
from comet_ice_sublimation.model_input import SublimationModelInput
from comet_ice_sublimation.molecular_species import MolecularSpecies

def make_sublimation_model_input(
    rh_au: float, sub_solar_latitude: float
) -> SublimationModelInput:

    return SublimationModelInput(
        species=MolecularSpecies.h2o,
        visual_albedo=0.05,
        infrared_albedo=0.0,
        rh_au=abs(rh_au),
        sub_solar_latitude=sub_solar_latitude,
        num_latitude_gridpoints=1001,
        t_init_K=180,
    )
```

### Estimate the comet's active area by running the model
If we know the production rate of the given species q in molecules/second, we can compute the active area required to exhibit that level of production.
This function will take the relevant values specified as an astropy Quantity:
```python
import astropy.units as u

from comet_ice_sublimation.model_output import SublimationModelResult
from comet_ice_sublimation.model_runner import run_sublimation_model

def estimate_active_area(
    q: u.Quantity, rh: u.Quantity, sub_solar_latitude: u.Quantity
) -> u.Quantity:

    smi = make_sublimation_model_input(
        rh_au=rh.to_value(u.AU),
        sub_solar_latitude=sub_solar_latitude.to_value(u.degree),
    )

    smr: SublimationModelResult = run_sublimation_model(smi=smi)

    # output z_bar is in mol/cm^2/sec, so we return a quantity in units of area
    return q / (smr.z_bar / (u.cm**2 * u.s))
```
