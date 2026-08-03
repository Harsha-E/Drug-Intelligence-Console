import json
import os
import uuid
from datetime import datetime
from pathlib import Path

class ExecutionStore:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.log_file = self.storage_dir / "execution_history.jsonl"
        self._memory_cache = []
        
        # Ensure dir exists
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Hydrate memory cache from disk
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            self._memory_cache.append(json.loads(line))
                        except Exception:
                            pass
                            
        # Keep only latest 100 in memory
        self._memory_cache = self._memory_cache[-100:]

    def record_execution(self, analysis_id, patient_id, latency_ms, status, context, graph, recommendations, versions):
        record = {
            "analysis_id": analysis_id,
            "patient_id": patient_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "latency_ms": latency_ms,
            "status": status,
            "context": context,
            "graph": graph,
            "recommendations": recommendations,
            "versions": versions
        }
        
        self._memory_cache.append(record)
        self._memory_cache = self._memory_cache[-100:]
        
        # Append to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + "\n")
            
        return record

    def get_history(self):
        return list(reversed(self._memory_cache))
        
    def get_execution(self, analysis_id):
        for r in self._memory_cache:
            if r["analysis_id"] == analysis_id:
                return r
        return None
