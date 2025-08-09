import datetime
from enum import IntEnum
from typing import TYPE_CHECKING

from .base import SsasRenameRecord

if TYPE_CHECKING:
    from .model import Model


class ModelPermission(IntEnum):
    _None = 1
    Read = 2
    ReadRefresh = 3
    Refresh = 4
    Administrator = 5


class Role(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/94a8e609-b1ae-4814-b8dc-963005eebade)
    """

    description: str | None = None
    model_id: int
    model_permission: ModelPermission
    name: str

    modified_time: datetime.datetime

    def model(self) -> "Model":
        return self.tabular_model.model
