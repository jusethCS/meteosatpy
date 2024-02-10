#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Setup file for meteosat. """

import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.1'
PACKAGE_NAME = 'meteosat'
AUTHOR = 'Juseth Enrique Chancay Sánchez'
AUTHOR_EMAIL = 'juseth.chancay'
URL = 'https://github.com/jusethCS/meteosat'

LICENSE = 'GNU'
DESCRIPTION = 'Library designed for downloading and managing hydro-meteorological data sourced from satellites and global models'
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8')
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'pandas',
      ]

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