import json
import os
import sys
from pathlib import Path

# Add the compiler directory to the path so we can import the spec
sys.path.insert(0, str(Path(__file__).resolve().parent))
from spec.knowledge_spec import KNOWLEDGE_SPEC

def load_evidence_ids(evidence_dir):
    evidence_ids = set()
    for root, _, files in os.walk(evidence_dir):
        for file in files:
            if file.endswith('.json'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "evidence_id" in data:
                            evidence_ids.add(data["evidence_id"])
                except Exception as e:
                    print(f"[Warning] Failed to read evidence {path}: {e}")
    return evidence_ids

def run_pass_1_syntax(path):
    """Pass 1: Syntax (Valid JSON)"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return True, data, []
    except json.JSONDecodeError as e:
        return False, None, [f"Syntax Error: {str(e)}"]

def run_pass_2_schema(data):
    """Pass 2: Schema (Fields exist and are typed correctly)"""
    errors = []
    meta = data.get("metadata", {})
    if meta.get("schema_version") != KNOWLEDGE_SPEC["schema_version"]:
        errors.append(f"Invalid schema_version. Expected {KNOWLEDGE_SPEC['schema_version']}")
    
    if data.get("entity_type") != KNOWLEDGE_SPEC["required_entity_type"]:
        errors.append(f"Invalid entity_type. Expected {KNOWLEDGE_SPEC['required_entity_type']}")
        
    identity = data.get("identity", {})
    for req in KNOWLEDGE_SPEC["identity"]["required"]:
        if req not in identity:
            errors.append(f"Missing required identity field: {req}")
            
    return len(errors) == 0, errors

def run_pass_3_semantic(data):
    """Pass 3: Semantic (Values are clinically sound)"""
    errors = []
    ck = data.get("clinical_knowledge", {})
    
    for req in KNOWLEDGE_SPEC["clinical_knowledge"]["required"]:
        if req not in ck:
            errors.append(f"Missing required clinical_knowledge field: {req}")

    for pd in ck.get("pharmacodynamic_effects", []):
        if pd.get("direction") not in KNOWLEDGE_SPEC["pharmacodynamic_effects"]["allowed_directions"]:
            errors.append(f"Invalid direction '{pd.get('direction')}'.")
        if pd.get("magnitude") not in KNOWLEDGE_SPEC["pharmacodynamic_effects"]["allowed_magnitudes"]:
            errors.append(f"Invalid magnitude '{pd.get('magnitude')}'.")
            
    for ci in ck.get("contraindications", []):
        if ci.get("severity") not in KNOWLEDGE_SPEC["contraindications"]["allowed_severities"]:
            errors.append(f"Invalid contraindication severity '{ci.get('severity')}'.")
            
    return len(errors) == 0, errors

def run_pass_4_referential(data, evidence_ids):
    """Pass 4: Referential Integrity (No dangling evidence_refs)"""
    errors = []
    refs = data.get("evidence_refs", [])
    for ref in refs:
        if ref not in evidence_ids:
            errors.append(f"Dangling root evidence_ref: {ref}")
            
    ck = data.get("clinical_knowledge", {})
    for ci in ck.get("contraindications", []):
        for ref in ci.get("evidence_refs", []):
            if ref not in evidence_ids:
                errors.append(f"Dangling evidence_ref in contraindication: {ref}")
                
    return len(errors) == 0, errors

def run_pass_5_quality(data):
    """Pass 5: Knowledge Quality"""
    warnings = []
    if not data.get("ingredients"):
        warnings.append("Quality Warning: Drug has no ingredients defined.")
    if not data.get("clinical_knowledge", {}).get("classifications"):
        warnings.append("Quality Warning: Drug has no classifications.")
    return warnings

def run_validation(knowledge_dir, evidence_dir):
    evidence_ids = load_evidence_ids(evidence_dir)
    
    report = {
        "total_packages": 0,
        "failed_packages": 0,
        "errors": {},
        "warnings": {}
    }
    
    for root, _, files in os.walk(knowledge_dir):
        for file in files:
            if file == "knowledge.json":
                report["total_packages"] += 1
                path = os.path.join(root, file)
                rel_path = str(Path(path).relative_to(Path(knowledge_dir).parent.parent))
                
                success, data, errs = run_pass_1_syntax(path)
                if not success:
                    report["errors"][rel_path] = errs
                    report["failed_packages"] += 1
                    continue
                    
                package_errors = []
                package_warnings = []
                
                _, errs = run_pass_2_schema(data)
                package_errors.extend(errs)
                
                _, errs = run_pass_3_semantic(data)
                package_errors.extend(errs)
                
                _, errs = run_pass_4_referential(data, evidence_ids)
                package_errors.extend(errs)
                
                warns = run_pass_5_quality(data)
                package_warnings.extend(warns)
                
                if package_errors:
                    report["errors"][rel_path] = package_errors
                    report["failed_packages"] += 1
                if package_warnings:
                    report["warnings"][rel_path] = package_warnings

    is_valid = report["failed_packages"] == 0
    return is_valid, report

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    KNOWLEDGE_DIR = BASE_DIR / "knowledge" / "drugs"
    EVIDENCE_DIR = BASE_DIR / "evidence"
    is_valid, report = run_validation(KNOWLEDGE_DIR, EVIDENCE_DIR)
    print(json.dumps(report, indent=2))
    if not is_valid:
        sys.exit(1)
