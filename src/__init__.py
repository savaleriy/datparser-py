"""
ESRP Spectrum Analyzer Trace export file format parser.

A module for parsing ESRP spectrum analyzer trace export files with
improved architecture and Pythonic practices.
"""

from .datparser import (
    TraceData,
    Trace,
    Scan,
    ESRPParser,
    ESRPFile,
)

__all__ = [
    "TraceData",
    "Trace",
    "Scan",
    "ESRPParser",
    "ESRPFile",
    "__version__",
]


def __version__():
    """Return the package version."""
    try:
        from importlib.metadata import version

        return version("datparser")
    except ImportError:
        return "0.1.0"  # Fallback version
