from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List
import os

from ingestion.unknown_pipeline import UnknownMedicinePipeline
from ingestion.review_queue import ReviewQueue
from ingestion.compiler import RegistryCompiler
from backend.core.runtime import runtime

router = APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])

backend_dir = os.path.dirname(os.path.dirname(__file__))
review_queue_dir = os.path.join(backend_dir, "registry", "review_queue")
accepted_dir = os.path.join(backend_dir, "registry", "accepted_knowledge")
registry_dir = os.path.join(backend_dir, "registry", "current")

pipeline = UnknownMedicinePipeline(review_queue_dir=review_queue_dir)
review_queue = ReviewQueue(review_dir=review_queue_dir, accepted_dir=accepted_dir)

class ProcessUnknownRequest(BaseModel):
    raw_string: str

@router.post("/process_unknown")
def process_unknown(req: ProcessUnknownRequest):
    """
    Submits an unknown medicine string to the external knowledge retrieval pipeline
    and places it in the clinical review queue.
    """
    tracking_id = pipeline.process_unknown_medicine(req.raw_string)
    return {"status": "queued", "tracking_id": tracking_id}

@router.post("/approve_all")
def approve_all():
    """Admin endpoint to approve all pending items in the review queue."""
    review_queue.approve_all()
    return {"status": "approved"}

@router.post("/compile")
def compile_registry():
    """
    Compiles all accepted knowledge into the live registry.
    Triggers a runtime reload to make them immediately available.
    """
    compiler = RegistryCompiler(accepted_dir, registry_dir)
    compiler.compile()
    
    # Reload runtime if compilation succeeded
    runtime.load(registry_dir)
        
    return {"status": "success"}
