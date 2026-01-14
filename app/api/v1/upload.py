"""
File upload endpoint
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.v1.schemas import FileUploadResponse
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a file (documents, images, etc.)
    
    Files are saved to uploads/ directory with unique names.
    """
    # Validate file size
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create family subdirectory
    family_dir = Path(settings.UPLOAD_DIR) / str(current_user.family_id)
    family_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = family_dir / unique_filename
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Return file URL (relative path)
    file_url = f"{current_user.family_id}/{unique_filename}"
    
    return FileUploadResponse(
        file_url=file_url,
        filename=file.filename or unique_filename,
        size=file_size,
    )
