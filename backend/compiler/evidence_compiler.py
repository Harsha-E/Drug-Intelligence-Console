import json
import os

def compile_evidence(evidence_dir):
    compiled = {}
    for root, _, files in os.walk(evidence_dir):
        for file in files:
            if file.endswith('.json'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "evidence_id" in data:
                            compiled[data["evidence_id"]] = data
                except:
                    pass
    return compiled
