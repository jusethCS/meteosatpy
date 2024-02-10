import os
import gzip
import rasterio
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
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