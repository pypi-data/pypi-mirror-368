import operator
import pathlib
from textwrap import dedent

import jinja2
from git import TYPE_CHECKING
from pbi_core.ruff.dax import DaxFormattingRules, DaxPerformanceRules
from pbi_core.ruff.layout import LayoutRules, SectionRules, ThemeRules, VisualRules

if TYPE_CHECKING:
    from pbi_core.ruff.base_rule import BaseRule


def get_sources(rule: type["BaseRule"]) -> str:
    source_mapping = {
        "measure": "[Measure](/SSAS/entities/measure)",
        "layout": "[Layout](/layout/layout)",
        "section": "[Section](/layout/section)",
        "themes": "[Theme](/general/theme)",
        "visual": "[Visual](/layout/visual)",
    }
    sources = [x for x in rule.check.__func__.__annotations__ if x != "return"]
    return (
        "\n".join(f"- {source_mapping.get(source, source)}" for source in sources)
        if sources
        else "__No sources specified__"
    )


templates = {
    x.stem: jinja2.Template(x.read_text())
    for x in (pathlib.Path(__file__).parent / "templates").iterdir()
    if x.suffix == ".md"
}
group_info = []
for group in [DaxFormattingRules, DaxPerformanceRules, LayoutRules, SectionRules, ThemeRules, VisualRules]:
    group_info.append({
        "name": group.name,
        "rules": len(group.rules),
    })
    with (
        pathlib.Path(__file__).parents[3] / "docs/docs/ruff/rule_groups/" / f"{group.name.replace(' ', '_')}.md"
    ).open("w", encoding="utf-8") as f:
        f.write(
            templates["group"].render(
                group=group,
                rules=sorted(group.rules, key=lambda r: r.id),
                get_sources=get_sources,
                dedent=dedent,
            ),
        )

with (pathlib.Path(__file__).parents[3] / "docs/docs/ruff/main.md").open("w", encoding="utf-8") as f:
    f.write(templates["entry"].render(groups=sorted(group_info, key=operator.itemgetter("name"))))
