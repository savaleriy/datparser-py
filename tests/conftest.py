""" ""
Pytest configuration and shared fixtures for ESRP parser tests.
"""

import pytest
from pathlib import Path
import tempfile
import os


@pytest.fixture
def sample_esrp_file():
    """Use the actual test.DAT file from tests/dats/ directory."""
    test_file_path = Path(__file__).parent / "dats" / "test_0.DAT"

    if not test_file_path.exists():
        pytest.fail(f"Test file not found: {test_file_path}")

    return test_file_path


@pytest.fixture
def sample_esrp_file_1():
    """Use the actual test.DAT file from tests/dats/ directory."""
    test_file_path = Path(__file__).parent / "dats" / "test_1.DAT"

    if not test_file_path.exists():
        pytest.fail(f"Test file not found: {test_file_path}")

    return test_file_path


@pytest.fixture
def sample_esrp_file_2():
    """Use the actual test.DAT file from tests/dats/ directory."""
    test_file_path = Path(__file__).parent / "dats" / "test_2.DAT"

    if not test_file_path.exists():
        pytest.fail(f"Test file not found: {test_file_path}")

    return test_file_path


@pytest.fixture
def invalid_esrp_file():
    """Create an invalid ESRP file for testing error handling."""
    invalid_content = """Invalid File
This is not a proper ESRP file
;;
Invalid; Data; Points;
100; -50; extra
"""

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".esrp", delete=False, encoding="utf-8"
    ) as f:
        f.write(invalid_content)
        f.flush()
        yield Path(f.name)

    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def empty_esrp_file():
    """Create an empty ESRP file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".esrp", delete=False, encoding="utf-8"
    ) as f:
        f.write("")
        f.flush()
        yield Path(f.name)

    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def esrp_parser(sample_esrp_file):
    """Create an ESRPParser instance with sample file."""
    from src.datparser import ESRPParser

    return ESRPParser(sample_esrp_file)


@pytest.fixture
def esrp_file(sample_esrp_file):
    """Create an ESRPFile instance with sample file."""
    from src.datparser import ESRPFile

    return ESRPFile(sample_esrp_file)


@pytest.fixture
def trace_data():
    """Create sample trace data for testing."""
    from src.datparser import TraceData

    return TraceData(x=[1.0, 2.0, 3.0], y=[-10.0, -20.0, -30.0])


@pytest.fixture
def trace():
    """Create a sample trace for testing."""
    from src.datparser import Trace, TraceData

    metadata = {"Trace Name": ["TestTrace"], "x-Unit": ["MHz"], "y-Unit": ["dBm"]}
    data = TraceData(x=[100.0, 200.0, 300.0], y=[-50.0, -45.0, -40.0])
    return Trace(metadata=metadata, data=data, name="TestTrace")
