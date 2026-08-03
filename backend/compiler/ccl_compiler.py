import yaml
import os
import json
import hashlib
import time
from pathlib import Path

def parse_ccl(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f)
        except Exception as e:
            print(f"Error parsing CCL file {file_path}: {e}")
            return None

def generate_ir(ast_raw):
    # Minimal validation/normalization for IR
    if "rule" not in ast_raw:
        return None
    return ast_raw

def optimize_ir(ir):
    # Pass-through for now, can implement logic pruning later
    return ir

def compile_ccl(rules_dir, registry_dir):
    rules_out_dir = Path(registry_dir) / "rules"
    os.makedirs(rules_out_dir, exist_ok=True)
    
    rules = {}
    priority_index = {}
    manifest_entries = []
    
    for root, _, files in os.walk(rules_dir):
        for file in files:
            if file.endswith('.ccl'):
                path = os.path.join(root, file)
                ast_raw = parse_ccl(path)
                if not ast_raw:
                    continue
                
                ir = generate_ir(ast_raw)
                if not ir:
                    continue
                    
                ast = optimize_ir(ir)
                rule_id = ast["rule"]
                rules[rule_id] = ast
                
                priority = ast.get("priority", "NORMAL")
                if priority not in priority_index:
                    priority_index[priority] = []
                priority_index[priority].append(rule_id)
                
                hasher = hashlib.sha256()
                hasher.update(json.dumps(ast, sort_keys=True).encode('utf-8'))
                rule_hash = hasher.hexdigest()
                
                manifest_entries.append({
                    "rule_id": rule_id,
                    "version": ast.get("version", "1.0"),
                    "priority": priority,
                    "hash": rule_hash,
                    "compiled_at": time.time()
                })
                
    # Write rule registry
    with open(rules_out_dir / "rules.json", 'w', encoding='utf-8') as f:
        json.dump(rules, f, indent=2)
        
    with open(rules_out_dir / "priority_index.json", 'w', encoding='utf-8') as f:
        json.dump(priority_index, f, indent=2)
        
    manifest = {
        "compiled_rules_count": len(rules),
        "rules": manifest_entries,
        "timestamp": time.time()
    }
    with open(rules_out_dir / "manifest.json", 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        
    return rules
