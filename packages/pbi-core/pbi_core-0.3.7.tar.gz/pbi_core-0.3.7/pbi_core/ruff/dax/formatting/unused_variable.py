from pbi_core.ruff.base_rule import BaseRule, RuleResult
from pbi_core.ssas.model_tables.measure import Measure
from pbi_parsers import dax


class UnusedMeasureVariables(BaseRule):
    id = "DAX-003"
    name = "Unused Measure Variables"
    description = """
        Measures should not contain unused variables.
        This helps maintain clarity and (in some cases?) performance in DAX expressions.
    """

    @classmethod
    def check(cls, measure: Measure) -> list[RuleResult]:
        """Check the measure for unused variables."""
        expr = measure.expression

        if not isinstance(expr, str):
            return []

        ast = dax.to_ast(expr)
        if not isinstance(ast, dax.exprs.ReturnExpression):
            return []

        unused_variables: dict[str, dax.Token] = {}
        for var in ast.variable_statements:
            for identifier in dax.utils.find_all(var, dax.exprs.IdentifierExpression):
                if identifier.name.text in unused_variables:
                    del unused_variables[identifier.name.text]
            unused_variables[var.var_name.text] = var.var_name
        for identifier in dax.utils.find_all(ast.ret, dax.exprs.IdentifierExpression):
            if identifier.name.text in unused_variables:
                del unused_variables[identifier.name.text]

        ret = []
        for token in unused_variables.values():
            message = f"Variable '{token.text}' is defined but never used."
            ret.append(
                RuleResult(
                    rule=cls,
                    message=message,
                    context=dax.utils.highlight_section(token),
                    context_vars={
                        "variable_name": token,
                    },
                    trace=("measure", measure.table().name, measure.name, "expression"),
                ),
            )
        return ret
