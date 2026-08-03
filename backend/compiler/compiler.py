import json
import os

def compile_knowledge(knowledge_dir):
    compiled = []
    for root, _, files in os.walk(knowledge_dir):
        for file in files:
            if file == "knowledge.json":
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        compiled.append(data)
                except:
                    pass
    return compiled
