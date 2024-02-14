import os
import sys
import urllib
import datetime as dt
from .utils import *
from .warnings import *


class CMORPH():
    """
    CMORPH class object for downloading and managing precipitation data of 
    Climate Data Record (CDR). It consists of satellite precipitation estimates 
    that have been bias corrected and reprocessed using the the Climate Prediction 
    Center (CPC) Morphing Technique (MORPH).
    """
    def __init__(self, root:str = ".") -> None:
        # Ignore warnings produced by Fiona Deprecation
        ignoreWarnings()

    def download(self, date:dt.datetime, timestep:str, outpath:str, 
                 extent:list = None) -> None:
        """
        Download CMORPH precipitation data

        Args:
            date: A datetime object representing the date/hour.
            timestep: A string specifying the timestep: "30min", "hourly", "daily"
            extent: An optional list specifying the extent.
        """
        # Validate timestep variable
        if timestep not in ["30min", "hourly", "daily"]:
            err = "Invalid timestep. Please provide '30min', 'hourly', 'daily'."
            raise ValueError(err)
        
        # Validate extent variable
        if extent == None:
            extent = (60, -60, -180, 180)
        else:
            if not len(extent) == 4:
                err = "Invalid extent. Please provide a list with coordinates:"
                err = f"{err} 'north', 'south', 'east', 'west'"
                raise ValueError(err)
        
        # Server variables
        server = "https://www.ncei.noaa.gov/data"
        product = "cmorph-high-resolution-global-precipitation-estimates/access"
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        hour = date.strftime("%H")
        df = date.strftime("%Y%m%d")
        
        # Determine filedate based on timestep
        if timestep == "30min":
            path = f"30min/8km/{year}/{month}/{day}/CMORPH_V1.0_ADJ_8km-30min_{df}{hour}.nc"
        elif timestep == "hourly":
            path = f"hourly/0.25deg/{year}/{month}/{day}/CMORPH_V1.0_ADJ_0.25deg-HLY_{df}{hour}.nc"
        else:
            path = f"daily/0.25deg/{year}/{month}/CMORPH_V1.0_ADJ_0.25deg-DLY_00Z_{df}.nc"
        
        # Construct and download URL
        url = f"{server}/{product}/{path}"
        try:
            urllib.request.urlretrieve(url, "temporal.nc")        
        except Exception as e:
            print(f"Error occurred while downloading: {e}")
            return
        
        # Parse NC to TIFF
        netcdf2TIFF("temporal.nc", var="cmorph", time=date.strftime("%Y-%m-%d %M:00"), 
                    isflip=True, correction=True)

        # Mask the raster file to required extent
        mask = createMask(north=extent[0], south=extent[1], 
                          east=extent[2], west=extent[3])
        raster, meta = maskTIFF("temporal.tif", mask)
        raster[raster<0] = np.nan
        writeRaster(raster, meta, path=outpath)
        
        # Remove the temporal file
        os.remove("temporal.tif")
        #os.remove("temporal.nc")

        # Print status mensages
        print(f"Downloaded CMORPH {timestep} file: {date}", end='\r')
        sys.stdout.flush()



