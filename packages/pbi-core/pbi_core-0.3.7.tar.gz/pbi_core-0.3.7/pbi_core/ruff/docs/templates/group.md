{{group.__doc__}}


{% for rule in rules %}
# {{ rule.id }}: {{ rule.name }}

**Applies to:**

{{ get_sources(rule)}}

**Fix State:** {{ rule.fixable.value }}

```
{{ dedent(rule.description) }}
```
{% endfor %}