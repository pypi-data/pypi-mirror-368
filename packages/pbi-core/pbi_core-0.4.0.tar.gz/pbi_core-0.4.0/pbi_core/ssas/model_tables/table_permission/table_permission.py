import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.enums import DataState
from pbi_core.ssas.server._commands import BaseCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import MetadataPermission

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.role import Role


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

    _commands: BaseCommands = PrivateAttr(default_factory=lambda: SsasCommands.table_permission)

    def role(self) -> "Role":
        return self.tabular_model.roles.find(self.role_id)
