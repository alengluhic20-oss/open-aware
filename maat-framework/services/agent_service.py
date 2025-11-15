"""
FastAPI service wrapper for individual agents.

Each agent can be deployed as an independent HTTP service.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import os

# Import agents
from agents import (
    CreativeNarrativeAgent,
    TruthSafetyAgent,
    UniversalEthicsAgent,
    LegalAttestationAgent,
    HumanTransparencyAgent
)

# Determine which agent to run based on environment variable
AGENT_TYPE = os.getenv("AGENT_TYPE", "CNA")

# Initialize the appropriate agent
if AGENT_TYPE == "CNA":
    agent = CreativeNarrativeAgent()
elif AGENT_TYPE == "TSA":
    agent = TruthSafetyAgent()
elif AGENT_TYPE == "UEA":
    agent = UniversalEthicsAgent()
elif AGENT_TYPE == "LAA":
    agent = LegalAttestationAgent()
elif AGENT_TYPE == "HTA":
    agent = HumanTransparencyAgent()
else:
    raise ValueError(f"Unknown AGENT_TYPE: {AGENT_TYPE}")

app = FastAPI(
    title=f"MA'AT Framework - {agent.agent_name}",
    description=f"Microservice for {agent.agent_name}",
    version=agent.version
)


class EvaluationRequest(BaseModel):
    """Request model for evaluation"""
    narrative: str
    metadata: Optional[Dict[str, Any]] = None
    agent_decisions: Optional[Dict[str, Any]] = None  # For HTA


class EvaluationResponse(BaseModel):
    """Response model for evaluation"""
    agent: str
    decision_data: Dict[str, Any]
    attestation: Dict[str, Any]
    audit_record: Optional[Dict[str, Any]] = None


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    """
    Evaluate content using this agent.
    """
    try:
        content = {
            "narrative": request.narrative,
            "metadata": request.metadata or {}
        }
        
        # HTA needs agent decisions
        if AGENT_TYPE == "HTA" and request.agent_decisions:
            content["agent_decisions"] = request.agent_decisions
        
        result = await agent.evaluate(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    try:
        health = await agent.health_check()
        return health
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/info")
async def get_info():
    """
    Get agent information.
    """
    return {
        "agent_id": agent.agent_id,
        "agent_name": agent.agent_name,
        "version": agent.version,
        "agent_type": AGENT_TYPE
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
