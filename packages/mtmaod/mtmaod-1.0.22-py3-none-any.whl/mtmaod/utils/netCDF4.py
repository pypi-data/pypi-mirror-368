import netCDF4 as nc


class NetCDF4:
    @staticmethod
    def open(file_path, mode="r", *args, **kwargs):
        return nc.Dataset(file_path, mode=mode)
    
    @staticmethod
    def read(fp, dataset_name, *args, **kwargs):
        return NetCDF4._jump(fp, dataset_name)

    @staticmethod
    def list_datasets(fp, full=False):
        datasets_name = list(NetCDF4._walk(fp))
        if not full:
            return datasets_name
        else:
            return {name: NetCDF4.get_dataset_info_from_fp(fp, name) for name in datasets_name}
        
    @staticmethod
    def _walk(fp, path=""):
        if not len(path) or path[-1] != "/":
            path += "/"
        current_variables = list(fp.variables.keys())
        for variable in current_variables:
            yield path + variable
        current_groups = list(fp.groups.keys())
        for group in current_groups:
            yield from NetCDF4._walk(fp.groups[group], path + group)

    @staticmethod
    def _jump(fp, path="/"):
        path_list = path.lstrip("/").split("/")
        if not len(path_list):
            return fp
        subnode_fp = fp.__getitem__(path_list[0])
        subnode_path = "/" + "/".join(path_list[1:])
        if len(path_list) == 1:
            return subnode_fp
        else:
            return NetCDF4._jump(subnode_fp, subnode_path)
        
    @staticmethod
    def get_dataset_info_from_dp(dp):
        info_dict = dp.__dict__
        info_dict.update({
            "dataset_name": dp.group().path + "/" + dp.name,
            "dataset_dims": dp.shape,
            "dataset_type": dp.datatype.name
        })
        return info_dict

    @staticmethod
    def get_dataset_info_from_fp(fp, dataset_name):
        return NetCDF4.get_dataset_info_from_dp(NetCDF4._jump(fp, dataset_name))