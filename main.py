from src.datparser import ESRPFile


# Simple example with tests dat's

files = ["tests/dats/test_0.DAT", "tests/dats/test_1.DAT", "tests/dats/test_2.DAT"]

for f in files:
    print(ESRPFile(f))
