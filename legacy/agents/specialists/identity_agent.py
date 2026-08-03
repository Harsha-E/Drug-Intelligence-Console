from core.schemas import ClinicalContext

class IdentityAgent:
    """Maps raw drug names to semantic concepts."""
    
    def execute(self, context: ClinicalContext):
        context.audit.agents_executed.append("IdentityAgent")
        context.reasoning_trace.path.append("IdentityAgent: Mapped input strings to Semantic Concept IDs.")
        
        # MOCK IMPLEMENTATION
        normalized_drugs = []
        for drug in context.interventions:
            if drug.lower() == "warfarin":
                normalized_drugs.append("RxNorm:11289")
            elif drug.lower() == "aspirin":
                normalized_drugs.append("RxNorm:1191")
            else:
                normalized_drugs.append(f"Unknown:{drug}")
                
        # We append findings to the context, we don't mutate the raw input
        context.patient_state["normalized_interventions"] = normalized_drugs
