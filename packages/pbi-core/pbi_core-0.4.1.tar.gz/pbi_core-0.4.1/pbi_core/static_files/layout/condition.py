from dataclasses import dataclass, field
from enum import IntEnum
from typing import Annotated, Any

from pydantic import Discriminator, Tag

from ._base_node import LayoutNode
from .sources import DataSource, LiteralSource, Source, SourceRef, TransformOutputRoleRef
from .sources.aggregation import AggregationSource, ScopedEvalExpression, SelectRef
from .sources.arithmetic import ArithmeticSource, ScopedEval
from .sources.column import ColumnSource
from .sources.group import GroupSource
from .sources.proto import ProtoSourceRef


class ExpressionVersion(IntEnum):
    VERSION_1 = 1
    VERSION_2 = 2


class _AnyValueHelper(LayoutNode):
    DefaultValueOverridesAncestors: bool


class AnyValue(LayoutNode):
    AnyValue: _AnyValueHelper


class QueryConditionType(IntEnum):
    """Names defined by myself, but based on query outputs from the query tester."""

    STANDARD = 0
    TOP_N = 2
    MEASURE = 3


class ComparisonKind(IntEnum):
    IS_EQUAL = 0
    IS_GREATER_THAN = 1
    IS_GREATER_THAN_OR_EQUAL_TO = 2
    IS_LESS_THAN = 3
    IS_LESS_THAN_OR_EQUAL_TO = 4

    def get_operator(self) -> str:
        OPERATOR_MAPPING = {  # noqa: N806
            ComparisonKind.IS_EQUAL: "=",
            ComparisonKind.IS_GREATER_THAN: ">",
            ComparisonKind.IS_GREATER_THAN_OR_EQUAL_TO: ">=",
            ComparisonKind.IS_LESS_THAN: "<",
            ComparisonKind.IS_LESS_THAN_OR_EQUAL_TO: "<=",
        }
        if self not in OPERATOR_MAPPING:
            msg = f"No operator is defined for: {self}"
            raise ValueError(msg)
        return OPERATOR_MAPPING[self]


class ComparisonHelper(LayoutNode):
    Left: DataSource
    Right: LiteralSource


@dataclass
class Expression:
    template: str
    source: str
    data: dict[str, str] = field(default_factory=dict)
    expr_type: str = ""

    def to_text(self) -> str:
        if self.data:
            return self.template.format(**self.data)
        return self.template


class ContainsCondition(LayoutNode):
    Contains: ComparisonHelper

    def natural_language(self) -> str:
        """Returns a natural language representation of the condition."""
        left = natural_language_source(self.Contains.Left)
        right = natural_language_source(self.Contains.Right)
        return f"{left} CONTAINS {right}"

    def get_sources(self) -> list[DataSource]:
        """Returns the sources used in the condition."""
        if isinstance(self.Contains.Right, LiteralSource):
            return [self.Contains.Left]
        return [self.Contains.Left, self.Contains.Right]


class InExpressionHelper(LayoutNode):
    Expressions: list[DataSource]
    Values: list[list[LiteralSource]]

    def vals(self) -> list[str]:
        return [str(y.value()) for x in self.Values for y in x]

    def __repr__(self) -> str:
        source = self.Expressions[0].__repr__()
        return f"In({source}, {', '.join(self.vals())})"

    def get_sources(self) -> list[DataSource]:
        return self.Expressions


class InTopNExpressionHelper(LayoutNode):
    """Internal representation of the Top N option."""

    Expressions: list[DataSource]
    Table: SourceRef

    def get_sources(self) -> list[DataSource]:
        return self.Expressions


def get_in_union_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "Table" in v:
            return "InTopNExpressionHelper"
        if "Values" in v:
            return "InExpressionHelper"
        raise TypeError(v)
    return v.__class__.__name__


InUnion = Annotated[
    Annotated[InExpressionHelper, Tag("InExpressionHelper")]
    | Annotated[InTopNExpressionHelper, Tag("InTopNExpressionHelper")],
    Discriminator(get_in_union_type),
]


def natural_language_source(d: Source | SourceRef | ScopedEvalExpression) -> str:
    if isinstance(d, ColumnSource):
        return d.Column.Property
    breakpoint()
    msg = f"Unsupported data source type: {d.__class__.__name__}"
    raise TypeError(msg)


class InCondition(LayoutNode):
    """In is how "is" and "is not" are internally represented."""

    In: InUnion

    def __repr__(self) -> str:
        return self.In.__repr__()

    def natural_language(self) -> str:
        expr = natural_language_source(self.In.Expressions[0])
        if isinstance(self.In, InTopNExpressionHelper):
            table = natural_language_source(self.In.Table)
            return f"{expr} IN TOP N {table}"
        return f"{expr} IN ({', '.join(str(x[0].value()) for x in self.In.Values)})"

    def get_sources(self) -> list[DataSource]:
        return self.In.get_sources()


class TimeUnit(IntEnum):
    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4
    WEEK = 5
    MONTH = 6
    QUARTER = 7
    YEAR = 8


class _NowHelper(LayoutNode):
    Now: dict[str, str]  # actually an empty string


def get_date_span_union_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "Literal" in v:
            return "LiteralSource"
        if "Now" in v:
            return "_NowHelper"
        raise TypeError(v)
    return v.__class__.__name__


DateSpanUnion = Annotated[
    Annotated[LiteralSource, Tag("LiteralSource")] | Annotated[_NowHelper, Tag("_NowHelper")],
    Discriminator(get_date_span_union_type),
]


class _DateSpanHelper(LayoutNode):
    Expression: DateSpanUnion
    TimeUnit: TimeUnit


