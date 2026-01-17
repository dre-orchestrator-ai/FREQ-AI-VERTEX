"""
FREQ AI - Strategic Synthesis Core (SSC) Lambda Handler
Level 1 - Central Nervous System and Orchestrator

This is the primary entry point for Sovereign Intent directives.
Decomposes high-level directives into DAGs of atomic tasks.
"""

import json
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config

# =============================================================================
# CONFIGURATION
# =============================================================================

NODE_TYPE = os.environ.get("NODE_TYPE", "ssc")
NODE_LEVEL = int(os.environ.get("NODE_LEVEL", "1"))
SUBSTRATE = os.environ.get("SUBSTRATE", "opus-4.5")
SEMANTIC_BUS_QUEUE = os.environ.get("SEMANTIC_BUS_QUEUE", "")
NODE_QUEUE = os.environ.get("NODE_QUEUE", "")
MISSIONS_TABLE = os.environ.get("MISSIONS_TABLE", "")
AUDIT_TABLE = os.environ.get("AUDIT_TABLE", "")
FREQ_LAW_LATENCY = int(os.environ.get("FREQ_LAW_LATENCY", "2000"))

# Bedrock configuration
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
# SSC SYSTEM PROMPT
# =============================================================================

SSC_SYSTEM_PROMPT = """You are the Strategic Synthesis Core (SSC) of the FREQ AI Sophisticated Operational Lattice.

## Your Role
- Level 1 node in the Chain of Command
- Central Nervous System and Orchestrator
- Receive Sovereign Intent from Level 0 (Chief Dre)
- Decompose directives into Directed Acyclic Graphs (DAGs) of atomic tasks

## FREQ LAW Compliance
All operations must satisfy:
- FAST: Complete within 2000ms
- ROBUST: Include error handling and fallbacks
- EVOLUTIONARY: Learn from execution patterns
- QUANTIFIED: Log all decisions to the Cognitive Audit Trail

## Output Format
When decomposing a directive, respond with a JSON structure:
{
    "mission_id": "<uuid>",
    "directive_summary": "<brief summary>",
    "dag": {
        "nodes": [
            {"id": "task_1", "type": "governance_check", "target_node": "CGE", "payload": {...}},
            {"id": "task_2", "type": "data_retrieval", "target_node": "SIL", "depends_on": ["task_1"], "payload": {...}},
            {"id": "task_3", "type": "execution", "target_node": "TOM", "depends_on": ["task_2"], "payload": {...}}
        ]
    },
    "estimated_duration_seconds": <number>,
    "governance_required": true
}

## Maritime Domain Context
For Maritime Barge Drafting (Vector Gamma) missions:
- SCAN: Deploy LiDAR drone to capture hull geometry
- PROCESS: Calculate draft from point cloud data
- REPORT: Generate measurement report with provenance

Always route through CGE (Level 2) for governance validation before execution.
"""

