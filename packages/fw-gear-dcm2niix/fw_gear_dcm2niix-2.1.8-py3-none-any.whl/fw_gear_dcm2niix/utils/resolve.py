"""Functions to resolve dcm2niix gear outputs."""

import logging
import os
import shutil

from fw_gear_dcm2niix.utils import metadata

log = logging.getLogger(__name__)


def setup(  # noqa: PLR0913
    output_image_files,
    output_sidecar_files,
    work_dir,
    dcm2niix_input_dir,
    output_dir,
    ignore_errors=False,
    retain_sidecar=False,
    retain_nifti=True,
    output_nrrd=False,
    classification=None,
    modality=None,
    save_sidecar_as_metadata=False,
):
    """Orchestrate resolution of gear, including metadata capture and file retention.

    Args:
        output_image_files (list): The absolute paths to converted image files to resolve.
            Typically, these are NIfTI files, but can be the two files constituting the
            NRRD format (i.e., ".raw" and ".nhdr") or the NRRD format (i.e., ".nrrd").
            Also contains ".bval", ".bvec", and ".mvec" files, if applicable.
        output_sidecar_files (list): The absolute paths to the sidecar files to be
            used as metadata on all files in the output_image_files input list.
        work_dir (str): The absolute path to the output directory of dcm2niix and where
            the metadata file generated is written to.
        dcm2niix_input_dir (str): The absolute path to the input directory to dcm2niix.
        output_dir (str): The absolute path to the output directory of dcm2niix.
        ignore_errors (bool): If true, errors are ignored.
        retain_sidecar (bool): If true, sidecar is retained in final output.
        retain_nifti (bool): If true, NIfTI is retained in final output.
        output_nrrd (bool): If true, export as NRRD instead of NIfTI.
        classification (dict): File classification, typically from gear config.
        modality (str): File modality, typically from gear config.
        save_sidecar_as_metadata (bool): Whether to save sidecar info into file metadata

    Returns:
        metadata_to_save (dict): contents of the .metadata.json file to be saved

    """
    # Ignoring errors configuration option; move all files from work_dir to output_dir
    if ignore_errors is True:
        log.warning("Applying Expert Option (ignore_errors).")

        if output_image_files is not None:
            # Capture metadata
            metadata_to_save = metadata.generate(
                output_image_files,
                output_sidecar_files,
                dcm2niix_input_dir,
                retain_sidecar=True,
                retain_nifti=True,
                output_nrrd=False,
                classification=classification,
                modality=modality,
                save_sidecar_as_metadata=save_sidecar_as_metadata,
            )
        else:
            metadata_to_save = {}

        for item in os.listdir(work_dir):
            item_path = os.path.join(work_dir, item)
            if not os.path.isdir(item_path):
                shutil.move(item_path, output_dir)
                log.info("Moving %s to output directory for upload to Flywheel.", item)

    else:
        # Capture metadata
        # pylint: disable=duplicate-code
        metadata_to_save = metadata.generate(
            output_image_files,
            output_sidecar_files,
            dcm2niix_input_dir,
            retain_sidecar=retain_sidecar,
            retain_nifti=retain_nifti,
            output_nrrd=output_nrrd,
            classification=classification,
            modality=modality,
            save_sidecar_as_metadata=save_sidecar_as_metadata,
        )
        # pylint: enable=duplicate-code

        # Retain gear outputs
        retain_gear_outputs(
            output_image_files,
            output_sidecar_files,
            output_dir,
            retain_sidecar=retain_sidecar,
            retain_nifti=retain_nifti,
            output_nrrd=output_nrrd,
        )

    return metadata_to_save


def retain_gear_outputs(  # noqa: PLR0913
    output_image_files,
    output_sidecar_files,
    output_dir,
    retain_sidecar=True,
    retain_nifti=True,
    output_nrrd=False,
):
    """Move selected gear outputs to the output directory.

    Args:
        output_image_files (list): The absolute paths to converted image files to resolve.
            Typically, these are NIfTI files, but can be the two files constituting the
            NRRD format (i.e., ".raw" and ".nhdr") or the NRRD format (i.e., ".nrrd").
            Also contains ".bval", ".bvec", and ".mvec" files, if applicable.
        output_sidecar_files (list): The absolute paths to the sidecar files to be
            used as metadata on all files in the output_image_files input list.
        output_dir (str): The absolute path to the gear output directory.
        retain_sidecar (bool): If true, sidecar is retained in final output.
        retain_nifti (bool): If true, NIfTI is retained in final output.
        output_nrrd (bool): If true, export as NRRD instead of NIfTI.

    Returns:
        None

    """
    log.info("Resolving gear outputs.")

    if (retain_nifti and output_nrrd) or (
        not retain_nifti and not output_nrrd and not retain_sidecar
    ):
        log.critical(
            "Function arguments retain_nifti and output_nrrd are exclusive. "
            "Gear config logic is broken. Exiting."
        )
        os.sys.exit(1)

    for sidecar in output_sidecar_files:
        # Move bids json sidecar file, if indicated
        if retain_sidecar:
            shutil.move(sidecar, output_dir)
            log.info("Moving %s to output directory.", sidecar)

        # Move data files, if indicated
        # Split sidecar into the "root" name by removing .json suffix
        stem = sidecar.split(".json")[0]
        for file in output_image_files:
            # pylint: disable=duplicate-code
            # Split image name by "root" name from sidecar
            substr = file.split(stem)
            # If the "root" name of sidecar is not a substring of image file
            #   We don't care about this image file.
            if len(substr) < 2:
                continue
            # Get "root" and what's "left" over after splitting of "root" name
            #   from sidecar
            _, left = substr
            # pylint: enable=duplicate-code

            if retain_nifti:
                # If "left" over is simply the extension, this image matches
                #   the current sidecar, move to output.
                if left in [".nii.gz", ".nii", ".bval", ".bvec", ".mvec"]:
                    log.info("Moving %s to output directory.", file)
                    shutil.move(file, output_dir)

            if output_nrrd:
                # If "left" over is simply the extension, this image matches
                #   the current sidecar, move to output.
                if left in [".raw.gz", ".nhdr", ".nrrd"]:
                    log.info("Moving %s to output directory.", file)
                    shutil.move(file, output_dir)

    log.info("Gear outputs resolved.")
