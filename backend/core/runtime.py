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
        if registry_dir is None:
            registry_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "registry", "current")
        
        # Check if registry directory exists and contains files
        needs_compile = False
        if not os.path.exists(registry_dir):
            needs_compile = True
        else:
            files = [f for f in os.listdir(registry_dir) if f.endswith('.json')]
            if not files or "drug_lookup.json" not in files:
                needs_compile = True
                
        if needs_compile:
            logger.info("Registry missing or incomplete. Triggering automatic compilation...")
            try:
                from ingestion.compile import build_registry
                build_registry()
            except Exception as e:
                logger.error(f"Automatic compilation failed: {e}")
                
        if not os.path.exists(registry_dir):
            logger.warning(f"Registry directory not found after compilation: {registry_dir}")
            return
            
        for filename in os.listdir(registry_dir):
            if filename.endswith('.json'):
                key = filename[:-5]
                filepath = os.path.join(registry_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self._cache[key] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load registry file {filename}: {e}")
        
        # Load rules if present in rules directory
        rules_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "registry", "rules", "rules.json")
        if os.path.exists(rules_file):
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    self._cache["rules"] = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load rules file: {e}")

        # Ensure canonical key aliases are set in cache
        if "drug_lookup" in self._cache:
            self._cache["knowledge"] = self._cache["drug_lookup"]
            self._cache["drugs"] = self._cache["drug_lookup"]
            
        self._is_loaded = True
        logger.info(f"Loaded {len(self._cache)} registries.")
        
        try:
            from backend.core.intelligence.knowledge_graph import CompiledKnowledgeGraph
            self.knowledge_graph = CompiledKnowledgeGraph.build_from_registry(registry_dir)
            logger.info(f"Compiled Knowledge Graph built with {len(self.knowledge_graph.nodes)} nodes.")
        except Exception as e:
            logger.error(f"Failed to build Knowledge Graph: {e}")
            self.knowledge_graph = None

    def get_registry(self, name: str) -> Dict[str, Any]:
        # Handle canonical aliases
        if name in ("knowledge", "drugs") and "drug_lookup" in self._cache:
            return self._cache["drug_lookup"]
        return self._cache.get(name, {})

    def get_registry_sizes(self) -> Dict[str, int]:
        sizes = {}
        for k, v in self._cache.items():
            if k in ("knowledge", "drugs"):
                continue # Skip alias duplicates in sizes dict
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
        
    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        with self._lock:
            return self.traces.get(trace_id)

runtime = RegistryRuntime()
