from typing import TYPE_CHECKING, Annotated, Any

from pydantic import Discriminator, Tag

from pbi_core.static_files.layout._base_node import LayoutNode

from .base import SourceExpression, SourceRef

if TYPE_CHECKING:
    from pbi_core.static_files.layout.filters import From


class PropertyVariationSource(LayoutNode):
    Expression: SourceRef
    Name: str
    Property: str

    def column(self) -> str:
        return self.Property


class _PropertyVariationSourceHelper(LayoutNode):
    PropertyVariationSource: PropertyVariationSource

    def table(self) -> str:
        return self.PropertyVariationSource.Expression.table()

    def column(self) -> str:
        return self.PropertyVariationSource.column()


def get_hierarchy_expression_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "PropertyVariationSource" in v:
            return "_PropertyVariationSourceHelper"
        if "SourceRef" in v:
            return "SourceRef"
        if "Property" in v:
            return "SourceExpression"
        raise ValueError
    return v.__class__.__name__


ConditionType = Annotated[
    Annotated[SourceExpression, Tag("SourceExpression")]
    | Annotated[_PropertyVariationSourceHelper, Tag("_PropertyVariationSourceHelper")]
    | Annotated[SourceRef, Tag("SourceRef")],
    Discriminator(get_hierarchy_expression_type),
]


class _HierarchySourceHelper(LayoutNode):
    Expression: ConditionType
    Hierarchy: str | None = None


class HierarchySource(LayoutNode):
    Hierarchy: _HierarchySourceHelper


class _HierarchyLevelSourceHelper(LayoutNode):
    _parent: "HierarchyLevelSource"  # pyright: ignore reportIncompatibleVariableOverride=false

    Expression: HierarchySource
    Level: str | None = None


class HierarchyLevelSource(LayoutNode):
    HierarchyLevel: _HierarchyLevelSourceHelper
    Name: str | None = None
    NativeReferenceName: str | None = None

    def __repr__(self) -> str:
        table = self.HierarchyLevel.Expression.Hierarchy.Expression.table()
        if isinstance(self.HierarchyLevel.Expression.Hierarchy.Expression, SourceRef):
            column = self.HierarchyLevel.Expression.Hierarchy.Hierarchy
        else:
            column = self.HierarchyLevel.Expression.Hierarchy.Expression.column()
        level = self.HierarchyLevel.Level
        return f"HierarchyLevelSource({table}.{column}.{level})"

    def to_query_text(self, target_tables: dict[str, "From"]) -> str:
        raise NotImplementedError
