import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import Json, PrivateAttr

from pbi_core.lineage import LineageNode
from pbi_core.pydantic.main import BaseValidation
from pbi_core.ssas.model_tables.base import RefreshType, SsasModelRecord
from pbi_core.ssas.server._commands import ModelCommands
from pbi_core.ssas.server.utils import SsasCommands

from .enums import DefaultDataView

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables.culture import Culture
    from pbi_core.ssas.model_tables.measure import Measure
    from pbi_core.ssas.model_tables.query_group import QueryGroup
    from pbi_core.ssas.model_tables.table import Table


class DataAccessOptions(BaseValidation):
    fastCombine: bool = True
    legacyRedirects: bool = False
    returnErrorValuesAsNull: bool = False


class Model(SsasModelRecord):
    """tbd.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/60094cd5-1c7e-4353-9299-251bfa838cc6)
    """

    _default_refresh_type = RefreshType.CALCULATE

    automatic_aggregation_options: str | None = None
    collation: str | None = None
    culture: str
    data_access_options: Json[DataAccessOptions] = DataAccessOptions()
    data_source_default_max_connections: int
    data_source_variables_override_behavior: int
    default_data_view: DefaultDataView
    default_measure_id: int | None = None
    default_mode: int
    default_powerbi_data_source_version: int
    description: str | None = None
    discourage_composite_models: bool = True
    discourage_implicit_measures: bool
    disable_auto_exists: int | None = None
    force_unique_names: bool
    m_attributes: str | None = None
    max_parallelism_per_refresh: int | None = None
    max_parallelism_per_query: int | None = None
    name: str
    source_query_culture: str = "en-US"
    storage_location: str | None = None
    version: int

    modified_time: datetime.datetime
    structure_modified_time: datetime.datetime

    _commands: ModelCommands = PrivateAttr(default_factory=lambda: SsasCommands.model)

    def default_measure(self) -> "Measure | None":
        if self.default_measure_id is None:
            return None
        return self.tabular_model.measures.find(self.default_measure_id)

    def cultures(self) -> set["Culture"]:
        return self.tabular_model.cultures.find_all({"model_id": self.id})

    def tables(self) -> set["Table"]:
        return self.tabular_model.tables.find_all({"model_id": self.id})

    def query_groups(self) -> set["QueryGroup"]:
        return self.tabular_model.query_groups.find_all({"model_id": self.id})

    @classmethod
    def _db_command_obj_name(cls) -> str:
        return "Model"

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(
                self,
                lineage_type,
                [c.get_lineage(lineage_type) for c in self.cultures()]
                + [t.get_lineage(lineage_type) for t in self.tables()]
                + [q.get_lineage(lineage_type) for q in self.query_groups()],
            )
        return LineageNode(self, lineage_type)
