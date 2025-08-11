import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import PrivateAttr

from pbi_core.lineage import LineageNode
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.server._commands import RenameCommands
from pbi_core.ssas.server.utils import SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.linguistic_metadata import LinguisticMetadata
    from pbi_core.ssas.model_tables.model import Model


class Culture(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/d3770118-47bf-4304-9edf-8025f4820c45)
    """

    linguistic_metadata_id: int
    model_id: int
    name: str

    modified_time: datetime.datetime
    structure_modified_time: datetime.datetime

    _commands: RenameCommands = PrivateAttr(default_factory=lambda: SsasCommands.culture)

    def linguistic_metdata(self) -> "LinguisticMetadata":
        return self.tabular_model.linguistic_metadata.find({"id": self.linguistic_metadata_id})

    def model(self) -> "Model":
        return self.tabular_model.model

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type, [self.linguistic_metdata().get_lineage(lineage_type)])
        return LineageNode(self, lineage_type, [self.model().get_lineage(lineage_type)])
