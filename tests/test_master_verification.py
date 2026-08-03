import sys
from fastapi.testclient import TestClient
from backend.main import app

def run_all_checks():
    print("=" * 60)
    print("RUNNING MASTER DIRECTIVE SYSTEM VALIDATION (IN-PROCESS)")
    print("=" * 60)

    results = {}

    with TestClient(app) as client:
        # 1. Health
        try:
            resp = client.get("/health")
            print(f"[PASS] GET /health -> {resp.status_code} : {resp.json()}")
            results["Health Check"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] GET /health -> {e}")
            results["Health Check"] = "FAIL"

        # 2. Ready
        try:
            resp = client.get("/ready")
            print(f"[PASS] GET /ready -> {resp.status_code} : {resp.json()}")
            results["Registry Bootstrap"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] GET /ready -> {e}")
            results["Registry Bootstrap"] = "FAIL"

        # 3. Metrics
        try:
            resp = client.get("/metrics")
            body = resp.json()
            print(f"[PASS] GET /metrics -> total_drugs={body.get('total_drugs')}, total_claims={body.get('total_claims')}, total_evidence={body.get('total_evidence')}, total_rules={body.get('total_rules')}")
            results["Metrics Endpoint"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] GET /metrics -> {e}")
            results["Metrics Endpoint"] = "FAIL"

        # 4. Version
        try:
            resp = client.get("/version")
            print(f"[PASS] GET /version -> {resp.status_code} : {resp.json()}")
            results["Version Check"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] GET /version -> {e}")
            results["Version Check"] = "FAIL"

        # 5. Registry Stats
        try:
            resp = client.get("/api/v1/registry/stats")
            body = resp.json()
            print(f"[PASS] GET /api/v1/registry/stats -> medicines={body['metrics']['medicines']}, claims={body['metrics']['claims']}")
            results["Registry Stats"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] GET /api/v1/registry/stats -> {e}")
            results["Registry Stats"] = "FAIL"

        # 6. Registry Knowledge & Drugs
        try:
            resp = client.get("/api/v1/registry/knowledge")
            body = resp.json()
            print(f"[PASS] GET /api/v1/registry/knowledge -> {len(body)} entries loaded")
            results["Registry APIs"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] GET /api/v1/registry/knowledge -> {e}")
            results["Registry APIs"] = "FAIL"

        # 7. Drug Search
        try:
            resp = client.get("/api/v1/drugs/search?q=atorvastatin")
            body = resp.json()
            print(f"[PASS] GET /api/v1/drugs/search?q=atorvastatin -> {len(body['results'])} matching drugs found")
            results["Search"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] GET /api/v1/drugs/search?q=atorvastatin -> {e}")
            results["Search"] = "FAIL"

        # 8. Analyze Pipeline
        try:
            payload = {
                "medications": [
                    {"id": "DIC_DRUG_920EDDE5", "name": "Atorvastatin", "strength": 20.0, "unit": "mg"},
                    {"id": "DIC_DRUG_41FF21E8", "name": "Warfarin", "strength": 5.0, "unit": "mg"}
                ],
                "patient": {
                    "age": 62,
                    "sex": "MALE",
                    "active_conditions": ["HYPERTENSION"],
                    "renal_clearance": "NORMAL"
                }
            }
            resp = client.post("/api/v1/analyze", json=payload)
            body = resp.json()
            print(f"[PASS] POST /api/v1/analyze -> {resp.status_code} : execution_id={body['execution_id']}, status={body['clinical_report']['status']}")
            results["Analyze Pipeline"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] POST /api/v1/analyze -> {e}")
            results["Analyze Pipeline"] = "FAIL"

        # 9. Interactions
        try:
            payload = {"medication_ids": ["DIC_DRUG_920EDDE5", "DIC_DRUG_41FF21E8"]}
            resp = client.post("/api/v1/interactions", json=payload)
            body = resp.json()
            print(f"[PASS] POST /api/v1/interactions -> {resp.status_code} : {len(body['interactions'])} interactions")
            results["Interactions"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] POST /api/v1/interactions -> {e}")
            results["Interactions"] = "FAIL"

        # 10. History
        try:
            resp = client.get("/api/v1/history")
            body = resp.json()
            print(f"[PASS] GET /api/v1/history -> {len(body)} records")
            results["History"] = "PASS" if resp.status_code == 200 else "FAIL"
        except Exception as e:
            print(f"[FAIL] GET /api/v1/history -> {e}")
            results["History"] = "FAIL"

    print("\n" + "=" * 60)
    print("SUMMARY VERIFICATION MATRIX")
    print("=" * 60)
    for comp, outcome in results.items():
        print(f"| {comp:<25} | {outcome:<10} |")
    print("=" * 60)

    if any(v == "FAIL" for v in results.values()):
        sys.exit(1)

if __name__ == "__main__":
    run_all_checks()
