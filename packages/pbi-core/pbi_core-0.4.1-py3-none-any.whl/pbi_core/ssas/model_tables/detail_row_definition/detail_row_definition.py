import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.enums import DataState, ObjectType
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.measure import Measure
    from pbi_core.ssas.model_tables.table import Table


class DetailRowDefinition(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/7eb1e044-4eed-467d-b10f-ce208798ddb0)

    Note:
        Additional details can be found here: [SQLBI](https://www.sqlbi.com/articles/controlling-drillthrough-in-excel-pivottables-connected-to-power-bi-or-analysis-services/)

    """

    error_message: str
    expression: str
    object_id: int
    object_type: ObjectType
    state: DataState

    modified_time: datetime.datetime

    _commands: BaseCommands = PrivateAttr(default_factory=lambda: SsasCommands.detail_row_defintion)

    @classmethod
    def _db_type_name(cls) -> str:
        return "DetailRowsDefinition"

    def object(self) -> "Table | Measure":
        match self.object_type:
            case ObjectType.MEASURE:
                return self.tabular_model.measures.find(self.object_id)
            case ObjectType.TABLE:
                return self.tabular_model.tables.find(self.object_id)
            case _:
                msg = f"No logic for object type: {self.object_type}"
                raise TypeError(msg)
