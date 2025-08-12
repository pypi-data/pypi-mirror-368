from dataclasses import dataclass

import numpy as np


@dataclass
class SublimationModelResult:
    # total average sublimation rate of exposed surface, molecules per cm^2 per second
    z_bar: np.float64
    # log base 10 of above z_bar
    log10_z_bar: np.float64

    latitudes_rad: np.ndarray | None
    zs: np.ndarray | None
    temps_K: np.ndarray | None
