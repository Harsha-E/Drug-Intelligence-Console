from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class AnalyticsEvent(BaseModel):
    event_type: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict

class AuditTrace(BaseModel):
    request_id: str
    latency_ms: float = 0.0
    agents_executed: List[str] = []
    knowledge_version: str = "1.0.0"

class EvidenceTrace(BaseModel):
    source: str
    url: Optional[str] = None
    confidence: str

class ReasoningTrace(BaseModel):
    path: List[str] = []
    constraints_evaluated: List[str] = []

class ClinicalReport(BaseModel):
    recommendations: List[str] = []
    warnings: List[str] = []
    severity: str = "LOW"

class ClinicalContext(BaseModel):
    """The Shared State Object passed between all agents."""
    request_id: str
    patient_state: Dict
    interventions: List[str]
    
    # The 5 Outputs generated over the lifecycle
    report: ClinicalReport = Field(default_factory=ClinicalReport)
    reasoning_trace: ReasoningTrace = Field(default_factory=ReasoningTrace)
    evidence_trace: List[EvidenceTrace] = []
    audit: AuditTrace
    analytics_events: List[AnalyticsEvent] = []
