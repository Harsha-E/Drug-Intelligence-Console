import pytest
from backend.core.execution import ExecutionRecord, ClinicalKnowledgeEdge, ExecutionLedger

def test_add_edge_uniqueness():
    record = ExecutionRecord(execution_id="test_1", timestamp=100.0, request_data={})
    edge1 = ClinicalKnowledgeEdge(source="A", target="B", relationship="INHIBITS")
    edge2 = ClinicalKnowledgeEdge(source="A", target="B", relationship="INHIBITS")
    
    record.add_edge(edge1)
    record.add_edge(edge2)
    
    assert len(record.knowledge_graph.edges) == 1, "Duplicate edge was added to knowledge_graph!"

def test_ledger_capacity_limit():
    ledger = ExecutionLedger(max_capacity=5)
    for i in range(10):
        ledger.create({"req": i})
        
    assert len(ledger.get_all()) == 5, f"Ledger size is {len(ledger.get_all())}, expected bounded limit of 5"
