"""
Tests for ESRPParser class.
"""

import pytest
from src.datparser import ESRPParser, TraceData


class TestESRPParser:
    """Test ESRPParser class functionality."""

    def test_parser_initialization(self, sample_esrp_file):
        """Test parser initialization with valid file."""
        parser = ESRPParser(sample_esrp_file)
        assert parser.file_path == sample_esrp_file
        assert parser._lines == []

    def test_parser_initialization_error(self):
        """Test parser initialization with invalid path type."""
        with pytest.raises(ValueError):
            ESRPParser(123)  # Invalid path type

    def test_parse_file(self, esrp_parser):
        """Test successful file parsing with actual test.DAT file."""
        metadata, scans, traces = esrp_parser.parse()

        # Check that we got some metadata
        assert isinstance(metadata, dict)
        assert len(metadata) > 0

        # Check that we have scans and traces (exact counts depend on the actual file)
        assert isinstance(scans, list)
        assert isinstance(traces, list)

        # For each trace, verify the structure
        for trace in traces:
            assert isinstance(trace.metadata, dict)
            assert isinstance(trace.data, TraceData)
            assert len(trace.data.x) == len(trace.data.y)
            if trace.data.x:  # If there are data points
                assert all(isinstance(x, float) for x in trace.data.x)
                assert all(isinstance(y, float) for y in trace.data.y)

    def test_parse_file_content(self, esrp_parser):
        """Test specific content parsing from actual test.DAT file."""
        metadata, scans, traces = esrp_parser.parse()

        # Verify we can access the data without errors
        if traces:
            trace_data = traces[0].data
            assert hasattr(trace_data, "x")
            assert hasattr(trace_data, "y")
            assert trace_data.point_count == len(trace_data.x)

    def test_parse_empty_file(self, empty_esrp_file):
        """Test parsing empty file."""
        parser = ESRPParser(empty_esrp_file)
        metadata, scans, traces = parser.parse()

        assert metadata == {}
        assert scans == []
        assert traces == []

    def test_parse_line_valid(self, esrp_parser):
        """Test line parsing with valid input."""
        line = "Key; Value1; Value2; Value3"
        parts = esrp_parser._parse_line(line)
        assert parts == ["Key", "Value1", "Value2", "Value3"]

    def test_parse_line_empty(self, esrp_parser):
        """Test line parsing with empty input."""
        assert esrp_parser._parse_line("") == []
        assert esrp_parser._parse_line(";;;") == []

    def test_parse_line_with_whitespace(self, esrp_parser):
        """Test line parsing with whitespace."""
        line = "  Key  ;  Value1  ;  Value2  "
        parts = esrp_parser._parse_line(line)
        assert parts == ["Key", "Value1", "Value2"]

    def test_is_scan_section(self, esrp_parser):
        """Test scan section detection."""
        assert esrp_parser._is_scan_section("Scan 1:") is True
        assert esrp_parser._is_scan_section("Scan:") is True
        assert esrp_parser._is_scan_section("Scan 1") is False  # No colon
        assert esrp_parser._is_scan_section("TRACE 1") is False  # Wrong prefix

    def test_is_trace_section(self, esrp_parser):
        """Test trace section detection."""
        assert esrp_parser._is_trace_section("TRACE 1") is True
        assert esrp_parser._is_trace_section("TRACE") is True
        assert esrp_parser._is_trace_section("Trace 1") is False  # Wrong case
        assert esrp_parser._is_trace_section("Scan 1:") is False  # Wrong prefix

    def test_handle_scan_section(self, esrp_parser):
        """Test scan section handling."""
        scans = []
        scan = esrp_parser._handle_scan_section("Scan 1:", scans)

        assert scan.name == "Scan 1"
        assert scan.parameters == {}
        assert len(scans) == 1
        assert scans[0] is scan

    def test_handle_trace_section(self, esrp_parser):
        """Test trace section handling."""
        traces = []
        trace = esrp_parser._handle_trace_section(traces)

        assert trace.metadata == {}
        assert trace.data.x == []
        assert trace.data.y == []
        assert len(traces) == 1
        assert traces[0] is trace

    def test_handle_trace_data_point_invalid(self, trace):
        """Test trace data point handling with invalid data."""
        # Invalid numeric data
        parts = ["invalid", "data"]
        with pytest.raises(ValueError):
            ESRPParser._handle_trace_data_point(trace, parts)

    def test_handle_trace_data_point_insufficient_parts(self, trace):
        """Test trace data point handling with insufficient parts."""
        parts = ["100.0"]  # Only x value, no y value
        ESRPParser._handle_trace_data_point(trace, parts)

    def test_file_encoding_error(self, tmp_path):
        """Test file reading with encoding errors."""
        # Create a binary file that will cause encoding errors
        binary_file = tmp_path / "binary.esrp"
        binary_file.write_bytes(b"\x80\x81\x82\x83")

        parser = ESRPParser(binary_file)
        with pytest.raises(ValueError):
            parser.parse()

    def test_parse_line_error_handling(self, esrp_parser):
        """Test line parsing error handling."""
        # This should not raise an exception due to error handling
        result = esrp_parser._parse_line("normal line")
        assert isinstance(result, list)
