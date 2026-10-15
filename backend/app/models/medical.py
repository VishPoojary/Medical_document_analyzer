from typing import Optional
from pydantic import BaseModel, Field

class Medication(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None

class LabResult(BaseModel):
    name: str
    value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None

class MedicalExtraction(BaseModel):
    patient_name: Optional[str] = None
    diagnosis: list[str] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    lab_results: list[LabResult] = Field(default_factory=list)
    important_findings: list[str] = Field(default_factory=list)