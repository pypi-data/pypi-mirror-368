import datetime
import os
from typing import Iterable

import numpy as np
import numpy.ma as ma
import pandas as pd

from mtmaod.path import Extractor
from mtmaod.utils.netCDF4 import NetCDF4
from mtmaod.utils.pyhdf import SDS, PyHDF

from ._template import (
    SatelliteProductDataNetCDF4,
    SatelliteProductDataPyHDF,
    SatelliteProductReaderNetCDF4,
    SatelliteProductReaderPyHDF,
)


# ===================================================================================================
class MXD02Data(SatelliteProductDataPyHDF):

    def scale_and_offset(self, data: np.ndarray):
        infos: dict = self.infos()
        radiance_scales = MXD02Data.value_set_decimal(infos.get("reflectance_scales", 1), decimal=None)
        radiance_offsets = MXD02Data.value_set_decimal(infos.get("reflectance_offsets", 0), decimal=None)
        fill_value = infos.get("_FillValue")
        _data = ma.masked_values(data, fill_value, rtol=1e-8, atol=1e-9)
        return radiance_scales * (_data - radiance_offsets)


class MXD02Reader(SatelliteProductReaderPyHDF):
    Product_File_Time_Format = "[.]A%Y%j[.]%H%M[.]"
    LinkedDataClass = MXD02Data

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = PyHDF.read(fp, dataset_name, *args, **kwargs)
        DataClass = MXD02Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)

    @staticmethod
    def table_scales_and_offsets(fp, *args, **kwargs):
        bands = ["EV_1KM_RefSB", "EV_1KM_Emissive", "EV_250_Aggr1km_RefSB", "EV_500_Aggr1km_RefSB"]
        columns = [
            "band_names",
            "reflectance_scales",
            "reflectance_offsets",
            "radiance_scales",
            "radiance_offsets",
            "corrected_counts_scales",
            "corrected_counts_offsets",
        ]
        indexes_string = "1,2,3,4,5,6,7,8,9,10,11,12,13lo,13hi,14lo,14hi,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36"
        indexes = indexes_string.split(",")
        df_list = []
        for band in bands:
            info = MXD02Reader.read(fp, band, *args, **kwargs).infos()
            info["band_names"] = info.get("band_names").split(",")
            _info = {k: info[k] for k in columns if k in info}
            df_list.append(pd.DataFrame(_info))
        return pd.concat(df_list, ignore_index=True).set_index("band_names").loc[indexes, :]


# ===================================================================================================
class MXD04L2Reader(SatelliteProductReaderPyHDF):
    Product_File_Time_Format = "[.]A%Y%j[.]%H%M[.]"
    LinkedDataClass = SatelliteProductDataPyHDF
    Band_Latitude = "Latitude"
    Band_Longitude = "Longitude"

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = PyHDF.read(fp, dataset_name, *args, **kwargs)
        DataClass = MXD04L2Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)


# ===================================================================================================
class MXD09Reader(SatelliteProductReaderPyHDF):
    Product_File_Time_Format = "[.]A%Y%j[.]"
    LinkedDataClass = SatelliteProductDataPyHDF

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = PyHDF.read(fp, dataset_name, *args, **kwargs)
        DataClass = MXD09Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)


# ===================================================================================================
class MXDLabGridReader(SatelliteProductReaderNetCDF4):
    Product_File_Time_Format = "[.]%Y%j%H%M%S[.]"  # MOD021KM_L.1000.2021001040500.H26V05.000000.h5
    LinkedDataClass = SatelliteProductDataNetCDF4

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = NetCDF4.read(fp, dataset_name, *args, **kwargs)
        DataClass = MXDLabGridReader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)


