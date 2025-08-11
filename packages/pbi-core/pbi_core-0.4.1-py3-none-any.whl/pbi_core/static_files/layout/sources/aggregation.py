from enum import IntEnum
from typing import Annotated, Any

from pydantic import Discriminator, Field, Tag

from pbi_core.static_files.layout._base_node import LayoutNode

from .column import ColumnSource
from .hierarchy import HierarchyLevelSource
from .measure import MeasureSource


class ExpressionName(LayoutNode):
    ExpressionName: str


class SelectRef(LayoutNode):
    SelectRef: ExpressionName


def get_expression_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "Aggregation" in v:
            return "AggregationSource"
        if any(c in v for c in ("Column", "Measure", "HierarchyLevel")):
            return "DataSource"
        if "SelectRef" in v:
            return "SelectRef"
        raise TypeError(v)
    return v.__class__.__name__


class AllRolesRef(LayoutNode):
    AllRolesRef: dict[str, bool] = Field(default_factory=dict)  # no values have been seen in this field


class ScopedEval2(LayoutNode):
    Expression: "ScopedEvalExpression"
    Scope: list[AllRolesRef]


class ScopedEval(LayoutNode):  # copied from arithmetic.py to avoid circular dependencies
    ScopedEval: ScopedEval2


def get_data_source_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "Column" in v:
            return "ColumnSource"
        if "Measure" in v:
            return "MeasureSource"
        if "HierarchyLevel" in v:
            return "HierarchyLevelSource"
        if "ScopedEval" in v:  # Consider subclassing? This only happens for color gradient properties IME
            return "ScopedEval"
        raise TypeError(v)
    return v.__class__.__name__


DataSource = Annotated[
    Annotated[ColumnSource, Tag("ColumnSource")]
    | Annotated[MeasureSource, Tag("MeasureSource")]
    | Annotated[HierarchyLevelSource, Tag("HierarchyLevelSource")]
    | Annotated[ScopedEval, Tag("ScopedEval")],
    Discriminator(get_data_source_type),
]


class AggregationFunction(IntEnum):
    SUM = 0
    AVERAGE = 1
    COUNT = 2
    MIN = 3
    MAX = 4
    DISTINCT_COUNT = 5
    MEDIAN = 6
    STD_DEV_P = 7
    VAR_P = 8


class _AggregationSourceHelper(LayoutNode):
    Expression: DataSource
    Function: AggregationFunction


class AggregationSource(LayoutNode):
    Aggregation: _AggregationSourceHelper
    Name: str | None = None
    NativeReferenceName: str | None = None  # only for Layout.Visual.Query

    def get_sources(self) -> list[DataSource]:
        return [self.Aggregation.Expression]


ScopedEvalExpression = Annotated[
    Annotated[DataSource, Tag("DataSource")]
    | Annotated[AggregationSource, Tag("AggregationSource")]
    | Annotated[SelectRef, Tag("SelectRef")],
    Discriminator(get_expression_type),
]
