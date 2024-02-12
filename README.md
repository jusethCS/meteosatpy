# MeteoSatPy
[![PyPI Latest Release](https://img.shields.io/pypi/v/pandas.svg)](https://pypi.org/project/pandas/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/pandas.svg?label=PyPI%20downloads)](https://pypi.org/project/pandas/)
[![Conda Latest Release](https://anaconda.org/conda-forge/pandas/badges/version.svg)](https://anaconda.org/conda-forge/pandas) 
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/pandas.svg?label=Conda%20downloads)](https://anaconda.org/conda-forge/pandas)


## What is it?
**MeteoSatPy** is a Python library designed for downloading and managing hydro-meteorological data sourced from satellites and global models. It offers users efficient access to near-real-time and historical weather conditions globally. With features for data acquisition, processing, and analysis, **MeteoSatPy** is a versatile tool for meteorological research, forecasting, and decision-making across various sectors. 

## Where to get it?
The source code is currently hosted on GitHub at:
https://github.com/jusethCS/meteosatpy

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/meteosatpy)

```sh
# PyPI
pip install meteosatpy
```

## Dependencies
- [fiona](https://fiona.readthedocs.io/en/stable/README.html).- Streams simple feature data to and from GIS formats like GeoPackage and Shapefile.
- [shapely](https://shapely.readthedocs.io/en/stable/).- Manipulation and analysis of geometric objects in the Cartesian plane.
- [geopandas](https://readthedocs.org/projects/geopandas/).- Analysis and manipulation of geographical data.
- [rasterio](https://rasterio.readthedocs.io/en/stable/) .- Reads and writes raster formats and provides a Python API based on Numpy N-dimensional arrays and GeoJSON

We recommended prior to install **MeteoSatPy** by using PyPi, you should create a new conda environment with dependencies

```sh
# Conda
conda create -n [env_name] fiona shapely geopandas rasterio
```

## Examples

```python
import datetime as dt
from meteosatpy import *

# Target date
date = dt.datetime(2020, 1, 1) # year, month, day

# Instantiate the chirps object
ch = CHIRPS()

# Download CHIRPS data
ch.download(
    date=dates, 
    timestep="daily", 
    outpath=dates.strftime("chirps-output_%Y-%m-%d.tif"))
```