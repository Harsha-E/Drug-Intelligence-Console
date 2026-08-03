import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ClinicalKnowledgeNode(BaseModel):
    id: str
    type: str # Patient, Medication, Ingredient, Target, Enzyme, Pathway, Effect, Claim, Evidence, Rule, Decision
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class ClinicalKnowledgeEdge(BaseModel):
    source: str
    target: str
    relationship: str
    properties: Dict[str, Any] = Field(default_factory=dict)

class ClinicalKnowledgeGraph(BaseModel):
    nodes: List[ClinicalKnowledgeNode] = Field(default_factory=list)
    edges: List[ClinicalKnowledgeEdge] = Field(default_factory=list)

class ExecutionRecord(BaseModel):
    execution_id: str
    timestamp: float
    request_data: Dict[str, Any]
    
    # The clinical knowledge graph captures the full contextual web of reasoning
    knowledge_graph: ClinicalKnowledgeGraph = Field(default_factory=ClinicalKnowledgeGraph)
    
    # Event log tracks what happened when
    events: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Final outputs
    clinical_decision: Optional[Dict[str, Any]] = None
    status: str = "IN_PROGRESS" # IN_PROGRESS, COMPLETED, FAILED
    total_latency_ms: float = 0.0

    def add_node(self, node: ClinicalKnowledgeNode):
        # ensure unique
        if not any(n.id == node.id for n in self.knowledge_graph.nodes):
            self.knowledge_graph.nodes.append(node)

    def add_edge(self, edge: ClinicalKnowledgeEdge):
        self.knowledge_graph.edges.append(edge)

class ExecutionLedger:
    def __init__(self):
        self._records: Dict[str, ExecutionRecord] = {}
        
    def create(self, request_data: Dict[str, Any]) -> ExecutionRecord:
        exec_id = str(uuid.uuid4())
        record = ExecutionRecord(
            execution_id=exec_id,
            timestamp=time.time(),
            request_data=request_data
        )
        self._records[exec_id] = record
        return record
        
    def get(self, execution_id: str) -> Optional[ExecutionRecord]:
        return self._records.get(execution_id)
        
    def get_all(self) -> List[ExecutionRecord]:
        return list(self._records.values())

# Global singleton
ledger = ExecutionLedger()
