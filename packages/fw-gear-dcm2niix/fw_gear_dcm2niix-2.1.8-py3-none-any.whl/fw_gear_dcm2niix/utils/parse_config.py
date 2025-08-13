"""Function to parse gear config into gear args."""

import logging
import os
import pprint
import re
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext

from fw_gear_dcm2niix.utils.metadata import rename_infile

FILETYPES = {
    "dicom": [".dcm", ".dcm.zip", ".dicom.zip", ".dicom"],
    "parrec": [".parrec.zip", ".par-rec.zip", ".par"],
}


log = logging.getLogger(__name__)


def generate_prep_args(gear_context: GearToolkitContext) -> dict:
    """Generate gear arguments for the 'prepare' stage.

    Args:
        gear_context: Context and config needed to run gear

    Returns:
        dict: Gear arguments for the 'prepare' stage
    """
    log.info("%s", 100 * "-")
    log.info("Preparing arguments for gear stage >> prepare")

    infile = gear_context.get_input_path("dcm2niix_input")
    try:
        with open(infile, "r", encoding="utf-8") as f:
            log.debug("%s opened from dcm2niix_input.", f)

    except FileNotFoundError:
        # Path separation in filename may cause downloaded filename to be altered
        filename = (
            gear_context.config_json.get("inputs", {})
            .get("dcm2niix_input", {})
            .get("location", {})
            .get("name")
        )
        try:
            if len(filename.split("/")) > 1:
                infile = f"/flywheel/v0/input/dcm2niix_input/{filename.split('/')[-1]}"

                with open(infile, "r", encoding="utf-8"):
                    log.debug("%s opened from path separated dcm2niix_input.", infile)
        except (FileNotFoundError, AttributeError):
            log.info(
                "Path to dcm2niix_input: %s",
                gear_context.get_input_path("dcm2niix_input"),
            )
            log.error(
                "Filename not understood from Gear context. Unable to open dcm2niix_input. Exiting."
            )
            os.sys.exit(1)

    except UnicodeEncodeError:
        log.info(
            "Path to dcm2niix_input: %s",
            gear_context.get_input_path("dcm2niix_input"),
        )
        log.error(
            "Filename not understood from Gear context. Unable to open dcm2niix_input. Exiting."
        )
        os.sys.exit(1)

    # Validate that this is a DICOM file, DICOM archive, PARREC zip, or PAR file.
    file_type = (
        gear_context.get_input("dcm2niix_input").get("object", {}).get("type", None)
    )
    validate_input_filetype(file_type, infile)

    # Rename infile if outfile is using infile folder
    if (
        bool(re.search("%f", gear_context.config["filename"]))
        and gear_context.config["sanitize_filename"]
    ):
        infile = rename_infile(Path(infile))

    gear_args = {
        "infile": infile,
        "work_dir": gear_context.work_dir,
        "remove_incomplete_volumes": gear_context.config["remove_incomplete_volumes"],
        "decompress_dicoms": gear_context.config["decompress_dicoms"],
        "rec_infile": None,
    }

    if gear_context.get_input_path("rec_file_input"):
        rec_infile = Path(gear_context.get_input_path("rec_file_input"))
        if not rec_infile.is_file():
            log.error(
                "Configuration for rec_infile_input is not a valid path. Exiting."
            )
            os.sys.exit(1)
        # else:
        gear_args["rec_infile"] = str(rec_infile)

    gear_args_formatted = pprint.pformat(gear_args)
    log.info("Prepared gear stage arguments: \n\n%s\n", gear_args_formatted)

    return gear_args


def validate_input_filetype(file_type: str, infile: str):
    """Checks that input filetype is DICOM or parrec/par, exits if invalid type.

    This validation method currently depends first on the `file.type` set in
    Flywheel and if not set checks for known DICOM/parrec suffixes. This check
    does NOT currently validate whether the `file.type`/suffix matches the file
    contents (doesn't check to make sure it's a valid DICOM file).

    Args:
        file_type: File type from Flywheel file.type
        infile: Path to input file
    """
    if not file_type:
        # If file type is not set in Flywheel, try to determine by suffix
        for ft, suffixes in FILETYPES.items():
            if any([infile.lower().endswith(suffix) for suffix in suffixes]):
                file_type = ft
                break
    if file_type in ["dicom", "parrec"]:
        log.info(f"Input file type: {file_type}")
    else:
        log.error(f"Input file type {file_type} not supported.")
        os.sys.exit(1)


