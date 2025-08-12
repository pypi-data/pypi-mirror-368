import copy
import csv
import json
import pathlib
from dataclasses import asdict

from comet_ice_sublimation.model_input.sublimation_model_input import (
    SublimationModelInput,
)
from comet_ice_sublimation.model_output.sublimation_model_output import (
    SublimationModelResult,
)
from comet_ice_sublimation.parse_arguments import ModelOutputStorageFormat


def save_model(
    smi: SublimationModelInput,
    smr: SublimationModelResult,
    output_path: pathlib.Path,
    out_format: ModelOutputStorageFormat,
) -> None:
    out_dict = {**asdict(smi), **asdict(smr)}

    # we don't need to save this
    out_dict.pop("return_profile")

    if out_format == ModelOutputStorageFormat.json:
        _save_model_json(smi=smi, smr=smr, output_path=output_path)
    else:
        if (
            smr.latitudes_rad is not None
            or smr.zs is not None
            or smr.temps_K is not None
        ):
            print(
                "Warning: writing to csv with temperature profile information! Consider using json instead."
            )
        _save_model_csv(smi=smi, smr=smr, output_path=output_path)


def _save_model_json(
    smi: SublimationModelInput, smr: SublimationModelResult, output_path: pathlib.Path
) -> None:

    smr_cp = copy.deepcopy(smr)
    if smr_cp.latitudes_rad is not None:
        smr_cp.latitudes_rad = smr_cp.latitudes_rad.tolist()
    if smr_cp.zs is not None:
        smr_cp.zs = smr_cp.zs.tolist()
    if smr_cp.temps_K is not None:
        smr_cp.temps_K = smr_cp.temps_K.tolist()

    out_dict = {**asdict(smi), **asdict(smr_cp)}

    # we don't need to save this
    out_dict.pop("return_profile")

    with open(output_path, "w") as json_file:
        json.dump(out_dict, json_file)
    return


def _save_model_csv(
    smi: SublimationModelInput, smr: SublimationModelResult, output_path: pathlib.Path
) -> None:

    smr_cp = copy.deepcopy(smr)
    if smr_cp.latitudes_rad is not None:
        smr_cp.latitudes_rad = smr_cp.latitudes_rad.tolist()
    if smr_cp.zs is not None:
        smr_cp.zs = smr_cp.zs.tolist()
    if smr_cp.temps_K is not None:
        smr_cp.temps_K = smr_cp.temps_K.tolist()

    out_dict = {**asdict(smi), **asdict(smr_cp)}

    # we don't need to save this
    out_dict.pop("return_profile")

    fieldnames = list(out_dict.keys())
    with open(output_path, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(out_dict)
    return