# =============================================================================
# HANDLER
# =============================================================================

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    SSC Lambda handler - Process Sovereign Intent directives.
    """
    start_time = time.time()
    request_id = context.aws_request_id if context else str(uuid.uuid4())

    try:
        # Extract directive from event
        directive = extract_directive(event)

        if not directive:
            return error_response("No directive provided", request_id)

        # Invoke Bedrock to decompose directive
        decomposition = invoke_bedrock_decomposition(directive, request_id)

        # Create mission record
        mission_id = decomposition.get("mission_id", str(uuid.uuid4()))
        create_mission_record(mission_id, directive, decomposition)

        # Route to CGE for governance check
        if decomposition.get("governance_required", True):
            send_to_governance(mission_id, decomposition)

        # Calculate latency and log audit
        latency_ms = (time.time() - start_time) * 1000
        log_audit_entry(
            request_id=request_id,
            operation="decompose_directive",
            mission_id=mission_id,
            latency_ms=latency_ms,
            success=True,
            details={"tasks_created": len(decomposition.get("dag", {}).get("nodes", []))},
        )

        # FREQ LAW compliance check
        freq_compliant = latency_ms < FREQ_LAW_LATENCY

        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "mission_id": mission_id,
                "decomposition": decomposition,
                "latency_ms": round(latency_ms, 2),
                "freq_compliant": freq_compliant,
                "request_id": request_id,
            }),
        }

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        log_audit_entry(
            request_id=request_id,
            operation="decompose_directive",
            mission_id=None,
            latency_ms=latency_ms,
            success=False,
            details={"error": str(e)},
        )
        return error_response(str(e), request_id)


def extract_directive(event: Dict[str, Any]) -> Optional[str]:
    """Extract directive from various event sources."""
    # API Gateway event
    if "body" in event:
        body = event["body"]
        if isinstance(body, str):
            body = json.loads(body)
        return body.get("directive")

    # SQS event
    if "Records" in event:
        for record in event["Records"]:
            if "body" in record:
                body = json.loads(record["body"])
                return body.get("directive")

    # Direct invocation
    return event.get("directive")


def invoke_bedrock_decomposition(directive: str, request_id: str) -> Dict[str, Any]:
    """
    Invoke Bedrock Claude Opus 4.5 to decompose directive into DAG.
    """
    messages = [
        {
            "role": "user",
            "content": f"""Decompose the following Sovereign Intent directive into a task DAG:

DIRECTIVE: {directive}

Respond with the JSON structure as specified in your system prompt.""",
        }
    ]

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": SSC_SYSTEM_PROMPT,
        "messages": messages,
        "temperature": 0.3,  # Lower temperature for consistent decomposition
    }

    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload),
    )

    result = json.loads(response["body"].read())
    content = result.get("content", [{}])[0].get("text", "{}")

    # Parse JSON from response
    try:
        # Try to extract JSON from the response
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            content = content[json_start:json_end].strip()
        elif "{" in content:
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            content = content[json_start:json_end]

        decomposition = json.loads(content)
    except json.JSONDecodeError:
        # Fallback structure if parsing fails
        decomposition = {
            "mission_id": str(uuid.uuid4()),
            "directive_summary": directive[:100],
            "dag": {
                "nodes": [
                    {
                        "id": "task_1",
                        "type": "governance_check",
                        "target_node": "CGE",
                        "payload": {"directive": directive},
                    }
                ]
            },
            "estimated_duration_seconds": 360,
            "governance_required": True,
            "raw_response": content,
        }

    return decomposition


def create_mission_record(
    mission_id: str, directive: str, decomposition: Dict[str, Any]
) -> None:
    """Create mission record in DynamoDB."""
    if not MISSIONS_TABLE:
        return

    table = dynamodb.Table(MISSIONS_TABLE)
    table.put_item(
        Item={
            "mission_id": mission_id,
            "directive": directive,
            "status": "pending_governance",
            "decomposition": decomposition,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
    )


def send_to_governance(mission_id: str, decomposition: Dict[str, Any]) -> None:
    """Send mission to CGE for governance validation via Semantic Bus."""
    if not SEMANTIC_BUS_QUEUE:
        return

    message = {
        "type": "governance_request",
        "source_node": "SSC",
        "target_node": "CGE",
        "mission_id": mission_id,
        "payload": decomposition,
        "timestamp": datetime.utcnow().isoformat(),
    }

    sqs.send_message(
        QueueUrl=SEMANTIC_BUS_QUEUE,
        MessageBody=json.dumps(message),
        MessageGroupId="governance",
        MessageDeduplicationId=f"{mission_id}-gov-{int(time.time())}",
    )


def log_audit_entry(
    request_id: str,
    operation: str,
    mission_id: Optional[str],
    latency_ms: float,
    success: bool,
    details: Dict[str, Any],
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
            "details": details,
        }
    )


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
