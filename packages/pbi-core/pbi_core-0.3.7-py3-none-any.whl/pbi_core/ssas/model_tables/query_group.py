from typing import TYPE_CHECKING, Literal

from pbi_core.lineage import LineageNode

from .base import SsasEditableRecord

if TYPE_CHECKING:
    from .expression import Expression
    from .model import Model
    from .partition import Partition


class QueryGroup(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/40b3830b-25ee-41a6-87d2-49616028dd13)
    This class represents a group of queries that can be executed together.
    """

    _repr_name_field = "folder"

    description: str | None = None
    folder: str
    model_id: int

    def expressions(self) -> set["Expression"]:
        return self.tabular_model.expressions.find_all({"query_group_id": self.id})

    def partitions(self) -> set["Partition"]:
        return self.tabular_model.partitions.find_all({"query_group_id": self.id})

    def model(self) -> "Model":
        return self.tabular_model.model

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(
                self,
                lineage_type,
                [expression.get_lineage(lineage_type) for expression in self.expressions()]
                + [partition.get_lineage(lineage_type) for partition in self.partitions()],
            )
        return LineageNode(self, lineage_type, [self.model().get_lineage(lineage_type)])
