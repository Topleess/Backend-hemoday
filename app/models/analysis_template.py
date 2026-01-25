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
        on_delete=fields.CASCADE,
        null=True,
        default=None
    )
    
    name = fields.CharField(max_length=255)
    is_default = fields.BooleanField(default=False)
    # Removed: indicators_json
    
    class Meta:
        table = "analysis_templates"
    
    def __str__(self):
        return self.name

class AnalysisTemplateItem(WatermelonDBModel):
    """
    Item within an analysis template
    """
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="analysis_template_items",
        on_delete=fields.CASCADE,
        null=True,
        default=None
    )
    
    template = fields.ForeignKeyField(
        "models.AnalysisTemplate",
        related_name="items",
        on_delete=fields.CASCADE,
        to_field="id"
    )
    # Note: Mobile schema has 'template_id'. ForeignKeyField creates 'template_id'.
    
    name = fields.CharField(max_length=255)
    unit = fields.CharField(max_length=50)
    
    class Meta:
        table = "analysis_template_items"
    
    def __str__(self):
        return f"Template Item: {self.name} ({self.unit})"
