from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi.responses import JSONResponse

from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.sync import SyncService

router = APIRouter(prefix="/sync", tags=["Synchronization"])

@router.get("")
async def pull_changes(
    request: Request,
    last_pulled_at: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
):
    last_sync = None
    if last_pulled_at:
        last_sync = datetime.fromtimestamp(last_pulled_at / 1000, tz=timezone.utc)
    
    try:
        result = await SyncService.pull_changes(
            family_id=current_user.family_id,
            last_pulled_at=last_sync
        )
        return JSONResponse(content=result)
    except Exception as e:
        print(f"ERROR in pull_changes: {e}")
        raise

@router.post("")
async def push_changes(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    changes = data.get("changes", {})
    await SyncService.push_changes(
        family_id=current_user.family_id,
        changes=changes
    )
    return {"status": "ok"}
