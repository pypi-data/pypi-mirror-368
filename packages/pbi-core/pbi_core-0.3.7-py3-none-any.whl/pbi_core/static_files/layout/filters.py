from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Annotated, Any, cast

import pbi_prototype_query_translation
from pydantic import Discriminator, Tag

from pbi_core.pydantic.main import BaseValidation
from pbi_core.static_files.layout.sources.literal import LiteralSource
from pbi_core.static_files.model_references import ModelColumnReference, ModelMeasureReference

from ._base_node import LayoutNode
from .condition import AndCondition, ComparisonCondition, Condition, ConditionType, InCondition, NotCondition
from .sources import AggregationSource, ColumnSource, Entity, MeasureSource, Source
from .sources.aggregation import ScopedEval
from .visuals.properties.filter_properties import FilterObjects

if TYPE_CHECKING:
    from pbi_prototype_query_translation.main import TranslationResult

    from pbi_core.ssas.server import LocalTabularModel

    from .bookmark import BookmarkFilters
    from .layout import Layout
    from .section import Section


class Direction(IntEnum):
    ASCENDING = 1
    DESCENDING = 2


class Orderby(LayoutNode):
    Direction: Direction
    Expression: Source


class PrototypeQueryResult(BaseValidation):
    data: list[dict[str, Any]]
    dax_query: str
    column_mapping: dict[str, str]


class InputParameter(LiteralSource):
    Name: str


class InputTableColumn(BaseValidation):
    Expression: Source
    Role: str | None = None


class InputTable(BaseValidation):
    Name: str
    Columns: list[InputTableColumn]


class TransformInput(BaseValidation):
    Parameters: list[InputParameter]
    Table: InputTable


class TransformOutput(BaseValidation):
    Table: InputTable


class TransformMeta(BaseValidation):
    Name: str
    Algorithm: str
    Input: TransformInput
    Output: TransformOutput

    def table_mapping(self) -> dict[str, str]:
        ret: list[ColumnSource | MeasureSource] = []
        for col in self.Input.Table.Columns:
            ret.extend(PrototypeQuery.unwrap_source(col.Expression))
        input_tables: set[str] = set()
        for source in ret:
            if isinstance(source, ColumnSource):
                input_tables.add(source.Column.table())
            else:
                input_tables.add(source.Measure.table())
        if len(input_tables) > 1:
            msg = f"Don't know how to handle multiple inputs: {self}"
            raise ValueError(msg)

        (input_table,) = input_tables
        return {
            self.Output.Table.Name: input_table,
        }


class PrototypeQuery(LayoutNode):
    Version: int
    From: list["From"]
    Select: list[Source] = []
    Where: list[Condition] = []
    OrderBy: list[Orderby] = []
    Transform: list[TransformMeta] = []
    Top: int | None = None

    def table_mapping(self) -> dict[str, str]:
        ret: dict[str, str] = {}
        for from_clause in self.From:
            ret |= from_clause.table_mapping()
        for transform in self.Transform:
            # For measures using Transform outputs, we need to point to the source of that transform table
            transform_tables = transform.table_mapping()
            ret |= {k: ret[v] for k, v in transform_tables.items()}
        return ret

    @classmethod
    def unwrap_source(cls, source: Source | ConditionType | ScopedEval) -> list[ColumnSource | MeasureSource]:
        """Identifies the root sources (measures and columns) used in this filter.

        Raises:
            TypeError: Occurs when one of the source types has not been handled by the code.
                Should not occur outside development.

        """
        if isinstance(source, ColumnSource | MeasureSource):
            return [source]
        if isinstance(source, AggregationSource):
            return cls.unwrap_source(source.Aggregation.Expression)

        if isinstance(source, InCondition):
            ret: list[ColumnSource | MeasureSource] = []
            for expr in source.In.Expressions:
                ret.extend(cls.unwrap_source(expr))
            return ret
        if isinstance(source, NotCondition):
            return cls.unwrap_source(source.Not.Expression)
        if isinstance(source, AndCondition):
            return [
                *cls.unwrap_source(source.And.Left),
                *cls.unwrap_source(source.And.Right),
            ]
        if isinstance(source, ComparisonCondition):
            # Right has no dynamic options, so it's skipped
            return cls.unwrap_source(source.Comparison.Left)
        print(source)
        breakpoint()
        raise TypeError

    def get_ssas_elements(self) -> set[ModelColumnReference | ModelMeasureReference]:
        """Returns the SSAS elements (columns and measures) this query is directly dependent on."""
        ret: set[ColumnSource | MeasureSource] = set()
        for select in self.Select:
            ret.update(self.unwrap_source(select))
        for where in self.Where:
            ret.update(self.unwrap_source(where.Condition))
        for order_by in self.OrderBy:
            ret.update(self.unwrap_source(order_by.Expression))
        for transformation in self.Transform:
            for col in transformation.Input.Table.Columns:
                ret.update(self.unwrap_source(col.Expression))
        table_mappings: dict[str, str] = self.table_mapping()
        ret2: set[ModelColumnReference | ModelMeasureReference] = set()
        for source in ret:
            if isinstance(source, ColumnSource):
                ret2.add(
                    ModelColumnReference(
                        column=source.Column.column(),
                        table=table_mappings[source.Column.table()],
                    ),
                )
            else:
                ret2.add(
                    ModelMeasureReference(
                        measure=source.Measure.column(),
                        table=table_mappings[source.Measure.table()],
                    ),
                )
        return ret2

    def get_dax(self, model: "LocalTabularModel") -> "TranslationResult":
        """Creates a DAX query that returns the data for a visual based on the SSAS model supplied.

        Note:
            Although generally the DAX queries generated are identical across different models,
                they can theoretically be different. If you can create a specific case of this,
                please add it to the pbi_core repo!

        Args:
            model (LocalTabularModel): The SSAS model to generate the DAX against.

        Returns:
            DataViewQueryTranslationResult: an object containing the DAX query for this visual

        """
        raw_query = self.model_dump_json()
        return pbi_prototype_query_translation.prototype_query(
            raw_query,
            model.db_name,
            model.server.port,
        )

    def get_data(self, model: "LocalTabularModel") -> PrototypeQueryResult:
        dax_query = self.get_dax(model)
        data = model.server.query_dax(dax_query.dax)

        return PrototypeQueryResult(
            data=data,
            dax_query=dax_query.dax,
            column_mapping=dax_query.column_mapping,
        )


