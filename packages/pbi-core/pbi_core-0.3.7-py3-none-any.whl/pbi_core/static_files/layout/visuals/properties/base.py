from typing import Annotated, Any, Literal

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.condition import ConditionType
from pbi_core.static_files.layout.sources import LiteralSource, MeasureSource, Source
from pbi_core.static_files.layout.sources.aggregation import AggregationSource, SelectRef
from pbi_core.static_files.layout.sources.column import ColumnSource
from pydantic import Discriminator, Tag


class LiteralExpression(LayoutNode):
    expr: LiteralSource


class MeasureExpression(LayoutNode):
    expr: MeasureSource


class AggregationExpression(LayoutNode):
    expr: AggregationSource


class ThemeDataColor(LayoutNode):
    ColorId: int
    Percent: float


class ThemeExpression(LayoutNode):
    ThemeDataColor: ThemeDataColor


class FillRule(LayoutNode):
    FillRule: "Expression"
    Input: Source


class FillRuleExpression(LayoutNode):
    FillRule: FillRule


class ConditionalCase(LayoutNode):
    Condition: ConditionType
    Value: LiteralSource


class ConditionalSourceHelper(LayoutNode):
    Cases: list[ConditionalCase]


class ConditionalSource(LayoutNode):
    Conditional: ConditionalSourceHelper


class ConditionalExpression(LayoutNode):
    expr: ConditionalSource


def get_subexpr_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        keys = list(v.keys())
        assert len(keys) == 1, f"Expected single key, got {keys}"
        mapper = {
            "ThemeDataColor": "ThemeExpression",
            "Aggregation": "AggregationSource",
            "Literal": "LiteralSource",
            "Measure": "MeasureSource",
            "FillRule": "FillRuleExpression",
            "Conditional": "ConditionalSource",
        }
        if keys[0] in mapper:
            return mapper[keys[0]]
        msg = f"Unknown type: {v.keys()}"
        raise TypeError(msg)
    return v.__class__.__name__


ColorSubExpression = Annotated[
    Annotated[ThemeExpression, Tag("ThemeExpression")]
    | Annotated[LiteralSource, Tag("LiteralSource")]
    | Annotated[MeasureSource, Tag("MeasureSource")]
    | Annotated[FillRuleExpression, Tag("FillRuleExpression")]
    | Annotated[AggregationSource, Tag("AggregationSource")]
    | Annotated[ConditionalSource, Tag("ConditionalSource")],
    Discriminator(get_subexpr_type),
]


class ColorExpression(LayoutNode):
    expr: ColorSubExpression


def get_color_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "expr" in v:
            return "ColorExpression"
        if "Literal" in v:
            return "LiteralSource"
        msg = f"Unknown Color Type: {v.keys()}"
        raise TypeError(msg)
    return v.__class__.__name__


Color = Annotated[
    Annotated[ColorExpression, Tag("ColorExpression")] | Annotated[LiteralSource, Tag("LiteralSource")],
    Discriminator(get_color_type),
]


class SolidExpression(LayoutNode):
    color: Color
    value: LiteralSource | LiteralExpression | None = None  # TODO: explore the cases here more


class SolidColorExpression(LayoutNode):
    solid: SolidExpression


class StrategyExpression(LayoutNode):
    strategy: LiteralExpression | LiteralSource  # TODO: explore the cases here more


class ExtremeColor(LayoutNode):
    color: LiteralSource
    value: LiteralSource


