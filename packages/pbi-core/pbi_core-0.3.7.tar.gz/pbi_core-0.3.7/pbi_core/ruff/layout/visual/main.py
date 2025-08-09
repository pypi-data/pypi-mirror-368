from pbi_core.ruff.base_rule import RuleGroup, RuleResult
from pbi_core.static_files.layout.visual_container import VisualContainer

from .implicit_measures import DiscourageImplicitMeasures


class VisualRules(RuleGroup):
    """Group of rules related to visuals."""

    name = "Visual Rules"
    rules = [DiscourageImplicitMeasures]

    @classmethod
    def check(cls, visual: VisualContainer) -> list[RuleResult]:
        results = []
        for rule in cls.rules:
            results.extend(rule.check(visual))
        return results
