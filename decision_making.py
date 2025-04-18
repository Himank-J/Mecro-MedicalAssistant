import json
from config import client
from models import Decision
from typing import List

class DecisionMaker:

    def make_decision(self, patient_input: str, memory: List[dict]):
        PROMPT = f"""
        You are given a patient's input as well as past interactions with the medical assistant and you need to make a decision on what to do next.
        Analyse the patient's input and past interactions carefully before making a decision.
        
        Your decision should be either ONE of the following:
        - Book an appointment: If patient is looking to book an appointment with a doctor return "book_appointment".
        - Get details about previous appointments: If patient is looking to get details about previous appointments return "get_previous_appointments".
        - Set a reminder: If patient is looking to set a reminder for an appointment return "set_reminder".
        - Ask for more information: If patient is looking for more information return "ask_for_more_information".
        
        You must return ONLY one of the above decisions in JSON format. Do not include any other text or explanation.
        
        Here is the patient's input:
        {patient_input}

        Here is the past interactions:
        {memory}
        """  

        response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=PROMPT,
        config={
            'response_mime_type': 'application/json',
                'response_schema': Decision,
            }
        )
        return json.loads(response.text)      
