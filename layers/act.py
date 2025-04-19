import json, uuid
from typing import List
from helpers.config import client
from helpers.models import Appointment, DoctorSuggestion
from rich.console import Console
from rich.panel import Panel

console = Console(stderr=True)

class Action:
    def __init__(self):
        self.doctors_data = json.load(open("data/doctors.json"))
        self.appointments = []

    def get_doctors(self, patient_input: str, memory: List[dict]):
        
        available_doctors = []
        patient_details = []
        if memory:
            for record in memory:
                interaction = record.get("interaction")
                if interaction:
                    interaction = json.loads(interaction)

                if 'suggested_doctors' in interaction:
                    available_doctors.extend(interaction['suggested_doctors'])
                    console.print(Panel(f"Previous doctor suggestions: {available_doctors}", title="Using Memory", title_align="center", border_style="green"))

                if 'patient_details' in interaction:
                    patient_details.append(interaction['patient_details'])
                    console.print(Panel(f"Patient details: {patient_details}", title="Using Memory", title_align="center", border_style="green"))

        if not available_doctors:
            available_doctors = self.doctors_data

        if not patient_details:
            patient_details.append(patient_input)

        PROMPT = f"""
        You are a doctor assistant.
        You are given a patient's input and past interactions with the medical assistant.
        You need to suggest a doctor to the patient based on their input and preferences.

        Suggestions should be based on the following:
        - Patient's symptoms
        - Patient's preferences
        - Patient's location
        - Patient's language
        - Patient's medical history
        - Doctor's availability
        
        Patient's input:
        {patient_input}

        Patient details:
        {patient_details}

        Past interactions:
        {memory}

        Available doctors:
        {available_doctors}

        Important:
        - When giving suggestions make sure to highlight all possible options for patient from available doctors list only. However clearly point out the best options basis the patient's preferences and symptoms.
        - If patient is looking for a specific doctor, make sure to suggest that doctor.
        
        You must return ONLY a valid list of JSON objects representing the doctor suggestions with no additional text or explanation. Follow the schema below:
        {DoctorSuggestion.model_json_schema()}. Convert doctor_availability to a list of strings.
        
        Do not include any additional text or explanation in your response. Only return the list of doctor suggestions.
        """
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=PROMPT,
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        suggestions_data = json.loads(response.text)
        return [DoctorSuggestion(**suggestion) for suggestion in suggestions_data]
    
    def book_doctor_appointment(self, patient_input: str, memory: List[dict]):
        
        available_doctors = []
        patient_details = []
        if memory:
            for record in memory:
                interaction = record.get("interaction")
                if interaction:
                    interaction = json.loads(interaction)
                    
                if 'suggested_doctors' in interaction:
                    available_doctors.extend(interaction['suggested_doctors'])
                    console.print(Panel(f"Previous doctor suggestions: {available_doctors}", title="Using Memory", title_align="center", border_style="green"))

                if 'patient_details' in interaction:
                    patient_details.append(interaction['patient_details'])
                    console.print(Panel(f"Patient details: {patient_details}", title="Using Memory", title_align="center", border_style="green"))

        if not available_doctors:
            available_doctors = self.doctors_data

        if not patient_details:
            patient_details.append(patient_input)

        PROMPT = f"""
        As a doctor assistant you are given a patient's input and past interactions with the medical assistant.
        You need to book an appointment for the patient based on their input and update appointment list.
        As output return appointment details for the patient.

        For creating appointment you need patient details and doctor details.

        Patient details can be extracted from patient's input.
        Patient's input:
        {patient_details}

        Doctor details can be extracted from available doctors list. As per input, match Doctor name with doctors in available doctors list and pick the best match and consider it as doctor details.
        Available doctors:
        {available_doctors}

        Past interactions (for reference only):
        {memory}

        You must return ONLY a valid list of JSON objects representing the appointment with no additional text or explanation. Follow the schema below:
        {Appointment.model_json_schema()}
        
        Do not include any additional text or explanation in your response. Only return the appointment details.
        """

        response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=PROMPT,
        config={
            'response_mime_type': 'application/json',
                'response_schema': Appointment,
            }
        )
        appointment_details = json.loads(response.text)
        appointment_details["appointment_id"] = str(uuid.uuid4())
        self.appointments.append(appointment_details)
        console.print(Panel(f"Appointment details: {appointment_details}", title="Appointment details", title_align="center", border_style="green"))
        return appointment_details     