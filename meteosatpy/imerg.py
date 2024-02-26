import os
import sys
import shutil
import requests
import datetime as dt
from .warnings import ignoreWarnings
from .utils import min_code, earth_data_explorer_credential, netcdf2TIFF, createMask, maskTIFF, writeRaster

class IMERG():
    """
    IMERG class object for downloading and managing precipitation data of 
    Global Precipitation Measurement (GPM). Producto: Integrated Multi-satellitE 
    Retrievals for GPM (IMERG)

    Args:
        user: Username for account: NASA Earth Data Explorer
        pw: Password for account: NASA Earth Data Explorer
    """
    def __init__(self, user:str = None, pw:str = None, root:str = ".") -> None:
        # Ignore warnings produced by Fiona Deprecation
        ignoreWarnings()

        # Validate user/password
        if user is None or pw is None:
            err = "Username or password for Earth Data Explorer Account not provided."
            raise(err)
        
        # Generate Loggin
        auth_url = 'https://urs.earthdata.nasa.gov/login'
        auth_data = {'username': user, 'password': pw}
        response = requests.post(auth_url, data=auth_data)

        # Validate auth
        if response.status_code == 200:
            earth_data_explorer_credential(user, pw)
        else:
            err = "Invalid username or password. Please provide correct username and"
            err = f"{err} password for Earth Data Explorer Account. {response.read()}"
            raise(err)
       
        
    
    def download(self, date:dt.datetime, version:str, run:str, timestep:str, 
                 outpath:str, extent:list = None) -> None:
        """
        Download IMERG precipitation data

        Args:
            date: A datetime object representing the date.
            version: A string specifying the product version: "v06", "v07".
            run: A string specifying the product run: "early", "late", "final".
            timestep: A string specifying the timestep: "30min", "daily", "monthly".
            outpath: A string specifying the path for output file.
            extent: An optional list specifying the extent.
        """
        
        # Validate version variable
        if version not in ["v06", "v07"]:
            raise ValueError("Invalid product version. Please provide 'v06', or 'v07'.")

        # Validate run variable
        if run not in ["early", "late", "final"]:
            raise ValueError("Invalid run. Please provide 'early', 'late', or 'final'.")

        # Validate timestep variable
        if timestep not in ["30min", "daily", "monthly"]:
            raise ValueError("Invalid timestep. Please provide '30min', 'daily', or 'monthly'.")

        # Validate extent variable
        if extent is not None and len(extent) != 4:
            raise ValueError("Invalid extent. Please provide a list with coordinates: 'north', 'south', 'east', 'west'.")

        # Construct the url for required data
        server = "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3"
        server2 = "https://gpm1.gesdisc.eosdis.nasa.gov/opendap/hyrax/GPM_L3"
        year = date.strftime("%Y")
        month = date.strftime("%m")
        actual = date.strftime("%Y%m%d")
        yymm = date.strftime("%Y%m01")
        code = min_code(date)
        julian_day = date.strftime("%j")
        end_date = date + dt.timedelta(seconds=1799)  # 30min - 1s
        ss = date.strftime("%H%M%S")
        ee = end_date.strftime("%H%M%S")

        vv = version[1:]

        if version == "v06":
            var_name = "precipitationCal"
        else:
            var_name = "precipitation"

        if run == "final":
            if timestep == "30min":
                url = f"{server}/GPM_3IMERGHH.{vv}/{year}/{julian_day}"
                url = f"{url}/3B-HHR.MS.MRG.3IMERG.{actual}-S{ss}-E{ee}.{code}.V{vv}B.HDF5.nc4?"
                multidim = True

            elif timestep == "daily":
                url = f"{server}/GPM_3IMERGDF.{vv}/{year}/{month}"
                url = f"{url}/3B-DAY.MS.MRG.3IMERG.{actual}-S000000-E235959.V{vv}"
                if version == "v07":
                    url += "B.nc4.nc4?"
                    multidim = False
                else:
                    url += ".nc4.nc4?"
                    multidim = True

            else:
                url = f"{server}/GPM_3IMERGM.{vv}/{year}"
                url = f"{url}/3B-MO.MS.MRG.3IMERG.{yymm}-S000000-E235959.{month}.V{vv}B.HDF5.nc4?"
                multidim = True
                var_name = "precipitation"

        elif run in ["late", "early"]:
            multidim = True

            if timestep == "30min":
                url = f"{server2}/GPM_3IMERG{'HHL' if run == 'late' else 'HHE'}.{vv}/{year}/{julian_day}"
                url = f"{url}/3B-HHR-{'L' if run == 'late' else 'E'}.MS.MRG.3IMERG.{actual}-S{ss}-E{ee}.{code}.V{vv}B.HDF5.nc4?"
                
            elif timestep == "daily":
                url = f"{server}/GPM_3IMERG{'DL' if run == 'late' else 'DE'}.{vv}/{year}/{month}"
                url = f"{url}/3B-DAY-{'L' if run == 'late' else 'E'}.MS.MRG.3IMERG.{actual}-S000000-E235959.V{vv}.nc4.nc4?"
            
            else:
                raise("IMERG late- and early-run data do not include monthly information.")

        # Download data
        response = requests.get(url)
        if response.status_code == 200:
            with open("temporal.nc", 'wb') as f:
                f.write(response.content)
        else:
            raise("Error occurred while downloading")

        # Parse NC to TIFF
        netcdf2TIFF("temporal.nc", var=var_name, time=date.strftime("%Y-%m-%d %M:00"), 
                    multidimention = multidim, traspose = True, isflip = True)
        
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
        print(f"Downloaded IMERG {version} {run} run {timestep} file: {date}", end='\r')
        sys.stdout.flush()


