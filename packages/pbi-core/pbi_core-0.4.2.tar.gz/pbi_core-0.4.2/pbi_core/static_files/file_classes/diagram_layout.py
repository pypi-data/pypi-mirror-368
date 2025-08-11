from typing import Any, Literal
from uuid import UUID

from ._base import BaseFileModel

base_val = bool | int | str


class Position(BaseFileModel):
    x: int | float
    y: int | float


class Size(BaseFileModel):
    height: int | float
    width: int | float


class Node100(BaseFileModel):
    top: float
    left: float
    width: float
    height: float
    layedOut: bool
    nodeIndex: str


class Node110(BaseFileModel):
    location: Position
    nodeIndex: str
    nodeLineageTag: UUID | None = None
    size: Size
    zIndex: int


class BoundingBoxPosition(BaseFileModel):
    x: float
    y: float


class TableLayout(BaseFileModel):
    boundingBoxHeight: float
    boundingBoxWidth: float
    boundingBoxPosition: BoundingBoxPosition
    nodes: list[Node100]


class DiagramV100(BaseFileModel):
    name: str
    zoomValue: float
    isDefault: bool
    tables: list[str]
    layout: TableLayout


class DiagramV110(BaseFileModel):
    ordinal: int
    scrollPosition: Position
    nodes: list[Node110]
    name: str
    zoomValue: float
    pinKeyFieldsToTop: bool
    showExtraHeaderInfo: bool
    hideKeyFieldsWhenCollapsed: bool
    tablesLocked: bool = False


class DiagramLayoutV100(BaseFileModel):
    version: Literal["1.0.0"]
    diagrams: list[DiagramV100]
    selectedDiagram: str | None = None
    defaultDiagram: str | None = None
    showIntroduceNewModelViewDialog: bool = True


class DiagramLayoutV110(BaseFileModel):
    version: Literal["1.1.0"]
    diagrams: list[DiagramV110]
    selectedDiagram: str | None = None
    defaultDiagram: str | None = None


DiagramLayout = DiagramLayoutV100 | DiagramLayoutV110


def parse_diagram_layout(v: dict[str, Any]) -> DiagramLayout:
    if v["version"] == "1.0.0":
        return DiagramLayoutV100.model_validate(v)
    if v["version"] == "1.1.0":
        return DiagramLayoutV110.model_validate(v)
    msg = f"Unknown Version: {v['version']}"
    raise ValueError(msg)
