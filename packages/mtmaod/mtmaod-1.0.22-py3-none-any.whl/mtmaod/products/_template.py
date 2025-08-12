import numpy as np
import numpy.ma as ma

from mtmaod.utils.netCDF4 import NetCDF4
from mtmaod.utils.pyhdf import SDS, PyHDF


def int2binarystring(num: int, length: int = 0) -> str:
    return bin(num)[2:].zfill(length)


class SatelliteProductDataTemplate:
    def __init__(self) -> None:
        pass

    def infos(self):
        pass

    @staticmethod
    def value_set_decimal(values, decimal=None):
        values = np.array(values)
        values_int = values.astype(int)
        values_decimal = np.round(values, decimal) if decimal is not None else values
        return values_int if values_int == values else values_decimal

    def __getitem__(self, *item) -> np.ma.MaskedArray | np.ndarray:
        pass


class SatelliteProductReaderTemplate:
    Product_File_Time_Format = None
    LinkedDataClass = None
    Band_Latitude = None
    Band_Longitude = None

    @staticmethod
    def open(data_file, *args, **kwargs):
        pass

    @staticmethod
    def read(fp, dataset_name, *args, **kwargs):
        pass

    @staticmethod
    def list_datasets(fp, full: bool = False, *args, **kwargs):
        pass

    @staticmethod
    def read_bit_fields(dp, bit_start_pos: int, bit_end_pos: int, *args, **kwargs) -> np.ma.MaskedArray | np.ndarray:
        # Bit fields within each byte are numbered from the left:
        # 7, 6, 5, 4, 3, 2, 1, 0.
        # The left-most bit (bit 7) is the most significant bit.
        # The right-most bit (bit 0) is the least significant bit.
        # 左开右闭区间，即从bit_start_pos开始，到bit_end_pos结束，不包含bit_end_pos
        if isinstance(dp, SatelliteProductDataTemplate):
            data = np.array(dp.dp[:])
        elif isinstance(dp, np.ndarray) or isinstance(dp, ma.MaskedArray):
            data = dp
        else:
            data = np.array(dp[:])
        return (data >> bit_start_pos) % (2 ** (bit_end_pos - bit_start_pos))


# ===================================================================================================


class SatelliteProductDataPyHDF(SatelliteProductDataTemplate):
    def __init__(self, dp: SDS, isRaw: bool = False, *args, **kwargs) -> None:
        self.dp = dp
        self.isRaw = isRaw
        pass

    def scale_and_offset(self, data: np.ndarray) -> np.ma.MaskedArray:
        infos: dict = self.infos()
        scale_factor = SatelliteProductDataPyHDF.value_set_decimal(infos.get("scale_factor", 1), decimal=8)
        add_offset = SatelliteProductDataPyHDF.value_set_decimal(infos.get("add_offset", 0), decimal=8)
        fill_value = infos.get("_FillValue")
        _data = ma.masked_values(data, fill_value, rtol=1e-8, atol=1e-9)
        return _data * scale_factor + add_offset

    def infos(self):
        return PyHDF.get_dataset_info_from_dp(self.dp)

    def __getitem__(self, *item) -> np.ma.MaskedArray | np.ndarray:
        data = self.dp.__getitem__(*item)
        return self.scale_and_offset(np.array(data)) if not self.isRaw else data


class SatelliteProductReaderPyHDF(SatelliteProductReaderTemplate):
    Product_File_Time_Format = None
    LinkedDataClass = SatelliteProductDataPyHDF
    Band_Latitude = None
    Band_Longitude = None

    @staticmethod
    def open(data_file, *args, **kwargs):
        return PyHDF.open(data_file, *args, **kwargs)

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = PyHDF.read(fp, dataset_name, *args, **kwargs)
        DataClass = SatelliteProductReaderPyHDF.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)

    @staticmethod
    def list_datasets(fp, full: bool = False, *args, **kwargs):
        return PyHDF.list_datasets(fp, full=full, *args, **kwargs)


# ===================================================================================================


class SatelliteProductDataNetCDF4(SatelliteProductDataTemplate):
    def __init__(self, dp, isRaw: bool = False, *args, **kwargs) -> None:
        self.dp = dp
        self.isRaw = isRaw
        pass

    def infos(self):
        return NetCDF4.get_dataset_info_from_dp(self.dp)

    def __getitem__(self, *item) -> np.ma.MaskedArray | np.ndarray:
        data = self.dp.__getitem__(*item)
        return data if not self.isRaw else data.data


class SatelliteProductReaderNetCDF4(SatelliteProductReaderTemplate):
    Product_File_Time_Format = None
    LinkedDataClass = SatelliteProductDataNetCDF4
    Band_Latitude = None
    Band_Longitude = None

    @staticmethod
    def open(data_file, *args, **kwargs):
        return NetCDF4.open(data_file, *args, **kwargs)

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = NetCDF4.read(fp, dataset_name, *args, **kwargs)
        DataClass = SatelliteProductReaderNetCDF4.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)

    @staticmethod
    def list_datasets(fp, full: bool = False, *args, **kwargs):
        return NetCDF4.list_datasets(fp, full=full, *args, **kwargs)
