from setuptools import setup, Extension
from Cython.Build import cythonize
import os

extensions = [
    Extension(
        name="datparser.datparser",
        sources=[os.path.join("datparser", "datparser.pyx")],
    )
]

setup(
    name="datparser",
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
    packages=["datparser"],
)
