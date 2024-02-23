import os
import sys
import shutil
import datetime as dt
from .warnings import ignoreWarnings
from .utils import netcdf2TIFF, createMask, maskTIFF, writeRaster, is_installed

class MSWEP():
    """
    MSWEP class object for downloading and managing precipitation data of 
    Multi-Source Weighted-Ensemble Precipitation (MSWEP)
    """
    def __init__(self, root:str = ".") -> None:
        # Ignore warnings produced by Fiona Deprecation
        ignoreWarnings()

        # Determine if exists rclone dependency
        exist_rclone = is_installed("rclone")
        if not exist_rclone:
            err = "Rclone is not installed. Please install it using: 'pip install rclone'"
            err = f"{err} or 'conda install conda-forge::rclone'. To set up Rclone with a"
            err = f"{err} Google Drive account, we recommend watching this video tutorial"
            err = f"{err} https://www.youtube.com/watch?v=vPs9K_VC-lg"
            raise ValueError(err)
    
    def download(self, date:dt.datetime, timestep:str, dataset:str, outpath:str, 
                 extent:list = None) -> None:
        """
        Download MSWEP precipitation data

        Args:
            date: A datetime object representing the date.
            timestep: A string specifying the timestep: "3hourly","daily", "monthly".
            dataset: A string especifying the mswep dataset: "NTR", "Past", "Past_nogauge".
            outpath: A string specifying the path for output file.
            extent: An optional list specifying the extent.
        """
        # Validate timestep variable
        if timestep not in ["3hourly","daily", "monthly"]:
            err = "Invalid timestep. Please provide '3hourly', 'daily', or 'monthly'."
            raise ValueError(err)
        
        # Validate dataset variable
        if dataset not in ["NTR", "Past", "Past_nogauge"]:
            err = "Invalid dataset. Please provide 'NTR', 'Past', or 'Past_nogauge'."
            raise ValueError(err)
        
        # Validate extent variable
        if extent is not None and len(extent) != 4:
            err = "Invalid extent. Please provide a list with coordinates: 'north'"
            err = f"{err}, 'south', 'east', 'west'"
            raise ValueError(err)
        
        # Determine filedate based on timestep
        if timestep == "3hourly":
            file_name = date.strftime('%Y%j.%H.nc')
        
        if timestep ==  "daily":
            file_name = date.strftime('%Y%j.nc')
            timestep = "Daily"
        
        if timestep == "monthly":
            file_name = date.strftime('%Y%m.nc')
            timestep = "Monthly"

        # Construct the command and download data
        cmd = "rclone sync -v --drive-shared-with-me GoogleDrive:/MSWEP_V280"
        cmd = f"{cmd}/{dataset}/{timestep}/{file_name} ./"
        outcmd = os.system(cmd)

        if not outcmd==0:
            err = "Error occurred while downloading: No exist data for selected date"
            raise(err)
        else:
            os.rename(file_name, "temporal.nc")

        # Parse NC to TIFF
        netcdf2TIFF("temporal.nc", var="precipitation", time=date.strftime("%Y-%m-%d %M:00"), 
                    isflip=False, correction=False)

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
        os.remove("temporal.nc")

        # Print status mensages
        print(f"Downloaded MSWEP {timestep} file: {date}", end='\r')
        sys.stdout.flush()



