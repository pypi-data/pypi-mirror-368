from pbi_core.ruff.base_rule import BaseRule, RuleResult
from pbi_core.static_files.layout.sources.aggregation import AggregationSource
from pbi_core.static_files.layout.visual_container import VisualContainer


class DiscourageImplicitMeasures(BaseRule):
    id = "VIZ-001"
    name = "Discourage Implicit Measures"
    description = (
        "Using implicit measures (e.g., SUM(Column)) in visuals can lead to performance issues and unexpected results."
        " It's recommended to create explicit measures in the model for better control and optimization."
    )

    @classmethod
    def check(cls, visual: VisualContainer) -> list[RuleResult]:
        if visual.query is None:
            return []

        ret: list[RuleResult] = []
        for pt_query in visual.query.get_prototype_queries():
            ret.extend(
                RuleResult(
                    rule=cls,
                    trace=("section", visual._parent.name, "visual", visual.id or -1),
                    context_vars={
                        "visual_name": visual.id or -1,
                    },
                    message="Visual uses an implicit measure. "
                    "Consider creating an explicit measure in the model instead.",
                )
                for select in pt_query.Select
                if isinstance(select, AggregationSource)
            )
        return ret
