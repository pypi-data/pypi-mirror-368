

from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class DataBarsProperties(LayoutNode):
    axisColor: Expression
    hideText: Expression
    negativeColor: Expression
    positiveColor: Expression
    reverseDirection: Expression


class ColumnFormattingProperties(LayoutNode):
    alignment: Expression | None = None
    backColor: Expression | None = None
    dataBars: DataBarsProperties | None = None
    fontColor: Expression | None = None
    labelDisplayUnits: Expression | None = None
    labelPrecision: Expression | None = None
    styleHeader: Expression | None = None
    styleValues: Expression | None = None


class ColumnFormatting(LayoutNode):
    properties: ColumnFormattingProperties
    selector: Selector | None = None


class TotalProperties(LayoutNode):
    fontColor: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    outline: Expression | None = None
    totals: Expression | None = None


class Total(LayoutNode):
    properties: TotalProperties
    selector: Selector | None = None


class ValuesProperties(LayoutNode):
    backColor: Expression | None = None
    backColorPrimary: Expression | None = None
    backColorSecondary: Expression | None = None
    fontColor: Expression | None = None
    fontColorPrimary: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    outline: Expression | None = None
    urlIcon: Expression | None = None
    wordWrap: Expression | None = None


class Values(LayoutNode):
    properties: ValuesProperties
    selector: Selector | None = None


class ColumnHeadersProperties(LayoutNode):
    alignment: Expression | None = None
    autoSizeColumnWidth: Expression | None = None
    backColor: Expression | None = None
    bold: Expression | None = None
    fontColor: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    outline: Expression | None = None
    outlineStyle: Expression | None = None
    wordWrap: Expression | None = None


class ColumnHeaders(LayoutNode):
    properties: ColumnHeadersProperties
    selector: Selector | None = None


class ColumnWidthProperties(LayoutNode):
    value: Expression


class ColumnWidth(LayoutNode):
    properties: ColumnWidthProperties
    selector: Selector | None = None


class GridProperties(LayoutNode):
    gridHorizontal: Expression | None = None
    gridHorizontalColor: Expression | None = None
    gridHorizontalWeight: Expression | None = None
    gridVertical: Expression | None = None
    gridVerticalColor: Expression | None = None
    gridVerticalWeight: Expression | None = None
    imageHeight: Expression | None = None
    outlineColor: Expression | None = None
    outlineWeight: Expression | None = None
    rowPadding: Expression | None = None
    textSize: Expression | None = None


class Grid(LayoutNode):
    properties: GridProperties
    selector: Selector | None = None


class GeneralProperties(LayoutNode):
    pass


class General(LayoutNode):
    properties: GeneralProperties


class TableChartColumnProperties(LayoutNode):
    columnFormatting: list[ColumnFormatting] | None = None
    columnHeaders: list[ColumnHeaders] | None = None
    columnWidth: list[ColumnWidth] | None = None
    general: list[General] | None = None
    grid: list[Grid] | None = None
    total: list[Total] | None = None
    values: list[Values] | None = None


class TableChart(BaseVisual):
    visualType: str = "tableEx"
    objects: TableChartColumnProperties | None = None
    model_config = ConfigDict(extra="forbid")
    columnProperties: dict[str, ColumnProperty] | None = None
