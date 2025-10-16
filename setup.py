from setuptools import setup, find_packages
import os

# Check if we're building with Cython
try:
    from Cython.Build import cythonize
    HAS_CYTHON = True
except ImportError:
    HAS_CYTHON = False

extensions = []
if HAS_CYTHON:
    extensions = [
        Extension(
            name="datparser.datparser",
            sources=[os.path.join("src", "datparser", "datparser.py")],
        )
    ]
    ext_modules = cythonize(extensions, compiler_directives={"language_level": "3"})
else:
    ext_modules = []

setup(
    name="datparser",
    ext_modules=ext_modules,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
