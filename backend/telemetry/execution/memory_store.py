import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from .execution_store import ExecutionStoreInterface
from .execution_record import ExecutionRecord

class MemoryExecutionStore(ExecutionStoreInterface):
    def __init__(self, log_path: str = "execution_history.jsonl"):
        self.log_path = Path(log_path)
        self._cache: List[ExecutionRecord] = []
        self.listeners = []
        
        # Hydrate from disk if exists
        if self.log_path.exists():
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            self._cache.append(ExecutionRecord.from_dict(data))
                        except Exception:
                            pass
        
        # Keep only last 100 in memory
        self._cache = self._cache[-100:]

    def add_listener(self, queue):
        self.listeners.append(queue)

    def remove_listener(self, queue):
        if queue in self.listeners:
            self.listeners.remove(queue)

    def save(self, record: ExecutionRecord) -> None:
        # Check if updating an existing record (e.g. status changes)
        existing_idx = next((i for i, r in enumerate(self._cache) if r.analysis_id == record.analysis_id), None)
        if existing_idx is not None:
            self._cache[existing_idx] = record
        else:
            self._cache.append(record)
            
        self._cache = self._cache[-100:]
        
        # Append to jsonl (We just append all saves; a real DB would upsert)
        # For the hackathon, appending the final state is fine.
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record.to_dict()) + "\n")
            
        # Broadcast to listeners
        dict_record = record.to_dict()
        for q in self.listeners:
            try:
                q.put_nowait(dict_record)
            except Exception:
                pass

    def get(self, analysis_id: str) -> Optional[ExecutionRecord]:
        for r in self._cache:
            if r.analysis_id == analysis_id:
                return r
        return None

    def list(self) -> List[ExecutionRecord]:
        return list(reversed(self._cache))

    def latest(self, limit: int = 50) -> List[ExecutionRecord]:
        return list(reversed(self._cache))[:limit]

    def search(self, filters: Dict[str, Any]) -> List[ExecutionRecord]:
        results = []
        for r in self._cache:
            match = True
            for k, v in filters.items():
                if getattr(r, k, None) != v:
                    match = False
                    break
            if match:
                results.append(r)
        return list(reversed(results))

    def clear(self) -> None:
        self._cache = []
        if self.log_path.exists():
            self.log_path.unlink()
