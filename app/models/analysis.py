"""
Analysis models - blood analysis records (formerly BloodTest)
"""
from tortoise import fields
from app.models.base import WatermelonDBModel

class Analysis(WatermelonDBModel):
    """
    Analysis event (formerly BloodTest)
    """
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="analyses",
        on_delete=fields.CASCADE
    )
    
    name = fields.CharField(max_length=255)
    date = fields.CharField(max_length=255) # Mobile uses string
    template_name = fields.CharField(max_length=255, null=True)
    
    class Meta:
        table = "analyses"
        ordering = ["-date"]
    
    def __str__(self):
        return f"Analysis {self.name} - {self.date}"


class AnalysisItem(WatermelonDBModel):
    """
    Individual analysis item (formerly BloodTestResult)
    """
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="analysis_items",
        on_delete=fields.CASCADE
    )
    
    analysis = fields.ForeignKeyField(
        "models.Analysis",
        related_name="items", # Mobile schema implies relationship, but we need explicit FK here
        on_delete=fields.CASCADE,
        to_field="id" # Explicitly link to UUID if needed, but default is fine
    )
    # Note: Mobile schema has 'analysis_id' column. ForeignKeyField creates 'analysis_id'.
    
    name = fields.CharField(max_length=255)
    value = fields.CharField(max_length=255) # Mobile uses string
    unit = fields.CharField(max_length=50)
    
    class Meta:
        table = "analysis_items"
    
    def __str__(self):
        return f"{self.name}: {self.value} {self.unit}"
