"""
Analysis template model - user-created presets for blood tests
"""
from tortoise import fields

from app.models.base import WatermelonDBModel


class AnalysisTemplate(WatermelonDBModel):
    """
    User-created templates for blood test indicators
    """
    
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="analysis_templates",
        on_delete=fields.CASCADE
    )
    
    name = fields.CharField(max_length=255)
    
    # JSON array of indicator names, e.g., ["Hb", "Ferritin", "Iron"]
    indicators_json = fields.JSONField()
    
    class Meta:
        table = "analysis_templates"
    
    def __str__(self):
        return self.name
