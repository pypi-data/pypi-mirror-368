import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.model import Model


class Perspective(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/8bbe314e-f308-4732-875c-9530a1b0fe95)
    """

    description: int
    model_id: int
    name: str

    modified_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.perspective)

    def model(self) -> "Model":
        return self.tabular_model.model
