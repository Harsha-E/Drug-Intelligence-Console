import sys
import time
from pathlib import Path

from validator import run_validation
from compiler import compile_knowledge
from evidence_compiler import compile_evidence
from vocabulary_compiler import compile_vocabulary
from claim_compiler import compile_claims
from mapping_compiler import compile_mappings
from ccl_compiler import compile_ccl
from registry_builder import build_indexes
from manifest_builder import generate_manifest
from hash import generate_build_hash
from diagnostics import write_diagnostics
from spec.knowledge_spec import KNOWLEDGE_SPEC

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge" / "drugs"
EVIDENCE_DIR = BASE_DIR / "evidence"
VOCAB_DIR = BASE_DIR / "vocabulary"
CLAIMS_DIR = BASE_DIR / "claims"
MAPS_DIR = BASE_DIR / "maps"
RULES_DIR = BASE_DIR / "rules"
REGISTRY_DIR = BASE_DIR / "registry"
DIAGNOSTICS_DIR = BASE_DIR / "diagnostics"

def main():
    start_time = time.time()
    print("=======================================")
    print("  Drug Intelligence Cloud Build Engine ")
    print("=======================================\n")
    
    print("[1/6] Running Validators...")
    is_valid, validation_report = run_validation(KNOWLEDGE_DIR, EVIDENCE_DIR)
    write_diagnostics("validation_report.json", validation_report, DIAGNOSTICS_DIR)
    
    if not is_valid:
        print("\n[FAILED] Validation failed. Build aborted. See diagnostics/validation_report.json")
        sys.exit(1)
        
    print("[2/6] Compiling Knowledge, Evidence, and Graph Packages...")
    knowledge_objects = compile_knowledge(KNOWLEDGE_DIR)
    evidence_objects = compile_evidence(EVIDENCE_DIR)
    vocab_objects = compile_vocabulary(VOCAB_DIR)
    claim_objects = compile_claims(CLAIMS_DIR)
    mapping_objects = compile_mappings(MAPS_DIR)
    
    print("[3/6] Building Base Registry...")
    stats = build_indexes(knowledge_objects, evidence_objects, vocab_objects, claim_objects, mapping_objects, REGISTRY_DIR)
    
    print("[4/6] Compiling CCL Rules (IR -> AST)...")
    compiled_rules = compile_ccl(RULES_DIR, REGISTRY_DIR)
    stats["rules"] = len(compiled_rules)
    
    print("[5/6] Generating Deterministic Hash...")
    build_hash = generate_build_hash(KNOWLEDGE_DIR, EVIDENCE_DIR, VOCAB_DIR, CLAIMS_DIR, MAPS_DIR, KNOWLEDGE_SPEC["schema_version"])
    
    print("[6/6] Generating Manifest...")
    manifest = generate_manifest(build_hash, stats, KNOWLEDGE_SPEC["schema_version"], REGISTRY_DIR)
    
    build_duration = time.time() - start_time
    build_report = {
        "status": "SUCCESS",
        "duration_seconds": round(build_duration, 4),
        "build_hash": build_hash,
        "manifest": manifest
    }
    write_diagnostics("build_report.json", build_report, DIAGNOSTICS_DIR)
    
    print("\n=======================================")
    print("            Build Successful           ")
    print("=======================================")
    print(f" Build ID   : {manifest['build_id']}")
    print(f" Hash       : {build_hash}")
    print(f" Drugs      : {stats['canonicals']}")
    print(f" Evidence   : {stats['evidence']}")
    print(f" Claims     : {stats['claims']}")
    print(f" Vocabulary : {stats['vocabulary']}")
    print(f" Duration   : {round(build_duration, 2)}s")
    print("=======================================")

if __name__ == "__main__":
    main()
