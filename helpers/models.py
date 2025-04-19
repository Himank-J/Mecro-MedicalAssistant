from pydantic import BaseModel
from typing import Optional, List
import uuid

class PatientPreferences(BaseModel):
  patient_location: Optional[str] = None
  patient_language: Optional[str] = None
  preferred_doctor_gender: Optional[str] = None
  preferred_time_slot: Optional[str] = None

class PatientDetails(BaseModel):
  patient_name: Optional[str] = None
  patient_age: Optional[int] = None
  patient_gender: Optional[str] = None
  patient_phone_number: Optional[str] = None
  patient_email: Optional[str] = None
  patient_preferences: Optional[PatientPreferences] = None
  patient_medical_history: Optional[List[str]] = None
  patient_current_symptoms: Optional[List[str]] = None

class Decision(BaseModel):
  decision: str

class DoctorSuggestion(BaseModel):
  doctor_name: str
  doctor_specialization: str
  doctor_address: str
  doctor_gender: str
  doctor_languages: List[str]
  clinic_name: str
  doctor_availability: List[str]

class Appointment(BaseModel):
  patient_name: str
  patient_age: int
  patient_gender: str
  patient_symptoms: List[str]
  patient_location: str
  patient_language: str
  preferred_time_slot: str
  doctor_name: str
  clinic_name: str
  appointment_date: str