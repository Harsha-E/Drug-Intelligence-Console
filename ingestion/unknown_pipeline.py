import json
import os
import time
import uuid

# In a real system this would be an external API/LLM call
def query_external_knowledge(unknown_string: str) -> dict:
    """Mock external knowledge retrieval (e.g. LLM or NIH API)"""
    # Simulate API latency
    time.sleep(1)
    
    # Simple heuristic mock for demo purposes
    normalized = unknown_string.lower().strip()
    ingredients = []
    
    # Hardcode a few typical unknown examples that might get scanned
    if "tylenol" in normalized:
        candidate_ingredients = ["acetaminophen"]
    elif "advil" in normalized:
        candidate_ingredients = ["ibuprofen"]
    else:
        candidate_ingredients = [normalized]
        
    return {
        "confidence": 0.85,
        "source": "Identity_Resolution_AI",
        "candidate_ingredients": candidate_ingredients
    }

class UnknownMedicinePipeline:
    def __init__(self, review_queue_dir: str):
        self.review_queue_dir = review_queue_dir
        os.makedirs(self.review_queue_dir, exist_ok=True)
            
    def process_unknown_medicine(self, raw_string: str) -> str:
        """
        Takes an unknown string (e.g. from OCR), queries external knowledge,
        and adds it to the Clinical Review Queue.
        Returns a temporary tracking ID.
        """
        tracking_id = f"review_{uuid.uuid4().hex[:8]}"
        
        # 1. Identity Resolution (No mocked graph nodes!)
        extraction_result = query_external_knowledge(raw_string)
        
        # 2. Add to Clinical Review Queue
        normalized_record = {
            "tracking_id": tracking_id,
            "raw_string": raw_string,
            "timestamp": time.time(),
            "extraction": extraction_result,
            "status": "PENDING_REVIEW"
        }
        queue_file = os.path.join(self.review_queue_dir, f"unknown_{tracking_id}.json")
        with open(queue_file, "w") as f:
            json.dump([normalized_record], f, indent=2)
            
        return tracking_id
