from pbi_core.static_files.layout._base_node import LayoutNode

from .base import SourceExpression


class ColumnSource(LayoutNode):
    Column: SourceExpression
    Name: str | None = None  # only seen on a couple TopN filters
    NativeReferenceName: str | None = None  # only for Layout.Visual.Query

    def __repr__(self) -> str:
        return f"ColumnSource({self.Column.Expression.table()}.{self.Column.Property})"

    def filter_name(self) -> str:
        return self.Column.Property

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ColumnSource):
            return False
        return (self.Column.column() == other.Column.column()) and (self.Column.table() == other.Column.table())

    def __hash__(self) -> int:
        return hash((self.Column.column(), self.Column.table()))
