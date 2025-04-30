import sys
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from layers.perception import extract_patient_details
from helpers.models import PatientDetails, Decision
from layers.memory import Memory
from layers.decision_making import DecisionMaker
from layers.act import Action
from typing import List
from helpers.gmail_tools import GmailService
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import faiss, json, requests, numpy as np

console = Console(stderr=True)
EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 256
CHUNK_OVERLAP = 40
ROOT = Path(__file__).parent.resolve()

# instantiate an MCP server client
mcp = FastMCP("Mecro Assistant")
memory = Memory()
decision_maker = DecisionMaker()
action = Action()

# Initialize Gmail service
# gmail_service = GmailService("/Users/himank.jain/Desktop/Desktop/EAGV1/Mecro-MedicalAssistant/client_secret_787538940061-v4ledsjcugs34fkc7a7boh0cr91triod.apps.googleusercontent.com.json", "/Users/himank.jain/Desktop/Desktop/EAGV1/Mecro-MedicalAssistant/app_tokens.json")

@mcp.tool()
def get_patient_details(text: str):
    """
    Analyses the text and return patient details in a structured format.
    """
    patient_details = PatientDetails(**extract_patient_details(text))
    console.print(Panel(f"Tool: get_patient_details\nPatient details: {patient_details}", title="Patient details", title_align="center", border_style="green"))
    interaction = {
        "patient_name": patient_details.patient_name,
        "patient_details": patient_details.model_dump(),
    }
    memory.add_interaction(interaction, "medical_assistant")
    return patient_details

@mcp.tool()
def make_decision(patient_input: str):
    """
    This tool is used to make a decision based on the patient's input and the memory.
    """
    decision = Decision(**decision_maker.make_decision(patient_input, memory.recall()))
    console.print(Panel(f"Tool: make_decision\nDecision: {decision.decision}", title="Decision", title_align="center", border_style="yellow"))
    memory.add_interaction({
        "patient_input": patient_input,
        "decision_by": "medical_assistant",
        "decision": decision.decision,
    }, "medical_assistant")
    return decision.decision

@mcp.tool()
def suggest_doctors(patient_input: str):
    """
    This tool is used to suggest doctors based on the patient's input and the memory. This is a pre-cursor to booking an appointment unless the patient is looking for a specific doctor.
    """
    doctors = action.get_doctors(patient_input, memory.recall())
    console.print(Panel(f"Tool: suggest_doctors\nSuggested doctors: {doctors}", title="Suggested doctors", title_align="center", border_style="purple"))
    memory.add_interaction({
        "patient_input": patient_input,
        "suggested_doctors": [doctor.model_dump() for doctor in doctors],
    }, "medical_assistant")
    return doctors

@mcp.tool()
def book_appointment(patient_input: str):
    """
    This tool is used to book an appointment based on the patient's input and the memory. If a patient is looking for a specific doctor, you can use this tool to book an appointment for them.
    """
    appointment_details = action.book_doctor_appointment(patient_input, memory.recall())
    console.print(Panel(f"Tool: book_appointment\nAppointment details: {appointment_details}", title="Appointment details", title_align="center", border_style="blue"))
    memory.add_interaction({
        "patient_input": patient_input,
        "appointment_details": appointment_details,
    }, "medical_assistant")
    return appointment_details

@mcp.tool()
async def send_reminder(recipient_id: str):
    """
    This tool is used to send a reminder to the patient regarding their appointment
    """
    reminder_details = await gmail_service.send_email(recipient_id, "Appointment Reminder", memory.recall())
    console.print(Panel(f"Tool: send_reminder\nReminder details: {reminder_details}", title="Reminder details", title_align="center", border_style="red"))
    memory.add_interaction({
        "recipient_id": recipient_id,
        "reminder_details": reminder_details,
    }, "medical_assistant")
    return reminder_details

def get_embedding(text: str) -> np.ndarray:
    response = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype=np.float32)

@mcp.tool()
def search_documents(query: str) -> list[str]:
    """Search for relevant content from uploaded documents. Only call this tool if intent of patient is to search for relevant content from documents."""
    try:
        index = faiss.read_index(str(ROOT / "faiss_index" / "index.bin"))
        metadata = json.loads((ROOT / "faiss_index" / "metadata.json").read_text())
        query_vec = get_embedding(query).reshape(1, -1)
        D, I = index.search(query_vec, k=5)
        results = []
        for idx in I[0]:
            data = metadata[idx]
            results.append(f"{data['chunk']}\n[Source: {data['doc']}, ID: {data['chunk_id']}]")
        
        parsed_results = action.parse_search_results(query, results)
        return parsed_results
    except Exception as e:
        return [f"ERROR: Failed to search: {str(e)}"]

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    print("STARTING ...")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run() 
    else:
        mcp.run(transport="stdio") 