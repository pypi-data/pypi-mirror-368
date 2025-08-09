# Layout Changes

{{layout_changes.to_markdown()}}

{% for section in layout_changes.sections %}
{% if section.change_type != ChangeType.NO_CHANGE %}
## Section: {{ section.entity.displayName }}

{{ section.to_markdown() }}

{% for visual in section.visuals %}
{% if visual.change_type != ChangeType.NO_CHANGE %}
### Visual: {{ visual.entity.pbyx_name() }}

{{ visual.to_markdown() }}
{% endif  %}
{% endfor %}
{% endif %}
{% endfor %}