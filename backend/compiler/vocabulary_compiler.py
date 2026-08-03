import yaml
import os

def compile_vocabulary(vocab_dir):
    compiled = {}
    if not os.path.exists(vocab_dir):
        return compiled
        
    for root, _, files in os.walk(vocab_dir):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and "term_id" in data:
                            compiled[data["term_id"]] = data
                except Exception as e:
                    print(f"Error compiling vocabulary {file}: {e}")
    return compiled
