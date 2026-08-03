import json
import os
import time
from typing import Dict, Any

class RegistryCompiler:
    def __init__(self, accepted_dir: str, output_dir: str):
        self.accepted_dir = accepted_dir
        self.output_dir = output_dir
        
    def load_accepted_data(self) -> Dict[str, Any]:
        accepted_data = {}
        if not os.path.exists(self.accepted_dir):
            return accepted_data
            
        for filename in os.listdir(self.accepted_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.accepted_dir, filename), "r") as f:
                    accepted_data[filename] = json.load(f)
        return accepted_data
        
    def compile(self):
        print("Starting deterministic ingestion pipeline...")
        t0 = time.time()
        
        accepted_data = self.load_accepted_data()
        
        drugs = {}
        claims = {}
        claim_index = {}
        evidence = {}
        
        # In a real system, there would be Review and Validation stages here.
        # For this execution, we assume the data is already accepted.
        
        for source_file, records in accepted_data.items():
            for wrapper in records:
                # Normalizer wraps the actual clinical data in a "data" key
                record = wrapper.get("data", wrapper)
                
                # 1. Normalize Evidence
                for ev in record.get("evidence", []):
                    ev_id = ev["evidence_id"]
                    if ev_id not in evidence:
                        evidence[ev_id] = {
                            "evidence_id": ev_id,
                            "source": ev["source"],
                            "publication": ev.get("publication", ""),
                            "retrieval_date": ev.get("retrieval_date", time.strftime("%Y-%m-%d")),
                            "confidence": ev.get("confidence", "HIGH"),
                            "source_version": ev.get("source_version", "1.0")
                        }
                
                # Also extract from claims if present
                for claim in record.get("claims", []):
                    for ev in claim.get("evidence_payloads", []):
                        ev_id = ev["evidence_id"]
                        if ev_id not in evidence:
                            evidence[ev_id] = {
                                "evidence_id": ev_id,
                                "source": ev["source"],
                                "publication": ev.get("publication", ""),
                                "retrieval_date": ev.get("retrieval_date", time.strftime("%Y-%m-%d")),
                                "confidence": ev.get("confidence", "HIGH"),
                                "source_version": ev.get("source_version", "1.0")
                            }
                        
                # 2. Normalize Ingredients & Drugs
                drug_id = record.get("drug_id")
                if drug_id:
                    drugs[drug_id] = {
                        "entity_type": "DrugKnowledge",
                        "drug_id": drug_id,
                        "identity": record.get("identity", {}),
                        "ingredients": record.get("ingredients", []),
                        "clinical_knowledge": record.get("clinical_knowledge", {})
                    }
                    
                # 3. Normalize Claims
                for claim in record.get("claims", []):
                    c_id = claim["claim_id"]
                    subj = claim["subject"]
                    
                    if c_id not in claims:
                        claims[c_id] = {
                            "claim_id": c_id,
                            "subject": subj,
                            "predicate": claim["predicate"],
                            "object": claim["object"],
                            "object_name": claim.get("object_name"),
                            "effect": claim.get("effect"),
                            "strength": claim.get("strength"),
                            "evidence_refs": claim.get("evidence_refs", [])
                        }
                        
                    if subj not in claim_index:
                        claim_index[subj] = []
                    if c_id not in claim_index[subj]:
                        claim_index[subj].append(c_id)
                        
        # Validate Evidence References
        for c_id, claim in claims.items():
            for ev_ref in claim.get("evidence_refs", []):
                if ev_ref not in evidence:
                    raise ValueError(f"Dangling evidence reference: {ev_ref} in claim {c_id}")
                    
        # Publish to output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open(os.path.join(self.output_dir, "drug_lookup.json"), "w") as f:
            json.dump(drugs, f, indent=2)
            
        with open(os.path.join(self.output_dir, "claims.json"), "w") as f:
            json.dump(claims, f, indent=2)
            
        with open(os.path.join(self.output_dir, "claim_index.json"), "w") as f:
            json.dump(claim_index, f, indent=2)
            
        with open(os.path.join(self.output_dir, "evidence.json"), "w") as f:
            json.dump(evidence, f, indent=2)
            
        t1 = time.time()
        print(f"Compiled {len(drugs)} drugs, {len(claims)} claims, {len(evidence)} evidence objects in {(t1-t0)*1000:.2f}ms")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    accepted = os.path.join(base_dir, "registry", "accepted_knowledge")
    output = os.path.join(base_dir, "registry", "current")
    compiler = RegistryCompiler(accepted, output)
    compiler.compile()
