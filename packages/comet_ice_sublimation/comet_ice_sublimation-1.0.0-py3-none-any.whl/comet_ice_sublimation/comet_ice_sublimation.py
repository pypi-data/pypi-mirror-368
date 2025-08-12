#!/usr/bin/env python3

import logging
import sys

import numpy as np

from comet_ice_sublimation.heat_of_sublimation import *
from comet_ice_sublimation.model_input import *
from comet_ice_sublimation.model_output import *
from comet_ice_sublimation.model_runner import *
from comet_ice_sublimation.model_saver.model_saver import save_model
from comet_ice_sublimation.molecular_species import *
from comet_ice_sublimation.parse_arguments import *
from comet_ice_sublimation.surface_geometry import *


def main():
    args = parse_arguments()
    smi = sublimation_model_input_from_args(args=args)
    if smi is None:
        print("No valid input for model! exiting.")
        return 1

    print(f"Model input:\n------------\n{smi}\n------------\n")

    if args.verbosity == 0:
        logging.basicConfig(level="WARNING")
    elif args.verbosity == 1:
        logging.basicConfig(level="INFO")
    else:
        logging.basicConfig(level="DEBUG")

    try:
        smr = run_sublimation_model(smi=smi)
        model_successful = True
        model_err_message = ""
    except Exception as e:
        model_successful = False
        model_err_message = str(e)

    if model_successful == False:
        print(f"Model failed with error message {model_err_message}!")
        return 1

    print(
        f"Results:\nrh (AU): {smi.rh_au:4.2f}\tlog rh (AU): {np.log10(smi.rh_au):6.4f}\tZbar: {smr.z_bar:6.4e}\tZlog: {smr.log10_z_bar:6.4f}"
    )

    if args.output_config is not None:
        save_model(
            smi=smi,
            smr=smr,
            output_path=args.output_config.output_path,
            out_format=args.output_config.output_format,
        )


if __name__ == "__main__":
    sys.exit(main())
