"""
FREQ AI - Cognitive Governance Engine (CGE) Lambda Handler
Level 2 - Policy and Guardrail Authority

Enforces FREQ LAW, validates compliance, and holds absolute VETO authority.
Uses strict deterministic configuration for reproducible governance decisions.
"""

import json
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config

# =============================================================================
# CONFIGURATION
# =============================================================================

NODE_TYPE = os.environ.get("NODE_TYPE", "cge")
NODE_LEVEL = int(os.environ.get("NODE_LEVEL", "2"))
SUBSTRATE = os.environ.get("SUBSTRATE", "opus-4.5")
SEMANTIC_BUS_QUEUE = os.environ.get("SEMANTIC_BUS_QUEUE", "")
MISSIONS_TABLE = os.environ.get("MISSIONS_TABLE", "")
AUDIT_TABLE = os.environ.get("AUDIT_TABLE", "")
GOVERNANCE_TABLE = os.environ.get("GOVERNANCE_TABLE", "")
FREQ_LAW_LATENCY = int(os.environ.get("FREQ_LAW_LATENCY", "2000"))

# Bedrock configuration - STRICT MODE for governance
BEDROCK_MODEL_ID = "anthropic.claude-opus-4-5-20251101-v1:0"
BEDROCK_REGION = os.environ.get("AWS_REGION", "us-east-1")

# =============================================================================
# AWS CLIENTS
# =============================================================================

bedrock_config = Config(
    retries={"max_attempts": 3, "mode": "adaptive"},
    connect_timeout=5,
    read_timeout=120,
)

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=BEDROCK_REGION,
    config=bedrock_config,
)
dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

# =============================================================================
# FREQ LAW POLICIES
# =============================================================================

FREQ_LAW_POLICIES = {
    "FAST": {
        "description": "Operations must complete within acceptable latency",
        "max_latency_ms": 2000,
        "warning_threshold_ms": 1500,
    },
    "ROBUST": {
        "description": "Operations must include redundancy and safety mechanisms",
        "min_quorum": 3,
        "require_fallback": True,
        "require_error_handling": True,
    },
    "EVOLUTIONARY": {
        "description": "System must learn from errors and execution patterns",
        "max_retry_attempts": 3,
        "require_reflexion_loop": True,
    },
    "QUANTIFIED": {
        "description": "Every action must be observable and auditable",
        "require_audit_trail": True,
        "min_trust_score": 0.95,
        "require_provenance": True,
    },
}

VETO_REASONS = {
    "SAFETY_VIOLATION": "Operation poses unacceptable safety risk",
    "FREQ_LAW_VIOLATION": "Operation violates FREQ LAW requirements",
    "UNAUTHORIZED_ACTION": "Operation not authorized for this context",
    "RESOURCE_EXHAUSTION": "Insufficient resources to complete safely",
    "POLICY_CONFLICT": "Operation conflicts with established policy",
    "SOVEREIGN_OVERRIDE": "Sovereign has explicitly blocked this operation type",
}

# =============================================================================
# CGE SYSTEM PROMPT
# =============================================================================

CGE_SYSTEM_PROMPT = """You are the Cognitive Governance Engine (CGE) of the FREQ AI Lattice.

## Your Role
- Level 2 node with ABSOLUTE VETO AUTHORITY
- Enforce FREQ LAW compliance for all operations
- Validate mission plans before execution
- Issue VETO when operations violate policy or pose risk

## FREQ LAW Requirements
1. FAST: All operations must complete within 2000ms
2. ROBUST: Must include error handling, fallbacks, and quorum consensus
3. EVOLUTIONARY: Must support self-correction via Reflexion Loop
4. QUANTIFIED: Must log all actions to Cognitive Audit Trail

## Maritime Safety Protocol
For Vector Gamma (Maritime Barge Drafting) operations:
- Human interlocks required for drone deployment
- Environmental conditions must be within safe limits
- Vessel identification must be verified
- No operations during adverse weather

## Decision Format
Respond with a JSON structure:
{
    "decision": "APPROVE" | "VETO" | "CONDITIONAL_APPROVE",
    "confidence": 0.0-1.0,
    "reasoning": "<explanation>",
    "freq_law_compliance": {
        "fast": {"compliant": bool, "note": "..."},
        "robust": {"compliant": bool, "note": "..."},
        "evolutionary": {"compliant": bool, "note": "..."},
        "quantified": {"compliant": bool, "note": "..."}
    },
    "conditions": ["<condition if conditional approval>"],
    "veto_reason": "<if vetoed, the reason code>",
    "governance_hash": "<computed hash for audit>"
}

You must be DETERMINISTIC. Given identical inputs, produce identical outputs.
When in doubt, VETO. Safety is paramount.
"""

