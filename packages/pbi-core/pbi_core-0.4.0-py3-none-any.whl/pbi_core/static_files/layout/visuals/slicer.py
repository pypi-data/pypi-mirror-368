
from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.expansion_state import ExpansionState
from pbi_core.static_files.layout.selector import SelectorData

from .base import BaseVisual, PropertyDef
from .table import ColumnProperty


class SyncGroup(LayoutNode):
    groupName: str
    fieldChanges: bool
    filterChanges: bool = True


class CachedFilterDisplayItems(LayoutNode):
    id: SelectorData
    displayName: str


class Slicer(BaseVisual):
    visualType: str = "slicer"
    model_config = ConfigDict(extra="forbid")
    columnProperties: dict[str, ColumnProperty] | None = None
    syncGroup: SyncGroup | None = None
    cachedFilterDisplayItems: list[CachedFilterDisplayItems] | None = None
    expansionStates: list[ExpansionState] | None = None
    objects: dict[str, list[PropertyDef]] | None = None
