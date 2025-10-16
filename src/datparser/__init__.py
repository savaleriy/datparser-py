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

__version__ = "0.1.0"  # Define version as string, not function
__all__ = [
    "TraceData",
    "Trace",
    "Scan",
    "ESRPParser",
    "ESRPFile",
]
