import json
from datetime import datetime

class Memory:
    def __init__(self):
        self.memory = []

    def add_interaction(self, interaction, role):
        
        if isinstance(interaction, dict):
            interaction = json.dumps(interaction)
        self.memory.append({
            "interaction": interaction,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })
        print(f"Added interaction to memory: {interaction} by {role}")
        print(f"Current memory: {len(self.memory)}")

    def recall(self):
        return self.memory