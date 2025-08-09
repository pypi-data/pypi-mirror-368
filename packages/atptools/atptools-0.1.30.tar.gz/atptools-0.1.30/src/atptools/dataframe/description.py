import pandas as pd

from ..dict_default import DictDefault


def df_description_str(df: pd.DataFrame) -> str:
    number_of_coluumns = len(df.columns)

    string: str = ""
    string += "DataFrame describe [start]: -------------------------------------------"
    string += f"\nShape: {df.shape}"
    string += f"\nColumns [{number_of_coluumns}]:\n{df.columns}"
    string += f"\nRows [{len(df.index)}]:\n{df.index}"
    string += f"\nHead:\n{df.head()}"
    string += f"\nTail:\n{df.tail()}"

    string += f"\nDescribe:\n{df_describe(df)}"
    string += (
        "\nDataFrame describe [end]: ---------------------------------------------"
    )
    return string


def df_description_dict_default(df: pd.DataFrame) -> DictDefault:
    ret = DictDefault()
    ret["shape"] = df.shape
    ret["columns"] = df.columns.tolist()
    ret["index"] = df.index.tolist()
    df_des = df_describe(df)
    ret["describe"] = df_des.to_dict(orient="index")

    return ret


def df_describe(df: pd.DataFrame) -> pd.DataFrame:
    df_describe = df.describe(include="all").T
    df_nan_count = df.isna().sum()
    df_nan_count.name = "count_nan"
    df_dtypes = df.dtypes
    df_dtypes.name = "dtypes"
    df_dtypes.astype(str)
    return pd.concat([df_describe, df_nan_count, df_dtypes], axis=1)
