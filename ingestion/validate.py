import os
import yaml
import sys
import logging
from typing import Dict, Set, List, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
VOCAB_DIR = BASE_DIR / "vocabulary"
CLAIMS_DIR = BASE_DIR / "claims"
EVIDENCE_DIR = BASE_DIR / "evidence"
KNOWLEDGE_DIR = BASE_DIR / "knowledge" / "drugs"
MAPPINGS_DIR = BASE_DIR / "mappings"
RULES_DIR = BASE_DIR / "reasoning" / "rules" / "registry"

def load_yaml(filepath: Path) -> Any:
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to parse {filepath}: {e}")
        return None

def validate_pipeline() -> None:
    logger.info("Starting Production Clinical Content Validator...")
    errors: List[str] = []
    
    # 1. Load Vocabulary
    vocab_ids: Set[str] = set()
    for file_path in VOCAB_DIR.rglob('*.yaml'):
        data = load_yaml(file_path)
        if data and 'term_id' in data:
            term_id = data['term_id']
            if term_id in vocab_ids:
                errors.append(f"Duplicate Vocabulary ID: {term_id} in {file_path}")
            vocab_ids.add(term_id)
            
    logger.info(f"Validated {len(vocab_ids)} unique vocabulary IDs.")

    # 2. Load Evidence
    evidence_ids: Set[str] = set()
    for file_path in EVIDENCE_DIR.rglob('*.yaml'):
        data = load_yaml(file_path)
        if data and 'evidence_id' in data:
            ev_id = data['evidence_id']
            if ev_id in evidence_ids:
                errors.append(f"Duplicate Evidence ID: {ev_id} in {file_path}")
            evidence_ids.add(ev_id)
            
    logger.info(f"Validated {len(evidence_ids)} unique evidence objects.")

    # 3. Load Mappings (Aliases)
    alias_map: Dict[str, str] = {}
    alias_dir = MAPPINGS_DIR / "aliases"
    if alias_dir.exists():
        for file_path in alias_dir.rglob('*.yaml'):
            data = load_yaml(file_path)
            if data and 'alias' in data and 'canonical_id' in data:
                alias = data['alias']
                canon = data['canonical_id']
                if alias in alias_map and alias_map[alias] != canon:
                    errors.append(f"Duplicate Alias Conflict: '{alias}' points to {alias_map[alias]} and {canon}")
                if canon not in vocab_ids:
                    errors.append(f"Alias '{alias}' points to unknown canonical ID: {canon}")
                alias_map[alias] = canon
                
                # Check circular mappings
                if canon in alias_map:
                    errors.append(f"Circular mapping detected: {alias} -> {canon} -> {alias_map[canon]}")

    # 4. Validate Claims
    claims_count = 0
    for file_path in CLAIMS_DIR.rglob('*.yaml'):
        data = load_yaml(file_path)
        if data:
            claims_count += 1
            if 'subject' in data and data['subject'] not in vocab_ids:
                errors.append(f"Claim {file_path.name} references unknown subject: {data['subject']}")
            if 'object' in data and data['object'] not in vocab_ids:
                errors.append(f"Claim {file_path.name} references unknown object: {data['object']}")
            if 'effect' in data and data['effect'] not in vocab_ids:
                errors.append(f"Claim {file_path.name} references unknown effect: {data['effect']}")
            if 'evidence' in data:
                for ev_id in data['evidence']:
                    if ev_id not in evidence_ids:
                        errors.append(f"Claim {file_path.name} references unknown evidence ID: {ev_id}")

    logger.info(f"Validated {claims_count} claims for referential integrity.")

    # Report Output
    if errors:
        logger.error(f"VALIDATION FAILED with {len(errors)} errors:")
        for err in errors:
            logger.error(f"  - {err}")
        sys.exit(1)
    else:
        logger.info("VALIDATION PASSED. Zero referential integrity violations.")
        sys.exit(0)

if __name__ == "__main__":
    validate_pipeline()
