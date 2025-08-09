# ruff: noqa: N815

from pydantic import ConfigDict

from .base import BaseVisual, PropertyDef
from .column_property import ColumnProperty


class BarChart(BaseVisual):
    visualType: str = "barChart"
    model_config = ConfigDict(extra="forbid")
    columnProperties: dict[str, ColumnProperty] | None = None
    objects: dict[str, list[PropertyDef]] | None = None
