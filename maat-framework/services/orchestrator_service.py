"""
MA'AT Framework Orchestrator HTTP Service

Provides REST API for narrative processing through all agents.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.orchestrator import MAATOrchestrator

app = FastAPI(
    title="MA'AT Framework Orchestrator",
    description="Multi-agent AI governance system for content evaluation",
    version="1.0.0"
)

orchestrator = MAATOrchestrator()


class NarrativeRequest(BaseModel):
    """Request model for single narrative evaluation"""
    narrative: str
    metadata: Optional[Dict[str, Any]] = None


class BatchRequest(BaseModel):
    """Request model for batch narrative evaluation"""
    narratives: List[Dict[str, Any]]


class NarrativeResponse(BaseModel):
    """Response model for narrative evaluation"""
    narrative_hash: str
    processing_time_seconds: float
    governance_outcome: str
    agent_decisions: Dict[str, Any]
    ipfs_hash: str
    timestamp: str
    blocking_reason: Optional[str] = None


@app.post("/evaluate", response_model=NarrativeResponse)
async def evaluate_narrative(request: NarrativeRequest):
    """
    Evaluate a single narrative through all governance agents.
    
    The narrative will be evaluated by:
    - CNA: Creative quality and coherence
    - TSA: Factual accuracy and truth
    - UEA: Fairness and ethics
    - LAA: Legal compliance
    - HTA: Transparency and archival
    """
    try:
        result = await orchestrator.process_narrative(
            request.narrative,
            request.metadata
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch")
async def evaluate_batch(request: BatchRequest, background_tasks: BackgroundTasks):
    """
    Evaluate a batch of narratives.
    
    Returns immediately with batch ID and processes in background.
    """
    try:
        result = await orchestrator.process_batch(request.narratives)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Health check for orchestrator and all agents.
    """
    try:
        health = await orchestrator.health_check()
        return health
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/statistics")
async def get_statistics():
    """
    Get governance statistics from HTA.
    """
    try:
        stats = orchestrator.hta.get_governance_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit-trail")
async def get_audit_trail():
    """
    Get complete audit trail from HTA.
    """
    try:
        trail = orchestrator.hta.get_audit_trail()
        return {
            "total_records": len(trail),
            "records": trail
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """
    API information.
    """
    return {
        "service": "MA'AT Framework Orchestrator",
        "version": "1.0.0",
        "description": "Multi-agent AI governance system",
        "agents": {
            "CNA": "Creative Narrative Agent",
            "TSA": "Truth & Safety Agent",
            "UEA": "Universal Ethics Agent",
            "LAA": "Legal Attestation Agent",
            "HTA": "Human Transparency Agent"
        },
        "endpoints": {
            "POST /evaluate": "Evaluate single narrative",
            "POST /batch": "Evaluate batch of narratives",
            "GET /health": "Health check",
            "GET /statistics": "Governance statistics",
            "GET /audit-trail": "Complete audit trail"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
