from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.sync import SyncService

router = APIRouter(prefix="/sync", tags=["Synchronization"])

@router.get("")
async def pull_changes(
    last_pulled_at: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
):
    last_sync = None
    if last_pulled_at:
        # Используем UTC для консистентности
        last_sync = datetime.fromtimestamp(last_pulled_at / 1000, tz=timezone.utc)
    
    result = await SyncService.pull_changes(
        family_id=current_user.family_id,
        last_pulled_at=last_sync
    )
    
    # Возвращаем напрямую, минуя валидацию response_model
    return JSONResponse(content=result)

@router.post("")
async def push_changes(
    data: dict, # Принимаем как сырой словарь для надежности
    current_user: User = Depends(get_current_user),
):
    changes = data.get("changes", {})
    await SyncService.push_changes(
        family_id=current_user.family_id,
        changes=changes
    )
    return {"status": "ok"}
