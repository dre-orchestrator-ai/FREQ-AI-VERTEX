"""
FREQ AI API Schemas

Request/response schemas for the FREQ AI Command Center API.
Based on OpenAPI 3.0 specification patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

@dataclass
class SovereignIntentRequest:
    """
    Request to submit a Sovereign Intent directive.

    The Sovereign (Level 0) uses this to issue directives to the lattice.
    Supports natural language (Vibe Coding) and structured commands.
    """

    # Directive content
    directive: str  # Natural language or structured command
    directive_type: str = "natural_language"  # natural_language, structured, vibe_code

    # Mission context
    vector: Optional[str] = None  # alpha, gamma, etc.
    priority: str = "medium"  # critical, high, medium, low

    # Options
    require_governance_review: bool = True
    max_execution_time_seconds: Optional[int] = None
    dry_run: bool = False  # Simulate without executing

    # Metadata
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "directive": self.directive,
            "directiveType": self.directive_type,
            "vector": self.vector,
            "priority": self.priority,
            "options": {
                "requireGovernanceReview": self.require_governance_review,
                "maxExecutionTimeSeconds": self.max_execution_time_seconds,
                "dryRun": self.dry_run,
            },
            "requestId": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class AuditQueryRequest:
    """Request to query the Cognitive Audit Trail."""

    # Time range
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # Filters
    node_types: Optional[List[str]] = None
    event_types: Optional[List[str]] = None
    severities: Optional[List[str]] = None
    mission_id: Optional[str] = None
    success_only: bool = False
    vetoed_only: bool = False
    min_latency_ms: Optional[float] = None
    search_text: Optional[str] = None

    # Pagination
    page: int = 1
    page_size: int = 50

    # Sorting
    sort_by: str = "timestamp"
    sort_order: str = "desc"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timeRange": {
                "startTime": self.start_time.isoformat() if self.start_time else None,
                "endTime": self.end_time.isoformat() if self.end_time else None,
            },
            "filters": {
                "nodeTypes": self.node_types,
                "eventTypes": self.event_types,
                "severities": self.severities,
                "missionId": self.mission_id,
                "successOnly": self.success_only,
                "vetoedOnly": self.vetoed_only,
                "minLatencyMs": self.min_latency_ms,
                "searchText": self.search_text,
            },
            "pagination": {
                "page": self.page,
                "pageSize": self.page_size,
            },
            "sorting": {
                "sortBy": self.sort_by,
                "sortOrder": self.sort_order,
            },
        }


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

@dataclass
class APIResponse:
    """Base API response wrapper."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "errorCode": self.error_code,
            "requestId": self.request_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LatticeStatusResponse:
    """Response containing lattice node statuses."""

    nodes: List[Dict[str, Any]]
    aggregates: Dict[str, Any]
    freq_compliant: bool
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nodes": self.nodes,
            "aggregates": self.aggregates,
            "freqCompliant": self.freq_compliant,
            "lastUpdated": self.last_updated.isoformat(),
        }


@dataclass
class MissionResponse:
    """Response containing mission information."""

    mission_id: str
    status: str
    progress_percent: float
    eta_display: str
    governance: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "missionId": self.mission_id,
            "status": self.status,
            "progressPercent": self.progress_percent,
            "etaDisplay": self.eta_display,
            "governance": self.governance,
            "result": self.result,
        }


@dataclass
class ProviderStatusResponse:
    """Response containing provider statuses."""

    providers: Dict[str, Dict[str, Any]]
    primary_provider: str
    healthy_count: int
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "providers": self.providers,
            "primaryProvider": self.primary_provider,
            "healthyCount": self.healthy_count,
            "totalCount": self.total_count,
        }


@dataclass
class FreqComplianceResponse:
    """Response containing FREQ LAW compliance status."""

    metrics: Dict[str, Dict[str, Any]]
    overall_status: str
    is_compliant: bool
    violations: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metrics": self.metrics,
            "overallStatus": self.overall_status,
            "isCompliant": self.is_compliant,
            "violations": self.violations,
        }


# =============================================================================
# WEBSOCKET MESSAGE SCHEMAS
# =============================================================================

class WebSocketMessageType(Enum):
    """Types of WebSocket messages."""

    # Client -> Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"

    # Server -> Client
    LATTICE_UPDATE = "lattice_update"
    MISSION_UPDATE = "mission_update"
    AUDIT_ENTRY = "audit_entry"
    COMPLIANCE_UPDATE = "compliance_update"
    PROVIDER_UPDATE = "provider_update"
    ERROR = "error"
    PONG = "pong"


@dataclass
class WebSocketMessage:
    """WebSocket message envelope."""

    type: WebSocketMessageType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlationId": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebSocketMessage":
        """Create from dictionary."""
        return cls(
            type=WebSocketMessageType(data.get("type", "error")),
            payload=data.get("payload", {}),
            correlation_id=data.get("correlationId"),
        )
