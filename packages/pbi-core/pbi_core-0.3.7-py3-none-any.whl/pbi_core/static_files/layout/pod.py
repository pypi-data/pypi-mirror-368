# ruff: noqa: N815
from enum import IntEnum
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Json

from ._base_node import LayoutNode
from .sources import ColumnSource

if TYPE_CHECKING:
    from .layout import Layout


class Parameter(LayoutNode):
    _parent: "Pod"  # pyright: ignore reportIncompatibleVariableOverride=false

    name: str
    boundFilter: str
    fieldExpr: ColumnSource | None = None
    isLegacySingleSelection: bool | None = False
    asAggregation: bool | None = False


class PodType(IntEnum):
    NA1 = 1
    NA2 = 2


class PodConfig(LayoutNode):
    acceptsFilterContext: bool = False


class Pod(LayoutNode):
    _parent: "Layout"  # pyright: ignore reportIncompatibleVariableOverride=false

    id: int | None = None
    name: str
    boundSection: str
    config: Json[PodConfig]
    parameters: Json[list[Parameter]] = []
    type: PodType | None = None
    referenceScope: int | None = None
    cortanaEnabled: bool | None = None
    objectId: UUID | None = None
