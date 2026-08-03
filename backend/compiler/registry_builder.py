import json
import os
from pathlib import Path

def build_indexes(knowledge_objects, evidence_objects, vocab_objects, claim_objects, mapping_objects, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    canonical_index = {}
    alias_index = {}
    ingredient_index = {}
    classification_index = {}
    characteristic_index = {}
    
    for obj in knowledge_objects:
        identity = obj.get("identity", {})
        canonical = identity.get("canonical_name", "").lower()
        if not canonical:
            continue
            
        canonical_index[canonical] = obj
        alias_index[canonical] = canonical
        
        for alias in identity.get("aliases", []):
            alias_index[alias.lower()] = canonical
            
        for ing in obj.get("ingredients", []):
            name = ing.get("name", "").lower()
            if name not in ingredient_index:
                ingredient_index[name] = []
            ingredient_index[name].append(canonical)
            
        ck = obj.get("clinical_knowledge", {})
        for cls in ck.get("classifications", []):
            c_name = cls.lower()
            if c_name not in classification_index:
                classification_index[c_name] = []
            classification_index[c_name].append(canonical)
            
        for char in ck.get("clinical_characteristics", []):
            c_name = char.lower()
            if c_name not in characteristic_index:
                characteristic_index[c_name] = []
            characteristic_index[c_name].append(canonical)
            
    def _write(name, data):
        with open(Path(output_dir) / name, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
    _write("canonical_index.json", canonical_index)
    _write("alias_index.json", alias_index)
    _write("ingredient_index.json", ingredient_index)
    _write("classification_index.json", classification_index)
    _write("characteristic_index.json", characteristic_index)
    
    _write("evidence_index.json", evidence_objects)
    _write("vocabulary_index.json", vocab_objects)
    _write("claim_index.json", claim_objects)
    _write("mapping_index.json", mapping_objects)
    
    return {
        "canonicals": len(canonical_index),
        "aliases": len(alias_index),
        "ingredients": len(ingredient_index),
        "classifications": len(classification_index),
        "characteristics": len(characteristic_index),
        "evidence": len(evidence_objects),
        "vocabulary": len(vocab_objects),
        "claims": len(claim_objects),
        "mappings": len(mapping_objects)
    }
