from typing import Annotated, Any

from pydantic import Discriminator, Tag

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector
from pbi_core.static_files.layout.sources import Source


class TextStyle(LayoutNode):
    color: str | None = None  # TODO: check that it's hex
    fontSize: str | None = None
    fontFamily: str | None = None
    fontStyle: str | None = None  # italic, etc
    fontWeight: str | None = None  # bold, etc
    textDecoration: str | None = None  # underline, etc


class CasePattern(LayoutNode):
    expr: Source


class Case(LayoutNode):
    pattern: CasePattern
    textRuns: list["TextRun"]


class DefaultCaseTextRun(LayoutNode):
    value: str


class DefaultCase(LayoutNode):
    textRuns: list[DefaultCaseTextRun]


class PropertyIdentifier(LayoutNode):
    objectName: str | None = None
    propertyName: str | None = None
    selector: Selector | None = None
    propertyIdentifier: "PropertyIdentifier | None" = None


class TextRunExpression(LayoutNode):
    propertyIdentifier: PropertyIdentifier
    selector: Selector | None = None


def get_text_run_type(v: object | str | dict[str, Any]) -> str:
    if isinstance(v, str):
        return "str"
    if isinstance(v, dict) and "propertyIdentifier" in v:
        return "PropertyIdentifier"
    return v.__class__.__name__


TextRunValue = Annotated[
    Annotated[str, Tag("str")] | Annotated[PropertyIdentifier, Tag("PropertyIdentifier")],
    Discriminator(get_text_run_type),
]


class TextRun(LayoutNode):
    textStyle: TextStyle | None = None
    value: TextRunValue | None = None
    cases: list[Case] | None = None
    defaultCase: DefaultCase | None = None
    url: str | None = None
    expression: TextRunExpression | None = None


class Paragraph(LayoutNode):
    horizontalTextAlignment: str | None = None  # TODO: convert to enum
    textRuns: list[TextRun]
