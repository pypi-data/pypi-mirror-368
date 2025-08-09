import datetime
from typing import TYPE_CHECKING

from pbi_core.ssas.model_tables.table_permission import MetadataPermission, TablePermission

from .base import SsasEditableRecord

if TYPE_CHECKING:
    from .column import Column


class ColumnPermission(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/10566cbb-390d-470d-b0ff-fc2713277031)
    """

    column_id: int
    metadata_permission: MetadataPermission
    table_permission_id: int

    modified_time: datetime.datetime

    def table_permission(self) -> TablePermission:
        return self.tabular_model.table_permissions.find(self.table_permission_id)

    def column(self) -> "Column":
        return self.tabular_model.columns.find(self.column_id)
