import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import DataSourceType, ImpersonationMode, Isolation

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.model import Model


class DataSource(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/ee12dcb7-096e-4e4e-99a4-47caeb9390f5)
    """

    account: str | None = None
    connection_string: str
    context_expression: str | None = None
    credential: str | None = None
    description: str | None = None
    impersonation_mode: ImpersonationMode
    isolation: Isolation
    max_connections: int
    model_id: int
    name: str
    options: str | None = None
    password: str | None = None
    provider: str | None = None
    timeout: int
    type: DataSourceType

    modified_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.data_source)

    def model(self) -> "Model":
        return self.tabular_model.model
