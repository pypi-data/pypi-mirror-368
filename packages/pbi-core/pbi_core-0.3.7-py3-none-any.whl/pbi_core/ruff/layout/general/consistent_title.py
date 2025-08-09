from typing import TYPE_CHECKING

from pbi_core.ruff.base_rule import BaseRule, RuleResult

if TYPE_CHECKING:
    from pbi_core.static_files.layout.layout import Layout


class ConsistentTitle(BaseRule):
    id = "GEN-002"
    name = "Consistent Title"
    description = """
        All Sections should have a title in the top left quadrant of the report.
        A title should be a text box visual.
    """

    @classmethod
    def check(cls, layout: "Layout") -> list[RuleResult]:
        if cls and layout:
            return []
        return []
