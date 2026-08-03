import yaml
import os

def compile_mappings(maps_dir):
    compiled = {}
    if not os.path.exists(maps_dir):
        return compiled
        
    for root, _, files in os.walk(maps_dir):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data and "mappings" in data:
                            map_name = os.path.splitext(file)[0]
                            compiled[map_name] = data["mappings"]
                except Exception as e:
                    print(f"Error compiling mapping {file}: {e}")
    return compiled
