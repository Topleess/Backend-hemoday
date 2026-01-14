"""
User model - application users with JWT authentication
"""
from tortoise import fields

from app.models.base import WatermelonDBModel


class User(WatermelonDBModel):
    """
    User model with JWT authentication and family relationship
    """
    
    email = fields.CharField(max_length=255, unique=True, index=True)
    password_hash = fields.CharField(max_length=255)
    
    # Foreign key to Family
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="users",
        on_delete=fields.CASCADE
    )
    
    class Meta:
        table = "users"
    
    def __str__(self):
        return self.email
