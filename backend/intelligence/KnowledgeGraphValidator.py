import re
from typing import List, Dict, Optional, Tuple

class KnowledgeGraphValidator:
    """
    Unified Knowledge Graph Validator.
    Replaces AliasResolver, BrandResolver, GenericNameResolver, and ManufacturerResolver.
    Evaluates OCR blocks against a verified medicine database to resolve entities.
    """
    
    def __init__(self):
        self.min_similarity_threshold = 0.65

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        if s1 == s2:
            return 1.0
        
        # Substring bonus
        if s1 in s2 or s2 in s1:
            ratio = min(len(s1), len(s2)) / max(len(s1), len(s2))
            return 0.7 + (ratio * 0.25)
            
        # Simple Levenshtein distance
        len_s1, len_s2 = len(s1), len(s2)
        if len_s1 == 0 or len_s2 == 0:
            return 0.0
            
        dp = [[0] * (len_s1 + 1) for _ in range(len_s2 + 1)]
        
        for i in range(len_s1 + 1):
            dp[0][i] = i
        for j in range(len_s2 + 1):
            dp[j][0] = j
            
        for j in range(1, len_s2 + 1):
            for i in range(1, len_s1 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                dp[j][i] = min(
                    dp[j][i-1] + 1,      # deletion
                    dp[j-1][i] + 1,      # insertion
                    dp[j-1][i-1] + cost  # substitution
                )
                
        distance = dp[len_s2][len_s1]
        max_len = max(len_s1, len_s2)
        return 1.0 - (distance / max_len)

    def resolve_entity(self, ocr_text: str, dataset: List[Dict], entity_type: str = 'brand') -> Optional[Dict]:
        """
        Resolves an entity (brand, generic, or manufacturer) from raw OCR text.
        """
        if not ocr_text or not dataset:
            return None
            
        cleaned_text = self.normalize_text(ocr_text)
        lines = re.split(r'[\n,;]', cleaned_text)
        candidates = []
        
        for line in lines:
            words = [w.strip() for w in line.split() if len(w.strip()) > 2]
            if not words:
                continue
                
            # Repetition handler (e.g. "dolo dolo" -> "dolo")
            unique_words = []
            seen = set()
            for w in words:
                if w not in seen:
                    seen.add(w)
                    unique_words.append(w)
            
            candidate_phrase = " ".join(unique_words)
            
            # Clean pure dosages
            clean_candidate = re.sub(r'\b\d+(?:\.\d+)?\s*(?:mg|mcg|ml|g|tab|cap)\b', '', candidate_phrase).strip()
            
            if len(clean_candidate) > 2:
                candidates.append(clean_candidate)
                
        if not candidates:
            return None
            
        best_match = None
        highest_score = 0.0
        
        for cand in candidates:
            norm_cand = self.normalize_text(cand)
            
            for record in dataset:
                # Extract targets based on entity type
                targets = []
                if entity_type == 'brand':
                    targets = record.get('brandNames', [record.get('brandName')] if record.get('brandName') else [])
                elif entity_type == 'generic':
                    targets = record.get('genericNames', [record.get('genericName')] if record.get('genericName') else [])
                elif entity_type == 'manufacturer':
                    targets = [record.get('manufacturer')] if record.get('manufacturer') else []
                    
                for target in targets:
                    if not target:
                        continue
                    norm_target = self.normalize_text(target)
                    score = self._calculate_similarity(norm_cand, norm_target)
                    
                    if score > highest_score:
                        highest_score = score
                        best_match = {
                            "matched_name": target,
                            "entity_type": entity_type,
                            "confidence": round(score * 100),
                            "record": record
                        }
                        
        if highest_score >= self.min_similarity_threshold:
            return best_match
        return None
