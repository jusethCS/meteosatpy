#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Setup file for meteosatpy. """

import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.4'
PACKAGE_NAME = 'meteosatpy'
AUTHOR = 'Juseth Enrique Chancay Sánchez'
AUTHOR_EMAIL = 'juseth.chancay@gmail.com'
URL = 'https://github.com/jusethCS/meteosatpy'

LICENSE = 'MIT'
DESCRIPTION = 'Library designed for downloading and managing meteorological data sourced from satellites and global models.'
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8')
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = ["rasterio", "xarray", "geopandas", "requests"]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True,
)