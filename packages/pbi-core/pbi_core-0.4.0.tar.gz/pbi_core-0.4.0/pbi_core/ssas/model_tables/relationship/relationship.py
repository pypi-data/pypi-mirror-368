import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import PrivateAttr

from pbi_core.lineage import LineageNode
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.enums import DataState
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import CrossFilteringBehavior, JoinOnDateBehavior, RelationshipType, SecurityFilteringBehavior

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.column import Column
    from pbi_core.ssas.model_tables.model import Model
    from pbi_core.ssas.model_tables.table import Table
    from pbi_core.ssas.model_tables.variation import Variation


class Relationship(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/35bb4a68-b97e-409b-a5dd-14695fd99139)
    This class represents a relationship between two tables in a Tabular model.
    """

    cross_filtering_behavior: CrossFilteringBehavior
    from_column_id: int
    from_cardinality: int
    from_table_id: int
    is_active: bool
    join_on_date_behavior: JoinOnDateBehavior
    model_id: int
    name: str
    relationship_storage_id: int | None = None
    relationship_storage2_id: int | None = None
    relationship_storage2id: int | None = None  # TODO: check which one is wrong
    rely_on_referential_integrity: bool
    security_filtering_behavior: SecurityFilteringBehavior
    state: DataState
    to_cardinality: int
    to_column_id: int
    to_table_id: int
    type: RelationshipType

    modified_time: datetime.datetime
    refreshed_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.relationship)

    def from_table(self) -> "Table":
        """Returns the table the relationship is using as a filter.

        Note:
            In the bi-directional case, this table is also filtered

        """
        return self.tabular_model.tables.find({"id": self.from_table_id})

    def to_table(self) -> "Table":
        """Returns the table the relationship is being filtered.

        Note:
            In the bi-directional case, this table is also used as a filter

        """
        return self.tabular_model.tables.find({"id": self.to_table_id})

    def from_column(self) -> "Column":
        """The column in the from_table used to join with the to_table."""
        return self.tabular_model.columns.find({"id": self.from_column_id})

    def to_column(self) -> "Column":
        """The column in the to_table used to join with the from_table."""
        return self.tabular_model.columns.find({"id": self.to_column_id})

    def model(self) -> "Model":
        """The DB model this entity exists in."""
        return self.tabular_model.model

    def variations(self) -> set["Variation"]:
        return self.tabular_model.variations.find_all({"relationship_id": self.id})

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(
                self,
                lineage_type,
                [variation.get_lineage(lineage_type) for variation in self.variations()],
            )
        return LineageNode(
            self,
            lineage_type,
            [
                self.from_table().get_lineage(lineage_type),
                self.to_table().get_lineage(lineage_type),
                self.from_column().get_lineage(lineage_type),
                self.to_column().get_lineage(lineage_type),
            ],
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id}, from: {self.from_table()!r}, to: {self.to_table()!r})"
