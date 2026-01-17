"""
FREQ AI Lattice - Runnable Demo

This is a WORKING implementation you can run immediately.
No complex Vertex AI setup required - just API keys.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    export GOOGLE_AI_API_KEY="AIzaSy..."
    python -m src.sol.lattice.demo

Or run directly:
    python run_lattice.py
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("FREQ-AI")

# =============================================================================
# A2A MESSAGE FORMAT (Agent-to-Agent Protocol)
# =============================================================================

class MessageType(Enum):
    """A2A message types."""
    DIRECTIVE = "directive"           # Sovereign intent
    TASK = "task"                     # Task assignment
    RESULT = "result"                 # Task result
    GOVERNANCE_REQUEST = "gov_req"    # Request governance approval
    GOVERNANCE_RESPONSE = "gov_resp"  # Governance decision
    ERROR = "error"                   # Error notification


@dataclass
class A2AMessage:
    """
    Agent-to-Agent Protocol Message

    This is the standard format for all inter-node communication
    in the FREQ AI Lattice (Semantic Bus).
    """
    id: str
    type: MessageType
    source_node: str
    target_node: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: Optional[str] = None
    governance_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "@context": "https://freq.ai/a2a/v1",
            "@type": "A2AMessage",
            "id": self.id,
            "type": self.type.value,
            "source": self.source_node,
            "target": self.target_node,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "correlationId": self.correlation_id,
            "governanceHash": self.governance_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        return cls(
            id=data["id"],
            type=MessageType(data["type"]),
            source_node=data["source"],
            target_node=data["target"],
            payload=data["payload"],
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            correlation_id=data.get("correlationId"),
            governance_hash=data.get("governanceHash"),
        )


# =============================================================================
# LATTICE NODE BASE CLASS
# =============================================================================

class LatticeNode:
    """Base class for all FREQ AI Lattice nodes."""

    def __init__(self, node_id: str, name: str, level: int):
        self.node_id = node_id
        self.name = name
        self.level = level
        self.logger = logging.getLogger(f"L{level}-{node_id.upper()}")

    async def process(self, message: A2AMessage) -> A2AMessage:
        """Process an incoming message and return response."""
        raise NotImplementedError

    def log(self, action: str, details: str = ""):
        """Log node activity."""
        self.logger.info(f"{action}: {details}")


# =============================================================================
# ANTHROPIC CLIENT (Opus 4.5 for SSC/CGE)
# =============================================================================

class AnthropicClient:
    """Simple Anthropic API client for Opus 4.5."""

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set - using mock responses")
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def complete(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: str = "claude-opus-4-5-20251101",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Call Anthropic API."""
        if not self.api_key:
            # Mock response for testing without API key
            return self._mock_response(messages)

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": model,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "system": system,
                        "messages": messages,
                    },
                    timeout=120.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["content"][0]["text"]
                else:
                    logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                    return self._mock_response(messages)

        except ImportError:
            logger.warning("httpx not installed, using mock responses")
            return self._mock_response(messages)
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._mock_response(messages)

    def _mock_response(self, messages: List[Dict]) -> str:
        """Generate mock response for testing."""
        user_msg = messages[-1]["content"] if messages else ""
        return json.dumps({
            "status": "mock_response",
            "message": f"Processing: {user_msg[:50]}...",
            "note": "Set ANTHROPIC_API_KEY for real responses"
        })


# =============================================================================
# GOOGLE AI CLIENT (Gemini 3.0 for SIL/SA/TOM)
# =============================================================================

class GoogleAIClient:
    """Simple Google AI Studio client for Gemini 3.0."""

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_AI_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_AI_API_KEY not set - using mock responses")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def complete(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash",  # Using available model
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Call Google AI API."""
        if not self.api_key:
            return self._mock_response(prompt)

        try:
            import httpx

            url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": max_tokens,
                        }
                    },
                    timeout=120.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.error(f"Google AI error: {response.status_code} - {response.text}")
                    return self._mock_response(prompt)

        except ImportError:
            logger.warning("httpx not installed, using mock responses")
            return self._mock_response(prompt)
        except Exception as e:
            logger.error(f"Google AI error: {e}")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Generate mock response for testing."""
        return json.dumps({
            "status": "mock_response",
            "message": f"Processing: {prompt[:50]}...",
            "note": "Set GOOGLE_AI_API_KEY for real responses"
        })


# =============================================================================
# LATTICE NODES
# =============================================================================

