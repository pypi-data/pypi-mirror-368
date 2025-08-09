import datetime
from typing import TYPE_CHECKING

from .base import SsasEditableRecord

if TYPE_CHECKING:
    from .column import Column
    from .perspective_table import PerspectiveTable


class PerspectiveColumn(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/f468353f-81a9-4a95-bb66-8997602bcd6d)
    """

    column_id: int
    perspective_table_id: int

    modified_time: datetime.datetime

    def perspective_table(self) -> "PerspectiveTable":
        return self.tabular_model.perspective_tables.find(self.perspective_table_id)

    def column(self) -> "Column":
        return self.tabular_model.columns.find(self.column_id)
