from pbi_core.ruff.base_rule import BaseRule, RuleResult
from pbi_core.static_files.layout.section import Section


class OutOfBounds(BaseRule):
    id = "SEC-004"
    name = "Out of Bounds Visuals"
    description = "Checks if visuals are placed outside the bounds of the section."

    @classmethod
    def check(cls, section: Section) -> list[RuleResult]:
        ret = []
        for viz in section.visualContainers:
            too_high = viz.y < 0
            too_low = viz.y + viz.height > section.height
            too_left = viz.x < 0
            too_right = viz.x + viz.width > section.width
            if too_high or too_low or too_left or too_right:
                ret.append(
                    RuleResult(
                        rule=cls,
                        context_vars={
                            "visual": viz.name(),
                            "x": viz.x,
                            "y": viz.y,
                            "width": viz.width,
                            "height": viz.height,
                            "section_width": section.width,
                            "section_height": section.height,
                        },
                        message=f"Visual '{viz.name()}' is out of bounds at ({viz.x}, {viz.y})"
                        f" in section with size ({section.width}, {section.height}).",
                    ),
                )
        return ret
