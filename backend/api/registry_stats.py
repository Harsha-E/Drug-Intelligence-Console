from fastapi import APIRouter
from backend.core.runtime import runtime
import time
import os

router = APIRouter(prefix="/api/v1/registry", tags=["registry"])

@router.get("/stats")
def get_registry_stats():
    t0 = time.time()
    drugs = runtime.get_registry("drug_lookup")
    claims = runtime.get_registry("claims")
    evidence = runtime.get_registry("evidence")
    
    ingredients = set()
    mechanisms = set()
    targets = set()
    enzymes = set()
    transporters = set()
    pathways = set()
    brand_names = set()
    
    inferred_interactions = 0
    curated_interactions = 0
    
    # Calculate derived stats
    for d_id, drug in drugs.items():
        if "identity" in drug:
            brand_names.add(drug["identity"].get("canonical_name", ""))
            
        for ing in drug.get("ingredients", []):
            ingredients.add(ing.get("ingredient_id"))
            
    for c_id, claim in claims.items():
        pred = claim.get("predicate")
        obj = claim.get("object")
        
        if pred == "INHIBITS_ENZYME" or pred == "METABOLIZED_BY":
            enzymes.add(obj)
        elif pred == "HAS_TARGET":
            targets.add(obj)
        elif pred == "HAS_TRANSPORTER":
            transporters.add(obj)
        elif pred == "INVOLVED_IN_PATHWAY":
            pathways.add(obj)
        elif pred == "HAS_MECHANISM":
            mechanisms.add(obj)
            
        if pred == "INCREASED_RISK_WITH":
            curated_interactions += 1
            
    # Mocking inference count for metrics purposes based on the graph possibilities
    # Real inferred interactions happen at runtime during /analyze, but we can project the potential space
    inferred_interactions = len(ingredients) * len(enzymes) * 2  # heuristic for demo
    
    # Calculate registry size
    registry_dir = os.getenv("REGISTRY_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "registry", "current"))
    total_size = 0
    for root, dirs, files in os.walk(registry_dir):
        for f in files:
            total_size += os.path.getsize(os.path.join(root, f))
            
    t1 = time.time()
    
    manifest_data = runtime.get_registry("manifest")
    rules_data = runtime.get_registry("rules")
    vocab_data = runtime.get_registry("vocabulary")
    
    return {
        "manifest": manifest_data,
        "metrics": {
            "medicines": len(drugs),
            "ingredients": len(ingredients),
            "brand_names": len(brand_names),
            "enzymes": len(enzymes),
            "targets": len(targets),
            "transporters": len(transporters),
            "pathways": len(pathways),
            "mechanisms": len(mechanisms),
            "claims": len(claims),
            "evidence": len(evidence),
            "rules": len(rules_data),
            "vocabulary": len(vocab_data),
            "inferred_interactions": inferred_interactions,
            "curated_interactions": curated_interactions,
            "registry_size_bytes": total_size,
            "stats_generation_latency_ms": round((t1 - t0) * 1000, 2)
        }
    }
