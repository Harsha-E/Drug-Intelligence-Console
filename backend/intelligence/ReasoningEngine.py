from typing import Dict, List, Optional

class ReasoningEngine:
    """
    Python implementation of the Reasoning Engine.
    Analyzes Evidence Attribution ledgers and generates hypotheses.
    """
    def __init__(self):
        # We replace the hardcoded CONFIDENCE_THRESHOLD with a data-driven approach later,
        # but for now we port the structure.
        self.CONFIDENCE_THRESHOLD = 0.95
        self.POINTS_FOR_MAX_CONFIDENCE = 100.0

    def evaluate(self, entity_id: str, full_ledger: List[Dict]) -> Dict:
        """
        Evaluates the current ledger for an entity and returns the leading hypothesis.
        """
        hypothesis_groups = {}
        for entry in full_ledger:
            target_id = entry.get('targetHypothesisId')
            if target_id not in hypothesis_groups:
                hypothesis_groups[target_id] = []
            hypothesis_groups[target_id].append(entry)

        updated_hypotheses = {}
        leading_id = None
        max_confidence = -1.0

        for hyp_id, entries in hypothesis_groups.items():
            total_points = sum(e.get('points', 0) for e in entries)
            supporting = [e.get('evidenceId') for e in entries if e.get('points', 0) > 0]
            contradictory = [e.get('evidenceId') for e in entries if e.get('points', 0) < 0]

            confidence = max(0.0, min(1.0, total_points / self.POINTS_FOR_MAX_CONFIDENCE))

            hypothesis = {
                "id": hyp_id,
                "name": hyp_id,
                "confidenceScore": confidence,
                "supportingEvidenceIds": supporting,
                "contradictoryEvidenceIds": contradictory,
                "missingCriticalRegions": self._determine_missing_evidence(hyp_id, confidence)
            }

            updated_hypotheses[hyp_id] = hypothesis

            if confidence > max_confidence:
                max_confidence = confidence
                leading_id = hyp_id

        return {
            "hypotheses": updated_hypotheses,
            "leadingId": leading_id,
            "maxConfidence": max_confidence
        }

    def _determine_missing_evidence(self, hypothesis_id: str, current_confidence: float) -> List[str]:
        missing = []
        if current_confidence >= self.CONFIDENCE_THRESHOLD:
            return missing

        # TODO: Query the Knowledge Graph for expected schema.
        # Currently hardcoded for porting parity.
        missing.append('MANUFACTURER_LOGO_REQUIRED')
        missing.append('DOSAGE_CONFIRMATION_REQUIRED')

        return missing
