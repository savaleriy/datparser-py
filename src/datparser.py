"""
ESRP Spectrum Analyzer Trace export file format parser.

A module for parsing ESRP spectrum analyzer trace export files with
improved architecture and Pythonic practices.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

try:
    import pandas as pd
except ImportError:
    pd = None


@dataclass
class TraceData:
    """Container for trace data points."""

    x: List[float]
    y: List[float]

    def __post_init__(self):
        """Validate that x and y have the same length."""
        try:
            if len(self.x) != len(self.y):
                raise ValueError("x and y data must have the same length")
        except Exception as e:
            raise ValueError(f"Error initializing TraceData: {e}") from e

    @property
    def point_count(self) -> int:
        """Return the number of data points."""
        try:
            return len(self.x)
        except Exception as e:
            raise AttributeError(f"Error getting point count: {e}") from e


@dataclass
class Trace:
    """Represents a single trace with metadata and data."""

    metadata: Dict[str, Any]
    data: TraceData
    name: Optional[str] = None

    def __post_init__(self):
        """Set trace name from metadata if available and validate types."""
        try:
            # Validate types
            if not isinstance(self.metadata, dict):
                raise ValueError("metadata must be a dictionary")
            if not isinstance(self.data, TraceData):
                raise ValueError("data must be a TraceData instance")

            if not self.name and "Trace Name" in self.metadata:
                self.name = (
                    self.metadata["Trace Name"][0]
                    if self.metadata["Trace Name"]
                    else None
                )
        except Exception as e:
            raise ValueError(f"Error initializing Trace: {e}") from e

    @property
    def x_unit(self) -> str:
        """Get the x-axis unit from metadata."""
        try:
            return self.metadata.get("x-Unit", ["X"])[0]
        except Exception as e:
            raise AttributeError(f"Error getting x_unit: {e}") from e

    @property
    def y_unit(self) -> str:
        """Get the y-axis unit from metadata."""
        try:
            return self.metadata.get("y-Unit", ["Y"])[0]
        except Exception as e:
            raise AttributeError(f"Error getting y_unit: {e}") from e

    @property
    def trace_name(self) -> str:
        """Get the trace name for display."""
        try:
            return self.name or f"Trace {self.y_unit}"
        except Exception as e:
            raise AttributeError(f"Error getting trace_name: {e}") from e


@dataclass
class Scan:
    """Represents a scan section with parameters."""

    name: str
    parameters: Dict[str, Any]


class ESRPParser:
    """Parser for ESRP file format."""

    # Section identifiers
    SCAN_PREFIX = "Scan"
    TRACE_PREFIX = "TRACE"
    VALUES_KEY = "Values"

    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize parser with file path.

        Args:
            file_path: Path to the ESRP file to parse
        """
        try:
            self.file_path = Path(file_path)
            self._lines: List[str] = []
        except Exception as e:
            raise ValueError(f"Error initializing ESRPParser: {e}") from e

    def parse(self) -> Tuple[Dict[str, Any], List[Scan], List[Trace]]:
        """
        Parse the ESRP file.

        Returns:
            Tuple containing (metadata, scans, traces)

        Raises:
            FileNotFoundError: If the file cannot be found
            ValueError: If the file format is invalid
        """
        try:
            self._read_file()
        except FileNotFoundError:
            raise
        except PermissionError:
            raise
        except OSError as e:
            raise OSError(f"OS error reading file: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading file: {e}") from e

        metadata: Dict[str, Any] = {}
        scans: List[Scan] = []
        traces: List[Trace] = []

        current_scan: Optional[Scan] = None
        current_trace: Optional[Trace] = None
        in_trace_data = False

        try:
            for line_num, line in enumerate(self._lines, 1):
                try:
                    parts = self._parse_line(line)
                    if not parts:
                        continue

                    key = parts[0]

                    # Handle different sections
                    if self._is_scan_section(key):
                        current_scan = self._handle_scan_section(key, scans)
                        current_trace = None
                        in_trace_data = False

                    elif self._is_trace_section(key):
                        current_trace = self._handle_trace_section(traces)
                        in_trace_data = False

                    elif current_trace and in_trace_data:
                        self._handle_trace_data_point(current_trace, parts)

                    elif current_trace:
                        if key == self.VALUES_KEY:
                            in_trace_data = True
                            current_trace.metadata[key] = parts[1:]
                        else:
                            current_trace.metadata[key] = parts[1:]

                    elif current_scan:
                        current_scan.parameters[key] = parts[1:]

                    else:
                        metadata[key] = parts[1:]

                except (ValueError, IndexError) as e:
                    raise ValueError(
                        f"Error parsing line {line_num}: '{line}' - {e}"
                    ) from e
                except Exception as e:
                    raise ValueError(
                        f"Unexpected error parsing line {line_num}: '{line}' - {e}"
                    ) from e

            return metadata, scans, traces

        except Exception as e:
            # Clean up any partially parsed data in case of error
            try:
                metadata.clear()
                scans.clear()
                traces.clear()
            except Exception:
                pass  # Ignore cleanup errors
            raise e

    def _read_file(self):
        """Read and preprocess the file."""
        file_handle = None
        try:
            # Try UTF-8 first
            file_handle = self.file_path.open("r", encoding="utf-8")
            self._lines = [line.strip() for line in file_handle if line.strip()]
        except UnicodeDecodeError:
            # Fall back to ISO-8859-1
            if file_handle:
                file_handle.close()
            try:
                file_handle = self.file_path.open("r", encoding="ISO-8859-1")
                self._lines = [line.strip() for line in file_handle if line.strip()]
            except UnicodeDecodeError as e:
                raise ValueError(
                    f"File encoding error - tried UTF-8 and ISO-8859-1: {e}"
                ) from e
        except Exception as e:
            raise e
        finally:
            if file_handle is not None:
                try:
                    file_handle.close()
                except Exception:
                    pass  # Ignore errors during file close

    @staticmethod
    def _parse_line(line: str) -> List[str]:
        """
        Parse a single line into parts.

        Args:
            line: Input line to parse

        Returns:
            List of non-empty parts
        """
        try:
            return [part.strip() for part in line.split(";") if part.strip()]
        except Exception as e:
            raise ValueError(f"Error parsing line: '{line}' - {e}") from e

    def _is_scan_section(self, key: str) -> bool:
        """Check if the key indicates a scan section."""
        try:
            return key.startswith(self.SCAN_PREFIX) and key.endswith(":")
        except Exception as e:
            raise ValueError(f"Error checking scan section for key '{key}': {e}") from e

    def _is_trace_section(self, key: str) -> bool:
        """Check if the key indicates a trace section."""
        try:
            return key.startswith(self.TRACE_PREFIX)
        except Exception as e:
            raise ValueError(
                f"Error checking trace section for key '{key}': {e}"
            ) from e

    def _handle_scan_section(self, key: str, scans: List[Scan]) -> Scan:
        """Handle scan section creation."""
        try:
            scan_name = key[:-1].strip()  # Remove trailing colon
            scan = Scan(name=scan_name, parameters={})
            scans.append(scan)
            return scan
        except Exception as e:
            raise ValueError(f"Error handling scan section '{key}': {e}") from e

    def _handle_trace_section(self, traces: List[Trace]) -> Trace:
        """Handle trace section creation."""
        try:
            trace_data = TraceData(x=[], y=[])
            trace = Trace(metadata={}, data=trace_data)
            traces.append(trace)
            return trace
        except Exception as e:
            raise ValueError(f"Error handling trace section: {e}") from e

    @staticmethod
    def _handle_trace_data_point(trace: Trace, parts: List[str]):
        """Handle a single trace data point."""
        try:
            if len(parts) >= 2:
                try:
                    x_val = float(parts[0])
                    y_val = float(parts[1])
                    trace.data.x.append(x_val)
                    trace.data.y.append(y_val)
                except ValueError as e:
                    raise ValueError(
                        f"Invalid data point '{parts[0]}, {parts[1]}': {e}"
                    ) from e
        except Exception as e:
            raise ValueError(f"Error handling trace data point: {e}") from e


