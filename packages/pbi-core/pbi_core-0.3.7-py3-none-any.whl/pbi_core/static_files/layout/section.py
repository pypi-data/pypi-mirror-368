# ruff: noqa: N815
from enum import IntEnum
from typing import TYPE_CHECKING, Literal
from uuid import UUID

from pbi_core.lineage.main import LineageNode
from pbi_core.static_files.model_references import ModelColumnReference, ModelMeasureReference
from pydantic import ConfigDict, Json

from ._base_node import LayoutNode
from .filters import PageFilter
from .performance import Performance, get_performance
from .visual_container import VisualContainer

if TYPE_CHECKING:
    from pbi_core.ssas.server.tabular_model.tabular_model import BaseTabularModel, LocalTabularModel

    from .layout import Layout


class DisplayOption(IntEnum):
    FIT_TO_PAGE = 0
    FIT_TO_WIDTH = 1
    ACTUAL_SIZE = 2
    MOBILE = 3


class SectionVisibility(IntEnum):
    VISIBLE = 0
    HIDDEN = 1


class SectionConfig(LayoutNode):
    visibility: SectionVisibility = SectionVisibility.VISIBLE
    model_config = ConfigDict(extra="allow")


class Section(LayoutNode):
    _parent: "Layout"  # pyright: ignore reportIncompatibleVariableOverride=false
    height: int
    width: int
    displayOption: DisplayOption
    config: Json[SectionConfig]
    objectId: UUID | None = None
    visualContainers: list[VisualContainer]
    ordinal: int = 0
    filters: Json[list[PageFilter]]
    displayName: str
    name: str
    id: int | None = None

    def pbi_core_name(self) -> str:
        return self.name

    def get_ssas_elements(
        self,
        *,
        include_visuals: bool = True,
        include_filters: bool = True,
    ) -> set[ModelColumnReference | ModelMeasureReference]:
        """Returns the SSAS elements (columns and measures) this report page is directly dependent on."""
        ret: set[ModelColumnReference | ModelMeasureReference] = set()
        if include_visuals:
            for viz in self.visualContainers:
                ret.update(viz.get_ssas_elements())
        if include_filters:
            for f in self.filters:
                ret.update(f.get_ssas_elements())
        return ret

    def get_lineage(
        self,
        lineage_type: Literal["children", "parents"],
        tabular_model: "BaseTabularModel",
    ) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type)

        page_filters = self.get_ssas_elements()
        report_filters = self._parent.get_ssas_elements(include_sections=False)
        entities = page_filters | report_filters
        children_nodes = [ref.to_model(tabular_model) for ref in entities]

        children_lineage = [p.get_lineage(lineage_type) for p in children_nodes if p is not None]
        return LineageNode(self, lineage_type, children_lineage)

    def get_performance(self, model: "LocalTabularModel", *, clear_cache: bool = False) -> list[Performance]:
        """Calculates various metrics on the speed of the visual.

        Current Metrics:
            Total Seconds to Query
            Total Rows Retrieved
        """
        commands: list[str] = []
        for viz in self.visualContainers:
            if viz.query is not None:
                command = viz._get_data_command()
                if command is not None:
                    commands.append(command.get_dax(model).dax)
        if not commands:
            msg = "Cannot get performance for a page without any querying visuals"
            raise NotImplementedError(msg)
        return get_performance(model, commands, clear_cache=clear_cache)
