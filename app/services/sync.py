from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
import logging

from tortoise.expressions import Q
from tortoise.exceptions import IntegrityError
from app.models import (
    Transfusion, Analysis, AnalysisItem,
    AnalysisTemplate, AnalysisTemplateItem, Reminder, Document,
    ComponentType, ChelatorType
)

# Словарь моделей
# Ключи должны совпадать с именами таблиц в WatermelonDB на фронте
SYNC_MODELS = {
    "transfusions": Transfusion,
    "analyses": Analysis,
    "analysis_items": AnalysisItem,
    "analysis_templates": AnalysisTemplate,
    "analysis_template_items": AnalysisTemplateItem,
    "reminders": Reminder,
    "documents": Document,
    "component_types": ComponentType,
    "chelator_types": ChelatorType,
}

class SyncService:
    @staticmethod
    async def pull_changes(family_id: str, last_pulled_at: Optional[datetime] = None) -> Dict[str, Any]:
        changes = {}
        timestamp = datetime.now(timezone.utc)
        
        tables_to_sync = [
            "transfusions", "analyses", "analysis_items", 
            "analysis_templates", "analysis_template_items",
            "reminders",
            "component_types", "chelator_types"
        ]

        for table_name in tables_to_sync:
            res_created, res_updated, res_deleted = [], [], []
            
            model = SYNC_MODELS.get(table_name)
            if model:
                try:
                    # Determine filter based on whether the table is family-specific or global lookup
                    if table_name in ["component_types", "chelator_types"]:
                        # Pull items that are default OR belongs to this family
                        query = model.filter(Q(is_default=True) | Q(family_id=family_id))
                    elif table_name == "analysis_templates":
                        # Pull items that are default OR belongs to this family
                        query = model.filter(Q(is_default=True) | Q(family_id=family_id))
                    elif table_name == "analysis_template_items":
                        # Pull items where parent template is default OR template family is this family
                        # Complex query, simplified: pull all items connected to visible templates
                        # But simpler: pull items where (family_id is None) OR (family_id == family_id)
                        # Assuming we set family_id=None for global items too
                        query = model.filter(Q(family_id=None) | Q(family_id=family_id))
                    else:
                        has_family = "family" in model._meta.fields_map
                        if has_family:
                            query = model.filter(family_id=family_id)
                        else:
                            query = model.all()

                    if last_pulled_at:
                        query = query.filter(updated_at__gt=last_pulled_at)
                    
                    records = await query.all()
                    
                    for record in records:
                        record_dict = await SyncService._serialize_record(record)
                        if hasattr(record, 'deleted_at') and record.deleted_at is not None:
                            res_deleted.append(str(record_dict["id"]))
                        elif last_pulled_at is None or record.created_at > last_pulled_at:
                            res_created.append(record_dict)
                        else:
                            res_updated.append(record_dict)
                except Exception as e:
                    logging.error(f"Таблица {table_name} пропущена: {e}")
            
            changes[table_name] = {
                "created": res_created,
                "updated": res_updated,
                "deleted": res_deleted
            }

        return {
            "changes": changes,
            "timestamp": int(timestamp.timestamp() * 1000)
        }

    @staticmethod
    async def push_changes(family_id: str, changes: Dict[str, Any]) -> None:
        for table_name, table_changes in changes.items():
            model = SYNC_MODELS.get(table_name)
            if not model: continue
            
            try:
                # Check for family_id field
                has_family = "family" in model._meta.fields_map

                for record_data in table_changes.get("created", []):
                    # For lookups, only allow syncing non-default (custom) items
                    if table_name in ["component_types", "chelator_types", "analysis_templates"] and record_data.get("is_default"):
                        continue

                    if has_family:
                        record_data["family_id"] = family_id
                    await SyncService._create_or_update_record(model, record_data, family_id if has_family else None)
                for record_data in table_changes.get("updated", []):
                    if table_name in ["component_types", "chelator_types", "analysis_templates"] and record_data.get("is_default"):
                        continue

                    if has_family:
                        record_data["family_id"] = family_id
                    await SyncService._create_or_update_record(model, record_data, family_id if has_family else None)
                for record_id in table_changes.get("deleted", []):
                    if has_family:
                        await SyncService._soft_delete_record(model, record_id, family_id)
            except Exception as e:
                logging.error(f"Error syncing table {table_name}: {e}")
                raise e

    @staticmethod
    async def _serialize_record(record: Any) -> Dict[str, Any]:
        data = {}
        for field_name, field_object in record._meta.fields_map.items():
            value = getattr(record, field_name, None)
            
            # Skip relations themselves
            if field_name in record._meta.fk_fields:
                 # WatermelonDB expects _{field}_id suffix for relations
                 fk_id = getattr(record, f"{field_name}_id", None)
                 data[f"{field_name}_id"] = str(fk_id) if fk_id else None
            elif 'ReverseRelation' in field_object.__class__.__name__ or 'BackwardFKRelation' in field_object.__class__.__name__:
                continue
            else:
                if isinstance(value, datetime):
                    data[field_name] = int(value.timestamp() * 1000)
                elif hasattr(value, '_meta'): # It's a model instance
                    continue 
                else:
                    data[field_name] = value
        return data

    @staticmethod
    async def _create_or_update_record(model: Any, data: Dict[str, Any], family_id: Optional[str] = None) -> None:
        record_id = data.get("id")
        
        # Determine valid fields, including _{field}_id for all foreign keys
        valid_fields = set(model._meta.fields_map.keys())
        for field_name in model._meta.fk_fields:
            valid_fields.add(f"{field_name}_id")

        # Map WatermelonDB keys to Tortoise fields if necessary (usually they already match)
        # e.g. mapping camelCase if it was present, though here we use snake_case mostly.
        
        # Filter data to only include valid fields
        data = {k: v for k, v in data.items() if k in valid_fields or k == 'id'}

        # Обработка дат из timestamp
        for field in ["created_at", "updated_at", "deleted_at"]: 
            if field in data and isinstance(data[field], int):
                data[field] = datetime.fromtimestamp(data[field] / 1000, tz=timezone.utc)
        
        if "updated_at" not in data:
            data["updated_at"] = datetime.now(timezone.utc)

        query = model.filter(id=record_id)
        
        # Check if record exists (either belonging to family OR global)
        # Global records (family_id is NULL) should be found regardless of user's family_id
        if family_id:
             has_family = "family" in model._meta.fields_map
             if has_family:
                 query = query.filter(Q(family_id=family_id) | Q(family_id__isnull=True))

        existing = await query.first()
        if existing:
            # If it's a global record (family_id is None), DO NOT update it from a user sync
            # unless we specifically allow it (which we don't for defaults)
            if hasattr(existing, 'family_id') and existing.family_id is None:
                 return # Skip update for global record

            update_data = {k: v for k, v in data.items() if k != 'id'}
            await model.filter(id=record_id).update(**update_data)
        else:
            try:
                await model.create(**data)
            except IntegrityError:
                # If we hit a duplicate key error, it means the record exists but we missed it 
                # (e.g. global record that our filter didn't catch). 
                # In this case, it's safe to ignore as we don't want to overwrite it anyway.
                logging.warning(f"Skipping duplicate creation for {model.__name__} id={record_id}")
                pass

    @staticmethod
    async def _soft_delete_record(model: Any, record_id: str, family_id: str) -> None:
        try:
            # Removed UUID casting since ID is now string
            await model.filter(id=record_id, family_id=family_id).update(deleted_at=datetime.now(timezone.utc))
        except: pass
