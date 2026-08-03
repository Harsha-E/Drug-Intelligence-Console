import json
import os
from pathlib import Path
from datetime import datetime, timezone
import uuid

def generate_manifest(build_hash, stats, schema_version, output_dir):
    manifest = {
        "build_id": str(uuid.uuid4()),
        "build_hash": build_hash,
        "build_timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "compiler_version": "1.0",
        "schema_version": schema_version,
        "knowledge_version": "1.0",
        "evidence_version": "1.0",
        "rule_version": "pending_phase_4",
        "statistics": {
            "total_drugs": stats.get("canonicals", 0),
            "total_evidence_objects": stats.get("evidence", 0)
        }
    }
    
    os.makedirs(output_dir, exist_ok=True)
    with open(Path(output_dir) / "manifest.json", 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        
    return manifest
