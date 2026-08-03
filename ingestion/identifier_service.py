import hashlib
import json
from typing import Dict, Optional

class IdentifierService:
    """
    Guarantees stable, deterministic Drug Intelligence Cloud (DIC) IDs for clinical entities.
    External IDs (RxNorm, ATC) are strictly mappings.
    """
    
    PREFIXES = {
        "drug": "DIC_DRUG",
        "ingredient": "DIC_INGREDIENT",
        "effect": "DIC_EFFECT",
        "enzyme": "DIC_ENZYME",
        "pathway": "DIC_PATHWAY",
        "transporter": "DIC_TRANSPORTER",
        "target": "DIC_TARGET",
        "lab": "DIC_LAB",
        "disease": "DIC_DISEASE",
        "rule": "DIC_RULE",
        "evidence": "DIC_EVIDENCE"
    }

    def __init__(self):
        # Maps external ID strings to DIC IDs
        self._mappings: Dict[str, str] = {}
        
    def _generate_deterministic_id(self, entity_type: str, canonical_name: str) -> str:
        prefix = self.PREFIXES.get(entity_type.lower(), "DIC_UNKNOWN")
        # Deterministic hash of the lowercase canonical name
        hash_digest = hashlib.sha256(canonical_name.lower().strip().encode('utf-8')).hexdigest()[:8].upper()
        return f"{prefix}_{hash_digest}"
        
    def get_or_create_id(self, entity_type: str, canonical_name: str, external_ids: Dict[str, str] = None) -> str:
        """
        Returns a stable internal DIC ID.
        Registers external IDs as mappings to this DIC ID.
        """
        dic_id = self._generate_deterministic_id(entity_type, canonical_name)
        
        if external_ids:
            for system, ext_id in external_ids.items():
                mapping_key = f"{system.lower()}:{ext_id}"
                self._mappings[mapping_key] = dic_id
                
        return dic_id
        
    def resolve_external_id(self, system: str, ext_id: str) -> Optional[str]:
        """Resolves an external provider ID to the canonical DIC ID"""
        return self._mappings.get(f"{system.lower()}:{ext_id}")
