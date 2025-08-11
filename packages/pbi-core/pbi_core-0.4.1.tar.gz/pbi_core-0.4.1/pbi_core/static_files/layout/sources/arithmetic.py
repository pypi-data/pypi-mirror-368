from enum import IntEnum
from typing import Annotated, Any

from pydantic import Discriminator, Tag

from pbi_core.static_files.layout._base_node import LayoutNode

from .aggregation import AggregationSource, DataSource


def get_expression_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "Aggregation" in v:
            return "AggregationSource"
        if any(c in v for c in ("Column", "Measure", "HierarchyLevel")):
            return "DataSource"
        raise TypeError(v)
    return v.__class__.__name__


Expression = Annotated[
    Annotated[DataSource, Tag("DataSource")] | Annotated[AggregationSource, Tag("AggregationSource")],
    Discriminator(get_expression_type),
]


class AllRolesRef(LayoutNode):
    AllRolesRef: bool = True  # no values have been seen in this field


class ScopedEval2(LayoutNode):
    Expression: Expression
    Scope: list[AllRolesRef]


class ScopedEval(LayoutNode):
    ScopedEval: ScopedEval2


class ArithmeticOperator(IntEnum):
    DIVIDE = 3


class _ArithmeticSourceHelper(LayoutNode):
    Left: Expression
    Right: ScopedEval
    Operator: ArithmeticOperator


class ArithmeticSource(LayoutNode):
    Arithmetic: _ArithmeticSourceHelper
    Name: str | None = None

    def get_sources(self) -> list[DataSource]:
        left = self.Arithmetic.Left
        if isinstance(left, AggregationSource):
            return left.get_sources()
        return [left]
