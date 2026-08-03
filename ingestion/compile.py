import os
import yaml
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
VOCAB_DIR = BASE_DIR / "vocabulary"
CLAIMS_DIR = BASE_DIR / "claims"
EVIDENCE_DIR = BASE_DIR / "evidence"
KNOWLEDGE_DIR = BASE_DIR / "knowledge" / "drugs"
MAPPINGS_DIR = BASE_DIR / "mappings"
REGISTRY_DIR = BASE_DIR / "registry" / "current"

def load_yaml(filepath: Path) -> Any:
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def load_json(filepath: Path) -> Any:
    with open(filepath, 'r') as f:
        return json.load(f)

def build_registry() -> None:
    logger.info("Starting O(1) Compiler Pipeline...")
    
    if REGISTRY_DIR.exists():
        shutil.rmtree(REGISTRY_DIR)
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Compile Vocabulary -> dict
    vocabulary: Dict[str, dict] = {}
    for file_path in VOCAB_DIR.rglob('*.yaml'):
        data = load_yaml(file_path)
        if data and 'term_id' in data:
            vocabulary[data['term_id']] = data
            
    with open(REGISTRY_DIR / "vocabulary.json", 'w') as f:
        json.dump(vocabulary, f, indent=2)
    
    # 2. Compile Evidence -> dict
    evidence: Dict[str, dict] = {}
    for file_path in EVIDENCE_DIR.rglob('*.yaml'):
        data = load_yaml(file_path)
        if data and 'evidence_id' in data:
            evidence[data['evidence_id']] = data
            
    with open(REGISTRY_DIR / "evidence.json", 'w') as f:
        json.dump(evidence, f, indent=2)

    # 3. Compile Aliases -> dict
    alias_index: Dict[str, str] = {}
    alias_dir = MAPPINGS_DIR / "aliases"
    if alias_dir.exists():
        for file_path in alias_dir.rglob('*.yaml'):
            data = load_yaml(file_path)
            if data and 'alias' in data and 'canonical_id' in data:
                alias_index[data['alias'].lower()] = data['canonical_id']
                
    with open(REGISTRY_DIR / "alias_index.json", 'w') as f:
        json.dump(alias_index, f, indent=2)

    # 4. Compile Knowledge (Drugs) -> dict
    drug_lookup: Dict[str, dict] = {}
    for file_path in KNOWLEDGE_DIR.rglob('*.json'):
        data = load_json(file_path)
        if data and 'drug_id' in data:
            drug_lookup[data['drug_id']] = data
            
    with open(REGISTRY_DIR / "drug_lookup.json", 'w') as f:
        json.dump(drug_lookup, f, indent=2)

    # 5. Compile Claims & Generate Indexes -> dicts
    claims: Dict[str, dict] = {}
    claim_index: Dict[str, List[str]] = {} # keyed by subject drug_id
    
    for file_path in CLAIMS_DIR.rglob('*.yaml'):
        data = load_yaml(file_path)
        if data and 'claim_id' in data:
            c_id = data['claim_id']
            claims[c_id] = data
            
            # Index by subject
            if 'subject' in data:
                subject = data['subject']
                if subject not in claim_index:
                    claim_index[subject] = []
                claim_index[subject].append(c_id)
                
    with open(REGISTRY_DIR / "claims.json", 'w') as f:
        json.dump(claims, f, indent=2)
    with open(REGISTRY_DIR / "claim_index.json", 'w') as f:
        json.dump(claim_index, f, indent=2)

    # 6. Build Manifest
    manifest = {
        "version": "1.0.0",
        "compiled_at": datetime.now().isoformat(),
        "stats": {
            "vocabulary_count": len(vocabulary),
            "evidence_count": len(evidence),
            "claims_count": len(claims),
            "drugs_count": len(drug_lookup),
            "aliases_count": len(alias_index)
        }
    }
    with open(REGISTRY_DIR / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
        
    logger.info("COMPILATION SUCCESSFUL. O(1) indices generated.")

if __name__ == "__main__":
    build_registry()
