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

console = Console(stderr=True)

# instantiate an MCP server client
mcp = FastMCP("Mecro Assistant")
memory = Memory()
decision_maker = DecisionMaker()
action = Action()

# Initialize Gmail service
gmail_service = GmailService("/Users/himank.jain/Desktop/Desktop/EAGV1/Mecro-MedicalAssistant/client_secret_787538940061-v4ledsjcugs34fkc7a7boh0cr91triod.apps.googleusercontent.com.json", "/Users/himank.jain/Desktop/Desktop/EAGV1/Mecro-MedicalAssistant/app_tokens.json")

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