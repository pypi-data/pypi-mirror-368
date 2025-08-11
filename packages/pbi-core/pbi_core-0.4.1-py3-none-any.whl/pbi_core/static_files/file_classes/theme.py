
from pydantic_extra_types.color import Color

from ._base import BaseFileModel

base_val = bool | int | str


class TextClass(BaseFileModel):
    fontSize: int
    fontFace: str
    color: Color


class TextClasses(BaseFileModel):
    callout: TextClass
    title: TextClass
    header: TextClass
    label: TextClass


class ColorName(BaseFileModel):
    color: Color


class ColorThemeData(BaseFileModel):
    solid: ColorName


class Theme(BaseFileModel):
    """A class mapping the fields of the Theme JSON.

    Documented `here <https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes#set-theme-colors>`
    """

    name: str
    dataColors: list[str] = []
    foreground: str | None = None
    foregroundNeutralSecondary: Color | None = None
    foregroundNeutralTertiary: Color | None = None
    background: Color | None = None
    backgroundLight: Color | None = None
    backgroundNeutral: Color | None = None
    tableAccent: Color | None = None
    good: Color | None = None
    neutral: Color | None = None
    bad: Color | None = None
    maximum: Color | None = None
    center: Color | None = None
    minimum: Color | None = None
    null: Color | None = None
    hyperlink: Color | None = None
    visitedHyperlink: Color | None = None

    textClasses: TextClasses | None = None
    visualStyles: dict[str, dict[str, dict[str, list[dict[str, bool | int | str | ColorThemeData]]]]]
