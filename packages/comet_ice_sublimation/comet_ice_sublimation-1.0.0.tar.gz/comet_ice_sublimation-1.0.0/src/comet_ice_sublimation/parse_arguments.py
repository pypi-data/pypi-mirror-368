import argparse
import pathlib
from dataclasses import dataclass
from enum import StrEnum

from comet_ice_sublimation.model_input import *
from comet_ice_sublimation.molecular_species import *


class ModelOutputStorageFormat(StrEnum):
    csv = "csv"
    json = "json"


@dataclass
class ModelOutputConfig:
    output_path: pathlib.Path
    output_format: ModelOutputStorageFormat


@dataclass
class SublimationModelArguments:
    species: MolecularSpecies
    visual_albedo: float
    infrared_albedo: float
    heliocentric_distance: float
    sub_solar_latitude: float
    num_latitude_gridpoints: int
    initial_temperature_kelvin: float | None
    return_profile: bool
    output_config: ModelOutputConfig | None
    verbosity: int


description1 = (
    "This program calculates the average sublimation per unit area for a rapidly rotating cometary"
    " nucleus. For a sufficiently rapid rotation, or equivalently for sufficiently high thermal inertia,"
    " a parallel of latitude is an isotherm and this is assumed by the program."
)

description2 = (
    "The method integrates an energy balance equation with the Newton-Raphson method"
    " to derive an equilibrium temperature.  Simpson's rule is used to integrate over"
    " latitude."
)


def parse_arguments() -> SublimationModelArguments:
    parser = argparse.ArgumentParser(
        description="\n\n".join([description1, description2]),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "species",
        choices=MolecularSpecies.all_species(),
        help="Ice species to consider.",
    )
    parser.add_argument(
        "--Av",
        metavar="visual_albedo",
        type=float,
        required=True,
    )
    parser.add_argument(
        "--Air",
        metavar="infrared_albedo",
        type=float,
        required=True,
    )
    parser.add_argument(
        "--rh",
        metavar="heliocentric_distance",
        type=float,
        required=True,
    )
    parser.add_argument(
        "--ssl",
        metavar="sub_solar_latitude",
        type=float,
        required=True,
    )
    parser.add_argument(
        "--nlat", metavar="n", type=int, default=181, help="Number of latitude steps"
    )
    parser.add_argument(
        "--temp",
        metavar="temperature",
        type=float,
        default=None,
        help="Not passing a starting temperature will default to a species dependent starting value:\n"
        "H2O: 190 K\n"
        "H2O-CH4: 190 K\n"
        "CO2: 100 K\n"
        "CO: 60 K\n",
    )
    parser.add_argument(
        "--profiles",
        type=bool,
        default=False,
        help="Return temperatures and sublimation rates as function of latitude",
    )
    parser.add_argument(
        "-o", metavar="filename", dest="filename", help="Save results to this file name"
    )
    parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="output file format"
    )
    parser.add_argument(
        "--verbosity",
        "-v",
        metavar="verbosity",
        type=int,
        default=0,
        help="By default (verbosity = 0), only the final result will be displayed in stdout."
        " A verbosity of 1 will output the logger messages as well.",
    )

    args = parser.parse_args()

    output_config: ModelOutputConfig | None = None
    if args.filename is not None:
        output_config = ModelOutputConfig(
            output_path=pathlib.Path(args.filename), output_format=args.format
        )

    return SublimationModelArguments(
        species=MolecularSpecies(args.species),
        visual_albedo=args.Av,
        infrared_albedo=args.Air,
        heliocentric_distance=abs(args.rh),
        sub_solar_latitude=args.ssl,
        num_latitude_gridpoints=args.nlat,
        initial_temperature_kelvin=args.temp,
        return_profile=args.profiles,
        output_config=output_config,
        verbosity=args.verbosity,
    )


def sublimation_model_input_from_args(
    args: SublimationModelArguments,
) -> SublimationModelInput | None:

    smi = SublimationModelInput(
        species=args.species,
        visual_albedo=args.visual_albedo,
        infrared_albedo=args.infrared_albedo,
        rh_au=abs(args.heliocentric_distance),
        sub_solar_latitude=args.sub_solar_latitude,
        num_latitude_gridpoints=args.num_latitude_gridpoints,
        t_init_K=args.initial_temperature_kelvin,
        return_profile=args.return_profile,
    )

    if smi.visual_albedo < 0.0 or smi.visual_albedo > 1.0:
        print(f"Visual albedo must be between 0 and 1, inclusive!")
        return None
    if smi.infrared_albedo < 0.0 or smi.infrared_albedo > 1.0:
        print(f"Infrared albedo must be between 0 and 1, inclusive!")
        return None
    if smi.sub_solar_latitude > 90.0 or smi.sub_solar_latitude < -90.0:
        print(f"Sub-solar latitude must be between -90 degrees and +90 degrees!")
        return None

    # fill in starting temperature based on the selected species
    if smi.t_init_K is None:
        smi.t_init_K = get_starting_temperature(smi.species)

    return smi
