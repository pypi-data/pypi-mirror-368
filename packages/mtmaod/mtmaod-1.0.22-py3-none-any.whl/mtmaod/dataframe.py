import pandas as pd


def filter_prod_high_quality(df):
    """
    过滤高质量数据, "prod_name", "prod_algo", "prod_fqa" 三列必须存在
    """
    if "prod_name" not in df.columns:
        raise ValueError("The column 'prod_name' must be in the DataFrame.")
    if "prod_algo" not in df.columns:
        raise ValueError("The column 'prod_algo' must be in the DataFrame.")
    if "prod_fqa" not in df.columns:
        raise ValueError("The column 'prod_fqa' must be in the DataFrame.")
    _df_DT = df.query(f"prod_algo == 'DT' and prod_fqa >= 3")
    _df_DB = df.query(f"prod_algo == 'DB' and prod_fqa >= 2")
    _df_DTDB = df.query(f"prod_algo == 'DTB' and prod_fqa >= 2")
    _df_MAIAC = df.query(f"prod_algo == 'MAIAC'")
    return pd.concat([_df_DT, _df_DB, _df_DTDB, _df_MAIAC], ignore_index=True).sort_index()
