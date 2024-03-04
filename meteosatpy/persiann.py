import os
import sys
import json
import shutil
import requests
import rasterio
import datetime as dt
from zipfile import ZipFile
from .warnings import ignoreWarnings
from .utils import get_params_persiann, writeRaster, createMask, maskTIFF

class PERSIANN():
    """
    PERSIANN class object for downloading and managing precipitation data of 
    Precipitation Estimation from Remotely Sensed Information using Artificial 
    Neural Networks
    """
    def __init__(self, root:str = ".") -> None:
        # Ignore warnings produced by Fiona Deprecation
        ignoreWarnings()
    
    def download(self, date:dt.datetime, timestep:str, dataset:str, outpath:str, 
                 extent:list = None) -> None:
        """
        Download PERSIANN precipitation data.

        Args:
            date (datetime): A datetime object representing the date.
            timestep (str): A string specifying the timestep: "hourly", "3hourly", "6hourly", 
                            "daily", "monthly", "annual".
            dataset (str): A string specifying the dataset: "PERSIANN", "CCS", "CDR", "PDIR".
            outpath (str): Path to store the output file.
            extent (list, optional): An optional list specifying the extent. 
        """
        # Validate timestep variable
        if timestep not in ["hourly", "3hourly", "6hourly", "daily", "monthly", "annual"]:
            err = 'Invalid timestep. Please provide "hourly", "3hourly", "6hourly", "daily", "monthly", "annual"'
            raise ValueError(err)
        
        # Validate dataset variable
        if dataset not in ["PERSIANN", "CCS", "CDR", "PDIR"]:
            err = 'Invalid dataset. Please provide "PERSIANN", "CCS", "CDR", "PDIR".'
            raise ValueError(err)
        
        if dataset == "CDR" and timestep in ["hourly", "3hourly", "6hourly"]:
            err = "PERSIANN CDR does not provide subdaily data."
            raise ValueError(err)
        
        # Construct query URL
        query_url = 'https://chrsdata.eng.uci.edu/php/downloadWholeData.php'
        params = get_params_persiann(date, timestep, dataset)

        # Querying PERSIANN data server
        query = requests.get(query_url, params=params)
        if query.status_code != 200:
            raise Exception('Error while querying PERSIANN data server')
        body = json.loads(query.text)

        # Extract temporal credentials
        userip = body['userIP']
        zipFile = body['zipFile']

        folder = {'PERSIANN': 'PERSIANN',
                  'CCS': 'PERSIANN-CCS',
                  'CDR': 'PERSIANN-CDR',
                  'PDIR': 'PDIR'}

        # Generating download url and final query params
        gen_url = 'https://chrsdata.eng.uci.edu/php/emailDownload.php'
        dl_base = 'https://chrsdata.eng.uci.edu/userFile'
        file_name = f'{dataset}_{zipFile}.zip'
        file_url = f'{dl_base}/{userip}/temp/{folder[dataset]}/{file_name}'

        dparams = {
            'email': "prueba@gmail.com",
            'downloadLink': file_url,
            'fileExtension': "zip",
            'dataType': dataset,
            'startDate': params["startDate"],
            'endDate': params["endDate"],
            'timestep': timestep,
            'domain': 'wholemap',
            'domain_parameter': 'undefined'
        }

        # Create the request
        gen = requests.get(gen_url, params=dparams)
        if gen.status_code != 200:
            raise Exception('Error while generating download link')

        # Downloading the file
        response = requests.get(file_url, stream=True)
        with open("temporal.zip", 'wb') as f:
            for chunk in response.iter_content(chunk_size=2048):
                if chunk:
                    f.write(chunk)
                    f.flush()

        # Extracting the downloaded file
        with ZipFile("temporal.zip", "r") as zip_ref:
            zip_ref.extractall("temp")

        # Finding and copying the TIFF file
        tiff_file = [f for f in os.listdir("temp") if f.endswith(".tif")][0]
        shutil.copy(os.path.join("temp", tiff_file), "temporal.tif")

        # Removing temporary directory and files
        shutil.rmtree("temp")
        os.remove("temporal.zip")

        # Reprojecting
        with rasterio.open("temporal.tif") as src:
            raster = src.read()
            meta = src.meta
        meta.update({"crs": '+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0'})
        writeRaster(raster, meta, "temporal.tif")

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
        print(f"Downloaded PERSIANN {dataset} {timestep} file: {date}", end='\r')
        sys.stdout.flush()
