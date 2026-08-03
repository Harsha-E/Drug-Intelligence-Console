import json
import os
import time

class ReviewQueue:
    def __init__(self, review_dir: str, accepted_dir: str):
        self.review_dir = review_dir
        self.accepted_dir = accepted_dir
        os.makedirs(self.review_dir, exist_ok=True)
        os.makedirs(self.accepted_dir, exist_ok=True)
        
    def approve_all(self):
        """Mock function that human-approves or auto-approves queued records"""
        print("Approving all records in review queue...")
        accepted_data = []
        
        for filename in os.listdir(self.review_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.review_dir, filename)
                with open(filepath, "r") as f:
                    batch = json.load(f)
                    for item in batch:
                        accepted_data.append(item["data"])
                # Remove from queue after processing
                os.remove(filepath)
                
        if accepted_data:
            accepted_file = os.path.join(self.accepted_dir, f"accepted_{int(time.time())}.json")
            with open(accepted_file, "w") as f:
                json.dump(accepted_data, f, indent=2)
            print(f"Moved {len(accepted_data)} records to Accepted Knowledge.")
