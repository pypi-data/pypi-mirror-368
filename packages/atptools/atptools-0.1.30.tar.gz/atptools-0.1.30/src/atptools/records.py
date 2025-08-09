import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, TypeAdapter

from .c_py import di
from .dict_default import DictDefault
from .io import (
    load_from_file_str,
    load_from_file_str_async,
    save_to_file,
    save_to_file_async,
)
from .utils import _path_suffix_check


class Records(list[DictDefault]):
    def __init__(
        self,
        data: list | None = None,
        pydantic_model=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._pydantic_model = pydantic_model
        if data is not None:
            for arg in data:
                if isinstance(arg, DictDefault):
                    self.append(arg)
                else:
                    self.append(DictDefault(arg))

        # validate pydantic model
        if self._pydantic_model is not None:
            self.validate_pydantic()

    def validate_pydantic(self, pydantic_model=None) -> "Records":
        if pydantic_model is not None:
            self._pydantic_model = pydantic_model

        if self._pydantic_model is None:
            raise ValueError("Pydantic model is not defined.")
        if not issubclass(self._pydantic_model, BaseModel):
            raise ValueError("Invalid Pydantic model.")

        # validate pydantic model
        ta = TypeAdapter(list[self._pydantic_model])
        ta.validate_python(self)
        # for record in self:
        #     self._pydantic_model.model_validate(record)
        return self

    # Import from ---------------------------------------------
    def from_string(self, string: str) -> "Records":
        super().extend(json.loads(string))
        return self

    def from_json(self, path: str | Path) -> "Records":
        ret: str = load_from_file_str(path)
        self.from_string(ret)
        return self

    async def from_json_async(self, path: str | Path) -> "Records":
        ret: str = await load_from_file_str_async(path)
        self.from_string(ret)
        return self

    def from_dataframe(self, df: pd.DataFrame) -> "Records":
        records_dict: list = df.to_dict(orient="records")
        super().extend(records_dict)
        return self

    def from_csv(self, path: str | Path) -> "Records":
        df = pd.read_csv(path)
        self.from_dataframe(df)
        return self

    def from_sqlalchemy_row(self, rows: list) -> "Records":
        records = []
        for row in rows:
            records.append(row._asdict())

        super().extend(records)
        return self

    def from_sqlalchemy_model(self, models: list) -> "Records":
        models_dict = jsonable_encoder(models)
        super().extend(models_dict)
        return self

    def from_sqlalchemy(self, rows: list) -> "Records":
        if len(rows) == 0:
            raise ValueError("No data to convert.")
        if hasattr(rows[0], "_asdict"):
            return self.from_sqlalchemy_row(rows)
        else:
            return self.from_sqlalchemy_model(rows)

    async def from_azure_blob_async(self):
        # TODO: #30 Implement async version of from_azure_blob
        raise NotImplementedError("Azure Blob Storage not implemented yet.")

    async def from_s3_async(self):
        # TODO: #31 Implement async version of from_s3
        raise NotImplementedError("S3 Storage not implemented yet.")

    async def from_db_async(self, db, query: str) -> "Records":
        # TODO: #32 Implement async version of from_db
        raise NotImplementedError("Database not implemented yet.")

    # Export to ---------------------------------------------------------

    def to_json(
        self,
        path: str | Path | None = None,
        indent: int | None = None,
    ) -> str:
        ret = json.dumps(
            list(self),
            default=str,
            ensure_ascii=False,
            indent=indent,
        )
        if path is not None:
            path = _path_suffix_check(path, suffix=".json")
            save_to_file(ret, path)
        return ret

    async def to_json_async(
        self,
        path: str | Path | None = None,
        indent: int | None = None,
    ) -> str:
        ret = json.dumps(
            list(self),
            default=str,
            ensure_ascii=False,
            indent=indent,
        )
        if path is not None:
            path = _path_suffix_check(path, suffix=".json")
            await save_to_file_async(ret, path)
        return ret

    async def to_azure_blob_async(self):
        # TODO: #30 Implement async version of from_azure_blob
        raise NotImplementedError("Azure Blob Storage not implemented yet.")

    async def to_s3_async(self):
        # TODO: #31 Implement async version of from_s3
        raise NotImplementedError("S3 Storage not implemented yet.")

    async def to_db_async(self, db, query: str) -> "Records":
        # TODO: #32 Implement async version of from_db
        raise NotImplementedError("Database not implemented yet.")

    # Basic exports --------------------------------------
    def to_list(self) -> list:
        return list(self)

    def to_dict(self, keys: list) -> dict:
        return self.to_dict_default(keys).to_dict()

    def to_defaultdict(self, keys: list) -> defaultdict:
        return self.to_dict_default(keys).to_defaultdict()

    def to_dict_default(self, keys: list) -> DictDefault:
        ret: DictDefault = DictDefault()
        for record in self:
            p = id(ret)
            key_values = [record[key] for key in keys]
            key_values_len = len(key_values)
            for i in range(key_values_len):
                if i < key_values_len - 1:
                    if key_values[i] not in di(p):
                        di(p)[key_values[i]] = {}
                    p = id(di(p)[key_values[i]])
                else:
                    if key_values[i] in di(p):
                        raise ValueError("Keys should be unique in the dataset.")
                    di(p)[key_values[i]] = record

        return ret

    def to_list_by_key(self, key: str) -> list:
        ret = []
        for record in self:
            ret.append(record[key])
        return ret

    def group_by(self, keys: list, key_as_tuple: bool = False) -> DictDefault:
        if key_as_tuple:
            return self._group_by_tuplekey(keys)
        else:
            return self._group_by_hierarchy(keys)

    def _group_by_tuplekey(self, keys: list) -> DictDefault:
        ret = DictDefault()
        for record in self:
            key_values = tuple([record[key] for key in keys])
            if key_values not in ret:
                ret[key_values] = []
            ret[key_values].append(record)

        return ret

    def _group_by_hierarchy(self, keys: list) -> DictDefault:
        ret = DictDefault()
        for record in self:
            p = id(ret)
            key_values = [record[key] for key in keys]
            key_values_len = len(key_values)
            for i in range(key_values_len):
                if i < key_values_len - 1:
                    if key_values[i] not in di(p):
                        di(p)[key_values[i]] = {}
                    p = id(di(p)[key_values[i]])
                else:
                    if key_values[i] not in di(p):
                        di(p)[key_values[i]] = []
                    (di(p)[key_values[i]]).append(record)

        return ret

    def to_dataframe(
        self,
        index: list | None = None,
        columns: list | None = None,
    ) -> pd.DataFrame:
        df = pd.DataFrame(self)
        if index is not None and len(index) > 0:
            df.set_index(index, inplace=True)
        if columns is not None and len(columns) > 0:
            df = df[columns]
        return df

    def to_vectors(self, keys: list, flatten: bool = False) -> list:
        values = []

        for record in self:
            if not isinstance(record, DictDefault):
                record = DictDefault(record)
            value_list = record.to_vector(keys, flatten)
            values.append(value_list)
        return values

    def rename_keys(self, rename_dict: dict):
        # TODO: add support for nested keys
        for record in self:
            record.rename_keys(rename_dict)
        return self
