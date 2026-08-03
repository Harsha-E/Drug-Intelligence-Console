import os
import re

legacy_folders = [
    "agents", "analytics", "api", "audit", "claims", "contracts", "core", 
    "diagnostics", "docs", "evidence", "gateway", "governance", "infrastructure", 
    "knowledge", "mappings", "maps", "reasoning", "research", "rules", "semantic", 
    "testing", "vocabulary"
]

# We want to skip the legacy folders themselves and only check active folders
active_folders = ["backend", "frontend", "ingestion", "tests"]
root_files = ["Dockerfile", "docker-compose.yml", "README.md", "main.py", "server.js", "test_runtime.py"]

report = {folder: {"count": 0, "files": set()} for folder in legacy_folders}

def scan_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Regex to find references as words or paths (e.g. "core/", "from core", "/api/")
            for folder in legacy_folders:
                pattern = r'\b' + re.escape(folder) + r'\b'
                matches = len(re.findall(pattern, content, flags=re.IGNORECASE))
                if matches > 0:
                    report[folder]["count"] += matches
                    report[folder]["files"].add(filepath)
    except Exception as e:
        print(f"Failed reading {filepath}: {e}")

def walk_dir(directory):
    for root, _, files in os.walk(directory):
        # Skip pycache, venv, node_modules, and hidden
        if "__pycache__" in root or "/." in root.replace("\\", "/") or "\\." in root or "venv" in root or "node_modules" in root:
            continue
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.html', '.css', '.json', '.yml', '.yaml', '.md', '.txt')):
                scan_file(os.path.join(root, file))

for d in active_folders:
    walk_dir(d)

for f in root_files:
    if os.path.exists(f):
        scan_file(f)

# Write report to markdown
with open("reference_audit_report.md", "w") as f:
    f.write("# Legacy Folders Reference Audit\n\n")
    f.write("| Folder | Referenced? | Reference Count | Files Referencing It |\n")
    f.write("|--------|-------------|-----------------|----------------------|\n")
    for folder in legacy_folders:
        count = report[folder]["count"]
        referenced = "Yes" if count > 0 else "No"
        files = "<br>".join([os.path.relpath(p).replace("\\", "/") for p in report[folder]["files"]]) if count > 0 else "-"
        f.write(f"| {folder} | {referenced} | {count} | {files} |\n")
