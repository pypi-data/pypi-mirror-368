import datetime
from enum import IntEnum
from typing import TYPE_CHECKING

from .base import SsasRenameRecord

if TYPE_CHECKING:
    from .model import Model


class ImpersonationMode(IntEnum):
    Default = 1
    ImpersonateAccount = 2
    ImpersonateAnonymous = 3
    ImpersonateCurrentUser = 4
    ImpersonateServiceAccount = 5
    ImpersonateUnattendedAccount = 6


class DataSourceType(IntEnum):
    Provider = 1
    Structured = 2


class Isolation(IntEnum):
    ReadCommitted = 1
    Snapshot = 2


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

    def model(self) -> "Model":
        return self.tabular_model.model
