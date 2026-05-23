import os
import json

class DomainManager:
    def __init__(self, data_file="blocked_domains.json"):
        self.data_file = data_file
        
    def load_domains(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
        
    def save_domains(self, domains):
        with open(self.data_file, 'w') as f:
            json.dump(domains, f, indent=2)