import os
import json
import logging
from typing import Dict, Any

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
        return cls._instance

    def load(self, registry_dir: str):
        self._cache = {}
        if not os.path.exists(registry_dir):
            logger.warning(f"Registry directory not found: {registry_dir}")
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
        return self._cache.get(name, {})

    def get_registry_sizes(self) -> Dict[str, int]:
        sizes = {}
        for k, v in self._cache.items():
            if isinstance(v, list):
                sizes[f"{k}_count"] = len(v)
            elif isinstance(v, dict):
                sizes[f"{k}_count"] = len(v.keys())
            else:
                sizes[f"{k}_count"] = 1
        return sizes

    def add_history(self, record: Dict[str, Any]):
        self.history.append(record)

    def get_history(self) -> list:
        return self.history
        
    def add_trace(self, trace_id: str, trace: Dict[str, Any]):
        self.traces[trace_id] = trace
        
    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        return self.traces.get(trace_id)

runtime = RegistryRuntime()
