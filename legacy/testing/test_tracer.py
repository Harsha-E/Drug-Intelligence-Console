from fastapi.testclient import TestClient
import sys
import os

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app
import json

client = TestClient(app)

def test_clinical_workflow():
    payload = {
        "patient_state": {
            "age": 65,
            "diseases": ["Hypertension"]
        },
        "interventions": ["Warfarin", "Aspirin"]
    }
    
    response = client.post("/api/v1/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all 5 Outputs exist
    print("\n--- The 5 Required Outputs ---\n")
    print(f"1. Clinical Report:\n{json.dumps(data['report'], indent=2)}")
    print(f"\n2. Reasoning Trace:\n{json.dumps(data['reasoning_trace'], indent=2)}")
    print(f"\n3. Evidence Trace:\n{json.dumps(data['evidence_trace'], indent=2)}")
    print(f"\n4. Audit Trace:\n{json.dumps(data['audit'], indent=2)}")
    print(f"\n5. Analytics Events:\n{json.dumps(data['analytics_events'], indent=2)}")
    print("\n------------------------------\n")
    
    assert data["report"]["severity"] == "HIGH"
    assert "Warfarin" in data["report"]["warnings"][0]
    assert "IdentityAgent" in data["audit"]["agents_executed"]
    assert "CCLParser" in data["audit"]["agents_executed"]
    
if __name__ == "__main__":
    test_clinical_workflow()
    print("✅ Tracer Bullet End-to-End Workflow Passed!")
