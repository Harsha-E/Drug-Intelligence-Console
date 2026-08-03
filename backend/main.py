import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, AsyncGenerator
import uvicorn
from contextlib import asynccontextmanager

from backend.core.runtime import runtime
from backend.core.intelligence.ReasoningEngine import ReasoningEngine
from backend.core.execution import ledger
from backend.core.telemetry import telemetry
import asyncio
from backend.api.ingestion import router as ingestion_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    registry_path = os.getenv("REGISTRY_DIR", os.path.join(os.path.dirname(__file__), "registry", "current"))
    runtime.load(registry_path)
    yield

app = FastAPI(title="MedCheck Intelligence Cloud", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.ingestion import router as ingestion_router
from backend.api.registry_stats import router as registry_stats_router

app.include_router(ingestion_router)
app.include_router(registry_stats_router)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount frontend/console at the root, fallback to index.html for SPA routing
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "admin")
repo_root = os.path.dirname(os.path.dirname(__file__))

@app.get("/agents.md")
def serve_agents_md():
    agents_path = os.path.join(repo_root, "agents.md")
    if os.path.exists(agents_path):
        return FileResponse(agents_path)
    return {"message": "agents.md not found"}

@app.get("/")
def serve_frontend_index():
    if os.path.exists(os.path.join(frontend_dir, "index.html")):
        return FileResponse(os.path.join(frontend_dir, "index.html"))
    return {"message": "Frontend not found"}

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

engine = ReasoningEngine()

class MedicationInput(BaseModel):
    id: str
    name: str
    strength: Optional[float] = None
    unit: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None

class PatientContext(BaseModel):
    # Core
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    sex: Optional[str] = None
    is_pregnant: bool = False
    
    # Organs
    renal_clearance: str = "NORMAL"
    hepatic_impairment: str = "NONE"
    
    # Clinical
    active_conditions: List[str] = []
    diagnoses: List[str] = []
    allergies: List[str] = []
    laboratory_values: Dict[str, float] = {}

class AnalyzeRequest(BaseModel):
    medications: List[MedicationInput]
    patient: Optional[PatientContext] = None

class InteractionsRequest(BaseModel):
    medication_ids: List[str]

import time
from collections import deque
import statistics

# Metrics state
metrics = {
    "start_time": time.time(),
    "analyze_latencies": deque(maxlen=1000),
    "interactions_latencies": deque(maxlen=1000),
}

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    path = request.url.path
    if path == "/api/v1/analyze":
        metrics["analyze_latencies"].append(process_time)
    elif path == "/api/v1/interactions":
        metrics["interactions_latencies"].append(process_time)
        
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
def root():
    return {"status": "ok", "layer": "MedCheck Intelligence Cloud"}

