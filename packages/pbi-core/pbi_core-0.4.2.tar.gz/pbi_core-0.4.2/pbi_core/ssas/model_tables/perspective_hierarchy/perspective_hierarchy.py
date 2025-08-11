import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.hierarchy import Hierarchy
    from pbi_core.ssas.model_tables.perspective_table import PerspectiveTable


class PerspectiveHierarchy(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/07941935-98bf-4e14-ab40-ef97d5c29765)
    """

    hierarchy_id: int
    perspective_table_id: int

    modified_time: datetime.datetime

    _commands: BaseCommands = PrivateAttr(default_factory=lambda: SsasCommands.perspective_hierarchy)

    def perspective_table(self) -> "PerspectiveTable":
        return self.tabular_model.perspective_tables.find(self.perspective_table_id)

    def hierarchy(self) -> "Hierarchy":
        return self.tabular_model.hierarchies.find(self.hierarchy_id)
