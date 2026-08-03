import json
import os
import uuid
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path

from .execution import ExecutionRecord, MemoryExecutionStore

BASE_DIR = Path(__file__).resolve().parent.parent
REGISTRY_DIR = BASE_DIR / "registry"
LOG_PATH = BASE_DIR / "execution_history.jsonl"

class RuntimeEngine:
    def __init__(self):
        self.rules = self._load_json(REGISTRY_DIR / "rules" / "rules.json")
        self.canonicals = self._load_json(REGISTRY_DIR / "canonical_index.json")
        self.aliases = self._load_json(REGISTRY_DIR / "alias_index.json")
        self.mappings = self._load_json(REGISTRY_DIR / "mapping_index.json")
        self.claims = self._load_json(REGISTRY_DIR / "claim_index.json")
        self.evidence = self._load_json(REGISTRY_DIR / "evidence_index.json")
        self.vocabulary = self._load_json(REGISTRY_DIR / "vocabulary_index.json")
        self.manifest = self._load_json(REGISTRY_DIR / "manifest.json")
        
        self.store = MemoryExecutionStore(str(LOG_PATH))

    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _generate_analysis_id(self):
        date_str = datetime.utcnow().strftime("%Y%m%d")
        unique_part = uuid.uuid4().hex[:6].upper()
        return f"ANL-{date_str}-{unique_part}"

    def _get_idempotency_key(self, patient_context):
        pid = patient_context.get("patient_id", "unknown")
        raw_meds = patient_context.get("medications", [])
        med_strings = [m.get("name", "") if isinstance(m, dict) else str(m) for m in raw_meds]
        meds = sorted(med_strings)
        allergies = sorted([a.get("allergen_class", "") for a in patient_context.get("allergies", [])])
        seed = patient_context.get("_replay_seed", "")
        key_str = f"{pid}|{','.join(meds)}|{','.join(allergies)}|{seed}"
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()

    def _resolve_drug(self, name):
        canonical_name = self.aliases.get(name.lower())
        if canonical_name:
            return self.canonicals.get(canonical_name)
        return None

    def evaluate(self, patient_context):
        # 0. Idempotency Check
        idemp_key = self._get_idempotency_key(patient_context)
        recent_records = self.store.latest(20)
        now = datetime.utcnow()
        for r in recent_records:
            if r.idempotency_key == idemp_key and r.status in ["COMPLETED", "PENDING"]:
                # If executed in last 5 minutes, return it
                start_time = datetime.fromisoformat(r.request_timestamp.replace('Z', '+00:00')).replace(tzinfo=None)
                if now - start_time < timedelta(minutes=5):
                    return r.to_dict()

        # 1. Create Execution Record
        analysis_id = self._generate_analysis_id()
        patient_id = patient_context.get("patient_id", "unknown")
        
        patient_summary = {
            "patient_id": patient_id,
            "medications": patient_context.get("medications", []),
            "allergies": patient_context.get("allergies", [])
        }
        
        record = ExecutionRecord(analysis_id, patient_summary)
        record.idempotency_key = idemp_key
        
        # Hydrate versions from manifest if available
        if self.manifest:
            record.versions["build_hash"] = self.manifest.get("build_hash", "Unknown")
            record.versions["registry"] = self.manifest.get("timestamp", "Unknown")
            
        record.add_event("Execution Started", f"Patient {patient_id} with {len(patient_summary['medications'])} meds")
        record.add_node(patient_id, f"Patient {patient_id}", "Patient")
        
        self.store.save(record)
        if os.environ.get("DEMO_MODE_DELAY"): time.sleep(float(os.environ["DEMO_MODE_DELAY"]))

        # 2. Resolve Drugs
        enriched_meds = []
        for med_item in patient_context.get("medications", []):
            med_name = med_item.get("name") if isinstance(med_item, dict) else med_item
            if not med_name:
                continue
            drug = self._resolve_drug(med_name)
            if drug:
                enriched_meds.append(drug)
                canon_name = drug["identity"]["canonical_name"]
                record.add_node(canon_name, canon_name.title(), "Drug")
                record.add_edge(patient_id, canon_name, "takes")
                
        record.add_event("Knowledge Loaded", f"Resolved {len(enriched_meds)} drugs from aliases")
        self.store.save(record)
        if os.environ.get("DEMO_MODE_DELAY"): time.sleep(float(os.environ["DEMO_MODE_DELAY"]))
                
        results = []
        
        # 3. Evaluate Duplicate Therapy
        if "duplicate_therapy" in self.rules:
            classes_seen = {}
            for med in enriched_meds:
                canon_name = med["identity"]["canonical_name"]
                for cls in med.get("clinical_knowledge", {}).get("classifications", []):
                    record.add_node(cls, cls, "Vocabulary")
                    record.add_edge(canon_name, cls, "belongs_to_class")
                    
                    if cls in classes_seen:
                        record.add_event("Rule Matched", f"duplicate_therapy triggered on class {cls}")
                        results.append(self._build_trigger(
                            "duplicate_therapy",
                            med, classes_seen[cls],
                            f"Duplicate therapy detected: Both {canon_name} and {classes_seen[cls]['identity']['canonical_name']} belong to class(es): {cls}",
                            record
                        ))
                    classes_seen[cls] = med

        # 4. Evaluate Bleeding Risk
        if "bleeding_risk_interaction" in self.rules:
            bleeding_meds = []
            for med in enriched_meds:
                canon_name = med["identity"]["canonical_name"]
                chars = med.get("clinical_knowledge", {}).get("clinical_characteristics", [])
                if "PD_EFFECT_BLEEDING" in chars:
                    record.add_node("PD_EFFECT_BLEEDING", "PD_EFFECT_BLEEDING", "Vocabulary")
                    record.add_edge(canon_name, "PD_EFFECT_BLEEDING", "has_characteristic")
                    bleeding_meds.append(med)
            
            if len(bleeding_meds) > 1:
                record.add_event("Rule Matched", "bleeding_risk_interaction triggered")
                results.append(self._build_trigger(
                    "bleeding_risk_interaction",
                    bleeding_meds[0], bleeding_meds[1],
                    f"High Bleeding Risk: Concurrent use of {bleeding_meds[0]['identity']['canonical_name']} and {bleeding_meds[1]['identity']['canonical_name']} significantly increases the risk of hemorrhage.",
                    record
                ))
                
        # 5. Evaluate Allergy
        if "allergy_contraindication" in self.rules:
            allergies = patient_context.get("allergies", [])
            for med in enriched_meds:
                canon_name = med["identity"]["canonical_name"]
                drug_allergens = [ing.get("allergen_class", "").lower() for ing in med.get("ingredients", []) if ing.get("allergen_class")]
                
                for allergy in allergies:
                    allergen = allergy.get("allergen_class", "").lower()
                    if allergen in drug_allergens or (allergen == "penicillin" and "beta-lactam" in drug_allergens):
                        record.add_event("Rule Matched", f"allergy_contraindication triggered on {allergen}")
                        results.append(self._build_trigger(
                            "allergy_contraindication",
                            med, None,
                            f"Absolute Contraindication: Patient has a documented allergy to {allergen}, which conflicts with {canon_name}.",
                            record
                        ))

        record.add_event("Recommendation Generated", f"Found {len(results)} alerts")
        record.report["alerts"] = results
        
        record.complete("COMPLETED")
        self.store.save(record)
        if os.environ.get("DEMO_MODE_DELAY"): time.sleep(float(os.environ["DEMO_MODE_DELAY"]))

        return record.to_dict()

    def _build_trigger(self, rule_id, med1, med2, message, record: ExecutionRecord):
        claims_for_rule = self.mappings.get("rule_claim", {}).get(rule_id, {}).get("supports", [])
        
        record.add_node(rule_id, rule_id, "Rule")
        
        if med1:
            record.add_edge(med1["identity"]["canonical_name"], rule_id, "triggers")
        if med2:
            record.add_edge(med2["identity"]["canonical_name"], rule_id, "triggers")
            
        record.add_node(message, "Recommendation", "Recommendation")
        record.add_edge(rule_id, message, "generates")
        
        claim_objects = []
        for claim_id in claims_for_rule:
            if claim_id in self.claims:
                claim_obj = self.claims[claim_id]
                
                record.add_node(claim_id, claim_id, "Claim")
                record.add_edge(rule_id, claim_id, "supports")
                record.add_event("Claim Resolved", f"Resolved claim {claim_id}")
                
                evs = self.mappings.get("claim_evidence", {}).get(claim_id, {}).get("supports", [])
                evidence_list = []
                for ev in evs:
                    if ev in self.evidence:
                        ev_obj = self.evidence[ev]
                        evidence_list.append(ev_obj)
                        record.add_node(ev, ev_obj.get("title", ev), "Evidence")
                        record.add_edge(claim_id, ev, "supported_by")
                        record.add_event("Evidence Retrieved", f"Retrieved {ev}")
                        
                claim_obj["evidence"] = evidence_list
                claim_objects.append(claim_obj)
                    
        rule_def = self.rules.get(rule_id, {})
        
        return {
            "rule_id": rule_id,
            "message": message,
            "severity": rule_def.get("priority", "WARNING"),
            "drugs_involved": [m["identity"]["canonical_name"] for m in [med1, med2] if m],
            "claims": claim_objects
        }
