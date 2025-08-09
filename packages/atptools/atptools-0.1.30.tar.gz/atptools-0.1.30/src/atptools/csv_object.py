import io
from pathlib import Path

import pandas as pd

from .dict_default import DictDefault


class Csv:
    def __init__(
        self,
        df: pd.DataFrame | None = None,
        metadata: DictDefault = DictDefault(),
    ):
        self.df: pd.DataFrame | None = df
        self.metadata: DictDefault = metadata

        self.file_path: Path | None = None
        self.file_name: str | None = None

        self.columns: list[str] = []

        self.buffer: bytes | None = None

    def read_file(self, file_path: Path):
        self.file_path = file_path

        with open(file_path, "rb") as file:
            file_data = file.read()

        print("file_data type: ", type(file_data))
        self.read_buffer(io.BytesIO(file_data))

        return self

    def read_buffer(self, buffer: bytes | io.BytesIO | io.BufferedReader):
        print("buffer type: ", type(buffer))
        if isinstance(buffer, bytes):
            buffer = io.BytesIO(buffer)

        # copy buffer to self.buffer
        self.buffer = buffer.read()
        buffer.seek(0)

        # buffer_string = buffer.read().decode("utf-8")

        while line := buffer.readline():
            print("line: ", line)

        return self

    def read_string(self, buffer: io.StringIO):
        file_data = buffer.read()
        # iterate by line
        for line in file_data.split("\n"):
            print("line: ", line)

        return self
