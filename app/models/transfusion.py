"""
Transfusion model - blood transfusion records
"""
from tortoise import fields

from app.models.base import WatermelonDBModel


class Transfusion(WatermelonDBModel):
    """
    Blood transfusion records with medication and indicator tracking
    """
    
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="transfusions",
        on_delete=fields.CASCADE
    )
    
    date = fields.DatetimeField()
    volume_ml = fields.IntField()
    patient_weight_kg = fields.FloatField()
    
    # User-defined medication name
    medication_name = fields.CharField(max_length=255, null=True)
    
    # Indicator (default "Hemoglobin")
    indicator_name = fields.CharField(max_length=255, default="Hemoglobin")
    
    # Values before and after transfusion
    value_before = fields.FloatField()
    value_after = fields.FloatField()
    
    # Additional notes
    notes = fields.TextField(null=True)
    
    class Meta:
        table = "transfusions"
        ordering = ["-date"]
    
    def __str__(self):
        return f"Transfusion {self.date} - {self.volume_ml}ml"