@app.get("/metrics")
def get_metrics():
    sizes = runtime.get_registry_sizes()
    uptime = time.time() - metrics["start_time"]
    
    avg_analyze = statistics.mean(metrics["analyze_latencies"]) if metrics["analyze_latencies"] else 0
    p95_analyze = statistics.quantiles(metrics["analyze_latencies"], n=20)[18] if len(metrics["analyze_latencies"]) >= 20 else avg_analyze
    
    return {
        "uptime_seconds": round(uptime, 2),
        "registry_version": os.getenv("REGISTRY_VERSION", "1.0"),
        "registry_load_duration_ms": getattr(runtime, 'load_duration_ms', 0),
        "total_drugs": sizes.get("drug_lookup", 0),
        "total_claims": sizes.get("claims", 0),
        "total_evidence": sizes.get("evidence", 0),
        "total_rules": sizes.get("rules", 0),
        "runtime_cache_hits": getattr(runtime, 'cache_hits', 0),
        "runtime_cache_misses": getattr(runtime, 'cache_misses', 0),
        "average_analyze_latency_ms": round(avg_analyze * 1000, 2),
        "p95_analyze_latency_ms": round(p95_analyze * 1000, 2)
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/ready")
def readiness_check():
    sizes = runtime.get_registry_sizes()
    if not sizes or len(sizes) == 0:
        raise HTTPException(status_code=503, detail="Registries not loaded")
    return {"status": "ready", "registries": sizes}

@app.get("/version")
def version_check():
    commit_hash = os.getenv("GIT_COMMIT", "unknown")
    build_version = os.getenv("BUILD_VERSION", "1.0.0")
    api_version = "v1"
    
    sizes = runtime.get_registry_sizes()
    registry_version = "1.0" if sizes else "none"
    
    return {
        "build_version": build_version,
        "api_version": api_version,
        "registry_version": registry_version,
        "git_commit": commit_hash
    }

@app.get("/api/v1/drugs/search")
def search_drugs(q: str):
    q = q.lower()
    drug_lookup = runtime.get_registry("drug_lookup")
    alias_index = runtime.get_registry("alias_index")
    
    results = []
    for drug_id, drug_data in drug_lookup.items():
        canonical_name = drug_data.get("identity", {}).get("canonical_name", "")
        if q in canonical_name.lower() or q in drug_id.lower():
            # Inject id into the result dictionary
            res_item = dict(drug_data)
            res_item["id"] = drug_id
            results.append(res_item)
            
    # For a production DB this would be elasticsearch, but for O(1) in-memory it's fine for small dataset.
    return {"results": results[:50]}

@app.post("/api/v1/analyze")
def analyze_medications(req: AnalyzeRequest):
    # Create Immutable Execution Record
    execution = ledger.create(req.model_dump())
    
    # 1. Check for Unknown Medications
    unknown_meds = []
    
    medication_ids = [m.id for m in req.medications]
    t0 = time.time()
    
    for m in req.medications:
        if not runtime.knowledge_graph or not runtime.knowledge_graph.get_node(m.id):
            unknown_meds.append(m)
            # Auto-queue into the ingestion pipeline
            try:
                from backend.api.ingestion import pipeline
                pipeline.process_unknown_medicine(m.name)
            except Exception as e:
                pass # Ignore if pipeline fails in background
                
    # Run the Engine
    engine.check_interactions(execution, req.medications, req.patient, runtime.knowledge_graph)
    
    t1 = time.time()
    execution.total_latency_ms = (t1 - t0) * 1000
    
    if execution.clinical_decision is None:
        execution.clinical_decision = []
        
    if unknown_meds:
        execution.clinical_decision.append({
            "type": "UNKNOWN_MEDICINE",
            "message": "Medicine not yet present in the verified knowledge base.",
            "medicines": [m.name for m in unknown_meds]
        })
    
    clinical_report = {
        "status": "WARNING" if execution.clinical_decision else "OK",
        "medications_analyzed": len(req.medications),
        "interactions_found": len(execution.clinical_decision) if execution.clinical_decision else 0,
        "unknown_medications_queued": [m.name for m in unknown_meds]
    }
    
    # The frontend is going to read from the ExecutionRecord natively eventually,
    # but we will return it in the trace_data format for now.
    trace_data = {
        "execution_id": execution.execution_id,
        "clinical_report": clinical_report,
        "reasoning_trace": {
            "steps": execution.events,
            "hypotheses_evaluation": execution.clinical_decision,
            "total_latency_ms": execution.total_latency_ms
        },
        "evidence": execution.clinical_decision,
        "timestamp": execution.timestamp,
        "knowledge_graph": execution.knowledge_graph.model_dump()
    }
    
    runtime.add_trace(execution.execution_id, trace_data)
    runtime.add_history({
        "action": "analyze",
        "execution_id": execution.execution_id,
        "medication_count": len(req.medications),
        "interactions_found": len(execution.clinical_decision) if execution.clinical_decision else 0,
        "timestamp": execution.timestamp * 1000,
        "latency_ms": execution.total_latency_ms
    })
    
    return trace_data

from fastapi.responses import StreamingResponse

@app.get("/api/v1/stream")
async def stream_telemetry():
    """SSE endpoint for live telemetry"""
    queue = asyncio.Queue()
    telemetry.subscribe(queue)
    
    async def event_generator():
        try:
            while True:
                event = await queue.get()
                yield f"data: {event.model_dump_json()}\n\n"
        except asyncio.CancelledError:
            telemetry.unsubscribe(queue)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/v1/interactions")
def check_interactions(req: InteractionsRequest):
    execution = ledger.create({"medication_ids": req.medication_ids})
    engine.check_interactions(execution, req.medication_ids)
    interactions = execution.clinical_decision or []
    
    runtime.add_history({
        "action": "interactions_check",
        "medication_ids": req.medication_ids,
        "found": len(interactions)
    })
    
    return {"interactions": interactions}

@app.get("/api/v1/analysis/{id}")
def get_analysis(id: str):
    trace = runtime.get_trace(id)
    if not trace:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return trace

@app.get("/api/v1/history")
def get_history():
    return {"history": runtime.get_history()}

@app.get("/api/v1/registry/stats")
def get_registry_stats():
    sizes = runtime.get_registry_sizes()
    return sizes

@app.get("/api/v1/registry/{resource}")
def get_registry(resource: str):
    data = runtime.get_registry(resource)
    if not data:
        raise HTTPException(status_code=404, detail="Registry resource not found")
    return data

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)