# =============================================================================
# HANDLER
# =============================================================================

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    CGE Lambda handler - Validate governance for mission plans.
    """
    start_time = time.time()
    request_id = context.aws_request_id if context else str(uuid.uuid4())

    try:
        # Extract governance request from event
        governance_request = extract_governance_request(event)

        if not governance_request:
            return error_response("No governance request provided", request_id)

        mission_id = governance_request.get("mission_id")
        payload = governance_request.get("payload", {})

        # Pre-validation checks (fast path)
        pre_validation = perform_pre_validation(payload)
        if pre_validation.get("veto"):
            decision = create_veto_decision(
                pre_validation["reason"],
                pre_validation["details"],
            )
            record_decision(mission_id, decision, request_id)
            update_mission_status(mission_id, "vetoed", decision)
            return governance_response(decision, request_id, start_time)

        # Invoke Bedrock for deep governance analysis
        decision = invoke_bedrock_governance(payload, request_id)

        # Record decision
        record_decision(mission_id, decision, request_id)

        # Update mission status
        if decision["decision"] == "APPROVE":
            update_mission_status(mission_id, "approved", decision)
            route_to_execution(mission_id, payload, decision)
        elif decision["decision"] == "CONDITIONAL_APPROVE":
            update_mission_status(mission_id, "conditional", decision)
        else:
            update_mission_status(mission_id, "vetoed", decision)

        # Calculate latency and log audit
        latency_ms = (time.time() - start_time) * 1000
        log_audit_entry(
            request_id=request_id,
            operation="governance_validation",
            mission_id=mission_id,
            latency_ms=latency_ms,
            success=True,
            decision=decision["decision"],
        )

        return governance_response(decision, request_id, start_time)

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        log_audit_entry(
            request_id=request_id,
            operation="governance_validation",
            mission_id=None,
            latency_ms=latency_ms,
            success=False,
            decision="ERROR",
        )
        return error_response(str(e), request_id)


def extract_governance_request(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract governance request from various event sources."""
    # SQS event (from Semantic Bus)
    if "Records" in event:
        for record in event["Records"]:
            if "body" in record:
                return json.loads(record["body"])

    # Direct invocation
    if "mission_id" in event:
        return event

    # Nested in payload
    return event.get("governance_request")


def perform_pre_validation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fast pre-validation checks before invoking Bedrock.
    Returns early VETO for obvious violations.
    """
    dag = payload.get("dag", {})
    nodes = dag.get("nodes", [])

    # Check 1: DAG must have at least one task
    if not nodes:
        return {
            "veto": True,
            "reason": "POLICY_CONFLICT",
            "details": "Mission plan contains no executable tasks",
        }

    # Check 2: Estimated duration must be reasonable
    estimated_duration = payload.get("estimated_duration_seconds", 0)
    if estimated_duration > 3600:  # 1 hour max
        return {
            "veto": True,
            "reason": "RESOURCE_EXHAUSTION",
            "details": f"Estimated duration ({estimated_duration}s) exceeds maximum allowed",
        }

    # Check 3: All target nodes must be valid
    valid_nodes = {"SSC", "CGE", "SIL", "SA", "TOM"}
    for node in nodes:
        target = node.get("target_node", "")
        if target and target not in valid_nodes:
            return {
                "veto": True,
                "reason": "UNAUTHORIZED_ACTION",
                "details": f"Invalid target node: {target}",
            }

    return {"veto": False}


def invoke_bedrock_governance(payload: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    """
    Invoke Bedrock Claude Opus 4.5 in STRICT MODE for governance decision.
    Temperature = 0.0 for deterministic output.
    """
    messages = [
        {
            "role": "user",
            "content": f"""Evaluate the following mission plan for FREQ LAW compliance and governance approval:

MISSION PLAN:
{json.dumps(payload, indent=2)}

