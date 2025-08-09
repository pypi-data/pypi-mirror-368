from typing import TYPE_CHECKING

from pbi_git.change_classes import ChangeType, FilterChange

if TYPE_CHECKING:
    from pbyx.static_files.layout.filters import Filter


def filter_update_diff(parent_filter: "Filter", child_filter: "Filter") -> FilterChange | None:
    assert parent_filter.name is not None
    field_changes = {}
    for field in ("type", "howCreated", "isLockedInViewMode", "isHiddenInViewMode", "displayName", "ordinal"):
        if getattr(parent_filter, field) != getattr(child_filter, field):
            field_changes[field] = (
                getattr(parent_filter, field),
                getattr(child_filter, field),
            )

    if parent_filter.filter is not None and child_filter.filter is not None:
        parent_natural_expression = parent_filter.filter.Where[0].natural_language()
        child_natural_expression = child_filter.filter.Where[0].natural_language()
        if parent_natural_expression != child_natural_expression:
            field_changes["condition"] = (
                parent_natural_expression,
                child_natural_expression,
            )
    if field_changes:
        return FilterChange(
            id=parent_filter.name,
            change_type=ChangeType.UPDATED,
            entity=parent_filter,
            field_changes=field_changes,
        )
    return None


def filter_diff(parent_filters: "list[Filter]", child_filters: "list[Filter]") -> list[FilterChange]:
    parent_filter_dict = {f.name: f for f in parent_filters if f.name is not None}
    child_filter_dict = {f.name: f for f in child_filters if f.name is not None}
    filter_changes = [
        FilterChange(
            id=filter_name,
            change_type=ChangeType.DELETED,
            entity=parent_filter_dict[filter_name],
        )
        for filter_name in set(parent_filter_dict.keys()) - set(child_filter_dict.keys())
    ]
    filter_changes.extend(
        FilterChange(
            id=filter_name,
            change_type=ChangeType.ADDED,
            entity=child_filter_dict[filter_name],
        )
        for filter_name in set(child_filter_dict.keys()) - set(parent_filter_dict.keys())
    )

    for filter_name in set(parent_filter_dict.keys()) & set(child_filter_dict.keys()):
        parent_filter = parent_filter_dict[filter_name]
        child_filter = child_filter_dict[filter_name]
        changes = filter_update_diff(parent_filter, child_filter)
        if changes:
            filter_changes.append(changes)
    return filter_changes
