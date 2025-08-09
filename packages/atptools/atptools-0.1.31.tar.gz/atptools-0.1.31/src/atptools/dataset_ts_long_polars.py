import datetime as dt
import uuid

import pandas as pd

from .dict_default import DictDefault
from .records import Records


class AtpDatasetTsLongPolars:
    def __init__(
        self,
        name: str | None = None,
        uuid: uuid.UUID | None = None,
    ):
        # DataFrame with multiindex (datetime, name)
        self.init_dataframe()
        # Metadata
        self.metadata: DictDefault = DictDefault()
        self.metadata_series: DictDefault = DictDefault()
        # self.metadata = defaultdict(dict)

        self.metadata["name"] = name
        self.metadata["uuid"] = uuid
        self.metadata["series"] = {}
        return

    def init_dataframe(self) -> "AtpDatasetTsLongPolars":
        self.df: pd.DataFrame = pd.DataFrame(columns=["datetime", "name", "value"])
        self.df.set_index(["datetime"], inplace=True)
        return self

    def update_metadata_series(self, metadata: Records):
        for record in metadata:
            self.metadata_series.setdefault(record["name"], {}).update(record)
        return self

    def add_dataframe(
        self,
        df: pd.DataFrame,
        index_col: str = "datetime",
        name_col: str = "name",
        value_col: str = "value",
    ):
        # TODO: check if values are unique (overwrite???)
        df = df.rename(
            columns={index_col: "datetime", name_col: "name", value_col: "value"}
        )
        df = df[["datetime", "name", "value"]]
        # convert datetime to datetime
        df["datetime"] = pd.to_datetime(df["datetime"])

        df.set_index(["datetime"], inplace=True)
        self.df = pd.concat([self.df, df])
        self.df.sort_index(inplace=True)
        # set metadata names
        for name in df["name"].unique():
            self.metadata_series.setdefault(name, {})["name"] = name
        return self

    def add_series(
        self,
        series: pd.Series,
        name: str | None = None,
    ):
        # set series  index name
        series.index.name = "datetime"

        # rename columns
        if name is None:
            name = series.name
        series = series.rename("value")
        df: pd.DataFrame = series.to_frame()
        df["name"] = name
        self.df = pd.concat([self.df, df])
        self.metadata_series.setdefault(name, {})["name"] = name
        return self

    def to_dataframe(self) -> pd.DataFrame:
        return self.df

    def empty_data(self) -> "AtpDatasetTsLongPolars":
        del self.df
        self.init_dataframe()
        return self

    def get_time_range(self) -> tuple[dt.datetime, dt.datetime]:
        return self.df.index.min(), self.df.index.max()
