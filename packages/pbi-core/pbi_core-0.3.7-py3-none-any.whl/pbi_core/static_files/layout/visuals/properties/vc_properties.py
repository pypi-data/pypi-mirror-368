from pbi_core.static_files.layout._base_node import LayoutNode

from .base import Expression


class BackgroundProperties(LayoutNode):
    color: Expression | None = None
    show: Expression | None = None
    transparency: Expression | None = None


class Background(LayoutNode):
    properties: BackgroundProperties


class GeneralProperties(LayoutNode):
    altText: Expression | None = None
    keepLayerOrder: Expression | None = None


class General(LayoutNode):
    properties: GeneralProperties


class TitleProperties(LayoutNode):
    alignment: Expression | None = None
    background: Expression | None = None
    fontColor: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    heading: Expression | None = None
    show: Expression | None = None
    text: Expression | None = None
    titleWrap: Expression | None = None


class Title(LayoutNode):
    properties: TitleProperties


class VisualTooltipProperties(LayoutNode):
    background: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    section: Expression | None = None
    show: Expression | None = None
    titleFontColor: Expression | None = None
    type: Expression | None = None
    valueFontColor: Expression | None = None


class VisualTooltip(LayoutNode):
    properties: VisualTooltipProperties


class StylePresetProperties(LayoutNode):
    name: Expression | None = None


class StylePreset(LayoutNode):
    properties: StylePresetProperties


class BorderProperties(LayoutNode):
    background: Expression | None = None
    color: Expression | None = None
    radius: Expression | None = None
    show: Expression | None = None


class Border(LayoutNode):
    properties: BorderProperties


class VisualHeaderProperties(LayoutNode):
    background: Expression | None = None
    border: Expression | None = None
    foreground: Expression | None = None
    show: Expression | None = None
    showDrillDownExpandButton: Expression | None = None
    showDrillDownLevelButton: Expression | None = None
    showDrillRoleSelector: Expression | None = None
    showDrillToggleButton: Expression | None = None
    showDrillUpButton: Expression | None = None
    showFilterRestatementButton: Expression | None = None
    showFocusModeButton: Expression | None = None
    showOptionsMenu: Expression | None = None
    showPinButton: Expression | None = None
    showSeeDataLayoutToggleButton: Expression | None = None
    showSmartNarrativeButton: Expression | None = None
    showTooltipButton: Expression | None = None
    showVisualErrorButton: Expression | None = None
    showVisualInformationButton: Expression | None = None
    showVisualWarningButton: Expression | None = None
    transparency: Expression | None = None


class VisualHeader(LayoutNode):
    properties: VisualHeaderProperties


class VisualLinkProperties(LayoutNode):
    bookmark: Expression | None = None
    disabledTooltip: Expression | None = None
    drillthroughSection: Expression | None = None
    enabledTooltip: Expression | None = None
    navigationSection: Expression | None = None
    show: Expression | None = None
    tooltip: Expression | None = None
    type: Expression | None = None
    webUrl: Expression | None = None


class VisualLink(LayoutNode):
    properties: VisualLinkProperties | None = None


class VisualHeaderTooltipProperties(LayoutNode):
    background: Expression | None = None
    section: Expression | None = None
    text: Expression | None = None
    titleFontColor: Expression | None = None
    type: Expression | None = None


class VisualHeaderTooltip(LayoutNode):
    properties: VisualHeaderTooltipProperties


class DropShadowProperties(LayoutNode):
    angle: Expression | None = None
    color: Expression | None = None
    position: Expression | None = None
    preset: Expression | None = None
    shadowBlur: Expression | None = None
    shadowDistance: Expression | None = None
    shadowSpread: Expression | None = None
    show: Expression | None = None
    transparency: Expression | None = None


class DropShadow(LayoutNode):
    properties: DropShadowProperties


class LockAspectProperties(LayoutNode):
    show: Expression | None = None


class LockAspect(LayoutNode):
    properties: LockAspectProperties


class VCProperties(LayoutNode):
    background: list[Background] | None = None
    border: list[Border] | None = None
    dropShadow: list[DropShadow] | None = None
    general: list[General] | None = None
    lockAspect: list[LockAspect] | None = None
    stylePreset: list[StylePreset] | None = None
    title: list[Title] | None = None
    visualHeader: list[VisualHeader] | None = None
    visualHeaderTooltip: list[VisualHeaderTooltip] | None = None
    visualLink: list[VisualLink] | None = None
    visualTooltip: list[VisualTooltip] | None = None
