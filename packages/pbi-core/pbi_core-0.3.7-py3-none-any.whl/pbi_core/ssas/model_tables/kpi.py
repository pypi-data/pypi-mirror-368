import datetime
from typing import TYPE_CHECKING, Literal

from pbi_core.lineage import LineageNode

from .base import SsasEditableRecord

if TYPE_CHECKING:
    from .measure import Measure


class KPI(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/1289ceca-8113-4019-8f90-8132a91117cf)
    """

    description: str | None = None
    measure_id: int
    status_description: str | None = None
    status_expression: str
    status_graphic: str
    target_description: str | None = None
    target_expression: str
    target_format_string: str
    trend_description: str | None = None
    trend_expression: str | None = None

    modified_time: datetime.datetime

    def pbi_core_name(self) -> str:
        """Returns the name displayed in the PBIX report."""
        return self.measure().pbi_core_name()

    def measure(self) -> "Measure":
        return self.tabular_model.measures.find({"id": self.measure_id})

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type)
        return LineageNode(self, lineage_type, [self.measure().get_lineage(lineage_type)])

    @classmethod
    def _db_command_obj_name(cls) -> str:
        return "Kpis"
