"""The interfaces module.

Temporary resolution to include mvec files in output.
"""

import os
from copy import deepcopy

from nipype.interfaces.base import File, OutputMultiPath, traits
from nipype.interfaces.dcm2nii import (
    Dcm2niix,
    Dcm2niixInputSpec,
    Dcm2niixOutputSpec,
    search_files,
)


class Dcm2niixInputSpecEnhanced(Dcm2niixInputSpec):
    # pylint: disable=too-many-instance-attributes
    """Dcm2niixInputSpecEnhanced class."""

    # Current dcm2niix NiPype interface does not support the merge2d
    merge_imgs = traits.Enum(
        0,
        1,
        2,
        default=2,
        argstr="-m %s",
        desc="merge 2D slices from same series regardless of echo, exposure, etc. "
        "(0=no, 1=yes, 2=auto, default 2)",
    )


class Dcm2niixOutputSpecEnhanced(Dcm2niixOutputSpec):
    """Dcm2niixInputSpecEnhanced class."""

    # Current dcm2niix NiPype interface does not support mvec.
    # Nipype ticket submitted, https://github.com/nipy/nipype/issues/3553
    mvecs = OutputMultiPath(File(exists=True))


class Dcm2niixEnhanced(Dcm2niix):
    # pylint: disable=abstract-method
    """Dcm2niixEnhanced class."""

    input_spec = Dcm2niixInputSpecEnhanced
    output_spec = Dcm2niixOutputSpecEnhanced

    def _format_arg(self, opt, spec, val):
        """Same as parent but without merge_imgs."""
        bools = [
            "bids_format",
            "single_file",
            "verbose",
            "crop",
            "has_private",
            "anon_bids",
            "ignore_deriv",
            "philips_float",
            "to_nrrd",
        ]
        if opt in bools:
            spec = deepcopy(spec)
            if val:
                spec.argstr += " y"
            else:
                spec.argstr += " n"
                val = True
        if opt == "source_names":
            return spec.argstr % (os.path.dirname(val[0]) or ".")
        return super(Dcm2niix, self)._format_arg(opt, spec, val)

    def _parse_files(self, filenames):
        """Adds mvec to filetypes"""
        outfiles, bvals, bvecs, mvecs, bids = [], [], [], [], []
        outtypes = [".bval", ".bvec", ".mvec", ".json", ".txt"]
        if self.inputs.to_nrrd:
            outtypes += [".nrrd", ".nhdr", ".raw.gz"]
        else:
            outtypes += [".nii", ".nii.gz"]
        for filename in filenames:
            # search for relevant files, and sort accordingly
            for fl in search_files(filename, outtypes):
                if (
                    fl.endswith(".nii")
                    or fl.endswith(".gz")
                    or fl.endswith(".nrrd")
                    or fl.endswith(".nhdr")
                ):
                    outfiles.append(fl)
                elif fl.endswith(".bval"):
                    bvals.append(fl)
                elif fl.endswith(".bvec"):
                    bvecs.append(fl)
                elif fl.endswith(".mvec"):
                    mvecs.append(fl)
                elif fl.endswith(".json") or fl.endswith(".txt"):
                    bids.append(fl)
        self.output_files = outfiles
        self.bvecs = bvecs
        self.mvecs = mvecs
        self.bvals = bvals
        self.bids = bids

    def _list_outputs(self):
        """Adds mvecs to output"""
        outputs = self.output_spec().trait_get()
        outputs["converted_files"] = self.output_files
        outputs["bvecs"] = self.bvecs
        outputs["bvals"] = self.bvals
        outputs["mvecs"] = self.mvecs
        outputs["bids"] = self.bids
        return outputs