def generate_dcm2niix_args(gear_context: GearToolkitContext) -> dict:
    """Generate gear arguments for the 'dcm2niix' stage.

    Args:
        gear_context: Context and config needed to run gear

    Returns:
        dict: Gear arguments for the 'dcm2niix' stage
    """
    log.info("%s", 100 * "-")
    log.info("Preparing arguments for gear stage >> dcm2niix")

    filename = gear_context.config["filename"]
    # If filename is "%dicom%", use the dicom filename (without extension) as
    # output filename:
    if filename == "%dicom%":
        filename = Path(gear_context.get_input_path("dcm2niix_input")).stem
        # if there is still a ".dcm" extension, remove it:
        filename = filename.removesuffix(".dcm")
    filename = filename.replace(" ", "_")

    comment = gear_context.config["comment"]
    if len(comment) > 24:
        log.error(
            "The comment configuration option must be less than 25 characters. "
            "You have entered %d characters. Please edit and resubmit Gear. "
            "Exiting.",
            len(comment),
        )
        os.sys.exit(1)

    gear_args = {
        "anonymize_bids": gear_context.config["anonymize_bids"],
        "comment": comment,
        "compress_images": gear_context.config["compress_images"],
        "compression_level": gear_context.config["compression_level"],
        "convert_only_series": gear_context.config["convert_only_series"],
        "crop": gear_context.config["crop"],
        "filename": filename,
        "ignore_derived": gear_context.config["ignore_derived"],
        "ignore_errors": gear_context.config["ignore_errors"],
        "lossless_scaling": gear_context.config["lossless_scaling"],
        "merge2d": gear_context.config["merge2d"],
        "output_nrrd": gear_context.config["output_nrrd"],
        "philips_scaling": gear_context.config["philips_scaling"],
        "single_file_mode": gear_context.config["single_file_mode"],
        "text_notes_private": gear_context.config["text_notes_private"],
        "verbose": gear_context.config["dcm2niix_verbose"],
    }

    gear_args_formatted = pprint.pformat(gear_args)
    log.info("Prepared gear stage arguments: \n\n%s\n", gear_args_formatted)

    return gear_args


def generate_resolve_args(gear_context: GearToolkitContext) -> dict:  # noqa: PLR0912
    """Generate gear arguments for the 'resolve' stage.

    Args:
        gear_context: Context and config needed to run gear

    Returns:
        dict: Gear arguments for the 'resolve' stage
    """
    log.info("%s", 100 * "-")
    log.info("Preparing arguments for gear stage >> resolve")

    gear_args = {
        "ignore_errors": gear_context.config["ignore_errors"],
        "bids_sidecar": gear_context.config["bids_sidecar"],
        "retain_sidecar": True,
        "retain_nifti": True,
        "output_nrrd": gear_context.config["output_nrrd"],
        "classification": None,
        "modality": None,
    }

    if gear_context.config["bids_sidecar"] == "o" or gear_context.config["output_nrrd"]:
        gear_args["retain_nifti"] = False

    if gear_context.config["bids_sidecar"] == "n":
        gear_args["retain_sidecar"] = False

    # The save_sidecar_as_metadata arg exists to retain compatibility with
    # the previous Flywheel BIDS workflow, which depends on the sidecar info
    # being saved in file.info.
    if gear_context.config["save_sidecar_as_metadata"] == "y":
        # BIDS will ignore JSON sidecar. Sidecar will be stored as metadata.
        gear_args["save_sidecar_as_metadata"] = True
    elif gear_context.config["save_sidecar_as_metadata"] == "n":
        # Default, expected behavior. BIDS will utilize JSON sidecar.
        gear_args["save_sidecar_as_metadata"] = False
    else:
        # If arg not set, check to see if the project has old style BIDS metadata
        container_id = gear_context.destination["id"]
        container = gear_context.client.get(container_id)
        project_id = container.parents["project"]
        project = gear_context.client.get(project_id)
        if "BIDS" in project.info:
            if "Acknowledgements" in project.info["BIDS"]:
                # Curated the old way
                log.info(
                    "Parent project identified as utilizing older BIDS "
                    "curation workflow. Sidecar info will be stored in "
                    "file.info for compatibility."
                )
                gear_args["save_sidecar_as_metadata"] = True
            else:
                log.info(
                    "Parent project identified as utilizing current BIDS "
                    "workflow. JSON sidecar info will not be saved as metadata."
                )
                gear_args["save_sidecar_as_metadata"] = False
        else:
            log.info(
                "Parent project was not found to have BIDS info. "
                "JSON sidecar info will not be saved as metadata."
            )
            gear_args["save_sidecar_as_metadata"] = False

    try:
        classification = (
            gear_context.config_json.get("inputs", {})
            .get("dcm2niix_input", {})
            .get("object", {})
            .get("classification")
        )
        # If modality is set and classification is not set, classification returned as {'Custom':[]}
        # If modality and classification are not set, classification returned as {}
        if classification not in ({}, {"Custom": []}):
            gear_args["classification"] = classification
    except KeyError:
        log.info("Cannot determine classification from configuration.")

    try:
        gear_args["modality"] = (
            gear_context.config_json.get("inputs", {})
            .get("dcm2niix_input", {})
            .get("object", {})
            .get("modality")
        )
    except KeyError:
        log.info("Cannot determine modality from configuration.")

    tag = gear_context.config.get("tag", "")
    if tag != "":
        gear_args["tag"] = tag

    gear_args_formatted = pprint.pformat(gear_args)
    log.info("Prepared gear stage arguments: \n\n%s\n", gear_args_formatted)

    # bids_sidecar is useful to have logged for debugging, but doesn't need
    # to be passed to the actual resolve stage.
    del gear_args["bids_sidecar"]

    return gear_args
