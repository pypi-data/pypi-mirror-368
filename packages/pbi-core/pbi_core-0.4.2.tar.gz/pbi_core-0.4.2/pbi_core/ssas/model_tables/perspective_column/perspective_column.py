import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.column import Column
    from pbi_core.ssas.model_tables.perspective_table import PerspectiveTable


class PerspectiveColumn(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/f468353f-81a9-4a95-bb66-8997602bcd6d)
    """

    column_id: int
    perspective_table_id: int

    modified_time: datetime.datetime

    _commands: BaseCommands = PrivateAttr(default_factory=lambda: SsasCommands.perspective_column)

    def perspective_table(self) -> "PerspectiveTable":
        return self.tabular_model.perspective_tables.find(self.perspective_table_id)

    def column(self) -> "Column":
        return self.tabular_model.columns.find(self.column_id)
