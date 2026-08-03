import pytest
from backend.core.execution import ExecutionRecord
from backend.core.intelligence.ReasoningEngine import ReasoningEngine

def test_engine_exception_handling():
    engine = ReasoningEngine()
    record = ExecutionRecord(execution_id="fail_test", timestamp=100.0, request_data={})
    
    # Pass invalid/corrupted graph that causes an unexpected AttributeError/TypeError
    engine.check_interactions(record, ["DRUG_1"], None, graph="corrupted_graph_object")
    
    assert record.status == "FAILED", f"Record status is {record.status}, expected FAILED on exception"
    assert any(e.get("event") == "ERROR" for e in record.events), "No ERROR event emitted on exception!"
