import json
from config import client
from models import PatientDetails

def extract_patient_details(text: str) -> dict:
    PROMPT = """
    You are an expert in extracting data in converting unstructured data into structured data.
    You will be given a text and you need to extract the patient details from the text.
    You must return ONLY a valid JSON object following the exact schema below, with no additional text or explanation.

    Schema:
    {
        "patient_name": string,
        "patient_age": number,
        "patient_gender": string,
        "patient_phone_number": string,
        "patient_email": string,
        "patient_preferences": {
            "patient_location": string,
            "patient_language": string,
            "preferred_doctor_gender": string,
            "preferred_time_slot": string
        },
        "patient_medical_history": array of strings,
        "patient_current_symptoms": array of strings
    }
    For any fields where infomation is not found in input text do not include them in the output.
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=PROMPT + text,
        config={
            'response_mime_type': 'application/json',
            'response_schema': PatientDetails,
        },
    )
    return json.loads(response.text)