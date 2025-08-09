from pbi_core.static_files.layout._base_node import LayoutNode

from .base import Expression


# TODO: subclass filters so that the properties have fewer None defaults
class FilterProperties(LayoutNode):
    isInvertedSelectionMode: Expression | None = None
    requireSingleSelect: Expression | None = None


class FilterPropertiesContainer(LayoutNode):
    properties: FilterProperties


class FilterObjects(LayoutNode):
    general: list[FilterPropertiesContainer] | None = None
