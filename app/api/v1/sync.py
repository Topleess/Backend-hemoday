"""
WatermelonDB synchronization endpoints
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.schemas import SyncPullResponse, SyncPushRequest
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.sync import SyncService


router = APIRouter(prefix="/sync", tags=["Synchronization"])


@router.get("", response_model=SyncPullResponse)
async def pull_changes(
    last_pulled_at: Optional[int] = Query(
        None,
        description="Timestamp in milliseconds of last sync"
    ),
    current_user: User = Depends(get_current_user),
):
    """
    Pull changes from server since last_pulled_at timestamp.
    
    WatermelonDB protocol implementation for pulling server changes.
    
    Args:
        last_pulled_at: Unix timestamp in milliseconds (None for initial sync)
        current_user: Current authenticated user
    
    Returns:
        Changes for each table and new timestamp
    """
    # Convert milliseconds to datetime
    last_sync = None
    if last_pulled_at:
        last_sync = datetime.fromtimestamp(last_pulled_at / 1000)
    
    # Get changes for user's family
    result = await SyncService.pull_changes(
        family_id=current_user.family_id,
        last_pulled_at=last_sync
    )
    
    return result


@router.post("")
async def push_changes(
    data: SyncPushRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Push changes from client to server.
    
    WatermelonDB protocol implementation for pushing client changes.
    
    Args:
        data: Changes for each table (created, updated, deleted)
        current_user: Current authenticated user
    
    Returns:
        Success confirmation
    """
    # Convert Pydantic models to dict
    changes = {}
    for table_name, table_changes in data.changes.items():
        changes[table_name] = {
            "created": table_changes.created,
            "updated": table_changes.updated,
            "deleted": table_changes.deleted,
        }
    
    # Push changes for user's family
    await SyncService.push_changes(
        family_id=current_user.family_id,
        changes=changes
    )
    
    return {"status": "ok"}
