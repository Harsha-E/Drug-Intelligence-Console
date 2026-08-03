from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from agents.orchestrators.clinical_orchestrator import ClinicalOrchestrator
from backend.core.schemas import ClinicalContext

app = FastAPI(title="Drug Intelligence Cloud API", version="0.1.0")
orchestrator = ClinicalOrchestrator()

class AnalyzeRequest(BaseModel):
    patient_state: Dict
    interventions: List[str]

@app.post("/api/v1/analyze", response_model=ClinicalContext)
async def analyze_clinical_state(request: AnalyzeRequest):
    """
    Executes the main clinical workflow for a given patient state and set of interventions.
    Returns the 5 Outputs defined in the System Specification.
    """
    context = orchestrator.analyze(
        patient_state=request.patient_state,
        interventions=request.interventions
    )
    return context

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
