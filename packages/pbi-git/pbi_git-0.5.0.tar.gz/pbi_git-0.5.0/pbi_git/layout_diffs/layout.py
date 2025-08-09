from typing import TYPE_CHECKING

from pbi_git.change_classes import ChangeType, LayoutChange, SectionChange, VisualChange

from .filters import filter_diff
from .section import section_diff

if TYPE_CHECKING:
    from pbyx.static_files.layout.layout import Layout


def get_section_changes(
    parent: "Layout",
    child: "Layout",
) -> list[SectionChange]:
    parent_sections = {x.name: x for x in parent.sections}
    child_sections = {x.name: x for x in child.sections}
    section_changes: list[SectionChange] = [
        SectionChange(
            id=section_name,
            change_type=ChangeType.DELETED,
            entity=parent_sections[section_name],
            visuals=[
                VisualChange(visual.pbyx_id(), ChangeType.DELETED, visual)
                for visual in parent_sections[section_name].visualContainers
            ],
        )
        for section_name in set(parent_sections.keys()) - set(child_sections.keys())
    ]

    section_changes.extend(
        SectionChange(
            id=section_name,
            change_type=ChangeType.ADDED,
            entity=child_sections[section_name],
            visuals=[
                VisualChange(visual.pbyx_id(), ChangeType.ADDED, visual)
                for visual in child_sections[section_name].visualContainers
            ],
        )
        for section_name in set(child_sections.keys()) - set(parent_sections.keys())
    )

    for section_name in set(parent_sections.keys()) & set(child_sections.keys()):
        parent_section = parent_sections[section_name]
        child_section = child_sections[section_name]
        sub_section_changes = section_diff(parent_section, child_section)
        if sub_section_changes:
            section_changes.append(sub_section_changes)

    return section_changes


def layout_diff(parent: "Layout", child: "Layout") -> LayoutChange:
    field_changes = {}
    for field in []:  # no simple fields to compare in Layout
        parent_val = getattr(parent, field, None)
        child_val = getattr(child, field, None)
        if parent_val != child_val and not (parent_val is None and child_val is None):
            field_changes[field] = (parent_val, child_val)

    filter_changes = filter_diff(parent.filters, child.filters)  # type: ignore reportArgumentType
    section_changes = get_section_changes(parent, child)

    has_changed = field_changes or filter_changes or section_changes
    change_type = ChangeType.UPDATED if has_changed else ChangeType.NO_CHANGE

    return LayoutChange(
        id="layout",
        change_type=change_type,
        entity=parent,
        field_changes=field_changes,
        filters=filter_changes,
        sections=section_changes,
    )
