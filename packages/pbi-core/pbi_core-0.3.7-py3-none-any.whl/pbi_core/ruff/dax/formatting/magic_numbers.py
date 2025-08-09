from pbi_core.ruff.base_rule import BaseRule, RuleResult
from pbi_core.ssas.model_tables.measure import Measure
from pbi_parsers import dax

ACCEPTABLE_NUMBERS = {"1", "2", "3", "7", "30", "100", "1000"}


class MagicNumbers(BaseRule):
    id = "DAX-004"
    name = "Magic Numbers in DAX Expressions"
    description = """
        DAX expressions should not contain magic numbers.
        Magic numbers are numeric literals that appear in the code without explanation.
        They can make the code harder to understand and maintain.
        If the number is used multiple times, it should be assigned to a measure. If it is used only once,
        it should be assigned to a variable with a descriptive name.

        Basic numbers: (1, 2, 3, 7, 30, 100, 1000) are excluded from this rule.
    """

    @classmethod
    def check(cls, measure: Measure) -> list[RuleResult]:
        """Check the measure for magic numbers."""
        if not isinstance(measure.expression, str):
            return []
        ast = dax.to_ast(measure.expression)
        if ast is None:
            return []

        ret = []
        for token in dax.utils.find_all(ast, dax.exprs.LiteralNumberExpression):
            if token.value.text in ACCEPTABLE_NUMBERS:
                continue
            message = f"Magic number '{token.value.text}' found."
            ret.append(
                RuleResult(
                    rule=cls,
                    message=message,
                    context=dax.utils.highlight_section(token),
                    context_vars={
                        "magic_number": token.value.text,
                    },
                    trace=("measure", measure.table().name, measure.name, "expression"),
                ),
            )
        return ret
