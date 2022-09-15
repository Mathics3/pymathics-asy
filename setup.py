#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import platform
import os
from os import walk
import os.path as osp
import shutil
from setuptools import setup, find_namespace_packages

# Ensure user has the correct Python version
if sys.version_info < (3, 6):
    print("Mathics support Python 3.6 and above; you have %d.%d" % sys.version_info[:2])
    sys.exit(-1)

# stores __version__ in the current namespace
exec(compile(open("pymathics/asy/version.py").read(), "version.py", "exec"))

is_PyPy = platform.python_implementation() == "PyPy"

setup_path = osp.normcase(osp.dirname(osp.abspath(__file__)))
setup_path = osp.realpath(setup_path)


setup(
    name="pymathics-asy",
    version=__version__,
    packages=find_namespace_packages(include=["pymathics.asy.*"]),
    install_requires=["mathics3>=1.1.0"],
    package_data={"pymathics-asy": ["autoload/formats/*/Export.m"]},
    # don't pack Mathics in egg because of media files, etc.
    zip_safe=False,
    # metadata for upload to PyPI
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Interpreters",
    ],
    # TODO: could also include long_description, download_url,
)


# Install autoload path
