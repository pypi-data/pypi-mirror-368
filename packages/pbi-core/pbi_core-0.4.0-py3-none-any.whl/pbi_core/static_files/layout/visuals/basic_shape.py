from typing import TYPE_CHECKING

from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode

from .base import BaseVisual
from .properties.base import Expression

if TYPE_CHECKING:
    from pbi_core.static_files.model_references import ModelColumnReference, ModelMeasureReference


class FillPropertiesHelper(LayoutNode):
    fillColor: Expression | None = None
    show: Expression | None = None
    transparency: Expression | None = None


class FillProperties(LayoutNode):
    properties: FillPropertiesHelper


class GeneralPropertiesHelper(LayoutNode):
    shapeType: Expression | None = None


class GeneralProperties(LayoutNode):
    properties: GeneralPropertiesHelper


class LinePropertiesHelper(LayoutNode):
    lineColor: Expression | None = None
    roundEdge: Expression | None = None
    transparency: Expression | None = None
    weight: Expression | None = None


class LineProperties(LayoutNode):
    properties: LinePropertiesHelper


class RotationPropertiesHelper(LayoutNode):
    angle: Expression | None = None


class RotationProperties(LayoutNode):
    properties: RotationPropertiesHelper


class BasicShapeProperties(LayoutNode):
    fill: list[FillProperties] | None = None
    general: list[GeneralProperties] | None = None
    line: list[LineProperties] | None = None
    rotation: list[RotationProperties] | None = None


class BasicShape(BaseVisual):
    visualType: str = "basicShape"
    model_config = ConfigDict(extra="forbid")

    drillFilterOtherVisuals: bool = True
    objects: BasicShapeProperties | None = None

    def get_ssas_elements(self) -> "set[ModelColumnReference | ModelMeasureReference]":  # noqa: PLR6301
        return set()
