from pbi_core.ruff.base_rule import BaseRule, RuleResult
from pbi_core.ssas.model_tables.measure import Measure
from pbi_parsers import dax


def _to_camel_case(string: str) -> str:
    string = string.replace("-", "_").replace(" ", "_").replace(".", "_")
    word_list = string.split("_")
    for i, word in enumerate(word_list):
        word_list[i] = word if i == 0 else word.capitalize()

    return "".join(word_list)


class CamelCaseMeasureName(BaseRule):
    id = "DAX-002"
    name = "Camel Case Measure Names"
    description = """
        Measure names in DAX expressions should be in camelCase format.
        This helps maintain consistency and readability in DAX expressions.
    """

    @classmethod
    def check(cls, measure: Measure) -> list[RuleResult]:
        """Check the measure name for camelCase format."""
        if not isinstance(measure.name, str):
            return []

        correct_name = _to_camel_case(measure.name)
        if measure.name != correct_name:
            message = f"Measure name should be in camelCase format. It was {measure.name}, should be {correct_name}."
            return [
                RuleResult(
                    rule=cls,
                    message=message,
                    context_vars={
                        "measure_name": measure.name,
                        "correct_name": correct_name,
                    },
                    trace=("measure", measure.table().name, measure.name),
                ),
            ]

        return []


class CamelCaseVariable(BaseRule):
    id = "DAX-001"
    name = "Camel Case Variable Names"
    description = """
        Variable names in DAX expressions should be in camelCase format.
        This helps maintain consistency and readability in DAX expressions.
    """

    @classmethod
    def check(cls, measure: Measure) -> list[RuleResult]:
        """Check the AST for non-camelCase variable names."""
        if not isinstance(measure.expression, str):
            return []

        ast = dax.to_ast(measure.expression)
        if ast is None:
            return []

        variables = dax.utils.find_all(ast, dax.exprs.VariableExpression)

        results = []
        for var in variables:
            correct_name = _to_camel_case(var.var_name.text)
            if var.var_name.text != correct_name:
                message = (
                    f"Variable name should be in camelCase format. "
                    f"It was {var.var_name.text}, should be {correct_name}."
                )
                context = dax.utils.highlight_section(var.var_name)
                results.append(
                    RuleResult(
                        rule=cls,
                        message=message,
                        context=context,
                        trace=("measure", measure.table().name, measure.name, "expression"),
                    ),
                )

        return results
