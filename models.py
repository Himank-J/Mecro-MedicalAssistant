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

class DoctorAvailability(BaseModel):
  day: str
  start_time: str
  end_time: str
  is_available: bool

class DoctorSuggestion(BaseModel):
  doctor_name: str
  doctor_specialization: str
  doctor_address: str
  doctor_gender: str
  doctor_languages: List[str]
  clinic_name: str
  doctor_availability: List[DoctorAvailability]

class DoctorCard(BaseModel):
  name: str
  specialization: str
  clinic_name: str
  address: str
  languages: List[str]
  available_days: List[str]
  timings: str
  gender: str
  card_color: Optional[str] = "#f0f0f0"  # Default background color
  rating: Optional[float] = None
  experience_years: Optional[int] = None
  consultation_fee: Optional[str] = None
  profile_image: Optional[str] = None

class MakeAppointment(BaseModel):
  patient_name: str
  patient_age: int
  patient_gender: str
  patient_symptoms: List[str]
  patient_location: str
  patient_language: str
  preferred_time_slot: str
  doctor_name: str
  appointment_id: str = str(uuid.uuid4())
  appointment_date: str