import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from pydantic import PrivateAttr

from pbi_core.lineage import LineageNode
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.column import Column
    from pbi_core.ssas.model_tables.hierarchy import Hierarchy


class Level(SsasRenameRecord):
    """A level in a hierarchy. For example, in a hierarchy of "Date", the levels could be "Year", "Month", and "Day".

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/a010d75e-3b68-4825-898f-62fdeab4557f)
    """

    column_id: int
    description: str | None = None
    """A description of the level, which may be used in the hover tooltip in edit mode"""
    hierarchy_id: int
    name: str
    """The name of the level, e.g. "Year", "Quarter", "Month", "Day" in a Date hierarchy."""
    ordinal: int

    lineage_tag: UUID = uuid4()
    source_lineage_tag: UUID = uuid4()

    modified_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.level)

    def column(self) -> "Column":
        return self.tabular_model.columns.find({"id": self.column_id})

    def hierarchy(self) -> "Hierarchy":
        return self.tabular_model.hierarchies.find({"id": self.hierarchy_id})

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type)
        return LineageNode(
            self,
            lineage_type,
            [self.column().get_lineage(lineage_type), self.hierarchy().get_lineage(lineage_type)],
        )
