from typing import TYPE_CHECKING

from pbi_git.change_classes import ChangeType, VisualChange

from .filters import filter_diff

if TYPE_CHECKING:
    from pbyx.static_files.layout.visual_container import VisualContainer
    from pbyx.static_files.layout.visuals.base import BaseVisual


def compare_prototype_queries(
    parent_visual: "BaseVisual | None",
    child_visual: "BaseVisual | None",
) -> dict[str, dict[str, list[str]]]:
    if parent_visual is None or child_visual is None:
        return {}
    parent_query = parent_visual.prototypeQuery
    child_query = child_visual.prototypeQuery
    if parent_query == child_query or parent_query is None or child_query is None:
        return {}

    ret = {}
    for field in ["Select", "Where", "OrderBy", "Transform"]:
        field_ret = {}
        parent_fields: set[str] = {s.Name for s in getattr(parent_query, field)}
        child_fields: set[str] = {s.Name for s in getattr(child_query, field)}
        field_ret["added"] = sorted(child_fields - parent_fields)
        field_ret["removed"] = sorted(parent_fields - child_fields)
        if field_ret["added"] or field_ret["removed"]:
            ret[field] = field_ret
    return ret


def visual_diff(parent_visual: "VisualContainer", child_visual: "VisualContainer") -> VisualChange:
    field_changes = {}
    for k in ["x", "y", "z", "width", "height", "tabOrder"]:
        parent_val = getattr(parent_visual, k, None)
        child_val = getattr(child_visual, k, None)
        if parent_val != child_val and not (parent_val is None and child_val is None):
            field_changes[k] = (parent_val, child_val)

    data_changes = compare_prototype_queries(parent_visual.config.singleVisual, child_visual.config.singleVisual)

    filter_changes = filter_diff(parent_visual.filters, child_visual.filters)  # type: ignore reportArgumentType
    change_type = ChangeType.UPDATED if field_changes or filter_changes else ChangeType.NO_CHANGE

    return VisualChange(
        id=parent_visual.pbyx_id(),
        entity=parent_visual,
        change_type=change_type,
        field_changes=field_changes,
        filters=filter_changes,
        data_changes=data_changes,
    )
