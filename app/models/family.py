"""
Family model - represents a family unit with shared medical data
"""
import random
import string
from datetime import date

from tortoise import fields

from app.models.base import WatermelonDBModel


def generate_invite_code() -> str:
    """Generate unique 6-character invite code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Family(WatermelonDBModel):
    """
    Family model - users belong to families and data is isolated by family_id
    """
    
    invite_code = fields.CharField(max_length=6, unique=True, default=generate_invite_code)
    owner_id = fields.CharField(max_length=255, null=True)
    patient_name = fields.CharField(max_length=255, null=True)
    patient_current_weight = fields.FloatField(null=True)
    patient_birth_date = fields.DateField(null=True)
    
    class Meta:
        table = "families"
    
    def __str__(self):
        return f"Family {self.patient_name} ({self.invite_code})"
