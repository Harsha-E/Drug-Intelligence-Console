import pytest
from backend.core.runtime import RegistryRuntime

def test_runtime_capacity_limits():
    rt = RegistryRuntime()
    rt.max_capacity = 10
    for i in range(25):
        rt.add_history({"item": i})
        rt.add_trace(f"trace_{i}", {"trace": i})
        
    assert len(rt.get_history()) <= 10, f"History size {len(rt.get_history())} exceeded capacity 10!"
    assert len(rt.traces) <= 10, f"Traces dict size {len(rt.traces)} exceeded capacity 10!"
