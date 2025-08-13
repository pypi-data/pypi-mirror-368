# -*- coding: utf-8 -*-
"""Generate file metadata from dcm2niix output."""

import json
import logging
import os
from pathlib import Path

from flywheel_gear_toolkit.utils.file import sanitize_filename
from fw_gear_file_metadata_importer.files.dicom import (
    get_dicom_header,
    preprocess_input,
)
from pydicom.misc import is_dicom

log = logging.getLogger(__name__)


def generate(  # noqa: PLR0913
    output_image_files,
    output_sidecar_files,
    dcm2niix_input_dir=None,
    retain_sidecar=False,
    retain_nifti=True,
    output_nrrd=False,
    classification=None,
    modality=None,
    save_sidecar_as_metadata=False,
):
    """Generate file metadata from dcm2niix output.

        Using the BIDS json sidecar output from dcm2niix, generate file metadata
        (file.info.header.dicom) and set the classification (file.measurements)
        from the input configuration settings.

    Args:
        output_image_files (list): The absolute paths to converted image files to resolve.
            Typically these are NIfTI files, but can be the two files constituting the
            NRRD format (i.e., ".raw" and ".nhdr") or the NRRD format (i.e., ".nrrd").
            Also contains ".bval", ".bvec", and ".mvec" files, if applicable.
        output_sidecar_files (list): The absolute paths to the sidecar files to be
            used as metadata on all files in the output_image_files input list.
        dcm2niix_input_dir (str): The absolute path to a set of dicoms as input
            to dcm2niix.
        retain_sidecar (bool): If true, sidecar is retained in final output.
        retain_nifti (bool): If true, nifti is retained in final output.
        output_nrrd (bool): If true, export as NRRD instead of NIfTI.
        classification (dict): File classification, typically from gear config.
        modality (str): File modality, typically from gear config.
        save_sidecar_as_metadata (bool): Whether to save sidecar info into file metadata

    Returns:
        metadata (dict): The absolute path to the metadata file generated.

    """
    # pylint: disable=duplicate-code
    metadata = capture(
        output_image_files,
        output_sidecar_files,
        dcm2niix_input_dir=dcm2niix_input_dir,
        retain_sidecar=retain_sidecar,
        retain_nifti=retain_nifti,
        output_nrrd=output_nrrd,
        classification=classification,
        modality=modality,
        save_sidecar_as_metadata=save_sidecar_as_metadata,
    )
    # pylint: enable=duplicate-code

    log.info("Metadata generation completed successfully.")

    return metadata


