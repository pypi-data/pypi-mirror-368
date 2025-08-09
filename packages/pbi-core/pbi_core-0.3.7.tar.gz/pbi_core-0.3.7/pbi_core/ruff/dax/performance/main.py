from typing import TYPE_CHECKING

from pbi_core.ruff.base_rule import RuleGroup, RuleResult

from .literals_in_calculate import LiteralsInCalculate

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Measure


class DaxPerformanceRules(RuleGroup):
    """Group of rules related to DAX performance."""

    name = "DAX Performance Rules"
    rules = (LiteralsInCalculate,)

    @classmethod
    def check(cls, measure: "Measure") -> list["RuleResult"]:
        """Check the measure for DAX performance rules."""
        results = []
        for rule in cls.rules:
            results.extend(rule.check(measure))
        return results
