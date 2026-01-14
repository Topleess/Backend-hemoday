"""
Blood test models - test events and individual results
"""
from tortoise import fields

from app.models.base import WatermelonDBModel


class BloodTest(WatermelonDBModel):
    """
    Blood test event - represents a single blood test session
    """
    
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="blood_tests",
        on_delete=fields.CASCADE
    )
    
    date = fields.DatetimeField()
    comment = fields.TextField(null=True)
    
    class Meta:
        table = "blood_tests"
        ordering = ["-date"]
    
    def __str__(self):
        return f"Blood Test {self.date}"


class BloodTestResult(WatermelonDBModel):
    """
    Individual blood test result - specific indicators within a test
    """
    
    blood_test = fields.ForeignKeyField(
        "models.BloodTest",
        related_name="results",
        on_delete=fields.CASCADE
    )
    
    family = fields.ForeignKeyField(
        "models.Family",
        related_name="blood_test_results",
        on_delete=fields.CASCADE
    )
    
    # Indicator details
    name = fields.CharField(max_length=255)  # e.g., "Ferritin", "Hemoglobin"
    value = fields.FloatField()
    unit = fields.CharField(max_length=50)  # e.g., "g/L", "ng/mL"
    
    class Meta:
        table = "blood_test_results"
    
    def __str__(self):
        return f"{self.name}: {self.value} {self.unit}"
