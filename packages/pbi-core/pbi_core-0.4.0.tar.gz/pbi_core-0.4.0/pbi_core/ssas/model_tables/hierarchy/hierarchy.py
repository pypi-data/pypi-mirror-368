import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from pydantic import PrivateAttr

from pbi_core.lineage import LineageNode
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.enums import DataState
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import HideMembers

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.level import Level
    from pbi_core.ssas.model_tables.table import Table
    from pbi_core.ssas.model_tables.variation import Variation


class Hierarchy(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/4eff6661-1458-4c5a-9875-07218f1458e5)
    """

    description: str | None = None
    display_folder: str | None = None
    hide_members: HideMembers
    hierarchy_storage_id: int
    is_hidden: bool
    name: str
    state: DataState
    table_id: int
    """A foreign key to the Table object the hierarchy is stored under"""

    lineage_tag: UUID = uuid4()
    source_lineage_tag: UUID = uuid4()

    modified_time: datetime.datetime
    refreshed_time: datetime.datetime
    """The last time the sources for this hierarchy were refreshed"""
    structure_modified_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.hierarchy)

    def table(self) -> "Table":
        return self.tabular_model.tables.find({"id": self.table_id})

    def levels(self) -> set["Level"]:
        return self.tabular_model.levels.find_all({"hierarchy_id": self.id})

    def variations(self) -> set["Variation"]:
        return self.tabular_model.variations.find_all({"default_hierarchy_id": self.id})

    @classmethod
    def _db_command_obj_name(cls) -> str:
        return "Hierarchies"

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(
                self,
                lineage_type,
                [level.get_lineage(lineage_type) for level in self.levels()]
                + [variation.get_lineage(lineage_type) for variation in self.variations()],
            )

        return LineageNode(
            self,
            lineage_type,
            [
                self.table().get_lineage(lineage_type),
            ],
        )
