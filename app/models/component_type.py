"""
ComponentType model - blood component types (e.g. RBC, Platelets)
"""
from tortoise import fields
from app.models.base import WatermelonDBModel

class ComponentType(WatermelonDBModel):
    """
    Blood component types configuration
    """
    name = fields.CharField(max_length=255)
    icon_name = fields.CharField(max_length=255)
    is_default = fields.BooleanField(default=False)
    sort_order = fields.IntField(default=0)
    
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="custom_component_types",
        on_delete=fields.CASCADE,
        null=True,
        default=None
    )
    
    class Meta:
        table = "component_types"
        ordering = ["sort_order"]
    
    def __str__(self):
        return self.name
