from typing import Annotated, Any

from pydantic import Discriminator, Tag

from pbi_core.pydantic.main import BaseValidation

from .aggregation import AggregationSource, DataSource, SelectRef
from .arithmetic import ArithmeticSource
from .base import Entity, SourceRef
from .column import ColumnSource
from .group import GroupSource
from .hierarchy import HierarchyLevelSource
from .literal import LiteralSource
from .measure import MeasureSource
from .proto import ProtoSourceRef


class RoleRef(BaseValidation):
    Role: str


class TransformOutputRoleRef(BaseValidation):
    TransformOutputRoleRef: RoleRef
    Name: str | None = None


def get_source(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        mapper = {
            "Column": "ColumnSource",
            "HierarchyLevel": "HierarchyLevelSource",
            "GroupRef": "GroupSource",
            "Aggregation": "AggregationSource",
            "Measure": "MeasureSource",
            "Arithmetic": "ArithmeticSource",
            "SourceRef": "ProtoSourceRef",
            "TransformOutputRoleRef": "TransformOutputRoleRef",
            "Literal": "LiteralSource",
            "SelectRef": "SelectRef",
        }
        for key in v:
            if key in mapper:
                return mapper[key]
        msg = f"Unknown Filter: {v.keys()}"
        raise TypeError(msg)
    return v.__class__.__name__


Source = Annotated[
    Annotated[HierarchyLevelSource, Tag("HierarchyLevelSource")]
    | Annotated[ColumnSource, Tag("ColumnSource")]
    | Annotated[GroupSource, Tag("GroupSource")]
    | Annotated[AggregationSource, Tag("AggregationSource")]
    | Annotated[MeasureSource, Tag("MeasureSource")]
    | Annotated[ArithmeticSource, Tag("ArithmeticSource")]
    | Annotated[ProtoSourceRef, Tag("ProtoSourceRef")]
    | Annotated[TransformOutputRoleRef, Tag("TransformOutputRoleRef")]
    | Annotated[LiteralSource, Tag("LiteralSource")]
    | Annotated[SelectRef, Tag("SelectRef")],
    # Discriminator is used to determine the type based on the content of the object
    Discriminator(get_source),
]

__all__ = [
    "AggregationSource",
    "ArithmeticSource",
    "ColumnSource",
    "DataSource",
    "Entity",
    "GroupSource",
    "HierarchyLevelSource",
    "LiteralSource",
    "MeasureSource",
    "Source",
    "SourceRef",
]
