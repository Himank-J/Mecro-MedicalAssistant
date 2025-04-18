import sys
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from perception import extract_patient_details
from models import PatientDetails, Decision, DoctorCard
from memory import Memory
from decision_making import DecisionMaker
from act import Action
from typing import List

# instantiate an MCP server client
mcp = FastMCP("Mecro Assistant")
memory = Memory()
decision_maker = DecisionMaker()
action = Action()

@mcp.tool()
def get_patient_details(text: str):
    """
    Analyses the text and return patient details in a structured format.
    """
    return PatientDetails(**extract_patient_details(text))

@mcp.tool()
def add_interaction(interaction: str | dict, role: str):
    """
    This tool is used to add the interaction to the memory. 
    interaction: The interaction to add to the memory. Could be a message from patient or a message from medical assistant
    role: The role of the interaction (patient or medical assistant)
    """
    memory.add_interaction(interaction, role)

@mcp.tool()
def recall_memory():
    """
    This tool is used to recall the memory. Should be used each time you are about to respond to the patient.
    """
    return memory.recall()

@mcp.tool()
def make_decision(patient_input: str):
    """
    This tool is used to make a decision based on the patient's input and the memory.
    """
    return Decision(**decision_maker.make_decision(patient_input, memory.recall())).decision

@mcp.tool()
def suggest_doctors(patient_input: str) -> List[DoctorCard]:
    """
    This tool is used to suggest doctors based on the patient's input and the memory.
    Returns a list of doctor cards with formatted information for display.
    Each card contains:
    - Doctor's name and specialization
    - Clinic name and address
    - Available languages
    - Available days and timings
    - Gender and card styling
    """
    doctor_cards = action.get_doctors(patient_input, memory.recall())
    
    # Add the suggestions to memory
    memory.add_interaction(
        {
            "type": "doctor_suggestions",
            "suggestions": [card.dict() for card in doctor_cards]
        },
        "assistant"
    )
    
    return doctor_cards

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution