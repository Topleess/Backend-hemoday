"""
Base model with WatermelonDB required fields
"""
from datetime import datetime
from typing import Optional
import uuid

from tortoise import fields
from tortoise.models import Model


class WatermelonDBModel(Model):
    """
    Base model for all entities with WatermelonDB sync support.
    Every table must have: id, created_at, updated_at, deleted_at
    """
    
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True, default=None)
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Soft delete by setting deleted_at timestamp"""
        self.deleted_at = datetime.utcnow()
