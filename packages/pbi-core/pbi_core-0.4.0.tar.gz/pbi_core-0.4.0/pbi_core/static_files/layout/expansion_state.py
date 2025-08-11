
from ._base_node import LayoutNode
from .sources import Source


class Information(LayoutNode):
    method: str
    disabled: bool = False


class ExpansionStateLevel(LayoutNode):
    queryRefs: list[str]
    isCollapsed: bool = False
    isPinned: bool = False
    isLocked: bool = False
    identityKeys: list[Source] | None = None
    identityValues: list[None] | None = None
    AIInformation: Information | None = None


class ExpansionStateChild(LayoutNode):
    isToggled: bool = False
    identityValues: list[Source]
    children: list["ExpansionStateChild"] | None = None


class ExpansionStateRoot(LayoutNode):
    identityValues: list[None] | None = None
    isToggled: bool = False
    children: list[ExpansionStateChild] | None = None


class ExpansionState(LayoutNode):
    roles: list[str]
    isToggled: bool = False
    levels: list[ExpansionStateLevel] | None = None
    root: ExpansionStateRoot | None = None