Provide your governance decision in the specified JSON format.""",
        }
    ]

    bedrock_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "system": CGE_SYSTEM_PROMPT,
        "messages": messages,
        "temperature": 0.0,  # STRICT MODE - deterministic
        "top_p": 1.0,
    }

    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(bedrock_payload),
    )

    result = json.loads(response["body"].read())
    content = result.get("content", [{}])[0].get("text", "{}")

    # Parse JSON from response
    try:
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            content = content[json_start:json_end].strip()
        elif "{" in content:
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            content = content[json_start:json_end]

        decision = json.loads(content)
    except json.JSONDecodeError:
        # Default to conditional approval if parsing fails
        decision = {
            "decision": "CONDITIONAL_APPROVE",
            "confidence": 0.7,
            "reasoning": "Unable to fully analyze plan; manual review required",
            "freq_law_compliance": {
                "fast": {"compliant": True, "note": "Assumed compliant"},
                "robust": {"compliant": True, "note": "Assumed compliant"},
                "evolutionary": {"compliant": True, "note": "Assumed compliant"},
                "quantified": {"compliant": True, "note": "Assumed compliant"},
            },
            "conditions": ["Manual review required before execution"],
        }

    # Generate governance hash
    decision["governance_hash"] = generate_governance_hash(payload, decision)
    decision["request_id"] = request_id
    decision["timestamp"] = datetime.utcnow().isoformat()

    return decision


def create_veto_decision(reason: str, details: str) -> Dict[str, Any]:
    """Create a VETO decision structure."""
    return {
        "decision": "VETO",
        "confidence": 1.0,
        "reasoning": details,
        "veto_reason": reason,
        "veto_description": VETO_REASONS.get(reason, "Unknown reason"),
        "freq_law_compliance": {
            "fast": {"compliant": False, "note": "Vetoed before evaluation"},
            "robust": {"compliant": False, "note": "Vetoed before evaluation"},
            "evolutionary": {"compliant": False, "note": "Vetoed before evaluation"},
            "quantified": {"compliant": False, "note": "Vetoed before evaluation"},
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


def generate_governance_hash(payload: Dict, decision: Dict) -> str:
    """Generate a hash for governance audit trail."""
    import hashlib

    data = json.dumps({"payload": payload, "decision": decision["decision"]}, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def record_decision(mission_id: str, decision: Dict[str, Any], request_id: str) -> None:
    """Record governance decision in DynamoDB."""
    if not GOVERNANCE_TABLE:
        return

    table = dynamodb.Table(GOVERNANCE_TABLE)
    table.put_item(
        Item={
            "decision_id": f"{mission_id}-{request_id}",
            "mission_id": mission_id,
            "decision": decision["decision"],
            "confidence": str(decision.get("confidence", 0)),
            "reasoning": decision.get("reasoning", ""),
            "governance_hash": decision.get("governance_hash", ""),
            "freq_law_compliance": decision.get("freq_law_compliance", {}),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


def update_mission_status(mission_id: str, status: str, decision: Dict[str, Any]) -> None:
    """Update mission status in DynamoDB."""
    if not MISSIONS_TABLE or not mission_id:
        return

    table = dynamodb.Table(MISSIONS_TABLE)
    table.update_item(
        Key={"mission_id": mission_id},
        UpdateExpression="SET #status = :status, governance_decision = :decision, updated_at = :updated",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":status": status,
            ":decision": decision,
            ":updated": datetime.utcnow().isoformat(),
        },
    )


def route_to_execution(mission_id: str, payload: Dict[str, Any], decision: Dict[str, Any]) -> None:
    """Route approved mission to execution via Semantic Bus."""
    if not SEMANTIC_BUS_QUEUE:
        return

    message = {
        "type": "execution_request",
        "source_node": "CGE",
        "target_node": "TOM",
        "mission_id": mission_id,
        "payload": payload,
        "governance_hash": decision.get("governance_hash"),
        "timestamp": datetime.utcnow().isoformat(),
    }

    sqs.send_message(
        QueueUrl=SEMANTIC_BUS_QUEUE,
        MessageBody=json.dumps(message),
        MessageGroupId="execution",
        MessageDeduplicationId=f"{mission_id}-exec-{int(time.time())}",
    )


def log_audit_entry(
    request_id: str,
    operation: str,
    mission_id: Optional[str],
    latency_ms: float,
    success: bool,
    decision: str,
) -> None:
    """Log entry to Cognitive Audit Trail."""
    if not AUDIT_TABLE:
        return

    table = dynamodb.Table(AUDIT_TABLE)
    table.put_item(
        Item={
            "entry_id": f"{request_id}-{operation}",
            "timestamp": datetime.utcnow().isoformat(),
            "node_type": NODE_TYPE,
            "node_level": NODE_LEVEL,
            "operation": operation,
            "mission_id": mission_id or "none",
            "latency_ms": int(latency_ms),
            "success": success,
            "freq_compliant": latency_ms < FREQ_LAW_LATENCY,
            "governance_decision": decision,
        }
    )


def governance_response(decision: Dict[str, Any], request_id: str, start_time: float) -> Dict[str, Any]:
    """Generate governance response."""
    latency_ms = (time.time() - start_time) * 1000
    return {
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
            "decision": decision,
            "latency_ms": round(latency_ms, 2),
            "freq_compliant": latency_ms < FREQ_LAW_LATENCY,
            "request_id": request_id,
        }),
    }


def error_response(message: str, request_id: str) -> Dict[str, Any]:
    """Generate error response."""
    return {
        "statusCode": 500,
        "body": json.dumps({
            "success": False,
            "error": message,
            "request_id": request_id,
        }),
    }
