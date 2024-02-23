import os
import sys
import shutil
import urllib.request
import datetime as dt
from .warnings import ignoreWarnings
from .utils import ungzip, createMask, maskTIFF, writeRaster


class CHIRPS():
    """
    CHIRPS class object for downloading and managing precipitation data of 
    Climate Hazards Group InfraRed Precipitation with Station
    """
    def __init__(self, root:str = ".") -> None:
        # Ignore warnings produced by Fiona Deprecation
        ignoreWarnings()
    
    def download(self, date:dt.datetime, timestep:str, outpath:str, 
                 extent:list = None) -> None:
        """
        Download CHIRPS precipitation data

        Args:
            date: A datetime object representing the date.
            timestep: A string specifying the timestep: "daily", "monthly", "annual"
            outpath: A string specifying the path for output file.
            extent: An optional list specifying the extent.
        """
        # Validate timestep variable
        if timestep not in ["daily", "monthly", "annual"]:
            err = "Invalid timestep. Please provide 'daily', 'monthly', or 'annual'."
            raise ValueError(err)
        
        # Validate extent variable
        if extent is not None and len(extent) != 4:
            err = "Invalid extent. Please provide a list with coordinates: 'north'"
            err = f"{err}, 'south', 'east', 'west'"
            raise ValueError(err)

        # Server variables
        server = "https://data.chc.ucsb.edu"
        product = f"products/CHIRPS-2.0/global_{timestep}/tifs"
        year = date.strftime("%Y")

        # Determine filedate based on timestep
        if timestep == "daily":
            filedate = date.strftime("%Y.%m.%d")
        elif timestep == "monthly":
            filedate = date.strftime("%Y.%m")
        else:
            filedate = year

        # Construct download URL
        if timestep == "daily":
            url = f"{server}/{product}/p05/{year}/chirps-v2.0.{filedate}.tif.gz"
        else:
            url = f"{server}/{product}/chirps-v2.0.{filedate}.tif.gz"
        
        # Download and ungzip file
        try:
            urllib.request.urlretrieve(url, "temporal.tif.gz")        
        except Exception as e:
            print(f"Error occurred while downloading: {e}")
            return
            
        # Ungzip the file
        ungzip("temporal.tif.gz")

        # Mask the raster file to required extent
        if extent is None:
            shutil.copyfile("temporal.tif", outpath)
        else:
            mask = createMask(north=extent[0], south=extent[1], 
                              east=extent[2], west=extent[3])
            raster, meta = maskTIFF("temporal.tif", mask)
            raster[raster<0] = 0
            writeRaster(raster, meta, path=outpath)
        
        # Remove the temporal file
        os.remove("temporal.tif")

        # Print status mensages
        print(f"Downloaded CHIRPS {timestep} file: {date}", end='\r')
        sys.stdout.flush()

