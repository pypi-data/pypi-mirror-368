

from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression
from .text_box import GeneralProperties


class CategoryAxisProperties(LayoutNode):
    axisType: Expression | None = None
    concatenateLabels: Expression | None = None
    fontSize: Expression | None = None
    gridlineColor: Expression | None = None
    gridlineShow: Expression | None = None
    gridlineStyle: Expression | None = None
    innerPadding: Expression | None = None
    labelColor: Expression | None = None
    maxMarginFactor: Expression | None = None
    preferredCategoryWidth: Expression | None = None
    show: Expression | None = None
    showAxisTitle: Expression | None = None
    titleColor: Expression | None = None
    titleFontSize: Expression | None = None
    titleText: Expression | None = None


class CategoryAxis(LayoutNode):
    properties: CategoryAxisProperties
    selector: Selector | None = None


class DataPointProperties(LayoutNode):
    fill: Expression | None = None
    fillRule: Expression | None = None
    showAllDataPoints: Expression | None = None


class DataPoint(LayoutNode):
    properties: DataPointProperties
    selector: Selector | None = None


class LabelsProperties(LayoutNode):
    backgroundColor: Expression | None = None
    backgroundTransparency: Expression | None = None
    color: Expression | None = None
    enableBackground: Expression | None = None
    fontSize: Expression | None = None
    labelDensity: Expression | None = None
    labelDisplayUnits: Expression | None = None
    labelOrientation: Expression | None = None
    labelPosition: Expression | None = None
    show: Expression | None = None
    showAll: Expression | None = None


class Labels(LayoutNode):
    properties: LabelsProperties
    selector: Selector | None = None


class LegendProperties(LayoutNode):
    fontSize: Expression | None = None
    labelColor: Expression | None = None
    position: Expression | None = None
    show: Expression | None = None
    showTitle: Expression | None = None


class Legend(LayoutNode):
    properties: LegendProperties
    selector: Selector | None = None


class ValueAxisProperties(LayoutNode):
    axisScale: Expression | None = None
    fontSize: Expression | None = None
    gridlineShow: Expression | None = None
    logAxisScale: Expression | None = None
    show: Expression | None = None
    showAxisTitle: Expression | None = None
    start: Expression | None = None
    titleFontFamily: Expression | None = None


class ValueAxis(LayoutNode):
    properties: ValueAxisProperties
    selector: Selector | None = None


class General(LayoutNode):
    properties: GeneralProperties


class ZoomProperties(LayoutNode):
    show: Expression | None = None


class Zoom(LayoutNode):
    properties: ZoomProperties


class TotalProperties(LayoutNode):
    show: Expression | None = None


class Total(LayoutNode):
    properties: TotalProperties


class Y1AxisReferenceLineProperties(LayoutNode):
    displayName: Expression | None = None
    lineColor: Expression | None = None
    show: Expression | None = None
    style: Expression | None = None
    transparency: Expression | None = None
    value: Expression | None = None


class Y1AxisReferenceLine(LayoutNode):
    properties: Y1AxisReferenceLineProperties
    selector: Selector | None = None


class ColumnChartColumnProperties(LayoutNode):
    categoryAxis: list[CategoryAxis] | None = None
    dataPoint: list[DataPoint] | None = None
    general: list[General] | None = None
    labels: list[Labels] | None = None
    legend: list[Legend] | None = None
    valueAxis: list[ValueAxis] | None = None
    totals: list[Total] | None = None
    y1AxisReferenceLine: list[Y1AxisReferenceLine] | None = None
    zoom: list[Zoom] | None = None


class ColumnChart(BaseVisual):
    visualType: str = "columnChart"
    model_config = ConfigDict(extra="forbid")

    objects: ColumnChartColumnProperties | None = None
    columnProperties: dict[str, ColumnProperty] | None = None
