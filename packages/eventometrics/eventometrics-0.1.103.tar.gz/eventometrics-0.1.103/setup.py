from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

import os
import numpy as np

# package_dir = os.path.abspath("eventometrics")

# extensions = [
#     Extension(
#         "eventometrics.Lemke",
#         "eventometrics/Lemke.pyx",
#         include_dirs=[...],  # e.g., NumPy headers
#     )
# ]

setup(
    name='eventometrics',
    version='0.1.103',
    author='Korablev Yu.A.',
    packages=find_packages(),
    ext_modules=cythonize(

        ["eventometrics/*.pyx","eventometrics/*.pxd"],
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
            "cdivision": True
        }
    ,
    annotate=True,
    force=True,
    include_path=["eventometrics"],
    # build_dir='cython_build'
    )
    ,
    include_dirs=[np.get_include()],
    package_data={"my_package": ["data/*.csv"]},
)

# commands
# python setup.py clean --all
# python setup.py build_ext --inplace

# py -m build
# twine upload dist/*