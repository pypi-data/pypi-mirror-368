from pbi_core.ruff.base_rule import BaseRule, RuleResult
from pbi_core.ssas.model_tables.measure import Measure
from pbi_parsers import dax


class LiteralsInCalculate(BaseRule):
    id = "DAX-006"
    name = "Literals in CALCULATE"
    description = """
        CALCULATE expressions should not contain number/string literals.
        This helps maintain clarity and performance in DAX expressions.
    """

    @classmethod
    def check(cls, measure: Measure) -> list[RuleResult]:
        """Check the measure for literals in CALCULATE expressions."""
        if not isinstance(measure.expression, str):
            return []
        ast = dax.to_ast(measure.expression)
        if ast is None:
            return []
        ret = []
        for node in dax.utils.find_all(ast, dax.exprs.FunctionExpression):
            if node.function_name().lower() != "calculate":
                continue
            for token in dax.utils.find_all(
                node,
                (
                    dax.exprs.LiteralNumberExpression,
                    dax.exprs.LiteralStringExpression,
                ),
            ):
                message = f"Literal value '{token.value.text}' found in CALCULATE expression."
                ret.append(
                    RuleResult(
                        rule=cls,
                        message=message,
                        context=dax.utils.highlight_section(token),
                        context_vars={
                            "literal_value": token.value.text,
                        },
                        trace=("measure", measure.table().name, measure.name, "expression"),
                    ),
                )
        return ret
