"""
Main API v1 router combining all endpoints
"""
from fastapi import APIRouter

from app.api.v1 import auth, sync, upload


router = APIRouter(prefix="/api/v1")

# Include all routers
router.include_router(auth.router)
router.include_router(sync.router)
router.include_router(upload.router)
