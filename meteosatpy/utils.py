import os
import gzip
import xarray
import rasterio
import subprocess
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
from rasterio.transform import from_origin
from fiona.crs import from_epsg
from shapely.geometry import box


def ungzip(path:str, remove:bool = True) -> None:
    """
    Unzip file with extension gz and remove it
    
    Args:
        path: File path to unzip (type text)
        remove: Boolean required if you want to remove the gzip file
    """
    # Remove the extension
    ungzip_path = path.replace(".gz", "")

    # Ungzip the file
    with gzip.open(path, 'rb') as f_in:
        with open(ungzip_path, 'wb') as f_out:
            f_out.write(f_in.read())

    # Remove the gzip file if required
    if(remove):
        os.remove(path)



def createMask(north:float, south:float, east:float, west:float, 
               epsg:int = 4326) -> gpd.GeoDataFrame:
    """
    Create the mask for area clipping
    
    Args:
        north: max coordinate in X axis (top)
        south: min coordinate in X axis (bottom)
        east:  max coordinate in Y axis (rigth)
        west:  min coordinate in Y axis (rigth)
        epsg:  SRC coordinate projection. Default: 4326

    Return:
        gdf: a geopandas dataframe with the mask
    """
    bbox = box(west, south, east, north)
    gdf = gpd.GeoDataFrame({'geometry':[bbox]}, crs = from_epsg(epsg))
    return(gdf)



def maskTIFF(path:str, shp:gpd.GeoDataFrame) -> tuple:
    """
    Creates a masked GeoTIFF using input shapes. Pixels are masked or set 
    to nodata outside the input shapes.
    
    Args:
        path: Raster path to which the mask will be applied
        shp: A geopandas dataframe with iterable geometries

    Return:
        tuple (two elements):
            out_image: Data contained in the raster after applying the mask.
            out_meta: Information for mapping pixel coordinates in masked
    """
    # Read the file and crop to target area
    with rasterio.open(path) as src:
        out_image, out_transform = mask(src, shp.geometry, crop=True)
        out_meta = src.meta

    # Update the metadata of GeoTIFF file
    out_meta.update({
        "driver": "GTiff", 
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })
    return(out_image, out_meta)



def writeRaster(raster, meta, path:str) -> None:
    """
    Write a raster file
    
    Args:
        raster: Data contained in the raster to be written.
        meta: Information for mapping pixel coordinates of the raster
        path: Fle path to write
    """
    with rasterio.open(path, "w", **meta) as r:
        r.write(raster)


def netcdf2TIFF(path:str, var:str, time:str, isflip:bool, out_path:str = None, 
                correction:bool = False) -> None:
    """
    Parse a netcdf file to GeoTIFF
    
    Args:
        path: File path of the netcdf file
        var: Selected variable to write in the GeoTIFF file
        time: Selected timestamp (yyyy-mm-dd HH:MM) to write in the GeoTIFF
        out_path: Path where GeoTIFF will be write.
        correction: Conditional to data correction for CMORPH case
    """
    # Remove the extension
    if out_path==None:
        out_path = path.replace(".nc", ".tif")

    # Read the netcdf file
    ds = xarray.open_dataset(path)
    ds = ds.sel(time=time)

    # Extract data and coordinates
    data = ds[var].values
    lat = ds['lat'].values
    lon = ds['lon'].values

    # Compute the spatial resolution
    res_lat = abs(lat[1] - lat[0])
    res_lon = abs(lon[1] - lon[0])

    # Compute the spatial tranformation
    lon_min = lon.min() - res_lon/2
    lat_max = lat.max() + res_lat/2

    # Correction
    if correction==True:
        mcd = data.shape[1] // 2
        data = np.hstack((data[:, mcd:], data[:, :mcd]))
        lon_min = lon_min - 180
    
    # Transform the projection considering correction
    transform = from_origin(lon_min, lat_max, res_lon, res_lat)

    # Raster metadata
    meta = {"driver": "GTiff", 
            "height": data.shape[0],
            "width": data.shape[1],
            "transform": transform,
            "crs": '+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0',
            "count" : 1, 
            "dtype" :str(data.dtype)}
    
    # Flipping the image upright in the axis = 0 i.e., vertically
    if isflip:
        data = np.flip(data,0)

    # Save data as GeoTIFF file
    with rasterio.open(out_path, 'w', **meta) as dst:
        dst.write(data, 1)


def is_installed(program):
    """
    Determine if a program is installed
    
    Args:
        program: name of the program
    """
    try:
        subprocess.check_output([program, '--version'])
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return True 