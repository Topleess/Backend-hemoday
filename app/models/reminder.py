"""
Reminder model - scheduled reminders for users
"""
from tortoise import fields

from app.models.base import WatermelonDBModel


class Reminder(WatermelonDBModel):
    """
    Reminders for medical events, tests, or transfusions
    """
    
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="reminders",
        on_delete=fields.CASCADE
    )
    
    title = fields.CharField(max_length=255)
    remind_at = fields.DatetimeField()
    frequency = fields.CharField(max_length=50)  # e.g., "once", "daily", "weekly"
    text = fields.TextField(null=True)
    is_completed = fields.BooleanField(default=False)
    
    class Meta:
        table = "reminders"
        ordering = ["remind_at"]
    
    def __str__(self):
        return f"Reminder: {self.title} at {self.remind_at}"