class DateSpan(LayoutNode):
    DateSpan: _DateSpanHelper


class RangePercentHelper(LayoutNode):
    Min: ScopedEval
    Max: ScopedEval
    Percent: float


class RangePercent(LayoutNode):
    RangePercent: RangePercentHelper


def get_comparison_right_union_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "Literal" in v:
            return "LiteralSource"
        if "AnyValue" in v:
            return "AnyValue"
        if "DateSpan" in v:
            return "DateSpan"
        if "RangePercent" in v:
            return "RangePercent"
        raise TypeError(v)
    return v.__class__.__name__


ComparisonRightUnion = Annotated[
    Annotated[LiteralSource, Tag("LiteralSource")]
    | Annotated[AnyValue, Tag("AnyValue")]
    | Annotated[DateSpan, Tag("DateSpan")]
    | Annotated[RangePercent, Tag("RangePercent")],
    Discriminator(get_comparison_right_union_type),
]


class ComparisonConditionHelper(LayoutNode):
    ComparisonKind: ComparisonKind
    Left: ScopedEvalExpression
    Right: ComparisonRightUnion


class ComparisonCondition(LayoutNode):
    Comparison: ComparisonConditionHelper

    def natural_language(self) -> str:
        """Returns a natural language representation of the condition."""
        left = natural_language_source(self.Comparison.Left)
        right = (
            self.Comparison.Right.value()
            if isinstance(self.Comparison.Right, LiteralSource)
            else str(self.Comparison.Right)
        )
        operator = self.Comparison.ComparisonKind.get_operator()
        return f"{left} {operator} {right}"

    def get_sources(self) -> list[DataSource]:
        left = self.Comparison.Left
        if isinstance(left, AggregationSource):
            return left.get_sources()
        if isinstance(left, SelectRef):
            return []
        return [left]


class NotConditionHelper(LayoutNode):
    Expression: "ConditionType"


class NotCondition(LayoutNode):
    Not: NotConditionHelper

    def __repr__(self) -> str:
        return f"Not({self.Not.Expression.__repr__()})"

    def natural_language(self) -> str:
        """Returns a natural language representation of the condition."""
        return f"NOT {self.Not.Expression.natural_language()}"

    def get_sources(self) -> list[DataSource]:
        return self.Not.Expression.get_sources()


class ExistsConditionHelper(LayoutNode):
    Expression: Source  # cannot be DataSource, might only be a ProtoSourceRef?


class ExistsCondition(LayoutNode):
    Exists: ExistsConditionHelper

    def natural_language(self) -> str:
        """Returns a natural language representation of the condition."""
        return f"Exists({natural_language_source(self.Exists.Expression)})"

    def get_sources(self) -> list[DataSource]:
        expr = self.Exists.Expression
        if isinstance(expr, (AggregationSource, ArithmeticSource, GroupSource)):
            return expr.get_sources()
        if isinstance(expr, (ProtoSourceRef, SelectRef, LiteralSource, TransformOutputRoleRef)):
            return []
        return [
            expr,
        ]


class CompositeConditionHelper(LayoutNode):
    Left: "ConditionType"
    Right: "ConditionType"


class AndCondition(LayoutNode):
    And: CompositeConditionHelper

    def natural_language(self) -> str:
        """Returns a natural language representation of the condition."""
        return f"({self.And.Left.natural_language()} AND {self.And.Right.natural_language()})"

    def get_sources(self) -> list[DataSource]:
        return [*self.And.Left.get_sources(), *self.And.Right.get_sources()]


class OrCondition(LayoutNode):
    Or: CompositeConditionHelper

    def natural_language(self) -> str:
        """Returns a natural language representation of the condition."""
        return f"({self.Or.Left.natural_language()} OR {self.Or.Right.natural_language()})"

    def get_sources(self) -> list[DataSource]:
        return [
            *self.Or.Left.get_sources(),
            *self.Or.Right.get_sources(),
        ]


def get_type(v: object | dict[str, Any]) -> str:  # noqa: PLR0911
    if isinstance(v, dict):
        if "And" in v:
            return "AndCondition"
        if "Or" in v:
            return "OrCondition"
        if "Left" in v:
            return "NonCompositeConditions"
        if "In" in v:
            return "InCondition"
        if "Not" in v:
            return "NotCondition"
        if "Contains" in v:
            return "ContainsCondition"
        if "Comparison" in v:
            return "ComparisonCondition"
        if "Exists" in v:
            return "ExistsCondition"
        raise ValueError
    return v.__class__.__name__


ConditionType = Annotated[
    Annotated[AndCondition, Tag("AndCondition")]
    | Annotated[OrCondition, Tag("OrCondition")]
    | Annotated[InCondition, Tag("InCondition")]
    | Annotated[NotCondition, Tag("NotCondition")]
    | Annotated[ContainsCondition, Tag("ContainsCondition")]
    | Annotated[ComparisonCondition, Tag("ComparisonCondition")]
    | Annotated[ExistsCondition, Tag("ExistsCondition")],
    Discriminator(get_type),
]


class Condition(LayoutNode):
    Condition: ConditionType
    Target: list[Source] | None = None

    def __repr__(self) -> str:
        return f"Condition({self.Condition.__repr__()})"

    def natural_language(self) -> str:
        """Returns a natural language representation of the condition."""
        return self.Condition.natural_language()

    def get_sources(self) -> list[DataSource]:
        """Returns the sources used in the condition.

        Note: The left source must come first, since the
            order is used by PowerBI and this library
            to identify the default display name of filters
        """
        return self.Condition.get_sources()
