"""
Sintetic Client Library
Python library to interact with Sintetic GeoDB REST services.
"""

from .core import SinteticClient, TemporalResolution, SubcompartmentType,SINTETIC_ENDPOINTS

__version__ = "0.4.0"
__author__ = "Leandro Rocchi"
__email__ = "leandro.rocchi@cnr.it"

# Supply the TemporalResolution enum for temporal resolution options
__all__ = [
    "SinteticClient",
    "TemporalResolution",
    "SubcompartmentType",
    "SINTETIC_ENDPOINTS"
]