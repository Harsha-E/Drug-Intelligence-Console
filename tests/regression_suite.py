import os
import shutil
import time
import sys
root_dir = os.path.dirname(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient

from ingestion.identifier_service import IdentifierService
from ingestion.providers.openfda import OpenFDAProvider
from ingestion.providers.rxnorm import RxNormProvider
from ingestion.normalizer import Normalizer
from ingestion.review_queue import ReviewQueue
from ingestion.compiler import RegistryCompiler
from backend.core.runtime import runtime
from backend.main import app

def run_regression_suite():
    print("=========================================")
    print("CLINICAL REGRESSION SUITE")
    print("=========================================\n")
    
    review_queue_dir = os.path.join(backend_dir, "registry", "review_queue")
    accepted_dir = os.path.join(backend_dir, "registry", "accepted_knowledge")
    registry_dir = os.path.join(backend_dir, "registry", "current")
    
    # 0. Clean up previous state
    print("-> Cleaning up old state...")
    for d in [review_queue_dir, accepted_dir, registry_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)
        
    # 1. Ingestion Phase
    print("-> Running Ingestion Phase...")
    ident_svc = IdentifierService()
    providers = [OpenFDAProvider(), RxNormProvider()]
    
    normalizer = Normalizer(providers, ident_svc, review_queue_dir)
    normalizer.normalize_and_queue()
    
    # 2. Review Phase (Auto-Approve for test)
    print("-> Auto-approving review queue...")
    review = ReviewQueue(review_queue_dir, accepted_dir)
    review.approve_all()
    
    # 3. Compilation Phase
    print("-> Compiling Registry...")
    compiler = RegistryCompiler(accepted_dir, registry_dir)
    compiler.compile()
    
    # 4. Runtime Load
    print("-> Loading Runtime...")
    runtime.load(registry_dir)
    print(f"Graph loaded: {len(runtime.knowledge_graph.nodes)} nodes.")
    
    # 5. Run Scenarios
    print("\n-> Running Clinical Scenarios...\n")
    
    client = TestClient(app)
    
    def assert_interaction(res, expected_type, expected_effect, expected_severity=None):
        data = res.json()
        evidence_list = data.get("evidence", [])
        for interaction in evidence_list:
            if interaction["type"] == expected_type:
                if expected_effect in interaction.get("effect", "") or expected_effect in interaction.get("reason", ""):
                    if expected_severity:
                        if interaction.get("severity") == expected_severity or interaction.get("strength") == expected_severity:
                            return True
                    else:
                        return True
        print(f"FAILED TO FIND {expected_type} - {expected_effect} in: {evidence_list}")
        return False
        
    # Helper to find drug ID by name
    def get_drug_id(name):
        for n_id, node in runtime.knowledge_graph.nodes.items():
            if node.node_type == "Medication" and node.properties.get("canonical_name") == name:
                return n_id
        return ident_svc.get_or_create_id("drug", name)

    # SCENARIO 1: Pairwise Interaction (Transporter Overlap)
    print("Scenario 1: Atorvastatin + Cyclosporine (PK_TRANSPORTER_INHIBITION)")
    res1 = client.post("/api/v1/analyze", json={
        "medications": [
            {"id": get_drug_id("atorvastatin"), "name": "atorvastatin"},
            {"id": get_drug_id("cyclosporine"), "name": "cyclosporine"}
        ]
    })
    
    assert assert_interaction(res1, "PK_TRANSPORTER_INHIBITION", "Increased toxicity"), "Failed Scenario 1"
    print("  [PASS]")
    
    # SCENARIO 2: Patient Context - Pregnancy Contraindication
    print("Scenario 2: Methotrexate + Pregnant Patient (PATIENT_CONTRAINDICATION)")
    res2 = client.post("/api/v1/analyze", json={
        "medications": [
            {"id": get_drug_id("methotrexate"), "name": "methotrexate"}
        ],
        "patient": {
            "is_pregnant": True
        }
    })
    
    assert assert_interaction(res2, "PATIENT_CONTRAINDICATION", "Teratogenic", "SEVERE"), "Failed Scenario 2"
    print("  [PASS]")
    
    # SCENARIO 3: Patient Context - Renal Impairment
    print("Scenario 3: Lisinopril + Severe Renal Impairment (DOSAGE_ADJUSTMENT)")
    res3 = client.post("/api/v1/analyze", json={
        "medications": [
            {"id": get_drug_id("lisinopril"), "name": "lisinopril"}
        ],
        "patient": {
            "renal_clearance": "SEVERE_IMPAIRMENT"
        }
    })
    
    assert assert_interaction(res3, "DOSAGE_ADJUSTMENT", "dose adjustment", "MODERATE"), "Failed Scenario 3"
    print("  [PASS]")
    
    # SCENARIO 4: Combination Medicine Resolution
    print("Scenario 4: Augmentin resolving to Amoxicillin + Clavulanate")
    res4 = client.post("/api/v1/analyze", json={
        "medications": [
            {"id": get_drug_id("augmentin"), "name": "augmentin"}
        ]
    })
    
    data4 = res4.json()
    kg_nodes = data4["knowledge_graph"]["nodes"]
    names = [node["properties"].get("name") for node in kg_nodes]
    assert "amoxicillin" in names and "clavulanate" in names, f"Failed Scenario 4. Nodes: {names}"
    print("  [PASS]")
    
    print("\n[SUCCESS] All regression scenarios passed.")

if __name__ == "__main__":
    run_regression_suite()
