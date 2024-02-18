# MeteoSatPy

## What is it?
**MeteoSatPy** is a Python library designed for downloading and managing hydro-meteorological data sourced from satellites and global models. It offers users efficient access to near-real-time and historical weather conditions globally. With features for data acquisition, processing, and analysis. **MeteoSatPy** is a versatile tool for meteorological research, forecasting, and decision-making across various sectors.

## Where to get it?
The source code is currently hosted on GitHub at:
[https://github.com/jusethCS/meteosatpy](https://github.com/jusethCS/meteosatpy)

Binary installers for the latest released version are available at the [Python Package Index (PyPI)](https://pypi.org/project/meteosatpy/)

```sh
# PyPI
pip install meteosatpy
```

## Dependencies
- [fiona](https://fiona.readthedocs.io/en/stable/README.html): Streams simple feature data to and from GIS formats like GeoPackage and Shapefile.
- [shapely](https://shapely.readthedocs.io/en/stable/): Manipulation and analysis of geometric objects in the Cartesian plane.
- [geopandas](https://readthedocs.org/projects/geopandas/): Analysis and manipulation of geographical data.
- [rasterio](https://rasterio.readthedocs.io/en/stable/): Reads and writes raster formats based on Numpy N-dimensional arrays.
- [xarray](https://docs.xarray.dev/en/stable/): Works with labelled multi-dimensional arrays simple and efficient.
- [netcdf4](https://unidata.github.io/netcdf4-python/): Reads and writes netCDF files compatible with older versions of the library.
- [h5netcdf](https://h5netcdf.org/): A Python interface for the netCDF4 file-format that reads and writes local or remote HDF5 files.


Prior to installing **MeteoSatPy** using PyPi, we recommend creating a new conda environment with dependencies:

```sh
# Conda
conda create -n [env_name] fiona shapely geopandas rasterio netcdf4 h5netcdf xarray
```

If you need to download ["MSWEP"](https://www.gloh2o.org/mswep/) data, you'll need to install [Rclone](https://anaconda.org/conda-forge/rclone).

```sh
# Conda
conda install conda-forge::rclone
```

To set up Rclone with a Google Drive account, we recommend watching this [tutorial](https://www.youtube.com/watch?v=vPs9K_VC-lg). Note the MSWEP data are store on this Google Drive [repository](https://drive.google.com/drive/u/0/folders/1Kok05OPVESTpyyan7NafR-2WwuSJ4TO9).


## Examples

```python
import datetime as dt
from meteosatpy import *

# Target date
date = dt.datetime(2020, 1, 1) # year, month, day

# Download CHIRPS data
ch = CHIRPS()
ch.download(
    date=date, 
    timestep="daily", 
    outpath=date.strftime("chirps_%Y-%m-%d.tif")
)

# Download CMORPH data
cm = CMORPH()
cm.download(
    date=dates[i], 
    timestep="daily", 
    outpath=date.strftime("cmorph_%Y-%m-%d.tif")
)

# Download MSWEP data
mw = MSWEP()
mw.download(
    date=dates[i], 
    timestep="daily", 
    dataset="Past",
    outpath=date.strftime("mswep_%Y-%m-%d.tif"))
```
