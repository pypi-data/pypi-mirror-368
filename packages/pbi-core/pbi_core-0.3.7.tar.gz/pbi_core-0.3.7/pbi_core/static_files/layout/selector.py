from ._base_node import LayoutNode
from .condition import ConditionType


class DataViewWildcard(LayoutNode):
    matchingOption: int
    roles: list[str] | None = None


class SelectorData(LayoutNode):
    roles: list[str] | None = None
    dataViewWildcard: DataViewWildcard | None = None
    scopeId: ConditionType | None = None


# TODO: possibly replace with a union?
class Selector(LayoutNode):
    id: str | None = None
    # Weird values, pretty confident this is not an enum
    metadata: str | None = None
    data: list[SelectorData] | None = None
