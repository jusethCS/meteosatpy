import os
import gzip
import shutil
import xarray
import platform
import rasterio
import subprocess
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
from rasterio.transform import from_origin


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
        north: max coordinate in Y axis (top)
        south: min coordinate in Y axis (bottom)
        east:  max coordinate in X axis (right)
        west:  min coordinate in X axis (left)
        epsg:  SRC coordinate projection. Default: 4326

    Return:
        gdf: a geopandas dataframe with the mask
    """
    # Create a GeoDataFrame with a single rectangular polygon
    gdf = gpd.GeoDataFrame(geometry=[
                gpd.polygon.Polygon([
                    (west, south), (east, south), 
                    (east, north), (west, north)])])
    # Set the coordinate reference system (CRS)
    gdf.crs = f"EPSG:{epsg}"
    return gdf



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



def netcdf2TIFF(path:str, var:str, time:str, out_path:str = None, isflip:bool = False,
                correction:bool = False, multidimention:bool = False,
                traspose:bool = False) -> None:
    """
    Parse a netcdf file to GeoTIFF
    
    Args:
        path: File path of the netcdf file
        var: Selected variable to write in the GeoTIFF file
        time: Selected timestamp (yyyy-mm-dd HH:MM) to write in the GeoTIFF
        out_path: Path where GeoTIFF will be write.
        isflip: 
        correction: Conditional to data correction for CMORPH case
        multidim: Coditional, file contains aditional dimensions. For IMERG.
    """
    # Remove the extension
    if out_path==None:
        out_path = path.replace(".nc", ".tif")

    # Read the netcdf file
    ds = xarray.open_dataset(path)
    ds = ds.sel(time=time)

    # Extract data
    data = ds[var].values
    if multidimention:
        data = data[0]
    
    # Extract coordinates
    lat = ds['lat'].values
    lon = ds['lon'].values

    # Compute the spatial resolution
    res_lat = abs(lat[1] - lat[0])
    res_lon = abs(lon[1] - lon[0])

    # Compute the spatial tranformation
    lon_min = lon.min() - res_lon/2
    lat_max = lat.max() + res_lat/2

    # Traspose
    if traspose:
        data = np.transpose(data)

    # Correction
    if correction:
        mcd = data.shape[1] // 2
        data = np.hstack((data[:, mcd:], data[:, :mcd]))
        lon_min = lon_min - 180

    # Flipping the image upright in the axis = 0 i.e., vertically
    if isflip:
        data = np.flip(data,0)
    
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
    

def min_code(date):
    hora = date.hour
    minuto = date.minute
    codigo = hora * 60 + minuto
    return f"{codigo:04d}"



def earth_data_explorer_credential(username, password):
    # Earthdata URL to call for authentication 
    urs = 'urs.earthdata.nasa.gov'

    # Determine the root directory
    homeDir = os.path.expanduser("~") + os.sep

    # Write files
    with open(homeDir + '.netrc', 'w') as file:
        file.write('machine {} login {} password {}'.format(urs, username, password))
        file.close()
    with open(homeDir + '.urs_cookies', 'w') as file:
        file.write('')
        file.close()
    with open(homeDir + '.dodsrc', 'w') as file:
        file.write('HTTP.COOKIEJAR={}.urs_cookies\n'.format(homeDir))
        file.write('HTTP.NETRC={}.netrc'.format(homeDir))
        file.close()

    print('Saved .netrc, .urs_cookies, and .dodsrc to:', homeDir)

    # Set appropriate permissions for Linux/macOS
    if platform.system() != "Windows":
        subprocess.Popen('chmod og-rw ~/.netrc', shell=True)
    else:
        # Copy dodsrc to working directory in Windows  
        shutil.copy2(homeDir + '.dodsrc', os.getcwd())
        print('Copied .dodsrc to:', os.getcwd())




def get_params_persiann(date, timestep, data_type):
    """
    Get parameters for PERSIANN data download based on date, timestep, and data type.

    Args:
        date (datetime): A datetime object representing the date.
        timestep (str): A string specifying the timestep: "hourly", "3hourly", 
                        "6hourly", "daily", "monthly", or "yearly".
        data_type (str): A string specifying the data type: "PERSIANN", "CCS", 
                        "CDR", or "PDIR".

    Returns:
        dict: A dictionary containing parameters for PERSIANN data download.
    """
    if timestep == "hourly":
        ds = date.strftime("%Y%m%d%H")
        dtm = "1hrly"
        dtx = "1h"
    elif timestep == "3hourly":
        ds = date.strftime("%Y%m%d%H")
        dtm = "3hrly"
        dtx = "3h"
    elif timestep == "6hourly":
        ds = date.strftime("%Y%m%d%H")
        dtm = "6hrly"
        dtx = "6h"
    elif timestep == "daily":
        ds = date.strftime("%Y%m%d")
        dtm = timestep
        dtx = "1d"
    elif timestep == "monthly":
        ds = date.strftime("%Y%m")
        dtm = timestep
        dtx = "1m"
    elif timestep == "yearly":
        ds = date.strftime("%Y")
        dtm = timestep
        dtx = "1y"

    params = {
        'startDate': ds,
        'endDate': ds,
        'timestep': dtm,
        'timestepAlt': dtx,
        'dataType': data_type,
        'format': "Tif",
        'compression': "zip"
    }
    return params
