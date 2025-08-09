import datetime
from typing import TYPE_CHECKING

from .base import SsasRenameRecord

if TYPE_CHECKING:
    from .model import Model


class Perspective(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/8bbe314e-f308-4732-875c-9530a1b0fe95)
    """

    description: int
    model_id: int
    name: str

    modified_time: datetime.datetime

    def model(self) -> "Model":
        return self.tabular_model.model
