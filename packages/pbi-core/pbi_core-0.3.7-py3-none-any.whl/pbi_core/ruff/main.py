from pbi_core import LocalReport

from .base_rule import RuleResult
from .dax import DaxFormattingRules, DaxPerformanceRules
from .layout import LayoutRules, SectionRules, ThemeRules


def check_rules(report: LocalReport) -> list[RuleResult]:
    """Run all rules on the report."""
    # Run theme colors rule
    results = []

    # Layout rules
    results.extend(LayoutRules.check(report.static_files.layout))

    for section in report.static_files.layout.sections:
        results.extend(SectionRules.check(section))

    # Other static files rules
    if False:
        results.extend(ThemeRules.check(report.static_files.themes))

    # SSAS rules

    for measure in report.ssas.measures:
        results.extend(DaxFormattingRules.check(measure))
        results.extend(DaxPerformanceRules.check(measure))

    return results
