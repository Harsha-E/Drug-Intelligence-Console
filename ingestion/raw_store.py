import json
import os
import time

class RawStore:
    def __init__(self, raw_dir: str):
        self.raw_dir = raw_dir
        os.makedirs(self.raw_dir, exist_ok=True)
        
    def save_raw(self, source: str, data: list):
        filename = f"{source}_{int(time.time())}.json"
        with open(os.path.join(self.raw_dir, filename), "w") as f:
            json.dump(data, f, indent=2)
            
    def load_all_raw(self) -> dict:
        raw_data = {}
        for filename in os.listdir(self.raw_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.raw_dir, filename), "r") as f:
                    raw_data[filename] = json.load(f)
        return raw_data
