import time
import asyncio
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from backend.core.execution import ledger, ExecutionRecord, ClinicalKnowledgeNode, ClinicalKnowledgeEdge

import uuid

class TelemetryEvent(BaseModel):
    event_id: str
    execution_id: str
    stage: str
    event: str # START, COMPLETE, GRAPH_NODE_ADDED, GRAPH_EDGE_ADDED, ERROR
    timestamp: float
    duration_ms: float
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    graph_changes: Dict[str, Any] = Field(default_factory=dict)
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

class TelemetryCollector:
    def __init__(self):
        self.subscribers = []
        self.main_loop = None
        
    def subscribe(self, queue: asyncio.Queue):
        if self.main_loop is None:
            try:
                self.main_loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
        self.subscribers.append(queue)
        
    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.subscribers:
            self.subscribers.remove(queue)
            
    async def publish(self, event: TelemetryEvent):
        for queue in self.subscribers:
            await queue.put(event)

# Global singleton
telemetry = TelemetryCollector()

def emit_event(execution: ExecutionRecord, event_type: str, stage: str, payload: Dict[str, Any] = None, inputs: Dict[str, Any] = None, outputs: Dict[str, Any] = None, graph_changes: Dict[str, Any] = None):
    """Emits structured telemetry event complying with the frozen contract"""
    now = time.time()
    elapsed = (now - execution.timestamp) * 1000
    
    event_obj = TelemetryEvent(
        event_id=f"evt_{str(uuid.uuid4())[:8]}",
        execution_id=execution.execution_id,
        stage=stage,
        event=event_type,
        timestamp=now,
        duration_ms=round(elapsed, 2),
        inputs=inputs or payload or {},
        outputs=outputs or {},
        graph_changes=graph_changes or {},
        memory_mb=0.0,
        cpu_percent=0.0,
        warnings=[],
        errors=[payload.get("message")] if payload and "message" in payload and event_type == "ERROR" else []
    )
    
    # Store in immutable ledger
    execution.events.append(event_obj.model_dump())
    
    # Fire and forget publishing to SSE listeners
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(telemetry.publish(event_obj))
    except RuntimeError:
        # We are in a worker thread. We must use call_soon_threadsafe for each subscriber queue.
        if telemetry.main_loop:
            for queue in telemetry.subscribers:
                telemetry.main_loop.call_soon_threadsafe(queue.put_nowait, event_obj)

def add_graph_node(execution: ExecutionRecord, node_id: str, type: str, label: str, properties: Dict[str, Any] = None):
    node = ClinicalKnowledgeNode(id=node_id, type=type, label=label, properties=properties or {})
    execution.add_node(node)
    emit_event(
        execution, 
        event_type="GRAPH_NODE_ADDED", 
        stage="GRAPH_BUILDER", 
        graph_changes={"node": node.model_dump()}
    )

def add_graph_edge(execution: ExecutionRecord, source: str, target: str, rel: str, properties: Dict[str, Any] = None):
    edge = ClinicalKnowledgeEdge(source=source, target=target, relationship=rel, properties=properties or {})
    execution.add_edge(edge)
    emit_event(
        execution, 
        event_type="GRAPH_EDGE_ADDED", 
        stage="GRAPH_BUILDER", 
        graph_changes={"edge": edge.model_dump()}
    )
