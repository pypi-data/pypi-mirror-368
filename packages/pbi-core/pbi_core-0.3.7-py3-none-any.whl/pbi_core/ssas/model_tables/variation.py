from typing import TYPE_CHECKING, Literal

from pbi_core.lineage import LineageNode

from .base import SsasRenameRecord

if TYPE_CHECKING:
    from .column import Column
    from .hierarchy import Hierarchy
    from .relationship import Relationship


class Variation(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/b9dfeb51-cbb6-4eab-91bd-fa2b23f51ca3)
    """

    column: int | None = None  # TODO: pbi says this shouldn't exist
    column_id: int
    default_column_id: int | None = None
    default_hierarchy_id: int
    description: str | None = None
    is_default: bool
    name: str
    relationship_id: int

    def get_column(self) -> "Column":
        """Name is bad to not consistent with other methods because the column field in this entity :(."""
        return self.tabular_model.columns.find(self.column_id)

    def default_column(self) -> "Column | None":
        if self.default_column_id is None:
            return None
        return self.tabular_model.columns.find(self.default_column_id)

    def default_hierarchy(self) -> "Hierarchy":
        return self.tabular_model.hierarchies.find(self.default_hierarchy_id)

    def relationship(self) -> "Relationship":
        return self.tabular_model.relationships.find(self.relationship_id)

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type)
        return LineageNode(
            self,
            lineage_type,
            [
                self.default_hierarchy().get_lineage(lineage_type),
                self.relationship().get_lineage(lineage_type),
            ],
        )
