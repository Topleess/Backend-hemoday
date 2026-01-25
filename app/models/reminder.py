"""
Reminder model - scheduled reminders
"""
from tortoise import fields
from app.models.base import WatermelonDBModel

class Reminder(WatermelonDBModel):
    """
    Reminders for medical events
    """
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="reminders",
        on_delete=fields.CASCADE
    )
    
    title = fields.CharField(max_length=255)
    date = fields.CharField(max_length=255) # Mobile stores as string
    time = fields.CharField(max_length=255) # Mobile stores as string
    repeat = fields.CharField(max_length=50) # Renamed from frequency
    note = fields.TextField(null=True) # Renamed from text
    # Removed: is_completed, remind_at
    
    class Meta:
        table = "reminders"
        ordering = ["date", "time"]
    
    def __str__(self):
        return f"Reminder: {self.title} at {self.date} {self.time}"
