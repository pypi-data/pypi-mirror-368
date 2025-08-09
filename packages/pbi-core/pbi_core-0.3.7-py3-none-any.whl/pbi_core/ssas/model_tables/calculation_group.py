import datetime
from typing import TYPE_CHECKING

from .base import SsasEditableRecord

if TYPE_CHECKING:
    from .table import Table


class CalculationGroup(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/ed9dcbcf-9910-455f-abc4-13c575157cfb)
    """

    description: str
    precedence: int
    table_id: int

    modified_time: datetime.datetime

    def table(self) -> "Table":
        return self.tabular_model.tables.find(self.table_id)
