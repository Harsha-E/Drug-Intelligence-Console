import json
import os
import time
from typing import List
from .identifier_service import IdentifierService
from .providers.base import SourceProvider

class Normalizer:
    def __init__(self, providers: List[SourceProvider], identifier_service: IdentifierService, review_queue_dir: str):
        self.providers = providers
        self.identifier_service = identifier_service
        self.review_queue_dir = review_queue_dir
        os.makedirs(self.review_queue_dir, exist_ok=True)
        
    def normalize_and_queue(self):
        print("Normalizing raw provider data...")
        
        normalized_records = []
        for provider in self.providers:
            provider_name = provider.get_provider_name()
            raw_items = provider.fetch_all()
            
            for item in raw_items:
                canonical_name = item.get("canonical_name", "unknown")
                external_codes = item.get("codes", {})
                
                # 1. Resolve Drug ID
                drug_dic_id = self.identifier_service.get_or_create_id("drug", canonical_name, external_codes)
                
                # 2. Resolve Ingredients
                ingredients = []
                for ing in item.get("ingredients", []):
                    ing_name = ing.get("name")
                    ing_dic_id = self.identifier_service.get_or_create_id("ingredient", ing_name)
                    ingredients.append({
                        "ingredient_id": ing_dic_id,
                        "name": ing_name,
                        "role": ing.get("role"),
                        "confidence": 1.0,
                        "matched_source": provider_name,
                        "normalization_method": "Exact Match"
                    })
                    
                # 3. Resolve Claims
                claims = []
                for idx, claim in enumerate(item.get("claims", [])):
                    subject_name = claim.get("subject_name")
                    subj_dic_id = self.identifier_service.get_or_create_id("ingredient", subject_name)
                    
                    pred = claim.get("predicate")
                    obj_name = claim.get("object_name")
                    
                    # Determine object type from predicate
                    obj_type = "target"
                    if pred in ["INHIBITS_ENZYME", "METABOLIZED_BY"]: obj_type = "enzyme"
                    elif pred in ["INHIBITS_TRANSPORTER", "TRANSPORTED_BY"]: obj_type = "transporter"
                    elif pred == "MODULATES_PATHWAY": obj_type = "pathway"
                    elif pred == "ALTERS_LAB": obj_type = "lab"
                    elif pred in ["CONTRAINDICATED_FOR", "REQUIRES_RENAL_ADJUSTMENT_IF", "REQUIRES_HEPATIC_ADJUSTMENT_IF"]: obj_type = "disease"
                    elif pred == "PREGNANCY_CATEGORY": obj_type = "category"
                    elif pred == "HAS_EFFECT": obj_type = "effect"
                    elif pred == "INCREASED_RISK_WITH": obj_type = "ingredient"
                    
                    obj_dic_id = self.identifier_service.get_or_create_id(obj_type, obj_name)
                    
                    claim_dic_id = self.identifier_service.get_or_create_id("claim", f"{subj_dic_id}_{pred}_{obj_dic_id}")
                    ev_dic_id = self.identifier_service.get_or_create_id("evidence", f"EVD_{provider_name}_{drug_dic_id}_{idx}")
                    
                    ev_data = claim.get("evidence", {})
                    
                    claims.append({
                        "claim_id": claim_dic_id,
                        "subject": subj_dic_id,
                        "predicate": pred,
                        "object": obj_dic_id,
                        "object_name": obj_name,
                        "strength": claim.get("strength"),
                        "evidence_refs": [ev_dic_id],
                        "evidence_payloads": [
                            {
                                "evidence_id": ev_dic_id,
                                "source": provider_name,
                                "publication": f"{provider_name} Data",
                                "confidence": ev_data.get("confidence", "UNKNOWN")
                            }
                        ]
                    })
                
                record = {
                    "drug_id": drug_dic_id,
                    "identity": {
                        "canonical_name": canonical_name,
                        "codes": external_codes
                    },
                    "ingredients": ingredients,
                    "clinical_knowledge": {
                        "classifications": item.get("classifications", [])
                    },
                    "claims": claims
                }
                
                normalized_records.append({
                    "normalized_at": time.time(),
                    "source_provider": provider_name,
                    "data": record
                })
                
        # Push to review queue
        queue_file = os.path.join(self.review_queue_dir, f"batch_{int(time.time())}.json")
        with open(queue_file, "w") as f:
            json.dump(normalized_records, f, indent=2)
            
        print(f"Pushed {len(normalized_records)} normalized records to review queue.")
