from datetime import datetime
from typing import List, Dict, Any, Optional

class ExecutionRecord:
    def __init__(self, analysis_id: str, patient_summary: Dict[str, Any]):
        self.analysis_id = analysis_id
        self.request_timestamp = datetime.utcnow().isoformat() + "Z"
        self.completion_timestamp = None
        self.status = "PENDING"
        self.patient_summary = patient_summary
        self.idempotency_key = ""
        
        # Versions
        self.versions = {
            "runtime": "1.0.0",
            "registry": "Unknown",
            "knowledge": "Unknown",
            "claim": "Unknown",
            "evidence": "Unknown",
            "rule": "Unknown",
            "build_hash": "Unknown"
        }
        
        self.total_latency_ms = 0
        
        # Event Timeline
        self.events: List[Dict[str, str]] = []
        
        # Clinical Reasoning Graph
        self.graph = {
            "nodes": [],
            "edges": []
        }
        
        self.report = {
            "alerts": []
        }

    def add_event(self, event_name: str, details: str = ""):
        self.events.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event_name,
            "details": details
        })

    def add_node(self, node_id: str, label: str, node_type: str, metadata: Dict[str, Any] = None):
        if not any(n["id"] == node_id for n in self.graph["nodes"]):
            self.graph["nodes"].append({
                "id": node_id,
                "label": label,
                "type": node_type,
                "metadata": metadata or {}
            })

    def add_edge(self, source_id: str, target_id: str, relation: str = ""):
        edge_id = f"{source_id}->{target_id}"
        if not any(e["id"] == edge_id for e in self.graph["edges"]):
            self.graph["edges"].append({
                "id": edge_id,
                "source": source_id,
                "target": target_id,
                "relation": relation
            })

    def complete(self, status: str = "COMPLETED"):
        self.status = status
        self.completion_timestamp = datetime.utcnow().isoformat() + "Z"
        
        start = datetime.fromisoformat(self.request_timestamp.replace('Z', '+00:00'))
        end = datetime.fromisoformat(self.completion_timestamp.replace('Z', '+00:00'))
        self.total_latency_ms = int((end - start).total_seconds() * 1000)
        
        self.add_event(f"Execution {status}", f"Latency: {self.total_latency_ms}ms")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "idempotency_key": self.idempotency_key,
            "request_timestamp": self.request_timestamp,
            "completion_timestamp": self.completion_timestamp,
            "status": self.status,
            "patient_summary": self.patient_summary,
            "versions": self.versions,
            "total_latency_ms": self.total_latency_ms,
            "events": self.events,
            "graph": self.graph,
            "report": self.report
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionRecord':
        record = cls(data["analysis_id"], data["patient_summary"])
        record.request_timestamp = data["request_timestamp"]
        record.completion_timestamp = data.get("completion_timestamp")
        record.status = data.get("status", "PENDING")
        record.versions = data.get("versions", record.versions)
        record.total_latency_ms = data.get("total_latency_ms", 0)
        record.events = data.get("events", [])
        record.graph = data.get("graph", {"nodes": [], "edges": []})
        record.report = data.get("report", {"alerts": []})
        return record
