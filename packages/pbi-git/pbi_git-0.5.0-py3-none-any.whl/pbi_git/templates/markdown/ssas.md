# SSAS Changes


## SSAS Summary

| Table | Changes |
| ----- | ------- |
{% for table, changes in tables_with_changes.items() -%}
| [{{ name_formatter(table) }}](#{{ table|lower|replace(' ', '-')|replace('_', '-') }}) | {{ changes|length }} |
{% endfor %}

{% for table, changes in tables_with_changes.items() %}
## {{ name_formatter(table) }}

{% for change in changes %}
- {{ change.entity.__repr__() }}: **{{ change.change_type.value.capitalize() }}**
  {% if change.change_type.value == 'UPDATED' %}
   | Field | From | To  |
   | ----- | ---- | --- |
  {% for field, (old_value, new_value) in change.field_changes.items() -%}
   | {{ name_formatter(field) }} | <code>{{ old_value or "*No Value*" }}</code> | <code>{{ new_value or "*No Value*" }}</code> |
  {% endfor %}
  {% endif %}
{% endfor %}

{% endfor %}

**SSAS Metadata Tables Without Changes**: {{tables_without_changes}}