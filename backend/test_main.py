import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.runtime import runtime

# Setup real registry for tests
@pytest.fixture(scope="module", autouse=True)
def load_real_registry():
    registry_path = os.getenv("REGISTRY_DIR", os.path.join(os.path.dirname(__file__), "registry", "current"))
    # Fail if registry is not found, ensuring CI built it.
    assert os.path.exists(os.path.join(registry_path, "drug_lookup.json")), "Compiled registry not found!"
    runtime.load(registry_path)

client = TestClient(app)

def test_system_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_system_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert "registries" in response.json()
    sizes = response.json()["registries"]
    assert sizes.get("drug_lookup_count", 0) > 0

def test_system_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "uptime_seconds" in response.json()

def test_e2e_clinical_workflow():
    # 1. Search -> Drug Lookup
    search_res1 = client.get("/api/v1/drugs/search?q=atorvastatin")
    assert search_res1.status_code == 200
    drug1 = search_res1.json()["results"][0]["id"]
    
    search_res2 = client.get("/api/v1/drugs/search?q=cyclosporine")
    assert search_res2.status_code == 200
    drug2 = search_res2.json()["results"][0]["id"]
    
    # 2. Analyze -> Evidence Resolution -> API
    analyze_res = client.post("/api/v1/analyze", json={
        "medications": [
            {"id": drug1, "name": "Atorvastatin"},
            {"id": drug2, "name": "Cyclosporine"}
        ]
    })
    
    assert analyze_res.status_code == 200
    data = analyze_res.json()
    
    # 3. Audit
    assert "execution_id" in data
    
    # Check interaction output (PK_TRANSPORTER_INHIBITION)
    assert any(ev["type"] == "PK_TRANSPORTER_INHIBITION" for ev in data["evidence"])
