import yaml
import os

def compile_claims(claims_dir):
    compiled = {}
    if not os.path.exists(claims_dir):
        return compiled
        
    for root, _, files in os.walk(claims_dir):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and "claim_id" in data:
                            compiled[data["claim_id"]] = data
                except Exception as e:
                    print(f"Error compiling claim {file}: {e}")
    return compiled
