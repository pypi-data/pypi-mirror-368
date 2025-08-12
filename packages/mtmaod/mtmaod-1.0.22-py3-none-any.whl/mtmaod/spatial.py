import numpy as np
import numpy.ma as ma
from scipy.interpolate import griddata

try:
    from geopy import distance
except ImportError:
    pass


def is_point_in_gring(plat: float, plon: float, gringlat: np.ndarray, gringlon: np.ndarray):
    if (min(gringlat) <= plat <= max(gringlat)) and (min(gringlon) <= plon <= max(gringlon)):
        return True
    else:
        return False


def query_index_of_spatial_nearest_point(plat: float, plon: float, dlat: np.ndarray, dlon: np.ndarray):
    # 获取经纬度数组中离指定点最近的点在经纬度数组中的索引
    dlat = dlat if isinstance(dlat, ma.MaskedArray) else ma.array(dlat, mask=np.isnan(dlat))
    dlon = dlon if isinstance(dlon, ma.MaskedArray) else ma.array(dlon, mask=np.isnan(dlon))
    # 检测是否为全Masked数组
    if np.all(dlat.mask) or np.all(dlon.mask):
        return -1, -1, -1
    # 计算距离
    temp_res_array = (dlat - plat) ** 2 + (dlon - plon) ** 2
    if np.all(temp_res_array.mask):
        return -1, -1, -1
    # 获取最小值的索引
    temp_idx = temp_res_array.argmin()
    lat_idx, lon_idx = np.unravel_index(temp_idx, temp_res_array.shape)
    # 返回索引和距离值(平方和)
    return lat_idx, lon_idx, temp_res_array[lat_idx, lon_idx]


def get_point_buffer_box(plat: float, plon: float, buffer: float):
    gdistance = distance.distance(kilometers=buffer)
    north = gdistance.destination((plat, plon), bearing=0)
    northeast = gdistance.destination(north, bearing=90)
    northwest = gdistance.destination(north, bearing=270)
    south = gdistance.destination((plat, plon), bearing=180)
    southeast = gdistance.destination(south, bearing=90)
    southwest = gdistance.destination(south, bearing=270)
    east = gdistance.destination((plat, plon), bearing=90)
    west = gdistance.destination((plat, plon), bearing=270)
    dlat = np.array(
        [
            north.latitude,
            northeast.latitude,
            east.latitude,
            southeast.latitude,
            south.latitude,
            southwest.latitude,
            west.latitude,
            northwest.latitude,
        ]
    )
    dlon = np.array(
        [
            north.longitude,
            northeast.longitude,
            east.longitude,
            southeast.longitude,
            south.longitude,
            southwest.longitude,
            west.longitude,
            northwest.longitude,
        ]
    )
    return dlat, dlon


class NearestGridInterpolation:
    def __init__(self, points, xi) -> None:
        if isinstance(points, ma.MaskedArray):
            points = points.filled(np.nan)
        self.mask = np.sum(np.isnan(points), axis=1) == 0
        self.points = points[self.mask]
        self.values = np.arange(len(self.points))
        self.xi = xi
        self.idx = griddata(self.points, self.values, xi, method="nearest").astype(int)
        pass

    def interpolate(self, values):
        values = values[self.mask]
        if len(values) != len(self.values):
            raise ValueError("The length of values must be equal to the length of points.")
        return values[self.idx]

    @staticmethod
    def latlon2points(dlat: np.ndarray, dlon: np.ndarray):
        """将经纬度2D数据转换为(n, D)的点坐标数组"""
        return np.column_stack((dlat.flatten(), dlon.flatten()))

    @staticmethod
    def latlon2grid(dlat: np.ndarray, dlon: np.ndarray, step: float = 0.01):
        """将经纬度2D数据重采样成为规则的网格经纬度2D数据"""
        lat_min, lat_max = np.nanmin(dlat), np.nanmax(dlat)
        lon_min, lon_max = np.nanmin(dlon), np.nanmax(dlon)
        lat_min = np.floor(lat_min / step) * step
        lat_max = np.ceil(lat_max / step) * step
        lon_min = np.floor(lon_min / step) * step
        lon_max = np.ceil(lon_max / step) * step
        lat = np.arange(lat_min, lat_max + step, step)
        lon = np.arange(lon_min, lon_max + step, step)
        grid_lat, grid_lon = np.meshgrid(lat, lon)
        return grid_lat, grid_lon
