from pbyx.ssas.model_tables.base.base_ssas_table import SsasTable
from pbyx.ssas.server.tabular_model.tabular_model import LocalTabularModel

from .change_classes import ChangeType, SsasChange
from .utils import get_git_name

skip_fields: dict[str, list[str]] = {
    "columns": ["modified_time"],
    "measures": ["modified_time", "structure_modified_time"],
    "tables": ["modified_time", "system_managed"],
}


def compare_fields(
    ssas_category: str,
    parent_entity: SsasTable,
    child_entity: SsasTable,
) -> SsasChange | None:
    fields = set(parent_entity.model_fields.keys()) - {"tabular_model", "id"} - set(skip_fields.get(ssas_category, []))
    field_changes = {
        field_name: (getattr(parent_entity, field_name), getattr(child_entity, field_name))
        for field_name in fields
        if getattr(parent_entity, field_name) != getattr(child_entity, field_name)
    }
    if not field_changes:
        return None
    field_changes = {k: (get_git_name(v[0]), get_git_name(v[1])) for k, v in field_changes.items()}

    return SsasChange(
        entity_type=ssas_category,
        entity=parent_entity,
        id=str(parent_entity.id),
        change_type=ChangeType.UPDATED,
        field_changes=field_changes,
    )


def ssas_diff(parent_ssas: LocalTabularModel, child_ssas: LocalTabularModel) -> dict[str, list[SsasChange]]:
    ret: dict[str, list[SsasChange]] = {}
    parent_ssas.annotations[0]
    for ssas_category in parent_ssas.TABULAR_FIELDS():
        parent_entities = {x.id: x for x in getattr(parent_ssas, ssas_category)}
        child_entities = {x.id: x for x in getattr(child_ssas, ssas_category)}
        category_changes: list[SsasChange] = [
            SsasChange(
                id=entity_id,
                change_type=ChangeType.DELETED,
                entity_type=ssas_category,
                entity=parent_entities[entity_id],
            )
            for entity_id in set(parent_entities.keys()) - set(child_entities.keys())
        ]
        category_changes.extend(
            SsasChange(
                id=entity_id,
                change_type=ChangeType.ADDED,
                entity_type=ssas_category,
                entity=child_entities[entity_id],
            )
            for entity_id in set(child_entities.keys()) - set(parent_entities.keys())
        )
        for entity_id in set(parent_entities.keys()) & set(child_entities.keys()):
            parent_entity = parent_entities[entity_id]
            child_entity = child_entities[entity_id]
            field_changes = compare_fields(ssas_category, parent_entity, child_entity)
            if field_changes:
                category_changes.append(field_changes)

        ret[ssas_category] = category_changes

    return ret
