"""
Tests for data classes: TraceData, Trace, and Scan.
"""

import pytest
from src.datparser import TraceData, Trace, Scan


class TestTraceData:
    """Test TraceData class functionality."""

    def test_trace_data_initialization(self, trace_data):
        """Test TraceData initialization with valid data."""
        assert len(trace_data.x) == 3
        assert len(trace_data.y) == 3
        assert trace_data.x == [1.0, 2.0, 3.0]
        assert trace_data.y == [-10.0, -20.0, -30.0]

    def test_trace_data_point_count(self, trace_data):
        """Test point_count property."""
        assert trace_data.point_count == 3

    def test_trace_data_validation(self):
        """Test TraceData validation with mismatched lengths."""
        with pytest.raises(ValueError, match="x and y data must have the same length"):
            TraceData(x=[1.0, 2.0], y=[-10.0])  # Different lengths

    def test_trace_data_empty(self):
        """Test TraceData with empty lists."""
        empty_data = TraceData(x=[], y=[])
        assert empty_data.point_count == 0

    def test_trace_data_point_count_error_handling(self):
        """Test point_count property error handling."""
        trace_data = TraceData(x=[1.0, 2.0], y=[-10.0, -20.0])
        # Simulate an error by corrupting the x attribute
        trace_data.x = None
        with pytest.raises(AttributeError):
            _ = trace_data.point_count


class TestTrace:
    """Test Trace class functionality."""

    def test_trace_initialization(self, trace):
        """Test Trace initialization."""
        assert trace.name == "TestTrace"
        assert trace.metadata["Trace Name"] == ["TestTrace"]
        assert trace.data.point_count == 3

    def test_trace_name_from_metadata(self):
        """Test trace name extraction from metadata."""
        metadata = {"Trace Name": ["AutoTrace"]}
        data = TraceData(x=[], y=[])
        trace = Trace(metadata=metadata, data=data)
        assert trace.name == "AutoTrace"

    def test_trace_properties(self, trace):
        """Test trace property accessors."""
        assert trace.x_unit == "MHz"
        assert trace.y_unit == "dBm"
        assert trace.trace_name == "TestTrace"

    def test_trace_properties_defaults(self):
        """Test trace properties with missing metadata."""
        metadata = {}
        data = TraceData(x=[], y=[])
        trace = Trace(metadata=metadata, data=data)

        assert trace.x_unit == "X"  # Default from metadata.get
        assert trace.y_unit == "Y"  # Default from metadata.get
        assert "Trace" in trace.trace_name  # Generated name

    def test_trace_property_error_handling(self):
        """Test trace property error handling."""
        metadata = {"X-Unit": ["MHz"], "1-Unit": ["dBm"]}
        data = TraceData(x=[], y=[])
        trace = Trace(metadata=metadata, data=data)

        # Corrupt metadata to test error handling
        trace.metadata = None
        with pytest.raises(AttributeError):
            _ = trace.x_unit

    def test_trace_initialization_error_handling(self):
        """Test trace initialization error handling."""
        with pytest.raises(ValueError):
            # This should cause an error in __post_init__
            Trace(metadata="invalid", data="invalid")


class TestScan:
    """Test Scan class functionality."""

    def test_scan_initialization(self):
        """Test Scan initialization."""
        scan = Scan(name="Scan1", parameters={"param1": ["value1"]})
        assert scan.name == "Scan1"
        assert scan.parameters["param1"] == ["value1"]

    def test_scan_empty_parameters(self):
        """Test Scan with empty parameters."""
        scan = Scan(name="EmptyScan", parameters={})
        assert scan.name == "EmptyScan"
        assert scan.parameters == {}
