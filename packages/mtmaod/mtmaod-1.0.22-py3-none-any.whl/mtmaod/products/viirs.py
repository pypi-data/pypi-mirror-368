import numpy as np
import pandas as pd
from mtmaod.utils.netCDF4 import NetCDF4

from ._template import SatelliteProductReaderNetCDF4, SatelliteProductDataNetCDF4


class AERDTL2Reader(SatelliteProductReaderNetCDF4):
    Product_File_Time_Format = "[.]A%Y%j[.]%H%M[.]"
    LinkedDataClass = SatelliteProductDataNetCDF4
    Band_Longitude = "/geolocation_data/longitude"
    Band_Latitude = "/geolocation_data/latitude"

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = NetCDF4.read(fp, dataset_name, *args, **kwargs)
        DataClass = AERDTL2Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)


class AERDBL2Reader(SatelliteProductReaderNetCDF4):
    Product_File_Time_Format = "[.]A%Y%j[.]%H%M[.]"
    LinkedDataClass = SatelliteProductDataNetCDF4
    Band_Latitude = "/Latitude"
    Band_Longitude = "/Longitude"

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = NetCDF4.read(fp, dataset_name, *args, **kwargs)
        DataClass = AERDBL2Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)
