import time
import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel

from backend.core.execution import ledger, ExecutionRecord, ClinicalKnowledgeNode, ClinicalKnowledgeEdge

class TelemetryEvent(BaseModel):
    execution_id: str
    event_type: str
    stage: str
    timestamp: float
    elapsed_ms: float
    payload_version: str = "1.0"
    payload: Dict[str, Any]

class TelemetryCollector:
    def __init__(self):
        self.subscribers = []
        
    def subscribe(self, queue: asyncio.Queue):
        self.subscribers.append(queue)
        
    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.subscribers:
            self.subscribers.remove(queue)
            
    async def publish(self, event: TelemetryEvent):
        for queue in self.subscribers:
            await queue.put(event)

# Global singleton
telemetry = TelemetryCollector()

def emit_event(execution: ExecutionRecord, event_type: str, stage: str, payload: Dict[str, Any]):
    """Helper to emit events both to the execution record and to real-time subscribers"""
    now = time.time()
    elapsed = (now - execution.timestamp) * 1000
    
    event = TelemetryEvent(
        execution_id=execution.execution_id,
        event_type=event_type,
        stage=stage,
        timestamp=now,
        elapsed_ms=elapsed,
        payload=payload
    )
    
    # Store in immutable ledger
    execution.events.append(event.model_dump())
    
    # Fire and forget publishing
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(telemetry.publish(event))
    except RuntimeError:
        pass # Not in an async loop context

def add_graph_node(execution: ExecutionRecord, node_id: str, type: str, label: str, properties: Dict[str, Any] = None):
    node = ClinicalKnowledgeNode(id=node_id, type=type, label=label, properties=properties or {})
    execution.add_node(node)
    emit_event(execution, "GRAPH_NODE_ADDED", "GRAPH_BUILDER", {"node": node.model_dump()})

def add_graph_edge(execution: ExecutionRecord, source: str, target: str, rel: str, properties: Dict[str, Any] = None):
    edge = ClinicalKnowledgeEdge(source=source, target=target, relationship=rel, properties=properties or {})
    execution.add_edge(edge)
    emit_event(execution, "GRAPH_EDGE_ADDED", "GRAPH_BUILDER", {"edge": edge.model_dump()})