def capture(  # noqa: PLR0913, PLR0912, PLR0915
    output_image_files,
    output_sidecar_files,
    dcm2niix_input_dir=None,
    retain_sidecar=True,
    retain_nifti=True,
    output_nrrd=False,
    classification=None,
    modality=None,
    save_sidecar_as_metadata=False,
):
    """Capture file metadata for each dcm2niix output.

        Using the BIDS json sidecar output from dcm2niix, generate file metadata
        (file.info.header.dicom) and set the classification (file.measurements)
        from the input configuration settings.

    Args:
        output_image_files (list): The absolute paths to converted image files to resolve.
            Typically these are NIfTI files, but can be the two files constituting the
            NRRD format (i.e., ".raw" and ".nhdr") or the NRRD format (i.e., ".nrrd").
            Also contains ".bval", ".bvec", and ".mvec" files, if applicable.
        output_sidecar_files (list): The absolute paths to the sidecar files to be
            used as metadata on all files in the output_image_files input list.
        work_dir (str): The absolute path to the output directory of dcm2niix and where
            the metadata file generated is written to.
        dcm2niix_input_dir (str): The absolute path to a set of dicoms as input
            to dcm2niix.
        retain_sidecar (bool): If true, sidecar is retained in final output.
        retain_nifti (bool): If true, nifti is retained in final output.
        output_nrrd (bool): If true, export as NRRD instead of NIfTI.
        classification (dict): File classification, typically from gear config.
        modality (str): File modality, typically from gear config.
        save_sidecar_as_metadata (bool): Whether to save sidecar info into file metadata

    Returns:
        metadata (dict): Structured metadata information for a given file set.
    """
    log.info("Capturing metadata.")

    if (retain_nifti and output_nrrd) or (
        not retain_nifti and not output_nrrd and not retain_sidecar
    ):
        # pylint: disable=duplicate-code
        log.critical(
            "Function arguments retain_nifti and output_nrrd are exclusive. "
            "Gear config logic is broken. Exiting."
        )
        os.sys.exit(1)

    capture_metadata = []

    # Collate metadata from dicom header and from the associated bids sidecar

    for sidecar in output_sidecar_files:
        with open(sidecar, encoding="utf-8") as sidecar_file:
            sidecar_info = json.load(sidecar_file, strict=False)

            # Capture the fields required to select a single DICOM for metadata
            try:
                series_description = sidecar_info["SeriesDescription"]
            except KeyError:
                series_description = ""
            try:
                series_number = str(sidecar_info["SeriesNumber"])
            except KeyError:
                series_number = ""

            # Retain the modality set in the config; otherwise, replace with sidecar
            # captured modality determined via dcm2niix and if neither modality set
            # in the config or sidecar, then set modality to MR.
            if (modality is None) and ("Modality" in sidecar_info):
                modality = sidecar_info["Modality"]

        # Using the unique set of SeriesDescription and SeriesNumber from the DICOM
        # header, capture additional metadata.
        dicom_data = {}
        if dcm2niix_input_dir:
            dicoms = [
                path
                for path in Path(dcm2niix_input_dir).rglob("*")
                if not path.is_dir() and is_dicom(path)
            ]
            if len(dicoms) > 0:
                log.info(f"Capturing additional metadata from {len(dicoms)} DICOMs.")
            for dicom in dicoms:
                file_, _ = preprocess_input(dicom)
                dicom_data = get_dicom_header(file_)
                dicom_series_description = dicom_data.get(
                    "SeriesDescription", ""
                ).replace(" ", "_")
                dicom_series_number = str(dicom_data.get("SeriesNumber"))

                if (dicom_series_description == series_description) and (
                    dicom_series_number == series_number
                ):
                    break
                # else:
                continue

        else:
            log.info("Unable to capture additional metadata from DICOMs.")

        # Remove metadata with None value
        dicom_data = {k: v for k, v in dicom_data.items() if v is not None}
        log.debug("Structured metadata captured.")

        # Maintain functionality for older BIDS workflow:
        if save_sidecar_as_metadata:
            metadata = {"sidecar_info": sidecar_info, "dicom_data": dicom_data}
        else:
            metadata = {"dicom_data": dicom_data}

        # Apply collated metadata to all associated files

        # Sidecar file
        filedata = create_file_metadata(
            sidecar, "source code", classification, metadata, modality, retain_sidecar
        )
        if filedata is not None:
            capture_metadata.append(filedata)

        # Data files
        # Split sidecar into the "root" name by removing .json suffix
        stem = sidecar.removesuffix(".json")
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
                # NIfTI
                if left in [".nii.gz", ".nii"]:
                    filedata = create_file_metadata(
                        file,
                        "nifti",
                        classification,
                        metadata,
                        modality,
                        retain_sidecar,
                    )
                    capture_metadata.append(filedata)

                # bval, bvec, and mvec:
                elif left in [".bval", ".bvec", ".mvec"]:
                    # (left[1:] removes the initial "." from the string)
                    filedata = create_file_metadata(
                        file,
                        left[1:],
                        classification,
                        metadata,
                        modality,
                        retain_sidecar,
                    )
                    capture_metadata.append(filedata)

            if output_nrrd:
                # NRRD
                if left in [".raw.gz", ".nhdr", ".nrrd"]:
                    filedata = create_file_metadata(
                        file, "nrrd", classification, metadata, modality, retain_sidecar
                    )
                    capture_metadata.append(filedata)

    # If modality is not set, remove modality and classification from the metadata file
    if modality is None:
        for file in capture_metadata:
            file.pop("modality")
            file.pop("classification")

    # If classification is not set, remove classification from the metadata file
    if classification is None:
        for file in capture_metadata:
            try:
                file.pop("classification")
            except KeyError:
                continue

    # Collate the metadata and write to file
    metadata = {"acquisition": {"files": capture_metadata}}

    return metadata