class _SubqueryHelper2(LayoutNode):
    _parent: "_SubqueryHelper"  # pyright: ignore reportIncompatibleVariableOverride=false

    Query: PrototypeQuery


class _SubqueryHelper(LayoutNode):
    _parent: "Subquery"  # pyright: ignore reportIncompatibleVariableOverride=false

    Subquery: _SubqueryHelper2


class SubQueryType(IntEnum):
    NA = 2


class Subquery(LayoutNode):
    _parent: "VisualFilterExpression"  # pyright: ignore reportIncompatibleVariableOverride=false

    Name: str
    Expression: _SubqueryHelper
    Type: SubQueryType

    def table_mapping(self) -> dict[str, str]:
        return self.Expression.Subquery.Query.table_mapping()


def get_from(v: Any) -> str:
    if isinstance(v, dict):
        if "Entity" in v:
            return "Entity"
        if "Expression" in v:
            return "Subquery"
        msg = f"Unknown Filter: {v.keys()}"
        raise ValueError(msg)
    return cast("str", v.__class__.__name__)


From = Annotated[
    Annotated[Entity, Tag("Entity")] | Annotated[Subquery, Tag("Subquery")],
    Discriminator(get_from),
]


class HowCreated(IntEnum):
    AUTOMATIC = 0
    MANUAL = 1
    NA = 4
    NA2 = 5


class FilterType(Enum):
    Advanced = "Advanced"
    Categorial = "Categorical"
    Exclude = "Exclude"
    Passthrough = "Passthrough"
    RelativeDate = "RelativeDate"
    TopN = "TopN"


class Scope(LayoutNode):
    scopeId: ConditionType


class CachedDisplayNames(LayoutNode):
    displayName: str
    id: Scope


class Filter(LayoutNode):
    name: str | None = None
    type: FilterType = FilterType.Categorial
    howCreated: HowCreated = HowCreated.AUTOMATIC
    expression: Source | None = None
    isLockedInViewMode: bool = False
    isHiddenInViewMode: bool = False
    objects: FilterObjects | None = None
    filter: PrototypeQuery | None = None
    displayName: str | None = None
    ordinal: int = 0
    cachedDisplayNames: list[CachedDisplayNames] | None = None
    isLinkedAsAggregation: bool = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.displayName or self.name})"

    def __str__(self) -> str:
        return super().__str__()

    def get_display_name(self) -> str:
        if self.displayName is not None:
            return self.displayName
        if self.filter is None:
            msg = "Unknown default display name"
            raise ValueError(msg)
        default_name_source = self.filter.Where[0].get_sources()[0]
        if isinstance(default_name_source, ColumnSource):
            return default_name_source.Column.Property
        if isinstance(default_name_source, MeasureSource):
            return default_name_source.Measure.Property
        return "--"

    def get_ssas_elements(self) -> set[ModelColumnReference | ModelMeasureReference]:
        """Returns the SSAS elements (columns and measures) this filter is directly dependent on."""
        if self.filter is None:
            return set()
        return self.filter.get_ssas_elements()


class VisualFilterExpression(LayoutNode):
    _parent: "VisualFilter"  # pyright: ignore reportIncompatibleVariableOverride=false

    Version: int | None = None
    From: list["From"] | None = None
    Where: list[Condition]


# TODO: Filter specialization, only done to create better type completion.
# TODO: visual needs extra fields because it allows measure sources I think


class HighlightScope(LayoutNode):
    scopeId: ConditionType


class CachedValueItems(LayoutNode):
    identities: list[HighlightScope]
    valueMap: dict[str, str] | list[str]


class FilterExpressionMetadata(LayoutNode):
    expressions: list[Source]
    cachedValueItems: list[CachedValueItems]


class VisualFilter(Filter):
    restatement: str | None = None
    filterExpressionMetadata: FilterExpressionMetadata | None = None

    def to_bookmark(self) -> "BookmarkFilter":
        return cast("BookmarkFilter", self)


class BookmarkFilter(VisualFilter):
    _parent: "BookmarkFilters"  # pyright: ignore reportIncompatibleVariableOverride=false


class PageFilter(Filter):
    _parent: "Section"  # pyright: ignore reportIncompatibleVariableOverride=false


class GlobalFilter(Filter):
    _parent: "Layout"  # pyright: ignore reportIncompatibleVariableOverride=false
