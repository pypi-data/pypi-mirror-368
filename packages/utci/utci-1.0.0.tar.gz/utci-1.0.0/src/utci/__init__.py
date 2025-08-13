"""
UTCI - Universal Thermal Climate Index

A Python implementation of the Universal Thermal Climate Index (UTCI) algorithm,
translated from the original Fortran code (Version a 0.002, October 2009).

This package provides functions for calculating the UTCI based on:
- Air temperature
- Mean radiant temperature
- Wind speed
- Water vapor pressure or relative humidity

Basic usage:
    >>> from utci import utci_approx, rh_to_vp
    >>> ta = 25.0      # Air temperature in °C
    >>> rh = 60.0      # Relative humidity in %
    >>> tmrt = 30.0    # Mean radiant temperature in °C
    >>> va = 2.0       # Wind speed at 10m in m/s
    >>> vp = rh_to_vp(ta, rh)
    >>> utci = utci_approx(ta, vp, tmrt, va)
    >>> print(f"UTCI: {utci:.1f} °C")
    UTCI: 26.5 °C

For more information, see: https://github.com/marvell/utci
"""

from ._version import __version__
from .utci import es, rh_to_vp, utci_approx

__author__ = "Marvell"
__license__ = "MIT"

# Based on original UTCI Fortran code by Peter Bröde et al. (2009)
# Original work developed under COST Action 730
# Reference: Bröde et al. (2012) Int J Biometeorol 56(3):481-494

__all__ = [
    "utci_approx",
    "rh_to_vp",
    "es",
    "__version__"
]
