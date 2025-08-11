from typing import TYPE_CHECKING, Any

from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector
from pbi_core.static_files.layout.sources.paragraphs import Paragraph

from .base import BaseVisual
from .properties.base import Expression

if TYPE_CHECKING:
    from pbi_core.static_files.model_references import ModelColumnReference, ModelMeasureReference


class GeneralProperties(LayoutNode):
    paragraphs: list[Paragraph] | None = None
    responsive: Expression | None = None


class General(LayoutNode):
    properties: GeneralProperties


class ValuePropertiesHelper(LayoutNode):
    context: Any | None = None  # TODO: should be Source, but causes circular import issues with Subquery
    expr: Any | None = None  # TODO: should be Source, but causes circular import issues with Subquery
    value: Any | None = None  # TODO: should be Source, but causes circular import issues with Subquery
    propertyDefinitionKind: str | None = None


class ValueProperties(LayoutNode):
    expr: ValuePropertiesHelper
    formatString: Expression | None = None


class Value(LayoutNode):
    properties: ValueProperties | None = None
    selector: Selector | None = None


class TextBoxProperties(LayoutNode):
    general: list[General]
    values: list[Value] | None = None


class TextBox(BaseVisual):
    visualType: str = "textbox"
    model_config = ConfigDict(extra="forbid")

    drillFilterOtherVisuals: bool = True
    objects: TextBoxProperties | None = None

    def get_ssas_elements(self) -> "set[ModelColumnReference | ModelMeasureReference]":  # noqa: PLR6301
        return set()
