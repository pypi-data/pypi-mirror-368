import uuid
from pathlib import Path

import pandas as pd

from .csv import csv_str_to_dataframe, dataframe_to_csv_str
from .csv_object import Csv


class AtpDataset:
    def __init__(
        self,
        df: pd.DataFrame | None = None,
        metadata: dict | None = None,
    ):
        self.name: str | None = None
        self.uuid: uuid.UUID | None = None
        self.df: pd.DataFrame | None = df
        self._metadata: dict | None = metadata
        return

    # Properties
    @property
    def metadata(self) -> dict | None:
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict | None):
        self._metadata = value
        if value is None:
            return
        if "name" in value:
            self.name = value["name"]
        if "uuid" in value:
            self.uuid = uuid.UUID(value["uuid"])
        return

    # Imports
    def from_csv_object(self, csv_obj: Csv) -> "AtpDataset":
        self.df = csv_obj.df
        self.metadata = csv_obj.metadata
        return self

    def from_csv_str(self, csv_str: str):
        self.df, self.metadata = csv_str_to_dataframe(csv_str)
        return self

    def from_csv_file(self, file_path: str | Path):
        with open(file_path) as f:
            csv_str = f.read()
        return self.from_csv_str(csv_str)

    # Exports
    def to_csv_object(self) -> Csv:
        csv_obj = Csv()
        csv_obj.df = self.df
        csv_obj.metadata = self.metadata
        return csv_obj

    def to_csv_str(self) -> str:
        return dataframe_to_csv_str(self.df, self.metadata)

    def to_csv_file(self, file_path: str | Path):
        with open(file_path, "w") as f:
            f.write(self.to_csv_str())
        return self
