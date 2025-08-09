from typing import TYPE_CHECKING

from pbi_core.ruff.base_rule import RuleGroup, RuleResult

from .camel_case_variable import CamelCaseMeasureName, CamelCaseVariable
from .capitalize_functions import CapitalizeFunctionNames
from .magic_numbers import MagicNumbers
from .unused_variable import UnusedMeasureVariables

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Measure


class DaxFormattingRules(RuleGroup):
    """Group of rules related to DAX formatting."""

    name = "DAX Formatting Rules"
    rules = (
        CamelCaseMeasureName,
        CamelCaseVariable,
        CapitalizeFunctionNames,
        UnusedMeasureVariables,
        MagicNumbers,
    )

    @classmethod
    def check(cls, measure: "Measure") -> list["RuleResult"]:
        """Check the measure for DAX formatting rules."""
        results = []
        for rule in cls.rules:
            results.extend(rule.check(measure))
        return results