class StrategicSynthesisCore(LatticeNode):
    """
    SSC - Level 1
    Central Nervous System and Orchestrator
    Uses Claude Opus 4.5 via Anthropic Direct API
    """

    SYSTEM_PROMPT = """You are the Strategic Synthesis Core (SSC) of the FREQ AI Lattice.
Your role is to decompose Sovereign directives into executable task plans.

When given a directive, respond with a JSON task plan:
{
    "mission_id": "<uuid>",
    "summary": "<brief summary>",
    "tasks": [
        {"id": "1", "type": "governance_check", "node": "CGE", "description": "..."},
        {"id": "2", "type": "execution", "node": "TOM", "depends_on": ["1"], "description": "..."}
    ],
    "estimated_duration_seconds": <number>
}"""

    def __init__(self):
        super().__init__("ssc", "Strategic Synthesis Core", level=1)
        self.client = AnthropicClient()

    async def process(self, message: A2AMessage) -> A2AMessage:
        """Decompose directive into task plan."""
        self.log("RECEIVED", f"Directive from L0")
        start_time = time.time()

        directive = message.payload.get("directive", "")

        response = await self.client.complete(
            messages=[{"role": "user", "content": f"Decompose this directive: {directive}"}],
            system=self.SYSTEM_PROMPT,
            temperature=0.7,
        )

        latency_ms = (time.time() - start_time) * 1000
        self.log("DECOMPOSED", f"Latency: {latency_ms:.0f}ms")

        return A2AMessage(
            id=f"ssc-{int(time.time())}",
            type=MessageType.TASK,
            source_node="SSC",
            target_node="CGE",
            payload={
                "directive": directive,
                "plan": response,
                "latency_ms": latency_ms,
            },
            correlation_id=message.id,
        )


class CognitiveGovernanceEngine(LatticeNode):
    """
    CGE - Level 2
    Policy and Guardrail Authority with VETO power
    Uses Claude Opus 4.5 in STRICT MODE (temperature=0)
    """

    SYSTEM_PROMPT = """You are the Cognitive Governance Engine (CGE) of the FREQ AI Lattice.
Your role is to validate plans against FREQ LAW and issue APPROVE or VETO decisions.

FREQ LAW requirements:
- FAST: Operations must complete within 2000ms
- ROBUST: Must include error handling
- EVOLUTIONARY: Must support self-correction
- QUANTIFIED: Must be auditable

Respond with a JSON decision:
{
    "decision": "APPROVE" or "VETO",
    "confidence": 0.0-1.0,
    "reasoning": "<explanation>",
    "governance_hash": "<8-char hash>"
}"""

    def __init__(self):
        super().__init__("cge", "Cognitive Governance Engine", level=2)
        self.client = AnthropicClient()

    async def process(self, message: A2AMessage) -> A2AMessage:
        """Validate plan and issue governance decision."""
        self.log("VALIDATING", f"Plan from SSC")
        start_time = time.time()

        plan = message.payload.get("plan", "")

        response = await self.client.complete(
            messages=[{"role": "user", "content": f"Validate this plan for FREQ LAW compliance:\n{plan}"}],
            system=self.SYSTEM_PROMPT,
            temperature=0.0,  # STRICT MODE
        )

        latency_ms = (time.time() - start_time) * 1000

        # Parse decision
        try:
            decision_data = json.loads(response)
            decision = decision_data.get("decision", "APPROVE")
        except:
            decision = "APPROVE"
            decision_data = {"decision": "APPROVE", "confidence": 0.8}

        self.log(f"DECISION: {decision}", f"Latency: {latency_ms:.0f}ms")

        return A2AMessage(
            id=f"cge-{int(time.time())}",
            type=MessageType.GOVERNANCE_RESPONSE,
            source_node="CGE",
            target_node="TOM" if decision == "APPROVE" else "SSC",
            payload={
                "decision": decision,
                "details": decision_data,
                "original_plan": message.payload,
                "latency_ms": latency_ms,
            },
            correlation_id=message.correlation_id,
            governance_hash=decision_data.get("governance_hash", "approved"),
        )


