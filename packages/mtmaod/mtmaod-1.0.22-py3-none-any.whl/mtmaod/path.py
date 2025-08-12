import os, glob
from mtmtool.time import auto_parse_time_with_datefmt
import pandas as pd
from datetime import timezone
import re


class Extractor:
    @staticmethod
    def file_datetime(datefmt: str, *args, **kwargs):
        """按照规则, 获取文件的时间, 并设置时区为UTC

        Parameters
        ----------
        datefmt : str, optional
            文件名中时间的格式, %Y为年, %m为月, %d为月日, %j为年日, %H为时, %M为分, %S为秒, 如果一个文件有多个时间匹配该规则, 取第一个时间为文件时间, by default "A%Y%j.%H%M" (MODIS系列文件的时间格式)
        """
        return lambda x: auto_parse_time_with_datefmt(x, datefmt=datefmt)[0].replace(tzinfo=timezone.utc)

    @staticmethod
    def file_hv(*args, **kwargs):
        """获取文件的HV分区, 额外支持hxxvxx"""
        pattern = re.compile(r"[.](h(?:(?:\d{2})|(?:xx))v(?:(?:\d{2})|(?:xx)))[.]")
        return lambda x: re.findall(pattern, x.lower())[0]


def find_paths_with_extractor(root_dir: str, columns: list, indexes: dict, ext: str = ".hdf") -> pd.DataFrame:
    """寻找同一时刻的文件, 并返回一个DataFrame, 列名即为columns参数中的元素, 可以按需添加时间列

    Parameters
    ----------
    root_dir : str
        根目录, 该目录下的所有子文件夹都会被遍历
    columns : list
        查找的文件类型关键字, 如"MOD02", "MOD03"等
    indexes : dict
        将依据规则将提取结果添加到DataFrame中作为索引, 并以此合并不同的列。
        key为列名, value为一个函数, 该函数接受一个文件路径, 返回一个值
        value参数可以是mtmtool.path.Extractor中的静态方法, 也可以是自定义的函数
    ext : str, optional
        文件的后缀名称列表, 注意必须带'.', by default ".hdf" (MODIS系列文件的后缀名)

    Returns
    -------
    pd.DataFrame
        一个DataFrame, 列名即为columns参数中的元素, 索引为文件的时间, 无效数据为NaN
    """
    # 检查输入参数
    if not os.path.isdir(root_dir):
        raise ValueError(f"root_dir: {root_dir} 不是一个有效的文件夹路径")
    if not isinstance(columns, list) or len(columns) == 0:
        raise ValueError(f"columns: {columns} 不是一个有效的列表")
    if not isinstance(indexes, dict):
        raise ValueError(f"indexes: {indexes} 不是一个有效的字典")
    # 寻找同一时刻的文件, 并返回一个DataFrame, 列名即为columns参数中的元素
    df_list = []
    for file_type in columns:
        # 保存临时数据的字典
        temp_data_dict = {}
        # 遍历所有子文件夹, 寻找符合条件的文件
        path = os.path.join(root_dir, "**", f"*{file_type}*{ext}")  # 通配符 "**" 表示匹配0个或多个子文件夹
        for idx, _path in enumerate(glob.glob(path, recursive=True)):

            _temp_dict = {}
            for k, v in indexes.items():
                try:
                    _temp_dict[k] = v(_path)
                except:
                    pass
            _temp_dict[file_type] = _path
            temp_data_dict[idx] = _temp_dict
        # 将字典转换为DataFrame, 方便后续合并不同列的数据
        _df = pd.DataFrame.from_dict(temp_data_dict, orient="index")
        indexes_names = list(indexes.keys())
        for i in indexes_names:
            if i not in _df.columns:
                _df[i] = None
        if len(indexes_names) > 0:
            _df = _df.set_index(indexes_names)
        df_list.append(_df)

    df: pd.DataFrame = pd.concat(df_list, axis=1, join="outer")  # 按照索引合并不同列的数据
    return df
