from pbi_core.static_files.layout._base_node import LayoutNode

from .base import SourceExpression


class MeasureSource(LayoutNode):
    Measure: SourceExpression
    Name: str | None = None
    NativeReferenceName: str | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MeasureSource):
            return False
        return (self.Measure.column() == other.Measure.column()) and (self.Measure.table() == other.Measure.table())

    def __hash__(self) -> int:
        return hash((self.Measure.table(), self.Measure.column()))
