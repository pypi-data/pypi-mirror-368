import pandas as pd


def pandas_counter_reset_detector(
    df: pd.DataFrame | pd.Series,
    value_col: str = "value",
) -> tuple[pd.Index, pd.Index]:
    """_summary_

    Parameters
    ----------
    df : pd.DataFrame | pd.Series
        pandas DataFrame or Series to detect counter resets
    value_col : str, optional
        _description_, by default "value"

    Returns
    -------
    tuple[pd.Index, pd.Index]
        Return a tuple of two pandas Indexes. The first Index contains the indexes where the counter resets to zero. The second Index is the first one shifted by -1.

    Raises
    ------
    ValueError
        If df is not a pandas Series or DataFrame
    """
    if isinstance(df, pd.Series):
        df_local = df
    elif isinstance(df, pd.DataFrame):
        df_local = df[value_col]
    else:
        raise ValueError("df must be a pandas Series or DataFrame")

    df_diff = df_local.diff()

    #  find the indexes where the counter resets
    df_reset_first = df_diff < 0
    df_reset_last = df_reset_first.shift(-1).fillna(False)

    # get vector of indexes where the counter resets
    df_reset_first_index = df_reset_first[df_reset_first].index
    df_reset_last_index = df_reset_last[df_reset_last].index

    return df_reset_last_index, df_reset_first_index
