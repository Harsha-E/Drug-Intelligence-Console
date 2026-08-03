import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
REGISTRY_DIR = BASE_DIR / "registry"
CURRENT_DIR = REGISTRY_DIR / "current"

def publish_registry():
    print("Starting Registry Publisher...")
    
    if not CURRENT_DIR.exists():
        print("[FAILED] No compiled registry found in registry/current. Run compile.py first.")
        return
        
    manifest_path = CURRENT_DIR / "manifest.json"
    if not manifest_path.exists():
        print("[FAILED] No manifest.json found in current registry.")
        return
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    version = manifest.get("version", "unknown")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    versioned_dir_name = f"v{version}_{timestamp}"
    versioned_dir = REGISTRY_DIR / versioned_dir_name
    
    print(f"Publishing registry version {version} to {versioned_dir_name}...")
    
    # Copy current to versioned dir
    shutil.copytree(CURRENT_DIR, versioned_dir)
    
    print(f"\n[SUCCESS] Immutable registry published to: {versioned_dir}")

if __name__ == "__main__":
    publish_registry()
