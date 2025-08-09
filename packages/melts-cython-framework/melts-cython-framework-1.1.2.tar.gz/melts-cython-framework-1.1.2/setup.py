#!/usr/bin/env python
""" file: setup.py
    modified: Mark S. Ghiorso, OFM Research
    date: October 25, 2021
    restructured: November 12, 2021
    restructured: November 16, 2021

    description: Setuptools installer script for melts Cython framework.
"""

import os
from setuptools import setup, find_packages, Extension

from setuptools import dist
dist.Distribution().fetch_build_eggs(['Cython>=0.29.23', 'numpy>=1.19.5'])

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

import numpy

from sys import platform
if platform == "linux" or platform == "linux2":
    from distutils import sysconfig
elif platform == "darwin":
    pass
elif platform == "win32":
    pass

# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions

extensions = [
    Extension(
        "melts.rMELTSframework",
        sources=[
            'src/melts/rMELTSframework.pyx',
            'src/melts/cframework.c',
            'src/albite.c', 
            'src/alloy-liquid.c', 
            'src/alloy-solid.c', 
            'src/amphibole.c', 
            'src/biotite.c', 
            'src/biotiteTaj.c', 
            'src/check_coexisting_liquids.c', 
            'src/check_coexisting_solids.c', 
            'src/clinopyroxene.c', 
            'src/cummingtonite.c', 
            'src/equality_constraints.c', 
            'src/est_saturation_state.c', 
            'src/est_satState_revised.c', 
            'src/evaluate_saturation.c', 
            'src/feldspar.c', 
            'src/fluid.c', 
            'src/fluidPhase.c', 
            'src/frac.c', 
            'src/garnet.c', 
            'src/gibbs.c', 
            'src/gradient_hessian.c', 
            'src/hornblende.c', 
            'src/ilmenite.c', 
            'src/lawson_hanson.c', 
            'src/leucite.c', 
            'src/linear_search.c', 
            'src/liquid.c', 
            'src/liquid_v34.c', 
            'src/liquid_CO2.c', 
            'src/liquid_CO2_H2O.c', 
            'src/liquidus.c', 
            'src/majorite.c', 
            'src/melilite.c', 
            'src/melts_support.c', 
            'src/melts_threads.c', 
            'src/mthread.c', 
            'src/nash.c', 
            'src/nepheline.c', 
            'src/kalsilite.c', 
            'src/olivine.c', 
            'src/olivine-sx.c', 
            'src/orthopyroxene.c', 
            'src/ortho-oxide.c', 
            'src/perovskite.c', 
            'src/read_write.c', 
            'src/recipes.c', 
            'src/rhombohedral.c', 
            'src/rhomsghiorso.c',
            'src/ringwoodite.c', 
            'src/silmin.c', 
            'src/silmin_support.c', 
            'src/spinel.c', 
            'src/subSolidusMuO2.c', 
            'src/wadsleyite.c', 
            'src/water.c', 
            'src/wustite.c'
        ],
        include_dirs=[
        './inc',
        './src/melts'
        ]
        +(['/usr/include/libxml2'] if platform == "linux" or platform == "linux2" else [])
        +[numpy.get_include()],
        extra_compile_args=[
        '-O3', 
        '-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION',
        '-DBATCH_VERSION',
        '-DRHYOLITE_ADJUSTMENTS']
        + (['-Wno-unused-but-set-variable'] if platform == "linux" or platform == "linux2" else [])
        + (['-Wno-misleading-indentation' ] if platform == "linux" or platform == "linux2" else []),
        library_dirs=['/usr/local/lib']
        +(['/usr/lib/x86_64-linux-gnu'] if platform == "linux" or platform == "linux2" else []),
        runtime_library_dirs=['/usr/local/lib']
        +(['/usr/lib/x86_64-linux-gnu'] if platform == "linux" or platform == "linux2" else []),
        extra_objects = (['/usr/lib/x86_64-linux-gnu/libxml2.so.2'] if platform == "linux" or platform == "linux2" else []),
        extra_link_args=[] # -L/usr/lib/x86_64-linux-gnu -lxml2
    ),
]

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0))) and cythonize is not None

if CYTHONIZE:
    compiler_directives = {"language_level": 3, "embedsignature": True}
    extensions = cythonize(extensions, compiler_directives=compiler_directives)
else:
    extensions = no_cythonize(extensions)

with open("requirements.txt") as fp:
    install_requires = fp.read().strip().split("\n")

setup(
    ext_modules=extensions,
    include_package_data=True,
    install_requires=install_requires,
)
