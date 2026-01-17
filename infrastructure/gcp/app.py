"""
FREQ AI Lattice - Google Cloud Run API

This FastAPI application exposes the FREQ AI Lattice as HTTP endpoints.
Deploy to Cloud Run for serverless execution.
"""

import asyncio
import json
import os
import time
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import the lattice components
import sys
sys.path.insert(0, '/app')
from run_lattice import (
    FreqAILattice,
    A2AMessage,
    MessageType,
    AnthropicClient,
    GoogleAIClient,
)

# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("FREQ-API")

# =============================================================================
# GLOBAL STATE
# =============================================================================

lattice: Optional[FreqAILattice] = None
mission_history: Dict[str, Dict] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize lattice on startup."""
    global lattice
    logger.info("Initializing FREQ AI Lattice...")
    lattice = FreqAILattice()
    logger.info("Lattice ready.")
    yield
    logger.info("Shutting down lattice...")

# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="FREQ AI Lattice API",
    description="Sophisticated Operational Lattice for Maritime Barge Operations",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class DirectiveRequest(BaseModel):
    """Request to process a Sovereign directive."""
    directive: str = Field(..., description="The command to execute", min_length=1)
    priority: str = Field(default="NORMAL", description="Priority level: LOW, NORMAL, HIGH, CRITICAL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DirectiveResponse(BaseModel):
    """Response from directive processing."""
    mission_id: str
    status: str
    directive: str
    total_latency_ms: float
    freq_compliant: bool
    chain_of_command: Dict[str, Any]

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    lattice_ready: bool
    timestamp: str
    providers: Dict[str, bool]

class MissionStatus(BaseModel):
    """Status of a mission."""
    mission_id: str
    status: str
    result: Optional[Dict[str, Any]]

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - API info."""
    return {
        "service": "FREQ AI Lattice",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Cloud Run."""
    anthropic_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    google_key = bool(os.environ.get("GOOGLE_AI_API_KEY"))

    return HealthResponse(
        status="healthy" if lattice else "initializing",
        lattice_ready=lattice is not None,
        timestamp=datetime.utcnow().isoformat(),
        providers={
            "anthropic_direct": anthropic_key,
            "google_ai_studio": google_key,
        }
    )


@app.post("/api/v1/directive", response_model=DirectiveResponse)
async def process_directive(request: DirectiveRequest):
    """
    Process a Sovereign directive through the FREQ AI Lattice.

    Flow: SOVEREIGN -> SSC -> CGE -> TOM -> SOVEREIGN
    """
    if not lattice:
        raise HTTPException(status_code=503, detail="Lattice not initialized")

    logger.info(f"Received directive: {request.directive[:50]}...")

    try:
        # Process through lattice
        result = await lattice.process_directive(request.directive)

        # Generate mission ID
        mission_id = f"mission-{int(time.time())}"

        # Store in history
        mission_history[mission_id] = {
            "status": "completed",
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return DirectiveResponse(
            mission_id=mission_id,
            status="completed",
            directive=request.directive,
            total_latency_ms=result["total_latency_ms"],
            freq_compliant=result["freq_compliant"],
            chain_of_command={
                "L1_SSC": result["ssc_response"],
                "L2_CGE": result["cge_response"],
                "L5_TOM": result["tom_response"],
            }
        )

    except Exception as e:
        logger.error(f"Directive processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/mission/{mission_id}", response_model=MissionStatus)
async def get_mission_status(mission_id: str):
    """Get the status of a specific mission."""
    if mission_id not in mission_history:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission = mission_history[mission_id]
    return MissionStatus(
        mission_id=mission_id,
        status=mission["status"],
        result=mission.get("result"),
    )


@app.get("/api/v1/missions")
async def list_missions(limit: int = 10):
    """List recent missions."""
    missions = list(mission_history.items())[-limit:]
    return {
        "count": len(missions),
        "missions": [
            {"mission_id": mid, "status": m["status"], "timestamp": m["timestamp"]}
            for mid, m in missions
        ]
    }


@app.post("/api/v1/test")
async def test_lattice():
    """
    Run a test directive to verify lattice is working.
    """
    test_directive = """
    TEST DIRECTIVE: Verify system operational status.
    Check all nodes: SSC, CGE, TOM.
    Report FREQ LAW compliance.
    """

    request = DirectiveRequest(directive=test_directive, priority="HIGH")
    return await process_directive(request)


# =============================================================================
# MARITIME-SPECIFIC ENDPOINTS
# =============================================================================

class BargeScanRequest(BaseModel):
    """Request to scan a barge."""
    barge_id: str = Field(..., description="Barge identifier (e.g., DELTA-7)")
    location: str = Field(..., description="Location (e.g., Mile Marker 142)")
    weather: Optional[str] = Field(default="Clear", description="Weather conditions")
    priority: str = Field(default="NORMAL")

@app.post("/api/v1/maritime/scan-barge")
async def scan_barge(request: BargeScanRequest):
    """
    Initiate a barge draft measurement scan.

    This creates a directive for the lattice to process,
    coordinating with drone systems for LiDAR scanning.
    """
    directive = f"""
    MARITIME OPERATION: Barge Draft Measurement

    Barge ID: {request.barge_id}
    Location: {request.location}
    Weather: {request.weather}
    Priority: {request.priority}

    Tasks:
    1. Validate weather conditions for drone operation
    2. Initialize LiDAR scanning sequence
    3. Calculate draft measurements from scan data
    4. Generate compliance report
    """

    directive_request = DirectiveRequest(
        directive=directive,
        priority=request.priority,
        metadata={
            "operation_type": "barge_scan",
            "barge_id": request.barge_id,
        }
    )

    return await process_directive(directive_request)


# =============================================================================
# RUN SERVER (for local testing)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
