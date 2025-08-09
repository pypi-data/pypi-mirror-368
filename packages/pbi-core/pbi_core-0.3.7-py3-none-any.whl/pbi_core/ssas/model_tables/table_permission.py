import datetime
from enum import IntEnum
from typing import TYPE_CHECKING

from pbi_core.ssas.model_tables.enums import DataState

from .base import SsasEditableRecord

if TYPE_CHECKING:
    from .role import Role


class MetadataPermission(IntEnum):
    """Source: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/ac2ceeb3-a54e-4bf5-85b0-a770d4b1716e)."""

    Default = 0
    _None = 1
    Read = 2


class TablePermission(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/ac2ceeb3-a54e-4bf5-85b0-a770d4b1716e)
    """

    error_message: str | None = None
    filter_expression: str | None = None
    metadata_permission: MetadataPermission
    role_id: int
    state: DataState
    table_id: int

    modified_time: datetime.datetime

    def role(self) -> "Role":
        return self.tabular_model.roles.find(self.role_id)
