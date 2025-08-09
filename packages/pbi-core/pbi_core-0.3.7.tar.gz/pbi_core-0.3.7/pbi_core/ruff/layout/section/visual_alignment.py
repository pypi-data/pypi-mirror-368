import itertools

from pbi_core.ruff.base_rule import BaseRule, RuleResult
from pbi_core.static_files.layout.section import Section

MIN_PIXEL_MISALIGNMNET = 10


class VisualXAlignment(BaseRule):
    id = "SEC-001"
    name = "X-axis Visual Alignment"
    description = """No visual should have its x-axis misaligned with other visuals in the
    same section by less than 10 pixel."""

    @classmethod
    def check(cls, section: Section) -> list[RuleResult]:
        ret: list[RuleResult] = []
        vizes = sorted(section.visualContainers, key=lambda viz: viz.x)
        for viz1, viz2 in itertools.pairwise(vizes):
            if abs((viz1.x + viz1.width) - viz2.x) < MIN_PIXEL_MISALIGNMNET:
                msg = f"Visuals '{viz1.name()}' and '{viz2.name()}' are misaligned by <10 pixels on the x-axis."
                ret.append(
                    RuleResult(
                        rule=cls,
                        context_vars={
                            "viz1": viz1.name(),
                            "viz2": viz2.name(),
                        },
                        message=msg,
                    ),
                )
        return ret


class VisualYAlignment(BaseRule):
    id = "SEC-002"
    name = "Y-axis Visual Alignment"
    description = """No visual should have its x-axis misaligned with other visuals in the
    same section by less than 10 pixel."""

    @classmethod
    def check(cls, section: Section) -> list[RuleResult]:
        ret: list[RuleResult] = []
        vizes = sorted(section.visualContainers, key=lambda viz: viz.y)
        for viz1, viz2 in itertools.pairwise(vizes):
            if abs((viz1.y + viz1.height) - viz2.y) < MIN_PIXEL_MISALIGNMNET:
                msg = f"Visuals '{viz1.name()}' and '{viz2.name()}' are misaligned by <10 pixels on the y-axis."
                ret.append(
                    RuleResult(
                        rule=cls,
                        context_vars={
                            "viz1": viz1.name(),
                            "viz2": viz2.name(),
                        },
                        message=msg,
                    ),
                )
        return ret
