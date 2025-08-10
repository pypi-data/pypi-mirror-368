"""Package for communicating with Leviton Load Data API."""

__all__ = [
    "LEG1_POSITIONS",
    "LEG2_POSITIONS",
    "RMS_VOLTAGE_FACTOR",
    "AuthError",
    "BreakerData",
    "CTData",
    "InvalidAuth",
    "LDATAConnector",
    "LDATAException",
    "PanelData",
    "ParsedData",
    "Residence",
]

from importlib.metadata import PackageNotFoundError, version

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


from .connector import LDATAConnector, Residence
from .const import LEG1_POSITIONS, LEG2_POSITIONS, RMS_VOLTAGE_FACTOR
from .errors import AuthError, InvalidAuth, LDATAException
from .parser import BreakerData, CTData, PanelData, ParsedData
