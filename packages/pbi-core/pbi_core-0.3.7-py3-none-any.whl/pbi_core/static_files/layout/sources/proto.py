from pbi_core.static_files.layout._base_node import LayoutNode


class ProtoSource(LayoutNode):
    Source: str


class ProtoSourceRef(LayoutNode):
    SourceRef: ProtoSource
