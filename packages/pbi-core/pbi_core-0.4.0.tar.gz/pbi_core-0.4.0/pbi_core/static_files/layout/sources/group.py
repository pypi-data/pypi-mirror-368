from typing import cast

from pbi_core.static_files.layout._base_node import LayoutNode

from .aggregation import DataSource
from .base import SourceRef
from .column import ColumnSource


class _GroupSourceHelper(LayoutNode):
    _parent: "GroupSource"  # pyright: ignore reportIncompatibleVariableOverride=false

    Expression: SourceRef
    GroupedColumns: list[ColumnSource]
    Property: str


class GroupSource(LayoutNode):
    GroupRef: _GroupSourceHelper
    Name: str | None = None

    def __repr__(self) -> str:
        table = self.GroupRef.Expression.table()
        column = self.GroupRef.Property
        return f"GroupRef({table}.{column})"

    def filter_name(self) -> str:
        return self.GroupRef.Property

    def get_sources(self) -> list[DataSource]:
        return cast("list[DataSource]", self.GroupRef.GroupedColumns)