# ===================================================================================================
class MCD19A2Reader(SatelliteProductReaderPyHDF):
    Product_File_Time_Format = "MCD19A2[.]A%Y%j[.]"
    LinkedDataClass = SatelliteProductDataPyHDF

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = PyHDF.read(fp, dataset_name, *args, **kwargs)
        DataClass = MCD19A2Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)

    @staticmethod
    def list_orbit_times(fp):
        return [i for i in fp.attributes()["Orbit_time_stamp"].split(" ") if i]

    @staticmethod
    def extract_orbit_times_infos(times: list):
        times_infos = []
        for idx, _time in enumerate(times):
            satellite = _time[-1:]
            layer_time = datetime.datetime.strptime(_time[:-1], "%Y%j%H%M")
            layer_time = layer_time.replace(tzinfo=datetime.timezone.utc)
            _time_info = {"satellite": satellite, "layeridx": idx, "datetime": layer_time}
            times_infos.append(_time_info)
        return times_infos

    @staticmethod
    def open_adjacent_files(data_file: str, data_files: Iterable, border_flags: tuple = None, *args, **kwargs):
        # MCD19A2.A2020001.h04v09.061.2023132152021.hdf
        # 获取hv
        func_ext_hv = Extractor.file_hv()
        hv = func_ext_hv(data_file)
        # 获取日期
        str_date = os.path.basename(data_file).split(".")[1]  # 获取日期, A2020001
        data_files = list(filter(lambda x: str_date in x, data_files))  # 只考虑同一天的数据
        # 获取数据文件字典
        data_files_dict = {func_ext_hv(i): i for i in data_files}  # data_files 中 hv 只能有一个, 因此不考虑hv重复的情况
        # 获取邻近文件hv
        h, v = int(hv[1:3]), int(hv[4:6])
        h_min, h_max = str(h - 1).zfill(2) if (h - 1) >= 0 else "35", str(h + 1).zfill(2) if (h + 1) <= 35 else "00"
        v_min, v_max = str(v - 1).zfill(2), str(v + 1).zfill(2)
        h, v = str(h).zfill(2), str(v).zfill(2)
        # 选取邻近文件
        adjacent_dict = {
            "nw": {"hv": f"h{h_min}v{v_min}"},
            "n": {"hv": f"h{h}v{v_min}"},
            "ne": {"hv": f"h{h_max}v{v_min}"},
            "w": {"hv": f"h{h_min}v{v}"},
            "c": {"hv": f"h{h}v{v}"},
            "e": {"hv": f"h{h_max}v{v}"},
            "sw": {"hv": f"h{h_min}v{v_max}"},
            "s": {"hv": f"h{h}v{v_max}"},
            "se": {"hv": f"h{h_max}v{v_max}"},
        }
        if border_flags is None:
            border_flags = (True, True, True, True)
        left, right, top, bottom = border_flags
        if not right:
            adjacent_dict.pop("ne", None)
            adjacent_dict.pop("e", None)
            adjacent_dict.pop("se", None)
        if not left:
            adjacent_dict.pop("nw", None)
            adjacent_dict.pop("w", None)
            adjacent_dict.pop("sw", None)
        if not top:
            adjacent_dict.pop("nw", None)
            adjacent_dict.pop("n", None)
            adjacent_dict.pop("ne", None)
        if not bottom:
            adjacent_dict.pop("sw", None)
            adjacent_dict.pop("s", None)
            adjacent_dict.pop("se", None)

        # 打开邻近文件, 将文件对象保存到字典中
        for k, info in adjacent_dict.items():
            _file = data_files_dict.get(info["hv"])
            if _file is None or os.path.exists(_file) is False:
                continue
            _file_name = os.path.basename(_file)
            if str_date not in _file_name:
                continue
            adjacent_dict[k]["fp"] = PyHDF.open(_file, *args, **kwargs)
        return adjacent_dict

    @staticmethod
    def merge_adjascent_files(adjacent_infos: dict, dataset_name, *args, **kwargs):
        datetime_left_border = datetime.timedelta(minutes=-10)
        datetime_right_border = datetime.timedelta(minutes=10)
        # 读取中心block的数据(必须步骤)，并构造一个3x3block的空数组，中心block的数据填充到中心位置
        central_data = MCD19A2Reader.read(adjacent_infos["c"]["fp"], dataset_name, *args, **kwargs)[:]
        band, height, width = central_data.shape[-3:]  # 获取后三个维度的大小
        arr = ma.zeros((band, height * 3, width * 3), dtype=central_data.dtype)
        arr.mask = True
        arr[:, height : 2 * height, width : 2 * width] = central_data
        # 直接获取中心block的时间信息并保存，避免重复生成
        central_times_strs = MCD19A2Reader.list_orbit_times(adjacent_infos["c"]["fp"])
        central_times_infos = MCD19A2Reader.extract_orbit_times_infos(central_times_strs)
        # 获取邻近block的时间信息，并进行对比，获取在一定时间范围内的数据
        time_usable_dict = {}
        for k in adjacent_infos.keys():
            if k == "c":
                continue
            _fp = adjacent_infos[k].get("fp")
            if adjacent_infos[k].get("fp") is None:
                continue
            adjacent_times_strs = MCD19A2Reader.list_orbit_times(_fp)
            adjacent_times_infos = MCD19A2Reader.extract_orbit_times_infos(adjacent_times_strs)
            for _central_time_info in central_times_infos:
                for _adjacent_time_info in adjacent_times_infos:
                    if _adjacent_time_info["satellite"] != _central_time_info["satellite"]:
                        continue
                    if (
                        datetime_left_border
                        <= (_adjacent_time_info["datetime"] - _central_time_info["datetime"])
                        <= datetime_right_border
                    ):
                        time_usable_dict.setdefault(k, []).append([_central_time_info, _adjacent_time_info])
                        break
        # 读取邻近block的数据，并填充到对应位置
        for k in time_usable_dict.keys():
            for _central_time_info, _adjacent_time_info in time_usable_dict[k]:
                _fp = adjacent_infos[k].get("fp")
                if adjacent_infos[k].get("fp") is None:
                    continue
                dp = MCD19A2Reader.read(_fp, dataset_name, *args, **kwargs)[:]
                layeridx_central = _central_time_info["layeridx"]
                layeridx_adjacent = _adjacent_time_info["layeridx"]
                if k == "nw":
                    arr[layeridx_central, :height, :width] = dp[layeridx_adjacent, :, :]
                elif k == "n":
                    arr[layeridx_central, :height, width : 2 * width] = dp[layeridx_adjacent, :, :]
                elif k == "ne":
                    arr[layeridx_central, :height, 2 * width :] = dp[layeridx_adjacent, :, :]
                elif k == "w":
                    arr[layeridx_central, height : 2 * height, :width] = dp[layeridx_adjacent, :, :]
                elif k == "e":
                    arr[layeridx_central, height : 2 * height, 2 * width :] = dp[layeridx_adjacent, :, :]
                elif k == "sw":
                    arr[layeridx_central, 2 * height :, :width] = dp[layeridx_adjacent, :, :]
                elif k == "s":
                    arr[layeridx_central, 2 * height :, width : 2 * width] = dp[layeridx_adjacent, :, :]
                elif k == "se":
                    arr[layeridx_central, 2 * height :, 2 * width :] = dp[layeridx_adjacent, :, :]
                else:
                    raise ValueError(f"Unknown key: {k}")
        return arr
