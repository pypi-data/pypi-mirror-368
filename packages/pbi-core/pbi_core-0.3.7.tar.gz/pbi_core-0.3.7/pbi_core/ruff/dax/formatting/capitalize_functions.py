from pbi_core.ruff.base_rule import BaseRule, RuleResult
from pbi_core.ssas.model_tables.measure import Measure
from pbi_parsers import dax


class CapitalizeFunctionNames(BaseRule):
    id = "DAX-007"
    name = "Capitalize Function Names"
    description = """
        Function names in DAX expressions should be upper case.
        This helps maintain consistency and readability in DAX expressions.
    """

    @classmethod
    def check(cls, measure: Measure) -> list[RuleResult]:
        if not isinstance(measure.expression, str):
            return []
        ast = dax.to_ast(measure.expression)
        if ast is None:
            return []

        ret = []
        for function in dax.utils.find_all(ast, dax.exprs.FunctionExpression):
            function_name = function.function_name()
            if not function_name.isupper():
                message = f"Function names should be upper case. It was '{function_name}', should be '{function_name.upper()}'."  # noqa: E501
                ret.append(
                    RuleResult(
                        rule=cls,
                        message=message,
                        context=dax.utils.highlight_section(function.name_parts),
                        context_vars={
                            "function_name": function_name,
                            "correct_name": function_name.upper(),
                        },
                        trace=("measure", measure.table().name, measure.name, "expression"),
                    ),
                )
        return ret
