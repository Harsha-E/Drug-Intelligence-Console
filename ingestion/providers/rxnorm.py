from typing import List, Dict, Any
from .base import SourceProvider

class RxNormProvider(SourceProvider):
    def get_provider_name(self) -> str:
        return "RxNorm"
        
    def fetch_all(self) -> List[Dict[str, Any]]:
        # Mock offline provider for RxNorm mappings and ingredients
        return [
            {
                "canonical_name": "warfarin",
                "codes": {"rxnorm": "11289"},
                "ingredients": [{"name": "warfarin", "role": "active"}],
                "claims": []
            }
        ]
