import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.perspective import Perspective
    from pbi_core.ssas.model_tables.table import Table


class PerspectiveTable(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/06bc5956-20e3-4bd2-8e5f-68a200efc18b)
    """

    include_all: bool
    perspective_id: int
    table_id: int

    modified_time: datetime.datetime

    _commands: BaseCommands = PrivateAttr(default_factory=lambda: SsasCommands.perspective_table)

    def perspective(self) -> "Perspective":
        return self.tabular_model.perspectives.find(self.perspective_id)

    def table(self) -> "Table":
        return self.tabular_model.tables.find(self.table_id)
