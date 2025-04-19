import json
from datetime import datetime

class Memory:
    def __init__(self):
        self.memory = json.load(open("data/agent_memory.json"))

    def add_interaction(self, interaction, role):
        
        if isinstance(interaction, dict):
            interaction = json.dumps(interaction)
        self.memory.append({
            "interaction": interaction,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })
        with open("data/agent_memory.json", 'w') as f:
            json.dump(self.memory, f, indent=4)

    def recall(self):
        return sorted(self.memory, key=lambda x: x['timestamp'])