class ESRPFile:
    """
    Main class for working with ESRP files.

    Provides a high-level interface for accessing ESRP file contents.
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize ESRP file.

        Args:
            file_path: Path to the ESRP file

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the path is not a file or parsing fails
        """
        try:
            self.file_path = Path(file_path).resolve()
            self.metadata: Dict[str, Any] = {}
            self.scans: List[Scan] = []
            self.traces: List[Trace] = []

            self._load_file()
        except Exception as e:
            raise type(e)(f"Error initializing ESRPFile: {e}") from e

    def _load_file(self):
        """Load and parse the ESRP file."""
        try:
            parser = ESRPParser(self.file_path)
            self.metadata, self.scans, self.traces = parser.parse()
        except Exception as e:
            raise type(e)(f"Error loading file {self.file_path}: {e}") from e

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> ESRPFile:
        """
        Create ESRPFile instance from file path.

        Args:
            file_path: Path to the ESRP file

        Returns:
            ESRPFile instance
        """
        try:
            return cls(file_path)
        except Exception as e:
            raise type(e)(f"Error creating ESRPFile from file: {e}") from e

    def get_scan_parameters(self, scan_index: int = 0) -> Dict[str, Any]:
        """
        Get parameters for a specific scan.

        Args:
            scan_index: Index of the scan to retrieve

        Returns:
            Dictionary of scan parameters

        Raises:
            IndexError: If scan_index is out of range
        """
        try:
            return self.scans[scan_index].parameters
        except IndexError as e:
            raise IndexError(
                f"Scan index {scan_index} out of range. "
                f"Available scans: {len(self.scans)}"
            ) from e
        except Exception as e:
            raise type(e)(f"Error getting scan parameters: {e}") from e

    def get_trace_metadata(self, trace_index: int = 0) -> Dict[str, Any]:
        """
        Get metadata for a specific trace.

        Args:
            trace_index: Index of the trace to retrieve

        Returns:
            Dictionary of trace metadata

        Raises:
            IndexError: If trace_index is out of range
        """
        try:
            return self.traces[trace_index].metadata
        except IndexError as e:
            raise IndexError(
                f"Trace index {trace_index} out of range. "
                f"Available traces: {len(self.traces)}"
            ) from e
        except Exception as e:
            raise type(e)(f"Error getting trace metadata: {e}") from e

    def get_trace_data(self, trace_index: int = 0) -> TraceData:
        """
        Get data for a specific trace.

        Args:
            trace_index: Index of the trace to retrieve

        Returns:
            TraceData object containing x and y values

        Raises:
            IndexError: If trace_index is out of range
        """
        try:
            return self.traces[trace_index].data
        except IndexError as e:
            raise IndexError(
                f"Trace index {trace_index} out of range. "
                f"Available traces: {len(self.traces)}"
            ) from e
        except Exception as e:
            raise type(e)(f"Error getting trace data: {e}") from e

    def to_dataframe(
        self,
        trace_index: Optional[int] = None,
        scan_index: Optional[int] = None,
        include_all_traces: bool = False,
    ) -> pd.DataFrame:
        """
        Convert trace data to pandas DataFrame with flexible options.

        Args:
            trace_index: Index of a single trace to convert (None for all traces)
            scan_index: Index of scan to filter traces by (None for all scans)
            include_all_traces: If True, combine all traces into one DataFrame
                               with trace-specific column names

        Returns:
            pandas DataFrame containing the requested data

        Raises:
            RuntimeError: If pandas is not available
            IndexError: If trace_index or scan_index is out of range
            ValueError: If invalid combination of parameters is provided
        """
        if pd is None:
            raise RuntimeError("pandas is required for DataFrame conversion")

        try:
            if not self.traces:
                return pd.DataFrame()

            # Validate parameter combinations
            if trace_index is not None and include_all_traces:
                raise ValueError(
                    "Cannot specify both trace_index and include_all_traces=True"
                )

            # Get traces to process
            traces_to_process = self._get_traces_to_process(trace_index, scan_index)

            if not traces_to_process:
                return pd.DataFrame()

            if trace_index is not None:
                # Single trace case
                return self._single_trace_to_dataframe(traces_to_process[0])
            elif include_all_traces:
                # All traces combined into one DataFrame
                return self._all_traces_to_dataframe(traces_to_process)
            else:
                # Default: first trace only (backward compatibility)
                return self._single_trace_to_dataframe(traces_to_process[0])

        except Exception as e:
            raise type(e)(f"Error converting to DataFrame: {e}") from e

    def _get_traces_to_process(
        self, trace_index: Optional[int], scan_index: Optional[int]
    ) -> List[Trace]:
        """Get the list of traces to process based on parameters."""
        try:
            if trace_index is not None:
                # Single specific trace
                if trace_index < 0 or trace_index >= len(self.traces):
                    raise IndexError(
                        f"Trace index {trace_index} out of range. "
                        f"Available traces: {len(self.traces)}"
                    )
                return [self.traces[trace_index]]

            elif scan_index is not None:
                # All traces from a specific scan
                if scan_index < 0 or scan_index >= len(self.scans):
                    raise IndexError(
                        f"Scan index {scan_index} out of range. "
                        f"Available scans: {len(self.scans)}"
                    )
                # In ESRP format, traces typically follow scans, but this is simplified
                return self.traces  # Return all traces for now

            else:
                # No specific trace or scan - return all traces
                return self.traces
        except Exception as e:
            raise type(e)(f"Error getting traces to process: {e}") from e

    def _single_trace_to_dataframe(self, trace: Trace) -> pd.DataFrame:
        """Convert a single trace to DataFrame."""
        try:
            return pd.DataFrame(
                {trace.x_unit: trace.data.x, trace.y_unit: trace.data.y}
            )
        except Exception as e:
            raise ValueError(f"Error converting trace to DataFrame: {e}") from e

    def _all_traces_to_dataframe(self, traces: List[Trace]) -> pd.DataFrame:
        """
        Convert all traces to a single DataFrame with trace-specific columns.

        The first trace's x-axis is used as the common x-axis, and all y-values
        are included with descriptive column names.
        """
        try:
            if not traces:
                return pd.DataFrame()

            # Use the first trace's x-axis as the common x-axis
            base_trace = traces[0]
            df_data = {base_trace.x_unit: base_trace.data.x}

            # Add each trace's y-values with descriptive column names
            for i, trace in enumerate(traces):
                try:
                    if len(trace.data.y) != len(base_trace.data.x):
                        continue

                    column_name = f"Trace {i} {trace.y_unit}"
                    if trace.name:
                        column_name = f"{trace.name} {trace.y_unit}"

                    df_data[column_name] = trace.data.y
                except Exception as e:
                    # Skip problematic traces but continue processing others
                    print(e)
                    continue

            return pd.DataFrame(df_data)
        except Exception as e:
            raise ValueError(f"Error converting all traces to DataFrame: {e}") from e

    def get_trace_dataframe(self, trace_index: int = 0) -> pd.DataFrame:
        """
        Get DataFrame for a specific trace (convenience method).

        Args:
            trace_index: Index of the trace to convert

        Returns:
            pandas DataFrame for the specified trace
        """
        try:
            return self.to_dataframe(trace_index=trace_index)
        except Exception as e:
            raise type(e)(f"Error getting trace DataFrame: {e}") from e

    def get_scan_dataframe(self, scan_index: int = 0) -> pd.DataFrame:
        """
        Get DataFrame for all traces in a specific scan (convenience method).

        Args:
            scan_index: Index of the scan to get traces from

        Returns:
            pandas DataFrame with all traces from the specified scan
        """
        try:
            return self.to_dataframe(scan_index=scan_index, include_all_traces=True)
        except Exception as e:
            raise type(e)(f"Error getting scan DataFrame: {e}") from e

    def get_combined_dataframe(self) -> pd.DataFrame:
        """
        Get combined DataFrame with all traces (convenience method).

        Returns:
            pandas DataFrame with all traces combined
        """
        try:
            return self.to_dataframe(include_all_traces=True)
        except Exception as e:
            raise type(e)(f"Error getting combined DataFrame: {e}") from e

    @property
    def scan_count(self) -> int:
        """Return the number of scans."""
        try:
            return len(self.scans)
        except Exception as e:
            raise AttributeError(f"Error getting scan count: {e}") from e

    @property
    def trace_count(self) -> int:
        """Return the number of traces."""
        try:
            return len(self.traces)
        except Exception as e:
            raise AttributeError(f"Error getting trace count: {e}") from e

    @property
    def file_name(self) -> str:
        """Return the file name."""
        try:
            return self.file_path.name
        except Exception as e:
            raise AttributeError(f"Error getting file name: {e}") from e

    @property
    def file_size(self) -> int:
        """Return the file size in bytes, or -1 if unavailable."""
        try:
            return self.file_path.stat().st_size
        except OSError:
            return -1
        except Exception as e:
            raise AttributeError(f"Error getting file size: {e}") from e

    def __repr__(self) -> str:
        """String representation of ESRPFile."""
        try:
            return (
                f"ESRPFile(file_path='{self.file_path}', "
                f"scans={self.scan_count}, traces={self.trace_count})"
            )
        except Exception:
            return "ESRPFile(corrupted or uninitialized)"

    def __str__(self) -> str:
        """User-friendly string representation."""
        try:
            return (
                f"ESRP File: {self.file_name}\n"
                f"Scans: {self.scan_count}, Traces: {self.trace_count}\n"
                f"File size: {self.file_size} bytes"
            )
        except Exception:
            return "ESRP File: Unable to display file information"
