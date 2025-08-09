import datetime
from typing import TYPE_CHECKING

from .base import SsasEditableRecord

if TYPE_CHECKING:
    from .perspective import Perspective
    from .table import Table


class PerspectiveTable(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/06bc5956-20e3-4bd2-8e5f-68a200efc18b)
    """

    include_all: bool
    perspective_id: int
    table_id: int

    modified_time: datetime.datetime

    def perspective(self) -> "Perspective":
        return self.tabular_model.perspectives.find(self.perspective_id)

    def table(self) -> "Table":
        return self.tabular_model.tables.find(self.table_id)
