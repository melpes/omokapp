# DO NOT TOUCH!
#
# This code allows cython to target the correct file for compilation.

from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("cythonfn.pyx"))
