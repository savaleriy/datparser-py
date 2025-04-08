from datparser import __version__
from datparser import ESRPFile


def test_version():
    assert __version__ == "0.1.0"


def test_single_trace():
    f = "test.DAT"
    x = ESRPFile(f)
