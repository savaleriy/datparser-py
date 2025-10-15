"""
Tests for ESRPFile class.
"""

import pytest
from pathlib import Path
from src.datparser import ESRPFile, TraceData


class TestESRPFile:
    """Test ESRPFile class functionality."""

    def test_esrp_file_initialization(self, esrp_file):
        """Test ESRPFile initialization with actual test.DAT file."""
        # These should work regardless of the specific file content
        assert hasattr(esrp_file, "metadata")
        assert hasattr(esrp_file, "scans")
        assert hasattr(esrp_file, "traces")
        assert isinstance(esrp_file.metadata, dict)
        assert isinstance(esrp_file.scans, list)
        assert isinstance(esrp_file.traces, list)

    def test_esrp_file_from_file_classmethod(self, sample_esrp_file):
        """Test from_file class method."""
        esrp_file = ESRPFile.from_file(sample_esrp_file)
        assert isinstance(esrp_file, ESRPFile)
        assert hasattr(esrp_file, "scan_count")

    def test_esrp_file_file_not_found(self):
        """Test ESRPFile with non-existent file."""
        with pytest.raises(FileNotFoundError):
            ESRPFile("nonexistent.esrp")

    def test_esrp_file_properties(self, esrp_file):
        """Test ESRPFile properties with actual test.DAT file."""
        # These should work for any valid file
        assert esrp_file.scan_count >= 0
        assert esrp_file.trace_count >= 0
        assert isinstance(esrp_file.file_name, str)
        assert esrp_file.file_size > 0  # File should not be empty

    def test_get_scan_parameters(self, esrp_file):
        """Test scan parameters retrieval."""
        if esrp_file.scan_count > 0:
            params = esrp_file.get_scan_parameters(0)
            assert isinstance(params, dict)

    def test_get_scan_parameters_invalid_index(self, esrp_file):
        """Test scan parameters retrieval with invalid index."""
        with pytest.raises(IndexError):
            esrp_file.get_scan_parameters(999)

    def test_get_trace_metadata(self, esrp_file):
        """Test trace metadata retrieval."""
        if esrp_file.trace_count > 0:
            metadata = esrp_file.get_trace_metadata(0)
            assert isinstance(metadata, dict)

    def test_get_trace_metadata_invalid_index(self, esrp_file):
        """Test trace metadata retrieval with invalid index."""
        with pytest.raises(IndexError):
            esrp_file.get_trace_metadata(999)

    def test_get_trace_data(self, esrp_file):
        """Test trace data retrieval from actual test.DAT file."""
        if esrp_file.trace_count > 0:
            trace_data = esrp_file.get_trace_data(0)
            assert isinstance(trace_data, TraceData)
            assert len(trace_data.x) == len(trace_data.y)

    def test_get_trace_data_invalid_index(self, esrp_file):
        """Test trace data retrieval with invalid index."""
        with pytest.raises(IndexError):
            esrp_file.get_trace_data(999)

    def test_to_dataframe_single_trace(self, esrp_file):
        """Test DataFrame conversion for single trace."""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        if esrp_file.trace_count > 0:
            df = esrp_file.to_dataframe(trace_index=0)
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0  # Should have data points

    def test_to_dataframe_all_traces(self, esrp_file):
        """Test DataFrame conversion for all traces."""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        if esrp_file.trace_count > 0:
            df = esrp_file.to_dataframe(include_all_traces=True)
            assert isinstance(df, pd.DataFrame)
            # Should have at least one column for x data and one for y data
            assert len(df.columns) >= 2

    def test_to_dataframe_invalid_combination(self, esrp_file):
        """Test DataFrame conversion with invalid parameters."""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        if esrp_file.trace_count > 0:
            with pytest.raises(ValueError):
                esrp_file.to_dataframe(trace_index=0, include_all_traces=True)

    def test_to_dataframe_no_traces(self, empty_esrp_file):
        """Test DataFrame conversion with no traces."""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        esrp_file = ESRPFile(empty_esrp_file)
        df = esrp_file.to_dataframe()
        assert df.empty

    def test_to_dataframe_pandas_not_available(self, esrp_file, monkeypatch):
        """Test DataFrame conversion when pandas is not available."""
        monkeypatch.setattr("src.datparser.pd", None)
        with pytest.raises(RuntimeError, match="pandas is required"):
            esrp_file.to_dataframe()

    def test_get_trace_dataframe(self, esrp_file):
        """Test convenience method for trace DataFrame."""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        if esrp_file.trace_count > 0:
            df = esrp_file.get_trace_dataframe(0)
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0

    def test_get_scan_dataframe(self, esrp_file):
        """Test convenience method for scan DataFrame."""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        if esrp_file.scan_count > 0:
            df = esrp_file.get_scan_dataframe(0)
            assert isinstance(df, pd.DataFrame)

    def test_get_combined_dataframe(self, esrp_file):
        """Test convenience method for combined DataFrame."""
        try:
            import pandas as pd
        except ImportError:
            pytest.skip("pandas not available")

        if esrp_file.trace_count > 0:
            df = esrp_file.get_combined_dataframe()
            assert isinstance(df, pd.DataFrame)

    def test_repr_and_str(self, esrp_file):
        """Test string representations."""
        repr_str = repr(esrp_file)
        str_str = str(esrp_file)

        assert "ESRPFile" in repr_str
        assert "ESRP File" in str_str
        assert "Scans" in str_str
        assert "Traces" in str_str

    def test_error_handling_in_properties(self, esrp_file, monkeypatch):
        """Test error handling in properties."""
        # Test scan_count error
        monkeypatch.setattr(esrp_file, "scans", None)
        with pytest.raises(AttributeError):
            _ = esrp_file.scan_count

        # Test trace_count error
        monkeypatch.setattr(esrp_file, "traces", None)
        with pytest.raises(AttributeError):
            _ = esrp_file.trace_count
