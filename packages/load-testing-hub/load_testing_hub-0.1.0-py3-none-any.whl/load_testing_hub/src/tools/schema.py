import csv
from typing import Self

import yaml
from pydantic import BaseModel, RootModel, FilePath


class YAMLSchema(BaseModel):
    @classmethod
    def from_yaml(cls, file: FilePath) -> Self:
        data = yaml.safe_load(file.open())
        return cls.model_validate(data)


class JSONSchema(BaseModel):
    @classmethod
    def from_json(cls, file: FilePath) -> Self:
        return cls.model_validate_json(file.read_text())


class CSVRootSchema(RootModel):
    @classmethod
    def from_csv(cls, file: FilePath) -> Self:
        reader = csv.DictReader(file.open())
        return cls.model_validate(reader)
