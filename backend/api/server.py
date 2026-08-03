import os
import sys
import asyncio
import json
from pathlib import Path
from typing import AsyncGenerator

# Ensure root directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.concurrency import run_in_threadpool
from backend.telemetry.engine import RuntimeEngine
import uvicorn

app = FastAPI(title="Drug Intelligence Cloud API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RuntimeEngine()

import time
import os
startup_time = time.time()

# --- Observability ---
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def ready_check():
    if not engine.rules or not engine.canonicals:
        return {"status": "unavailable"}
    return {"status": "ready"}

@app.get("/metrics")
async def get_metrics():
    uptime = time.time() - startup_time
    return {
        "uptime_seconds": round(uptime, 2),
        "total_executions": len(engine.store.history) if hasattr(engine.store, 'history') else 0,
        "total_rules": len(engine.rules),
        "total_canonicals": len(engine.canonicals),
    }

@app.get("/version")
async def get_version():
    return {
        "api_version": "1.0",
        "compiler_version": engine.manifest.get("compiler_version", "1.0.0"),
        "registry_version": engine.manifest.get("knowledge_version", "Unknown"),
        "rule_version": engine.manifest.get("rule_version", "1.0.0"),
        "git_commit": os.getenv("GIT_COMMIT", "unknown"),
        "build_time": engine.manifest.get("build_timestamp", "Unknown")
    }

# --- Execution Runtime ---
@app.post("/api/v1/analyze")
async def analyze_patient(request: Request):
    payload = await request.json()
    record_dict = await run_in_threadpool(engine.evaluate, payload)
    
    alerts = record_dict["report"].get("alerts", [])
    
    # Build a summarized version of warnings without claims/evidence
    warnings = []
    highest_severity = "NONE"
    
    for alert in alerts:
        severity = alert.get("severity", "WARNING")
        if severity == "CRITICAL" or (severity == "HIGH" and highest_severity != "CRITICAL"):
            highest_severity = severity
            
        warnings.append({
            "rule_id": alert.get("rule_id"),
            "severity": severity,
            "message": alert.get("message"),
            "drugs_involved": alert.get("drugs_involved", [])
        })

    # Basic summary derived from highest severity alert
    summary = {
        "severity": highest_severity,
        "title": f"{highest_severity.capitalize()} risk detected" if alerts else "No significant risks detected",
        "description": alerts[0]["message"] if alerts else "Safe to proceed."
    }

    return {
        "analysis_id": record_dict["analysis_id"],
        "status": record_dict["status"].lower(),
        "summary": summary,
        "warnings": warnings,
        "recommendations": [],
        "reasoning_summary": f"Analyzed {len(payload.get('medications', []))} medications.",
        "has_details": True
    }

# --- Observability / History ---
@app.post("/api/v1/analyze/replay/{analysis_id}")
async def replay_analysis(analysis_id: str):
    record = engine.store.get(analysis_id)
    if not record:
        return {"error": "Not Found"}
    # To bypass idempotency caching on explicit replay, we could mutate a bit or 
    # we can just run it. The idempotency check in evaluate only checks last 5 mins.
    # To ensure replay always runs, we temporarily disable idempotency cache for this call
    # by adding a random replay seed to patient_context.
    payload = dict(record.patient_summary)
    import uuid
    payload["_replay_seed"] = str(uuid.uuid4())
    record_dict = await run_in_threadpool(engine.evaluate, payload)
    return {"analysis_id": record_dict["analysis_id"], "status": record_dict["status"]}

@app.get("/api/v1/history/stream")
async def get_history_stream(request: Request):
    async def event_generator() -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        engine.store.add_listener(queue)
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    record_dict = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(record_dict)}\n\n"
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            engine.store.remove_listener(queue)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/v1/history")
async def get_history(limit: int = 50):
    records = engine.store.latest(limit)
    return [r.to_dict() for r in records]

@app.get("/api/v1/history/{analysis_id}")
async def get_execution(analysis_id: str):
    record = engine.store.get(analysis_id)
    if record:
        return record.to_dict()
    return {"error": "Not Found"}

# --- Registry API ---
@app.get("/api/v1/registry/rules")
async def get_rules():
    return engine.rules

@app.get("/api/v1/registry/knowledge")
async def get_knowledge():
    return engine.canonicals

@app.get("/api/v1/registry/claims")
async def get_claims():
    return engine.claims

@app.get("/api/v1/registry/evidence")
async def get_evidence():
    return engine.evidence

@app.get("/api/v1/registry/vocabulary")
async def get_vocabulary():
    return engine.vocabulary

@app.get("/api/v1/registry/mappings")
async def get_mappings():
    return engine.mappings

@app.get("/api/v1/registry/manifest")
async def get_manifest():
    return engine.manifest

# --- Control Center Dashboard ---
dashboard_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "admin"
os.makedirs(dashboard_dir, exist_ok=True)

# Mount the static files for the dashboard
app.mount("/dashboard", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")

# Redirect root to dashboard
@app.get("/")
async def root():
    return FileResponse(str(dashboard_dir / "index.html"))

if __name__ == "__main__":
    uvicorn.run("backend.api.server:app", host="0.0.0.0", port=8000, reload=True)
