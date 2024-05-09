# MeteoSatPy
[![PyPI Latest Release](https://img.shields.io/pypi/v/meteosatpy.svg)](https://pypi.org/project/meteosatpy/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/meteosatpy.svg?label=PyPI%20downloads)](https://pypi.org/project/meteosatpy/)
[![Conda Latest Release](https://anaconda.org/juseth.chancay/meteosatpy/badges/version.svg)](https://anaconda.org/juseth.chancay/meteosatpy) 
[![Conda Downloads](https://anaconda.org/juseth.chancay/meteosatpy/badges/downloads.svg)](https://anaconda.org/juseth.chancay/meteosatpy)

## What is it?
**MeteoSatPy** is a Python library designed for downloading and managing hydro-meteorological data sourced from satellites and global models. It offers users efficient access to near-real-time and historical weather conditions globally. With features for data acquisition, processing, and analysis. **MeteoSatPy** is a versatile tool for meteorological research, forecasting, and decision-making across various sectors.

## Where to get it?
The source code is currently hosted on GitHub at:
[https://github.com/jusethCS/meteosatpy](https://github.com/jusethCS/meteosatpy)

Binary installers for the latest released version are available at the [Python Package Index (PyPI)](https://pypi.org/project/meteosatpy/) and on [Conda](https://anaconda.org/juseth.chancay/meteosatpy)

```sh
# PyPI
pip install meteosatpy
```
```sh
# Conda
conda install juseth.chancay::meteosatpy
```

## Dependencies
- [rasterio](https://rasterio.readthedocs.io/en/stable/): Reads and writes raster formats based on Numpy N-dimensional arrays.
- [xarray](https://docs.xarray.dev/en/stable/): Works with labelled multi-dimensional arrays simple and efficient.
- [geopandas](https://readthedocs.org/projects/geopandas/): Analysis and manipulation of geographical data.
- [request](https://requests.readthedocs.io/en/latest/): HTTP library for making requests and working with web APIs.

Prior to installing **MeteoSatPy** using PyPi, we recommend creating a new conda environment with dependencies:

```sh
# Conda
conda create -n [env_name] geopandas rasterio xarray requests
```

If you need to download [MSWEP](https://www.gloh2o.org/mswep/) data, you'll need to install [Rclone](https://anaconda.org/conda-forge/rclone).

```sh
# Conda
conda install conda-forge::rclone
```

To set up Rclone with a Google Drive account, we recommend watching this [tutorial](https://www.youtube.com/watch?v=vPs9K_VC-lg). Note the MSWEP data are store on this Google Drive [repository](https://drive.google.com/drive/u/0/folders/1Kok05OPVESTpyyan7NafR-2WwuSJ4TO9).


## Examples

```python
import datetime as dt
import meteosatpy

# Target date
date = dt.datetime(2010, 1, 1) # year, month, day

# Download CHIRPS data
ch = meteosatpy.CHIRPS()
ch.download(
    date=date, 
    timestep="daily", 
    outpath=date.strftime("chirps_%Y-%m-%d.tif")
)

# Download CMORPH data
cm = meteosatpy.CMORPH()
cm.download(
    date=date, 
    timestep="daily", 
    outpath=date.strftime("cmorph_%Y-%m-%d.tif")
)

# Download MSWEP data
mw = meteosatpy.MSWEP()
mw.download(
    date=date, 
    timestep="daily", 
    dataset="Past",
    outpath=date.strftime("mswep_%Y-%m-%d.tif"))

# Download IMERG v07 final run
im = meteosatpy.IMERG(user="username", pw="pass")
im.download(
    date=date, 
    version="v07", 
    run="final", 
    timestep="daily", 
    outpath=date.strftime("imerg_%Y-%m-%d.tif")
)
```
