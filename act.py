import json
from typing import List
from config import client
from models import MakeAppointment, DoctorSuggestion

class Action:
    def __init__(self):
        self.doctors_data = json.load(open("data/doctors.json"))
        self.appointments = []

    def get_doctors(self, patient_input: str, memory: List[dict]):
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
        
        You can refer to the following doctor data to make the suggestions:
        {self.doctors_data}

        Patient's input:
        {patient_input}

        Past interactions:
        {memory}

        You must return ONLY a valid list of JSON objects representing the doctor suggestions with no additional text or explanation. Follow the schema below:
        {DoctorSuggestion.model_json_schema()}
        
        Do not include any additional text or explanation in your response. Only return the list of doctor suggestions.
        """
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=PROMPT,
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        # Parse the response and convert to DoctorSuggestion objects
        suggestions_data = json.loads(response.text)
        return [DoctorSuggestion(**suggestion) for suggestion in suggestions_data]