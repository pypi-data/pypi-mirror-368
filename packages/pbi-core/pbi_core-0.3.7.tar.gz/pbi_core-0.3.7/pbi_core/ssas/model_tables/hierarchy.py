import datetime
from enum import IntEnum
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from pbi_core.lineage import LineageNode
from pbi_core.ssas.model_tables.enums import DataState

from .base import SsasRenameRecord

if TYPE_CHECKING:
    from .level import Level
    from .table import Table
    from .variation import Variation


class HideMembers(IntEnum):
    Default = 0
    HideBlankMembers = 1


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
