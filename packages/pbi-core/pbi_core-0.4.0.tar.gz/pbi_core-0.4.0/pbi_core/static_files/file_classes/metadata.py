from pydantic import Field

from ._base import BaseFileModel

base_val = bool | int | str


class QueryNameMapping(BaseFileModel):
    Key: str
    Value: str


class Metadata(BaseFileModel):
    Version: int
    AutoCreatedRelationships: list[int] = []
    CreatedFrom: str
    CreatedFromRelease: str
    FileDescription: str | None = None
    QueryNameToKeyMapping: list[QueryNameMapping] = Field(alias="_queryNameToKeyMapping", default_factory=list)  # ruff: noqa: N815
