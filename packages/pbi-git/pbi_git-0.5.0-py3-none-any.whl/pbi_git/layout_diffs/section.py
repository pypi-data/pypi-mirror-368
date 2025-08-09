from typing import TYPE_CHECKING

from pbi_git.change_classes import ChangeType, SectionChange, VisualChange

from .filters import filter_diff
from .visual import visual_diff

if TYPE_CHECKING:
    from pbyx.static_files.layout.layout import Section


def get_visual_changes(
    parent_section: "Section",
    child_section: "Section",
) -> list[VisualChange]:
    visual_changes: list[VisualChange] = []

    parent_visuals = {visual.pbyx_id(): visual for visual in parent_section.visualContainers}
    child_visuals = {visual.pbyx_id(): visual for visual in child_section.visualContainers}

    visual_changes.extend(
        VisualChange(
            id=visual_id,
            change_type=ChangeType.DELETED,
            entity=parent_visuals[visual_id],
        )
        for visual_id in set(parent_visuals.keys()) - set(child_visuals.keys())
    )
    visual_changes.extend(
        VisualChange(
            id=visual_id,
            change_type=ChangeType.ADDED,
            entity=child_visuals[visual_id],
        )
        for visual_id in set(child_visuals.keys()) - set(parent_visuals.keys())
    )
    for visual_id in set(parent_visuals.keys()) & set(child_visuals.keys()):
        parent_visual = parent_visuals[visual_id]
        child_visual = child_visuals[visual_id]
        visual_object = visual_diff(parent_visual, child_visual)
        if visual_object.change_type != ChangeType.NO_CHANGE:
            visual_changes.append(visual_object)

    return visual_changes


def section_diff(parent: "Section", child: "Section") -> SectionChange:
    field_changes = {}
    for field in ["height", "width", "ordinal", "displayName"]:
        parent_val = getattr(parent, field, None)
        child_val = getattr(child, field, None)
        if parent_val != child_val and not (parent_val is None and child_val is None):
            field_changes[field] = (parent_val, child_val)

    for field in ["visibility"]:
        parent_val = getattr(parent.config, field, None)
        child_val = getattr(child.config, field, None)
        if parent_val != child_val and not (parent_val is None and child_val is None):
            field_changes[f"config.{field}"] = (parent_val, child_val)

    filter_changes = filter_diff(parent.filters, child.filters)  # type: ignore reportArgumentType
    visual_changes = get_visual_changes(parent, child)

    has_changed = visual_changes or filter_changes or field_changes
    change_type = ChangeType.UPDATED if has_changed else ChangeType.NO_CHANGE

    return SectionChange(
        id=parent.name,
        change_type=change_type,
        entity=parent,
        filters=filter_changes,  # type: ignore reportArgumentType
        visuals=visual_changes,
        field_changes=field_changes,
    )
