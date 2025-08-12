from pyhdf.SD import SD, SDC, SDS


class PyHDF:
    DATATYPES = {
        4: "char",
        3: "uchar",
        20: "int8",
        21: "uint8",
        22: "int16",
        23: "uint16",
        24: "int32",
        25: "uint32",
        5: "float32",
        6: "float64",
    }
    OPENMODES = {"r": SDC.READ, "w": SDC.WRITE}
    @staticmethod
    def open(file_path:str, mode='r', *args, **kwargs):
        return SD(file_path, mode=PyHDF.OPENMODES[mode], *args, **kwargs)

    @staticmethod
    def read(fp:SD, dataset_name:str):
        return fp.select(dataset_name)
    
    @staticmethod
    def list_datasets(fp:SD, full=False):
        datasets_name = list(fp.datasets().keys())
        if not full:
            return datasets_name
        else:
            return {name: PyHDF.get_dataset_info_from_fp(fp, name) for name in datasets_name}

    @staticmethod
    def get_dataset_info_from_dp(dp:SDS):
        # https://hdfeos.github.io/pyhdf/modules/SD.html
        attrs = dp.attributes()
        _info_list = dp.info()
        _info_dict = {
            "dataset_name": _info_list[0], 
            "dataset_rank": _info_list[1], 
            "dataset_dims": _info_list[2], 
            "dataset_type": PyHDF.DATATYPES[_info_list[3]]
        }
        _info_dict.update(attrs)
        return _info_dict
     
    @staticmethod
    def get_dataset_info_from_fp(fp:SD, dataset_name:str):
        # https://hdfeos.github.io/pyhdf/modules/SD.html
        return PyHDF.get_dataset_info_from_dp(fp.select(dataset_name))
    
