"""
Transfusion model - blood transfusion records
"""
from tortoise import fields
from app.models.base import WatermelonDBModel

class Transfusion(WatermelonDBModel):
    """
    Blood transfusion records
    """
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="transfusions",
        on_delete=fields.CASCADE
    )
    
    date = fields.CharField(max_length=255) # Mobile stores as string
    
    # New fields matching mobile schema
    component = fields.CharField(max_length=255, null=True)
    volume = fields.IntField() # Renamed from volume_ml
    weight = fields.FloatField() # Renamed from patient_weight_kg
    volume_per_kg = fields.FloatField(default=0.0)
    hb_before = fields.FloatField(default=0.0)
    hb_after = fields.FloatField(default=0.0)
    delta_hb = fields.FloatField(default=0.0)
    chelator = fields.CharField(max_length=255, null=True)
    
    # Removed: medication_name, indicator_name, value_before, value_after, notes
    
    class Meta:
        table = "transfusions"
        ordering = ["-date"]
    
    def __str__(self):
        return f"Transfusion {self.date} - {self.volume}ml"
