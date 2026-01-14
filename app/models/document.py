"""
Document model - uploaded files and documents
"""
from tortoise import fields

from app.models.base import WatermelonDBModel


class Document(WatermelonDBModel):
    """
    Uploaded documents (medical records, test results, etc.)
    """
    
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="documents",
        on_delete=fields.CASCADE
    )
    
    name = fields.CharField(max_length=255)
    category = fields.CharField(max_length=100, null=True)
    
    # Path to file on server
    file_url = fields.CharField(max_length=500)
    
    class Meta:
        table = "documents"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Document: {self.name}"