def get_color_helper_type(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        if "solid" in v:
            return "SolidExpression"
        if "color" in v:
            return "ExtremeColor"
        msg = f"Unknown class: {v.keys()}"
        breakpoint()
        raise TypeError(msg)
    return v.__class__.__name__


LinearGradient2HelperExtreme = Annotated[
    Annotated[SolidExpression, Tag("SolidExpression")] | Annotated[ExtremeColor, Tag("ExtremeColor")],
    Discriminator(get_color_helper_type),
]


class LinearGradient2Helper(LayoutNode):
    max: SolidExpression
    min: SolidExpression
    nullColoringStrategy: StrategyExpression


class LinearGradient2Expression(LayoutNode):
    linearGradient2: LinearGradient2Helper


class LinearGradient3Helper(LayoutNode):
    max: SolidExpression
    mid: SolidExpression
    min: SolidExpression
    nullColoringStrategy: StrategyExpression


class LinearGradient3Expression(LayoutNode):
    linearGradient3: LinearGradient3Helper


class ResourcePackageItem(LayoutNode):
    PackageName: str
    PackageType: int  # TODO: enum
    ItemName: str


class ResourcePackageAccessExpression(LayoutNode):
    ResourcePackageItem: ResourcePackageItem


class ResourcePackageAccess(LayoutNode):
    expr: ResourcePackageAccessExpression


class ImageKindExpression(LayoutNode):
    kind: Literal["Icon"]
    layout: LiteralExpression
    verticalAlignment: LiteralExpression
    value: ConditionalExpression


# TODO: centralize the expr: Source classes
class SelectRefExpression(LayoutNode):
    expr: SelectRef


class ImageExpressionHelper(LayoutNode):
    name: "Expression"
    scaling: "Expression"
    url: "Expression"


class ImageExpression(LayoutNode):
    image: ImageExpressionHelper


class GeoJsonExpressionHelper(LayoutNode):
    name: "Expression"
    content: "Expression"
    type: "Expression"


class GeoJsonExpression(LayoutNode):
    geoJson: GeoJsonExpressionHelper


class AlgorithmParameter(LiteralSource):
    Name: str


class AlgorithmExpression(LayoutNode):
    algorithm: str
    parameters: list[AlgorithmParameter]


class ExpressionList(LayoutNode):
    exprs: list["Expression"]
    kind: Literal["ExprList"]


class ColumnExpression(LayoutNode):
    expr: ColumnSource


def get_expression(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        mapper = {
            "solid": "SolidColorExpression",
            "linearGradient2": "LinearGradient2Expression",
            "linearGradient3": "LinearGradient3Expression",
            "image": "ImageExpression",
            "geoJson": "GeoJsonExpression",
            "algorithm": "AlgorithmExpression",
        }
        kind_mapper = {
            "Icon": "ImageKindExpression",
            "ExprList": "ExpressionList",
        }
        expr_mapper = {
            "Column": "ColumnExpression",
            "Measure": "MeasureExpression",
            "Literal": "LiteralExpression",
            "Aggregation": "AggregationExpression",
            "ResourcePackageItem": "ResourcePackageAccess",
            "SelectRef": "SelectRefExpression",
        }
        if "kind" in v:
            if v["kind"] in kind_mapper:
                return kind_mapper[v["kind"]]
            msg = f"Unknown kind: {v['kind']}"
            raise ValueError(msg)

        if "expr" in v:
            # Column has multiple keys, so we need to check them
            for k in v["expr"]:
                if k in expr_mapper:
                    return expr_mapper[k]
            msg = f"Unknown expression type: {v['expr']}"
            raise ValueError(msg)

        for key in v:
            if key in mapper:
                return mapper[key]

        msg = f"Unknown class: {v.keys()}"
        raise TypeError(msg)
    return v.__class__.__name__


Expression = Annotated[
    Annotated[LiteralExpression, Tag("LiteralExpression")]
    | Annotated[AlgorithmExpression, Tag("AlgorithmExpression")]
    | Annotated[ColumnExpression, Tag("ColumnExpression")]
    | Annotated[MeasureExpression, Tag("MeasureExpression")]
    | Annotated[AggregationExpression, Tag("AggregationExpression")]
    | Annotated[SolidColorExpression, Tag("SolidColorExpression")]
    | Annotated[LinearGradient2Expression, Tag("LinearGradient2Expression")]
    | Annotated[LinearGradient3Expression, Tag("LinearGradient3Expression")]
    | Annotated[ResourcePackageAccess, Tag("ResourcePackageAccess")]
    | Annotated[ImageKindExpression, Tag("ImageKindExpression")]
    | Annotated[ImageExpression, Tag("ImageExpression")]
    | Annotated[ExpressionList, Tag("ExpressionList")]
    | Annotated[GeoJsonExpression, Tag("GeoJsonExpression")]
    | Annotated[SelectRefExpression, Tag("SelectRefExpression")],
    Discriminator(get_expression),
]
