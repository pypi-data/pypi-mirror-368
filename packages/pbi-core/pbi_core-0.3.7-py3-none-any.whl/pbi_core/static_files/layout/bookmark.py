# ruff: noqa: N815
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import Discriminator, Tag

from ._base_node import LayoutNode
from .expansion_state import ExpansionStateLevel, ExpansionStateRoot
from .filters import BookmarkFilter, FilterExpressionMetadata, HighlightScope, Orderby
from .sources import Source
from .visuals.base import PropertyDef
from .visuals.properties.base import Expression

if TYPE_CHECKING:
    from .layout import Layout
    from .section import Section
    from .visuals.base import BaseVisual


class BookmarkFilters(LayoutNode):
    byExpr: list[BookmarkFilter] = []
    byType: list[BookmarkFilter] = []
    byName: dict[str, BookmarkFilter] = {}


class HighlightSelection(LayoutNode):
    dataMap: dict[str, list[HighlightScope]]
    metadata: list[str] | None = None


class Highlight(LayoutNode):
    selection: list[HighlightSelection]
    filterExpressionMetadata: FilterExpressionMetadata | None = None


class DisplayMode(Enum):
    hidden = "hidden"


class Display(LayoutNode):
    mode: DisplayMode


class Remove(LayoutNode):
    object: str
    property: str
    selector: None = None


class BookmarkPartialVisualObject(LayoutNode):
    merge: dict[str, list[PropertyDef]] | None = None
    remove: list[Remove] | None = None


class ExpansionState(LayoutNode):
    roles: list[str]
    levels: list[ExpansionStateLevel]
    root: ExpansionStateRoot


class BookmarkPartialVisual(LayoutNode):
    visualType: str
    objects: BookmarkPartialVisualObject
    orderBy: list[Orderby] | None = None
    activeProjections: dict[str, list[Source]] | None = None
    display: Display | None = None
    expansionStates: list[ExpansionState] | None = None


class BookmarkVisual(LayoutNode):
    filters: BookmarkFilters | None = None
    singleVisual: BookmarkPartialVisual
    highlight: Highlight | None = None


class VisualContainerGroup(LayoutNode):
    isHidden: bool = False


class BookmarkSection(LayoutNode):
    _parent: "ExplorationState"  # pyright: ignore reportIncompatibleVariableOverride=false

    visualContainers: dict[str, BookmarkVisual] | None = None
    filters: BookmarkFilters | None = None
    visualContainerGroups: dict[str, VisualContainerGroup] | None = None


class OutspacePaneProperties(LayoutNode):
    expanded: Expression | None = None
    visible: Expression | None = None


class OutspacePane(LayoutNode):
    properties: OutspacePaneProperties


class MergeProperties(LayoutNode):
    outspacePane: list[OutspacePane]


class ExplorationStateProperties(LayoutNode):
    merge: MergeProperties | None = None


class ExplorationState(LayoutNode):
    _parent: "Bookmark"  # pyright: ignore reportIncompatibleVariableOverride=false

    version: float
    sections: dict[str, BookmarkSection]
    activeSection: str  # matches the section name?
    filters: BookmarkFilters | None = None
    objects: ExplorationStateProperties | None = None


class BookmarkOptions(LayoutNode):
    _parent: "Bookmark"  # pyright: ignore reportIncompatibleVariableOverride=false

    targetVisualNames: list[str] | None = None
    applyOnlyToTargetVisuals: bool = False
    suppressActiveSection: bool = False
    suppressData: bool = False
    suppressDisplay: bool = False


class Bookmark(LayoutNode):
    _parent: "Layout"  # pyright: ignore reportIncompatibleVariableOverride=false

    options: BookmarkOptions | None
    explorationState: ExplorationState | None
    name: str  # acts as an ID
    displayName: str

    def match_current_filters(self) -> None:
        raise NotImplementedError

    @staticmethod
    def new(  # noqa: PLR0913
        section: "Section",
        selected_visuals: list["BaseVisual"],
        bookmark_name: str,
        *,
        include_data: bool = True,
        include_display: bool = True,
        include_current_page: bool = True,
    ) -> "Bookmark":
        raise NotImplementedError


class BookmarkFolder(LayoutNode):
    _parent: "Layout"  # pyright: ignore reportIncompatibleVariableOverride=false
    displayName: str
    name: str  # acts as an ID
    children: list[Bookmark]


def get_bookmark_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "explorationState" in v:
            return "Bookmark"
        return "BookmarkFolder"
    return v.__class__.__name__


LayoutBookmarkChild = Annotated[
    Annotated[Bookmark, Tag("Bookmark")] | Annotated[BookmarkFolder, Tag("BookmarkFolder")],
    Discriminator(get_bookmark_type),
]
