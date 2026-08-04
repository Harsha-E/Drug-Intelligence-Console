import os
import json
import logging
from typing import Dict, Any

import threading

logger = logging.getLogger(__name__)

class RegistryRuntime:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RegistryRuntime, cls).__new__(cls)
            cls._instance._cache = {}
            cls._instance._is_loaded = False
            cls._instance.history = []
            cls._instance.traces = {}
            cls._instance.knowledge_graph = None
            cls._instance.max_capacity = 1000
            cls._instance._lock = threading.Lock()
        return cls._instance

    def load(self, registry_dir: str = None):
        self._cache = {}
        base_backend = os.path.dirname(os.path.dirname(__file__))
        root_dir = os.path.dirname(base_backend)
        
        backend_current_dir = os.path.join(base_backend, "registry", "current")
        backend_rules_dir = os.path.join(base_backend, "registry", "rules")
        backend_index_dir = os.path.join(base_backend, "registry")
        root_current_dir = os.path.join(root_dir, "registry", "current")
        
        search_dirs = [
            backend_current_dir,
            registry_dir if registry_dir and os.path.exists(registry_dir) else None,
            root_current_dir,
            backend_rules_dir,
            backend_index_dir
        ]
        
        for sdir in search_dirs:
            if not sdir or not os.path.exists(sdir):
                continue
            for filename in os.listdir(sdir):
                if filename.endswith('.json'):
                    key = filename[:-5]
                    filepath = os.path.join(sdir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if data or key not in self._cache:
                                self._cache[key] = data
                    except Exception as e:
                        logger.error(f"Failed to load registry file {filename}: {e}")
        
        # Sync non-empty registries to root registry/current so files on disk are never empty
        try:
            os.makedirs(root_current_dir, exist_ok=True)
            for k, v in self._cache.items():
                if v and isinstance(v, (dict, list)):
                    dest_file = os.path.join(root_current_dir, f"{k}.json")
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        json.dump(v, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not mirror registries to root directory: {e}")
            
        # Ensure canonical key aliases are set in cache
        if "drug_lookup" in self._cache:
            self._cache["knowledge"] = self._cache["drug_lookup"]
            self._cache["drugs"] = self._cache["drug_lookup"]
        if "vocabulary_index" in self._cache and "vocabulary" not in self._cache:
            self._cache["vocabulary"] = self._cache["vocabulary_index"]
        if "mapping_index" in self._cache and "mappings" not in self._cache:
            self._cache["mappings"] = self._cache["mapping_index"]
            
        self._is_loaded = True
        logger.info(f"Loaded {len(self._cache)} registries.")
        
        try:
            from backend.core.intelligence.knowledge_graph import CompiledKnowledgeGraph
            kg_dir = backend_current_dir if os.path.exists(backend_current_dir) else registry_dir
            self.knowledge_graph = CompiledKnowledgeGraph.build_from_registry(kg_dir)
            logger.info(f"Compiled Knowledge Graph built with {len(self.knowledge_graph.nodes)} nodes.")
        except Exception as e:
            logger.error(f"Failed to build Knowledge Graph: {e}")
            self.knowledge_graph = None

        # Load historical execution traces from execution_history.jsonl
        try:
            hist_file = os.path.join(base_backend, "execution_history.jsonl")
            if os.path.exists(hist_file):
                with open(hist_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            record = json.loads(line)
                            exec_id = record.get("analysis_id") or record.get("execution_id") or record.get("id")
                            if exec_id:
                                self.traces[exec_id] = record
                                hist_item = {
                                    "analysis_id": exec_id,
                                    "request_timestamp": record.get("request_timestamp") or (record.get("timestamp", 0) * 1000),
                                    "status": record.get("status", "COMPLETED"),
                                    "total_latency_ms": record.get("total_latency_ms", 0),
                                    "patient_summary": record.get("patient_summary") or {"patient_id": record.get("patient_id", "Unknown")},
                                    "medications": record.get("medications", []),
                                    "events": record.get("events", []),
                                    "graph": record.get("graph", {}),
                                    "clinical_decision": record.get("clinical_decision", record.get("report", {}).get("alerts", []))
                                }
                                self.history.append(hist_item)
                        except Exception:
                            continue
                logger.info(f"Loaded {len(self.history)} historical executions from disk.")
        except Exception as e:
            logger.error(f"Failed to load execution_history.jsonl: {e}")

    def get_registry(self, name: str) -> Dict[str, Any]:
        if name in ("knowledge", "drugs", "drug_lookup"):
            return self._cache.get("drug_lookup", {})
        if name in ("rules",):
            return self._cache.get("rules", {})
        if name in ("claims",):
            return self._cache.get("claims", {})
        if name in ("evidence",):
            return self._cache.get("evidence", {})
        if name in ("vocabulary", "vocabulary_index"):
            return self._cache.get("vocabulary", self._cache.get("vocabulary_index", {}))
        if name in ("mappings", "mapping_index"):
            return self._cache.get("mappings", self._cache.get("mapping_index", {}))
        if name in ("manifest",):
            return self._cache.get("manifest", {})
        return self._cache.get(name, {})

    def sync_registry(self) -> Dict[str, int]:
        with self._lock:
            self.load()
            return self.get_registry_sizes()

    def get_registry_hashes(self) -> Dict[str, str]:
        import hashlib
        hashes = {}
        target_keys = ["manifest", "rules", "drug_lookup", "claims", "evidence", "vocabulary_index"]
        for key in target_keys:
            data = self._cache.get(key, {})
            data_str = json.dumps(data, sort_keys=True)
            h = hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:12]
            name_map = {
                "manifest": "manifest_hash",
                "rules": "rules_hash",
                "drug_lookup": "knowledge_hash",
                "claims": "claims_hash",
                "evidence": "evidence_hash",
                "vocabulary_index": "vocabulary_hash"
            }
            hashes[name_map[key]] = h
        return hashes

    def get_registry_sizes(self) -> Dict[str, int]:
        sizes = {}
        for k, v in self._cache.items():
            if k in ("knowledge", "drugs", "vocabulary_index", "mapping_index"):
                continue
            if isinstance(v, list):
                sizes[f"{k}_count"] = len(v)
            elif isinstance(v, dict):
                sizes[f"{k}_count"] = len(v.keys())
            else:
                sizes[f"{k}_count"] = 1
        return sizes

    def add_history(self, record: Dict[str, Any]):
        with self._lock:
            if len(self.history) >= self.max_capacity:
                self.history.pop(0)
            self.history.append(record)

    def get_history(self) -> list:
        with self._lock:
            return list(self.history)
        
    def add_trace(self, trace_id: str, trace: Dict[str, Any]):
        with self._lock:
            if len(self.traces) >= self.max_capacity:
                oldest_key = next(iter(self.traces))
                del self.traces[oldest_key]
            self.traces[trace_id] = trace
            # Append to execution_history.jsonl for persistent replay
            try:
                base_backend = os.path.dirname(os.path.dirname(__file__))
                hist_file = os.path.join(base_backend, "execution_history.jsonl")
                with open(hist_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(trace) + "\n")
            except Exception as e:
                logger.error(f"Failed to append to execution_history.jsonl: {e}")
        
    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        with self._lock:
            return self.traces.get(trace_id)

    def delete_trace(self, trace_id: str) -> bool:
        with self._lock:
            removed = False
            if trace_id in self.traces:
                del self.traces[trace_id]
                removed = True
            self.history = [h for h in self.history if h.get("analysis_id") != trace_id and h.get("id") != trace_id]
            try:
                base_backend = os.path.dirname(os.path.dirname(__file__))
                hist_file = os.path.join(base_backend, "execution_history.jsonl")
                if os.path.exists(hist_file):
                    new_lines = []
                    with open(hist_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                eid = obj.get("analysis_id") or obj.get("execution_id") or obj.get("id")
                                if eid != trace_id:
                                    new_lines.append(line)
                            except Exception:
                                new_lines.append(line)
                    with open(hist_file, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
            except Exception as e:
                logger.error(f"Failed to rewrite execution_history.jsonl after delete: {e}")
            return removed

runtime = RegistryRuntime()