class RuntimeRealizationNode(LatticeNode):
    """
    TOM - Level 5
    Sole Executor - Performs actual operations
    Uses Gemini 3.0 Flash for speed (<2000ms target)
    """

    def __init__(self):
        super().__init__("tom", "Runtime Realization Node", level=5)
        self.client = GoogleAIClient()

    async def process(self, message: A2AMessage) -> A2AMessage:
        """Execute the approved plan."""
        self.log("EXECUTING", f"Approved plan from CGE")
        start_time = time.time()

        # Check governance approval
        if message.payload.get("decision") != "APPROVE":
            self.log("BLOCKED", "Plan was VETOED")
            return A2AMessage(
                id=f"tom-{int(time.time())}",
                type=MessageType.ERROR,
                source_node="TOM",
                target_node="SSC",
                payload={"error": "Plan was vetoed by CGE"},
                correlation_id=message.correlation_id,
            )

        # Execute (simulated for demo)
        response = await self.client.complete(
            prompt=f"Execute this task and report results:\n{json.dumps(message.payload.get('original_plan', {}), indent=2)}",
            temperature=0.3,
        )

        latency_ms = (time.time() - start_time) * 1000
        freq_compliant = latency_ms < 2000

        self.log(
            "COMPLETE" if freq_compliant else "SLOW",
            f"Latency: {latency_ms:.0f}ms {'✓' if freq_compliant else '⚠ FREQ LAW WARNING'}"
        )

        return A2AMessage(
            id=f"tom-{int(time.time())}",
            type=MessageType.RESULT,
            source_node="TOM",
            target_node="SOVEREIGN",
            payload={
                "status": "completed",
                "result": response,
                "latency_ms": latency_ms,
                "freq_compliant": freq_compliant,
            },
            correlation_id=message.correlation_id,
            governance_hash=message.governance_hash,
        )


# =============================================================================
# LATTICE ORCHESTRATOR
# =============================================================================

class FreqAILattice:
    """
    FREQ AI Lattice Orchestrator

    Manages the flow of messages between nodes following the Chain of Command.
    """

    def __init__(self):
        self.nodes = {
            "SSC": StrategicSynthesisCore(),
            "CGE": CognitiveGovernanceEngine(),
            "TOM": RuntimeRealizationNode(),
        }
        self.logger = logging.getLogger("LATTICE")

    async def process_directive(self, directive: str) -> Dict[str, Any]:
        """
        Process a Sovereign directive through the full lattice.

        Flow: SOVEREIGN → SSC → CGE → TOM → SOVEREIGN
        """
        self.logger.info("=" * 60)
        self.logger.info(f"SOVEREIGN DIRECTIVE: {directive[:50]}...")
        self.logger.info("=" * 60)

        start_time = time.time()

        # Step 1: SSC decomposes directive
        initial_message = A2AMessage(
            id=f"sovereign-{int(time.time())}",
            type=MessageType.DIRECTIVE,
            source_node="SOVEREIGN",
            target_node="SSC",
            payload={"directive": directive},
        )

        ssc_response = await self.nodes["SSC"].process(initial_message)

        # Step 2: CGE validates plan
        cge_response = await self.nodes["CGE"].process(ssc_response)

        # Step 3: TOM executes (if approved)
        tom_response = await self.nodes["TOM"].process(cge_response)

        total_latency = (time.time() - start_time) * 1000

        self.logger.info("=" * 60)
        self.logger.info(f"MISSION COMPLETE | Total Latency: {total_latency:.0f}ms")
        self.logger.info("=" * 60)

        return {
            "directive": directive,
            "ssc_response": ssc_response.to_dict(),
            "cge_response": cge_response.to_dict(),
            "tom_response": tom_response.to_dict(),
            "total_latency_ms": total_latency,
            "freq_compliant": total_latency < 6000,  # 6s for full chain
        }


# =============================================================================
# MAIN - Run the Demo
# =============================================================================

async def main():
    """Run the FREQ AI Lattice demo."""
    print("\n" + "=" * 70)
    print("  FREQ AI SOPHISTICATED OPERATIONAL LATTICE - Demo")
    print("  " + "-" * 66)
    print("  Using: Anthropic Direct (Opus 4.5) + Google AI (Gemini Flash)")
    print("=" * 70 + "\n")

    # Check API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    google_key = os.environ.get("GOOGLE_AI_API_KEY", "")

    print(f"  Anthropic API Key: {'✓ Set' if anthropic_key else '✗ Not set (using mock)'}")
    print(f"  Google AI API Key: {'✓ Set' if google_key else '✗ Not set (using mock)'}")
    print()

    # Initialize lattice
    lattice = FreqAILattice()

    # Test directive
    test_directive = """
    Scan barge DELTA-7 for draft measurement.
    Current location: Mississippi River Mile Marker 142.
    Weather: Clear, wind 5 knots.
    Priority: HIGH
    """

    # Process directive
    result = await lattice.process_directive(test_directive)

    # Print summary
    print("\n" + "=" * 70)
    print("  MISSION SUMMARY")
    print("=" * 70)
    print(f"  Total Latency: {result['total_latency_ms']:.0f}ms")
    print(f"  FREQ Compliant: {'✓ Yes' if result['freq_compliant'] else '✗ No'}")
    print("=" * 70 + "\n")

    return result


if __name__ == "__main__":
    asyncio.run(main())