def dicom_metadata_extraction(dicom_header):  # noqa: PLR0912, PLR0915
    """Extract metadata from a dicom file header.

    Args:
        dicom_header (pydicom.dataset.FileDataset): A PyDicom header of a DICOM file.

    Returns:
        dicom_data (dict): Extracted dicom headers with their values.

    """
    dicom_data = {}

    # The time in seconds needed to run the prescribed pulse sequence
    try:
        dicom_data["AcquisitionDuration"] = dicom_header.AcquisitionDuration
    except AttributeError:
        dicom_data["AcquisitionDuration"] = None

    if dicom_data["AcquisitionDuration"] is None:
        try:
            dicom_data["AcquisitionDuration"] = dicom_header[0x0018, 0x9073].value
        except (AttributeError, KeyError):
            dicom_data["AcquisitionDuration"] = None

    try:
        dicom_data["NumberOfTemporalPositions"] = dicom_header.NumberOfTemporalPositions
    except AttributeError:
        dicom_data["NumberOfTemporalPositions"] = None

    try:
        dicom_data["Columns"] = dicom_header.Columns
    except AttributeError:
        dicom_data["Columns"] = None

    try:
        dicom_data["Rows"] = dicom_header.Rows
    except AttributeError:
        dicom_data["Rows"] = None

    try:
        dicom_data["SpacingBetweenSlices"] = float(dicom_header.SpacingBetweenSlices)
    except AttributeError:
        dicom_data["SpacingBetweenSlices"] = None

    try:
        dicom_data["PixelSpacing"] = [
            float(dicom_header.PixelSpacing[0]),
            float(dicom_header.PixelSpacing[1]),
        ]
    except AttributeError:
        dicom_data["PixelSpacing"] = None

    try:
        dicom_data["PercentPhaseFieldOfView"] = dicom_header.PercentPhaseFieldOfView
    except AttributeError:
        dicom_data["PercentPhaseFieldOfView"] = None

    try:
        dicom_data["PercentSampling"] = dicom_header.PercentSampling
    except AttributeError:
        dicom_data["PercentSampling"] = None

    try:
        dicom_data["InPlanePhaseEncodingDirection"] = (
            dicom_header.InPlanePhaseEncodingDirection
        )
    except AttributeError:
        dicom_data["InPlanePhaseEncodingDirection"] = None

    try:
        dicom_data["AcquisitionMatrix"] = dicom_header.AcquisitionMatrix
    except AttributeError:
        dicom_data["AcquisitionMatrix"] = None

    try:
        dicom_data["NumberOfEchos"] = dicom_header[0x2001, 0x1014].value
    except (AttributeError, KeyError):
        dicom_data["NumberOfEchos"] = None

    try:
        dicom_data["NumberOfSlices"] = dicom_header[0x2001, 0x1018].value
    except (AttributeError, KeyError):
        dicom_data["NumberOfSlices"] = None

    try:
        dicom_data["PrepulseDelay"] = dicom_header[0x2001, 0x101B].value
    except (AttributeError, KeyError):
        dicom_data["PrepulseDelay"] = None

    try:
        dicom_data["PrepulseType"] = dicom_header[0x2001, 0x101C].value
    except (AttributeError, KeyError):
        dicom_data["PrepulseType"] = None

    try:
        dicom_data["SliceOrientation"] = dicom_header[0x2001, 0x100B].value
    except (AttributeError, KeyError):
        dicom_data["SliceOrientation"] = None

    try:
        dicom_data["ScanningTechnique"] = dicom_header[0x2001, 0x1020].value
    except (AttributeError, KeyError):
        dicom_data["ScanningTechnique"] = None

    try:
        dicom_data["ScanType"] = dicom_header[0x2005, 0x10A1].value
    except (AttributeError, KeyError):
        dicom_data["ScanType"] = None

    return dicom_data


def create_file_metadata(  # noqa: PLR0913
    filename, filetype, classification, metadata, modality, retain_sidecar
):
    """Create a dictionary storing the file metadata."""

    # Return no metadata dictionary for JSON file if bids_sidecar
    # config option is set to 'n' (retain_sidecar is False)
    if retain_sidecar is False and filetype == "source code":
        return None

    filedata = {}
    filedata["name"] = Path(filename).name
    filedata["type"] = filetype
    filedata["classification"] = classification
    if "sidecar_info" in metadata:
        # If true, follow old behavior to be compatible with previous BIDS workflow
        filedata["info"] = metadata["sidecar_info"]
    elif metadata["dicom_data"]:
        filedata["info"] = {"header": {"dicom": metadata["dicom_data"]}}
    filedata["modality"] = modality

    return filedata


def serialize_bytes(obj):
    """Serialize bytes."""
    if isinstance(obj, bytes):
        try:
            obj = obj.decode("utf-8")
        except UnicodeDecodeError:
            try:
                obj = obj.decode("latin-1")
            except TypeError:
                log.critical(
                    "Unable to decode JSON sidecar produced by the dcm2niix tool. Exiting."
                )
                os.sys.exit(1)

    return obj


def rename_infile(infile_path):
    """Sanitize infile name by replacing invalid characters."""
    log.info("Sanitizing filename.")
    f_name = infile_path.name
    sanitized_f_name = sanitize_filename(f_name)
    if sanitized_f_name != f_name:
        log.debug("Renaming filename from %s to %s", f_name, sanitized_f_name)
        os.rename(infile_path.parent / f_name, infile_path.parent / sanitized_f_name)
    return infile_path.parent / sanitized_f_name
