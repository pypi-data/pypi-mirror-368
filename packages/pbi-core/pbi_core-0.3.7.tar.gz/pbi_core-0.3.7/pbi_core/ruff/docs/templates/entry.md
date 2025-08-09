# Ruff Rule Groups

| Group Name | Rule Count |
| ---------- | :--------: |
{% for group in groups -%}
| {{ group.name }} | [{{ group.rules }}](rule_groups/{{group.name.replace(" ", "_")}}.md) |
{% endfor %}