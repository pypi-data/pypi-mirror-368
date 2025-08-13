"""The fw_gear_dcm2niix package."""

from importlib.metadata import version

try:
    __version__ = version(__package__)
# pylint: disable-next=bare-except
except:  # noqa: E722
    pass
