from pbi_core.ruff.base_rule import RuleGroup, RuleResult
from pbi_core.static_files.layout.layout import Layout

from .consistent_font import ConsistentFont
from .consistent_title import ConsistentTitle


class LayoutRules(RuleGroup):
    """Group of rules related to the overall layout."""

    name = "Layout Rules"
    rules = [
        ConsistentFont,
        ConsistentTitle,
    ]

    @classmethod
    def check(cls, layout: Layout) -> list[RuleResult]:
        results = []
        for rule in cls.rules:
            results.extend(rule.check(layout))
        return results
