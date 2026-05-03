from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


# Prescription
class PrescriptionOut(BaseModel):
    id: int
    symptom_notes: Optional[str]
    file_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Analysis
class MedicineItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: Optional[str]

class AnalysisOut(BaseModel):
    id: int
    prescription_id: int
    medicines: Optional[str]
    doctor_advice: Optional[str]
    lifestyle_changes: Optional[str]
    created_at: datetime
    disclaimer: str = "⚠️ This is AI-generated information only and is NOT medical advice. Always consult a qualified healthcare professional."

    class Config:
        from_attributes = True