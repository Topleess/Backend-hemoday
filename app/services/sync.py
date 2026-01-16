from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from uuid import UUID
import logging

from app.models import (
    Transfusion, BloodTest, BloodTestResult,
    AnalysisTemplate, Reminder, Document
)

# Словарь моделей
SYNC_MODELS = {
    "transfusions": Transfusion,
    "blood_tests": BloodTest,
    "blood_test_results": BloodTestResult,
    "analysis_templates": AnalysisTemplate,
    "reminders": Reminder,
    "documents": Document,
}

class SyncService:
    @staticmethod
    async def pull_changes(family_id: UUID, last_pulled_at: Optional[datetime] = None) -> Dict[str, Any]:
        changes = {}
        timestamp = datetime.now(timezone.utc)
        
        for table_name in ["transfusions", "blood_tests", "blood_test_results", "analysis_templates", "reminders", "documents"]:
            # ЖЕСТКАЯ ГАРАНТИЯ: всегда начинаем с пустых списков
            res_created, res_updated, res_deleted = [], [], []
            
            model = SYNC_MODELS.get(table_name)
            if model:
                try:
                    # Проверяем связь с БД
                    _ = model._meta.db
                    
                    query = model.filter(family_id=family_id)
                    if last_pulled_at:
                        query = query.filter(updated_at__gt=last_pulled_at)
                    
                    # ПОЛУЧАЕМ ДАННЫЕ (список объектов)
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
            
            # В словарь ПОПАДАЮТ ТОЛЬКО СПИСКИ, созданные выше
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
    async def push_changes(family_id: UUID, changes: Dict[str, Any]) -> None:
        for table_name, table_changes in changes.items():
            model = SYNC_MODELS.get(table_name)
            if not model: continue
            try:
                _ = model._meta.db
                for record_data in table_changes.get("created", []):
                    record_data["family_id"] = family_id
                    await SyncService._create_or_update_record(model, record_data)
                for record_data in table_changes.get("updated", []):
                    record_data["family_id"] = family_id
                    await SyncService._create_or_update_record(model, record_data)
                for record_id in table_changes.get("deleted", []):
                    await SyncService._soft_delete_record(model, record_id, family_id)
            except: continue

    @staticmethod
    async def _serialize_record(record: Any) -> Dict[str, Any]:
        data = {}
        for field_name in record._meta.fields_map.keys():
            value = getattr(record, field_name, None)
            if isinstance(value, datetime):
                data[field_name] = int(value.timestamp() * 1000)
            elif isinstance(value, UUID):
                data[field_name] = str(value)
            else:
                data[field_name] = value
        return data

    @staticmethod
    async def _create_or_update_record(model: Any, data: Dict[str, Any]) -> None:
        record_id = data.get("id")
        for field in ["created_at", "updated_at", "deleted_at", "date", "remind_at"]:
            if field in data and isinstance(data[field], int):
                data[field] = datetime.fromtimestamp(data[field] / 1000, tz=timezone.utc)
        existing = await model.filter(id=record_id).first()
        if existing:
            await model.filter(id=record_id).update(**data)
        else:
            await model.create(**data)

    @staticmethod
    async def _soft_delete_record(model: Any, record_id: str, family_id: UUID) -> None:
        try:
            await model.filter(id=UUID(record_id), family_id=family_id).update(deleted_at=datetime.now(timezone.utc))
        except: pass
