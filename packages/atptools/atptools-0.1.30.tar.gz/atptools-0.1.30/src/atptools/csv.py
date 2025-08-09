import io
from pprint import pprint

import pandas as pd


def dataframe_to_csv_str(df: pd.DataFrame, metadata: dict | None = None) -> str:
    """Write a DataFrame to a CSV file."""

    ret = ""
    if metadata is None and isinstance(df.attrs, dict):
        metadata = df.attrs

    if metadata is not None:
        for key, value in metadata.items():
            ret += f"# {key}: {value}\n"
    ret += "\n"
    ret += df.to_csv(index=False)
    print("type(csv_buffer):", type(ret))
    return ret


def csv_str_to_dataframe(csv_str: str) -> pd.DataFrame:
    """Read a DataFrame from a CSV file."""

    metadata = {}
    for line in csv_str.split("\n"):
        if line.startswith("#"):
            key, value = line[2:].split(":")
            key = key.strip()
            metadata[key] = value.strip()

    pprint(metadata)
    df = pd.read_csv(io.StringIO(csv_str), comment="#")
    df.attrs = metadata
    return df, metadata
