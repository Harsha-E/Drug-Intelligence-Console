from core.schemas import ClinicalContext, EvidenceTrace, AnalyticsEvent

class CCLParser:
    """Mock parser for the Clinical Constraint Language (CCL)."""
    
    def evaluate(self, context: ClinicalContext):
        context.audit.agents_executed.append("CCLParser")
        
        normalized_drugs = context.patient_state.get("normalized_interventions", [])
        
        # MOCK CCL RULE EXECUTION
        # Rule 18: Warfarin + Aspirin -> Bleeding Risk
        if "RxNorm:11289" in normalized_drugs and "RxNorm:1191" in normalized_drugs:
            context.reasoning_trace.path.append("CCL Engine: Executed Rule 18 (Warfarin + Aspirin).")
            context.reasoning_trace.constraints_evaluated.append("IF DrugA=NSAID AND DrugB=Anticoagulant THEN Bleeding_Risk")
            
            context.report.warnings.append("Concurrent use of Warfarin and Aspirin significantly increases major bleeding risk.")
            context.report.severity = "HIGH"
            
            context.evidence_trace.append(EvidenceTrace(
                source="AHA/ACC Guidelines 2025",
                confidence="High"
            ))
            
            context.analytics_events.append(AnalyticsEvent(
                event_type="INTERACTION_FLAGGED",
                payload={"rule": "Rule_18", "severity": "HIGH"}
            ))
