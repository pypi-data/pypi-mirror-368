import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore", message=".*Covariance of the parameters could.*")

# 检查swifter模块是否开启
try:
    from swifter import set_defaults

    set_defaults(progress_bar=False)
    _swifter_enable = True
except ImportError:
    _swifter_enable = False
    pass


def group_arr_by_nan(arr):
    """将数组按nan分组, 返回字典, key为非nan的索引, value为对应的行索引"""
    index_dict = {}
    for idx, t in enumerate(arr):
        a = ",".join(map(str, np.where(~np.isnan(t))[0]))
        if a in index_dict:
            index_dict[a].append(idx)
        else:
            index_dict[a] = [idx]
    return index_dict


class LEVReader:
    """
    LEVReader实例的df变量即为读取的数据

    LEVReader实例的方法若不指定dataframe参数, 则默认使用实例的df变量作为数据源
    """

    def __init__(self, filepath, header=6) -> None:
        self.df = pd.read_csv(filepath, header=header, encoding="Windows 1252")
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
        df = df.query("AOD_440nm > 0.0")
        df = df.query("AOD_500nm > 0.0")
        df = df.query("AOD_675nm > 0.0")
        df = df.query("AOD_870nm > 0.0")
        return df.copy()

    def _convert_time_to_utc(self, dataframe=None):
        df = self._get_dataframe(dataframe)
        df.loc[:, "CustomDate"] = df.loc[:, "Date(dd:mm:yyyy)"] + " " + df.loc[:, "Time(hh:mm:ss)"]
        df.loc[:, "CustomDate"] = pd.to_datetime(df.loc[:, "CustomDate"], format="%d:%m:%Y %H:%M:%S", utc=True)
        df = df.infer_objects()
        df = df.set_index("CustomDate")
        df = df.sort_index()
        return df

    def _only_keep_aod_column(self, dataframe=None):
        """只保留AOD列, 并将列名改为波长名"""
        df = self._get_dataframe(dataframe)
        # 删除非AOD以及无效的数据列
        columns = [title for title in df.columns if title.startswith("AOD_") and "Empty" not in title]
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

    def interp_aod_xxxnm(self, dataframe=None, method="numpydeg2_polyfit", wavelength: float = 550) -> np.ndarray:
        """插值AOD到xxxnm波段

        Parameters
        ----------
        dataframe : pandas.DataFrame, optional
            输入的原始数据, 默认值为 None
        method : str, optional
            插值方法, 默认值为 "numpydeg2_polyfit". 可选值有: "linear","nearest", "nearest-up", "zero_spline", "slinear_spline", "quadratic_spline", "cubic_spline", "numpydeg2_polyfit", "numpydeg3_polyfit", "scipy_curvefit", "Angstrom", "cubic+scipy"

        wavelength : float, optional
            要插值的目标波段, 默认值为 550

        Returns
        -------
        np.ndarray
            插值后的AOD值
        """
        dataframe = self._get_dataframe(dataframe)
        if method in [
            "linear",
            "nearest",
            "nearest-up",
            "zero_spline",
            "slinear_spline",
            "quadratic_spline",
            "cubic_spline",
        ]:
            from scipy.interpolate import interp1d

            # 采用scipy的插值方法
            df_aod = self._only_keep_aod_column(dataframe.copy())
            x = np.array(list(map(int, df_aod.columns)))
            y = df_aod.to_numpy()
            method_real = method.replace("_spline", "")  # 为了兼容scipy的插值参数格式, 去掉_spline后缀
            group_dict = group_arr_by_nan(y)
            series_list = []
            for key in group_dict:
                columns = list(map(int, key.split(",")))
                x_temp = x[columns]
                if (method_real == "cubic" and len(x_temp) < 4) or min(x_temp) > wavelength or max(x_temp) < wavelength:
                    yfit_temp = np.full(len(group_dict[key]), np.nan)
                    series_list.append(pd.Series(data=yfit_temp, index=group_dict[key]))
                    continue
                y_temp = y[group_dict[key], :][:, columns]
                f = interp1d(x=x_temp, y=y_temp, kind=method_real, bounds_error=False)
                yfit_temp = f(wavelength)
                series_list.append(pd.Series(data=yfit_temp, index=group_dict[key]))
            yfit = pd.concat(series_list).sort_index()
        elif method in ["scipy_curvefit"]:
            from scipy.optimize import curve_fit

            def quadratic_polynomial_formula(x, a0, a1, a2):
                """二次多项式公式, 用于scipy.optimize.curve_fit(), 用于拟合AOD数据"""
                return np.exp(a0 + a1 * np.log(x) + a2 * np.log(x) ** 2)

            def polyfit2(df, wavelength=550, x=None):
                """单个数据行的AOD插值函数, 调用quadratic_polynomial_formula"""
                # 提取要拟合的数据列
                y = df.to_numpy()
                params, _ = curve_fit(quadratic_polynomial_formula, x, y, check_finite=False, nan_policy="omit")
                # print(params)
                yfit = quadratic_polynomial_formula(wavelength, *params)
                return yfit

            # https://blog.csdn.net/weixin_42182090/article/details/131018277
            df_aod = self._only_keep_aod_column(dataframe.copy())
            x = np.array(list(map(int, df_aod.columns)))
            if _swifter_enable:
                yfit = df_aod.swifter.apply(polyfit2, axis=1, wavelength=wavelength, x=x)
            else:
                warnings.warn("no module 'swifter' for useing multi cpus.")
                yfit = df_aod.apply(polyfit2, axis=1, wavelength=wavelength, x=x)
        elif method in ["numpydeg2_polyfit"]:
            df_aod = self._only_keep_aod_column(dataframe.copy())
            aod_columns = np.array(list(map(int, df_aod.columns)))
            x = np.log(np.array(list(map(int, df_aod.columns))))
            y = np.log(np.where(df_aod.to_numpy() <= 0, np.nan, df_aod.to_numpy()))
            # 分组拟合,防止nan值影响拟合结果
            group_dict = group_arr_by_nan(y)
            series_list = []
            for key in group_dict:
                idx_columns = list(map(int, key.split(",")))
                num_columns = aod_columns[idx_columns]
                x_temp = x[idx_columns]
                if len(x_temp) < 3 or min(num_columns) > wavelength or max(num_columns) < wavelength:
                    yfit_temp = np.full(len(group_dict[key]), np.nan)
                    series_list.append(pd.Series(data=yfit_temp, index=group_dict[key]))
                    continue
                y_temp = y[group_dict[key], :][:, idx_columns]
                coef = np.polyfit(x_temp, y_temp.T, deg=2)
                yfit_temp = np.exp(np.polyval(coef, np.log(wavelength)))
                series_list.append(pd.Series(data=yfit_temp, index=group_dict[key]))
            yfit = pd.concat(series_list).sort_index()
        elif method in ["numpydeg3_polyfit"]:
            df_aod = self._only_keep_aod_column(dataframe.copy())
            aod_columns = np.array(list(map(int, df_aod.columns)))
            x = np.log(np.array(list(map(int, df_aod.columns))))
            y = np.log(np.where(df_aod.to_numpy() <= 0, np.nan, df_aod.to_numpy()))
            # 分组拟合,防止nan值影响拟合结果
            group_dict = group_arr_by_nan(y)
            series_list = []
            for key in group_dict:
                idx_columns = list(map(int, key.split(",")))
                num_columns = aod_columns[idx_columns]
                x_temp = x[idx_columns]
                if len(x_temp) < 4 or min(num_columns) > wavelength or max(num_columns) < wavelength:
                    yfit_temp = np.full(len(group_dict[key]), np.nan)
                    series_list.append(pd.Series(data=yfit_temp, index=group_dict[key]))
                    continue
                y_temp = y[group_dict[key], :][:, idx_columns]
                coef = np.polyfit(x_temp, y_temp.T, deg=3)
                yfit_temp = np.exp(np.polyval(coef, np.log(wavelength)))
                series_list.append(pd.Series(data=yfit_temp, index=group_dict[key]))
            yfit = pd.concat(series_list).sort_index()
        elif method in ["Angstrom"]:
            df_raw = dataframe.copy()
            df_raw["440-675_Angstrom_Exponent"] = df_raw["440-675_Angstrom_Exponent"].astype(float)
            yfit = df_raw.apply(
                lambda x: x["AOD_440nm"] * np.power((wavelength / 440), -x["440-675_Angstrom_Exponent"]), axis=1
            )
        elif method in ["cubic+scipy"]:
            yfit_scipy = self.interp_aod_xxxnm(dataframe=dataframe, method="scipy_curvefit", wavelength=wavelength)
            yfit_cubic = self.interp_aod_xxxnm(dataframe=dataframe, method="cubic_spline", wavelength=wavelength)
            yfit = (yfit_scipy + yfit_cubic) / 2
        else:
            raise ValueError("method参数错误")
        return np.array(yfit)

    def interp_aod_xxxtime(
        self,
        srcdata: pd.DataFrame,
        objtime: pd.DataFrame,
        method: str = "average",
        time_range: tuple = (-1800, 1800),
    ) -> pd.DataFrame:
        """插值AOD到指定时间

        Parameters
        ----------
        srcdata : pd.DataFrame
            原始的数据,一般为Aeronet站点数据, 默认值为 None
        objtime : pd.DataFrame
            目标时刻数据,一般为卫星产品的过境时刻,必须含有"timestamp"列,存储UTC时刻,或者数据的索引为UTC的pandas.datatime64类型
        method : str, optional
            插值的方法,有"average"和"linear"两种,average会取一段时间内数据平均,linear会进行相邻时刻数据的线性插值, 默认值为"average"
        time_range : tuple, optional
            时间范围,单位为秒,以目标时刻为基准(目标时刻为0)。默认值为(-1800, 1800),-1800表示目标时刻前1800秒,1800表示目标时刻后1800秒,将在这前后半小时内进行插值操作。

        Returns
        -------
        pd.DataFrame
            插值后的数据,包含有两列,第一列为插值后的AOD值,第二列为插值的计数,即插值用到的数据个数。数据的索引为数据的排序数目,即第几个数据。
        """
        # dataframe 必须 包含 timestamp 列
        # timestamps 必须 包含 timestamp 列
        srcdata = srcdata.copy()
        # 检查输入参数
        if isinstance(srcdata, pd.Series):
            srcdata = pd.DataFrame(srcdata)
        assert isinstance(srcdata, pd.DataFrame), "srcdata 必须是一个Pandas 中的 DataFrame 或其子类"
        assert isinstance(objtime, pd.DataFrame), "objtime 必须是一个Pandas 中的 DataFrame 或其子类"
        if (
            pd.api.types.is_datetime64_dtype(srcdata.index) or pd.api.types.is_datetime64tz_dtype(srcdata.index)
        ) and "timestamp" not in srcdata.columns:
            srcdata["timestamp"] = [i.timestamp() for i in srcdata.index]
        assert "timestamp" in srcdata.columns, "srcdata 必须 包含 timestamp 列"
        assert "timestamp" in objtime.columns, "objtime 必须 包含 timestamp 列"

        # # 第一步： 获取以目标时间为中心的时间段内的原始数据
        from shapely.geometry import box
        import geopandas as gpd

        # 构造时间box几何序列
        pre_time_offset, post_time_offset = time_range
        gs_obj = gpd.GeoSeries([box(i + pre_time_offset, -1, i + post_time_offset, 1) for i in objtime["timestamp"]])
        # 原始数据点转为point几何
        gs_src = gpd.GeoSeries(gpd.points_from_xy(srcdata["timestamp"], 0))
        # 获取查找表,此时的lookup_table是一个二维数组, 每一列表示一个目标和来源的匹配关系,第一行是目标的索引,第二行是来源的索引
        lookup_table = gs_src.sindex.query(gs_obj, predicate="intersects")

        # # 第二步： 根据匹配关系,插值目标时间点的AOD值
        df_src = srcdata.iloc[lookup_table[1]].copy()
        df_src["_idx"] = lookup_table[0]
        if method == "average":
            df_src.drop(columns=["timestamp"], inplace=True)
            result_temp = df_src.groupby("_idx").mean()
            counts = df_src.groupby("_idx").count()
            result_temp["counts"] = counts
            result_temp.index = np.array(objtime.index)[np.unique(lookup_table[0])]  # 将索引改为目标时间点的索引
        elif method == "linear":
            # 筛选能被插值的数据时间
            counts = df_src.groupby("_idx").count().iloc[:, 0]
            counts = counts[(counts > 1).values]
            objtime_interp = objtime.iloc[counts.index]
            # 插值
            result_temp = pd.DataFrame(index=objtime_interp.index)
            for column in df_src.columns:
                if column in ["timestamp", "_idx", "counts"]:
                    continue
                result_temp[column] = np.interp(objtime_interp["timestamp"], srcdata["timestamp"], srcdata[column])
            # 添加计数列,由于是线性插值,所以计数列的值都是2
            result_temp["counts"] = 2
        else:
            raise ValueError("method参数错误")
        # 为插值失败的数据添加计数列,计数列的值为0
        result = pd.DataFrame(index=objtime.index, columns=result_temp.columns)
        result["counts"] = 0
        result.update(result_temp)
        return result

    def compare(self, dataframe=None, filter_high_quality=True, wavelength=500, methods=None):
        """对比不同AOD插值方法在xxxnm波段的表现, 并输出均值、最大值、耗时, 默认使用500nm波段"""
        import time

        df = self._get_dataframe(dataframe)
        df_src = df.query(f"AOD_{wavelength}nm > 0.0")
        if filter_high_quality:
            df_src = df_src.query("AOD_440nm > 0.0")
            df_src = df_src.query("AOD_500nm > 0.0")
            df_src = df_src.query("AOD_675nm > 0.0")
            df_src = df_src.query("AOD_870nm > 0.0")
        print("数据筛选与否: filter_high_quality = " + str(filter_high_quality))
        df = pd.DataFrame(index=df_src.index)
        df["true"] = df_src[f"AOD_{wavelength}nm"]
        df_src = df_src.drop(columns=[f"AOD_{wavelength}nm"])

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
