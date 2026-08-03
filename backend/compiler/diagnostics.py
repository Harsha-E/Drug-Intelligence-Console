import json
import os
from pathlib import Path

def write_diagnostics(report_name, data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    path = Path(output_dir) / report_name
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return path
