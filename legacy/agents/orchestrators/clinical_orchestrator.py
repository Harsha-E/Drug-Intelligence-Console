import uuid
import time
from core.schemas import ClinicalContext, AuditTrace, ClinicalReport
from agents.specialists.identity_agent import IdentityAgent
from reasoning.rules.ccl_parser import CCLParser

class ClinicalOrchestrator:
    """The central orchestrator for the Clinical Workflow."""
    
    def __init__(self):
        self.identity_agent = IdentityAgent()
        self.ccl_parser = CCLParser()
    
    def analyze(self, patient_state: dict, interventions: list) -> ClinicalContext:
        start_time = time.time()
        
        # 1. Context Building
        context = ClinicalContext(
            request_id=str(uuid.uuid4()),
            patient_state=patient_state,
            interventions=interventions,
            audit=AuditTrace(request_id="")
        )
        context.audit.request_id = context.request_id
        
        # 2. Agent Dispatch (Pipeline)
        # In a real system, this would use the Registry to discover agents dynamically
        
        # Step A: Normalization
        self.identity_agent.execute(context)
        
        # Step B: Reasoning
        self.ccl_parser.evaluate(context)
        
        # 3. Finalize Audit
        context.audit.latency_ms = (time.time() - start_time) * 1000
        
        # If no warnings, set a default recommendation
        if not context.report.warnings:
            context.report.recommendations.append("No immediate interactions found based on active rules.")
            context.reasoning_trace.path.append("CCL Engine: No constraints violated.")
            
        return context
