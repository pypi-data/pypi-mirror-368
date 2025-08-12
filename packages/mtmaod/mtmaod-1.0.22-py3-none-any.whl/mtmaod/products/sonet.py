import pandas as pd
import numpy as np
import warnings
from .aeronet import group_arr_by_nan
from .aeronet import LEVReader as AeronetReader

warnings.filterwarnings("ignore", message=".*Covariance of the parameters could.*")

# 检查swifter模块是否开启
try:
    from swifter import set_defaults

    set_defaults(progress_bar=False)
    _swifter_enable = True
except ImportError:
    _swifter_enable = False
    pass


class LEVReader(AeronetReader):
    """
    LEVReader实例的df变量即为读取的数据

    LEVReader实例的方法若不指定dataframe参数, 则默认使用实例的df变量作为数据源
    """

    def __init__(self, filepath, header=4) -> None:
        with open(filepath, "r", encoding="Windows 1252") as f:
            txt = f.read()
        txt = txt.replace("  ", " ").replace("  ", " ").replace("  ", " ")
        with open(filepath, "w", encoding="Windows 1252") as f:
            f.write(txt)
        self.df = pd.read_csv(filepath, header=header, sep=" ", encoding="Windows 1252")
        self.df = self.df.replace(-999.0, np.nan)
        self.df = self._convert_time_to_utc()

    def _get_dataframe(self, dataframe=None):
        if dataframe is None:
            df = self.df.copy()
        else:
            df = dataframe.copy()
        return df

    def filter_high_quality_aod_rows(self, dataframe=None):
        """筛选出质量较高的AOD数据行, 要求AOD_440nm, AOD_500nm, AOD_675nm, AOD_870nm均大于0

        Parameters
        ----------
        dataframe : DataFrame
            数据源

        Returns
        -------
        DataFrame
            筛选后的数据
        """
        df = self._get_dataframe(dataframe)
        df = df[df["440nm"] > 0.0]
        df = df[df["500nm"] > 0.0]
        df = df[df["675nm"] > 0.0]
        df = df[df["870nm"] > 0.0]
        return df.copy()

    def _convert_time_to_utc(self, dataframe=None):
        df = self._get_dataframe(dataframe)
        df.loc[:, "CustomDate"] = df.loc[:, "date"] + " " + df.loc[:, "time(UTC)"]
        df.loc[:, "CustomDate"] = pd.to_datetime(df.loc[:, "CustomDate"], format="%d/%m/%Y %H:%M:%S", utc=True)
        df = df.infer_objects()
        df = df.set_index("CustomDate")
        df = df.sort_index()
        return df

    def _only_keep_aod_column(self, dataframe=None):
        """只保留AOD列, 并将列名改为波长名"""
        df = self._get_dataframe(dataframe)
        # 删除非AOD以及无效的数据列
        columns = [title for title in df.columns if title.endswith("nm")]
        df = df.loc[:, columns]
        df = df.replace(-999.0, np.nan)
        df = df.dropna(axis=1, how="all")
        # 将数据列名改为波长名
        columns = df.columns
        columns = [i.replace("AOD_", "").replace("nm", "") for i in columns]
        df.columns = columns
        # 根据波长大小对列名进行排序
        try:
            columns = [(int(i), i) for i in columns]
        except Exception as e:
            print("Aeronet数据格式与代码不同,请修改!")
            raise e
        columns = sorted(columns, key=lambda x: x[0])
        _, columns = zip(*columns)
        df = df.loc[:, columns]
        return df.copy()

    def compare(self, dataframe=None, filter_high_quality=True, wavelength=500, methods=None):
        """对比不同AOD插值方法在xxxnm波段的表现, 并输出均值、最大值、耗时, 默认使用500nm波段"""
        import time

        df = self._get_dataframe(dataframe)
        df_src = df.query(f"{wavelength}nm > 0.0")
        if filter_high_quality:
            df_src = df_src.query("440nm > 0.0")
            df_src = df_src.query("500nm > 0.0")
            df_src = df_src.query("675nm > 0.0")
            df_src = df_src.query("870nm > 0.0")
        print("数据筛选与否: filter_high_quality = " + str(filter_high_quality))
        df = pd.DataFrame(index=df_src.index)
        df["true"] = df_src[f"{wavelength}nm"]
        df_src = df_src.drop(columns=[f"{wavelength}nm"])

        if methods is None:
            methods = ["Angstrom", "quadratic_spline", "cubic_spline", "numpydeg2_polyfit", "numpydeg3_polyfit"]

        for method in methods:
            name = method.split("_")[0]
            t_start = time.time()
            df[name] = self.interp_aod_xxxnm(dataframe=df_src, method=method, wavelength=wavelength)
            t_spended = time.time() - t_start
            bias = np.abs(df[name] - df["true"])
            print(
                "{:15s}: 均误差{:10.6f}, 最大误差{:10.6f}, 耗时{:6.3f}s".format(
                    name, bias.mean(), bias.max(), t_spended
                )
            )
