"""
FREQ AI Audit Timeline Component

Displays the Cognitive Audit Trail with filtering and drill-down.
Visualizes operation history for compliance and debugging.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AuditEventType(Enum):
    """Types of audit events."""
    DIRECTIVE_RECEIVED = "directive_received"
    PLAN_CREATED = "plan_created"
    GOVERNANCE_CHECK = "governance_check"
    QUORUM_VOTE = "quorum_vote"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    VETO_ISSUED = "veto_issued"
    REFLEXION_TRIGGERED = "reflexion_triggered"
    PROVIDER_SWITCH = "provider_switch"
    MISSION_COMPLETED = "mission_completed"


class AuditSeverity(Enum):
    """Severity level of audit events."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """
    Single audit trail entry.

    Follows JSON-LD provenance format for regulatory compliance.
    """

    # Identity
    entry_id: str
    timestamp: datetime

    # Source
    node_id: str
    node_type: str
    node_level: int = 0

    # Event details
    event_type: AuditEventType = AuditEventType.TASK_STARTED
    operation: str = ""
    description: str = ""
    severity: AuditSeverity = AuditSeverity.INFO

    # Context
    mission_id: Optional[str] = None
    request_id: Optional[str] = None
    parent_entry_id: Optional[str] = None

    # Performance
    latency_ms: float = 0.0
    success: bool = True

    # Governance
    governance_hash: Optional[str] = None
    quorum_achieved: bool = False
    was_vetoed: bool = False
    veto_reason: Optional[str] = None

    # Payload (for drill-down)
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_severity_color(self) -> str:
        """Get semantic color for severity."""
        color_map = {
            AuditSeverity.INFO: "info",
            AuditSeverity.SUCCESS: "success",
            AuditSeverity.WARNING: "warning",
            AuditSeverity.ERROR: "danger",
            AuditSeverity.CRITICAL: "danger",
        }
        return color_map.get(self.severity, "neutral")

    def get_status_icon(self) -> str:
        """Get icon for entry status."""
        if self.was_vetoed:
            return "⊘"
        if not self.success:
            return "✗"
        if self.severity == AuditSeverity.WARNING:
            return "⚠"

        icon_map = {
            AuditEventType.DIRECTIVE_RECEIVED: "↓",
            AuditEventType.PLAN_CREATED: "◈",
            AuditEventType.GOVERNANCE_CHECK: "◉",
            AuditEventType.QUORUM_VOTE: "◎",
            AuditEventType.TASK_STARTED: "▸",
            AuditEventType.TASK_COMPLETED: "✓",
            AuditEventType.TASK_FAILED: "✗",
            AuditEventType.VETO_ISSUED: "⊘",
            AuditEventType.REFLEXION_TRIGGERED: "↻",
            AuditEventType.PROVIDER_SWITCH: "⇄",
            AuditEventType.MISSION_COMPLETED: "●",
        }
        return icon_map.get(self.event_type, "○")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "@context": "https://freq.ai/audit/v1",
            "@type": "AuditEntry",
            "entryId": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "source": {
                "nodeId": self.node_id,
                "nodeType": self.node_type,
                "nodeLevel": self.node_level,
            },
            "event": {
                "type": self.event_type.value,
                "operation": self.operation,
                "description": self.description,
                "severity": self.severity.value,
            },
            "context": {
                "missionId": self.mission_id,
                "requestId": self.request_id,
                "parentEntryId": self.parent_entry_id,
            },
            "performance": {
                "latencyMs": self.latency_ms,
                "success": self.success,
            },
            "governance": {
                "hash": self.governance_hash,
                "quorumAchieved": self.quorum_achieved,
                "wasVetoed": self.was_vetoed,
                "vetoReason": self.veto_reason,
            },
            "payload": {
                "inputSummary": self.input_summary,
                "outputSummary": self.output_summary,
                "metadata": self.metadata,
            },
            "display": {
                "severityColor": self.get_severity_color(),
                "statusIcon": self.get_status_icon(),
            },
        }

    def to_table_row(self) -> Dict[str, str]:
        """Format as table row for timeline display."""
        return {
            "time": self.timestamp.strftime("%H:%M:%S"),
            "node": self.node_type,
            "operation": self.operation[:24] if self.operation else "-",
            "status": "OK" if self.success else "FAIL",
            "latency": f"{self.latency_ms:.0f}ms" if self.latency_ms else "-",
            "icon": self.get_status_icon(),
        }


@dataclass
class AuditFilter:
    """Filter criteria for audit entries."""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    node_types: Optional[List[str]] = None
    event_types: Optional[List[AuditEventType]] = None
    severities: Optional[List[AuditSeverity]] = None
    mission_id: Optional[str] = None
    success_only: bool = False
    vetoed_only: bool = False
    min_latency_ms: Optional[float] = None
    search_text: Optional[str] = None

    def matches(self, entry: AuditEntry) -> bool:
        """Check if an entry matches this filter."""
        if self.start_time and entry.timestamp < self.start_time:
            return False
        if self.end_time and entry.timestamp > self.end_time:
            return False
        if self.node_types and entry.node_type not in self.node_types:
            return False
        if self.event_types and entry.event_type not in self.event_types:
            return False
        if self.severities and entry.severity not in self.severities:
            return False
        if self.mission_id and entry.mission_id != self.mission_id:
            return False
        if self.success_only and not entry.success:
            return False
        if self.vetoed_only and not entry.was_vetoed:
            return False
        if self.min_latency_ms and entry.latency_ms < self.min_latency_ms:
            return False
        if self.search_text:
            search = self.search_text.lower()
            if (
                search not in entry.operation.lower()
                and search not in entry.description.lower()
                and search not in entry.node_type.lower()
            ):
                return False

        return True


@dataclass
class AuditTimeline:
    """
    Audit Timeline Widget

    Displays chronological audit trail with filtering and pagination.

    Layout:
    ┌─────────────────────────────────────────────────────────────────────┐
    │  COGNITIVE AUDIT TRAIL                           [Filter▾] [Export] │
    ├─────────────────────────────────────────────────────────────────────┤
    │ TIME       │ NODE │ OPERATION          │ STATUS  │ LATENCY │ DETAIL│
    ├────────────┼──────┼────────────────────┼─────────┼─────────┼───────┤
    │ 14:23:01   │ SSC  │ Decompose DAG      │ ✓ OK    │ 1247ms  │ [View]│
    │ 14:23:02   │ CGE  │ Validate Plan      │ ✓ OK    │  892ms  │ [View]│
    │ 14:23:03   │ TOM  │ Execute Scan       │ ⟳ RUN   │    -    │ [View]│
    └─────────────────────────────────────────────────────────────────────┘
    """

    title: str = "COGNITIVE AUDIT TRAIL"
    entries: List[AuditEntry] = field(default_factory=list)

    # Pagination
    page_size: int = 50
    current_page: int = 1

    # Current filter
    active_filter: Optional[AuditFilter] = None

    # Statistics
    total_entries: int = 0
    success_rate: float = 100.0
    average_latency_ms: float = 0.0

    def add_entry(self, entry: AuditEntry) -> None:
        """Add a new audit entry."""
        self.entries.insert(0, entry)  # Most recent first
        self._update_statistics()

    def get_entries(
        self,
        filter_criteria: Optional[AuditFilter] = None,
        page: Optional[int] = None,
    ) -> List[AuditEntry]:
        """Get filtered and paginated entries."""
        entries = self.entries

        # Apply filter
        if filter_criteria:
            entries = [e for e in entries if filter_criteria.matches(e)]

        # Apply pagination
        if page is not None:
            start = (page - 1) * self.page_size
            end = start + self.page_size
            entries = entries[start:end]

        return entries

    def get_by_mission(self, mission_id: str) -> List[AuditEntry]:
        """Get all entries for a specific mission."""
        return [e for e in self.entries if e.mission_id == mission_id]

    def get_by_node(self, node_type: str) -> List[AuditEntry]:
        """Get all entries for a specific node type."""
        return [e for e in self.entries if e.node_type == node_type]

    def get_recent(self, count: int = 10) -> List[AuditEntry]:
        """Get most recent entries."""
        return self.entries[:count]

    def get_failures(self) -> List[AuditEntry]:
        """Get all failed entries."""
        return [e for e in self.entries if not e.success]

    def get_vetoes(self) -> List[AuditEntry]:
        """Get all vetoed entries."""
        return [e for e in self.entries if e.was_vetoed]

    def _update_statistics(self) -> None:
        """Update aggregate statistics."""
        self.total_entries = len(self.entries)

        if self.entries:
            successful = sum(1 for e in self.entries if e.success)
            self.success_rate = (successful / len(self.entries)) * 100

            latencies = [e.latency_ms for e in self.entries if e.latency_ms > 0]
            if latencies:
                self.average_latency_ms = sum(latencies) / len(latencies)

    def export_to_bigquery_format(self) -> List[Dict[str, Any]]:
        """Export entries in BigQuery-compatible format."""
        return [
            {
                "id": e.entry_id,
                "timestamp": e.timestamp.isoformat(),
                "operation": e.operation,
                "node_id": e.node_id,
                "node_type": e.node_type,
                "execution_time_ms": e.latency_ms,
                "success": e.success,
                "error": e.description if not e.success else None,
                "quorum_achieved": e.quorum_achieved,
                "was_vetoed": e.was_vetoed,
                "metadata": e.metadata,
            }
            for e in self.entries
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert widget state to dictionary."""
        return {
            "title": self.title,
            "pagination": {
                "pageSize": self.page_size,
                "currentPage": self.current_page,
                "totalPages": (self.total_entries + self.page_size - 1) // self.page_size,
            },
            "statistics": {
                "totalEntries": self.total_entries,
                "successRate": self.success_rate,
                "averageLatencyMs": self.average_latency_ms,
                "failureCount": len(self.get_failures()),
                "vetoCount": len(self.get_vetoes()),
            },
            "entries": [e.to_dict() for e in self.get_recent(self.page_size)],
        }

    def render_text(self, limit: int = 10) -> str:
        """Render text representation for CLI/logs."""
        lines = [
            f"{'═' * 75}",
            f"  {self.title}",
            f"{'─' * 75}",
            f" {'TIME':<10} │ {'NODE':<5} │ {'OPERATION':<20} │ {'STATUS':<7} │ {'LATENCY':<8} │",
            f"{'─' * 75}",
        ]

        for entry in self.get_recent(limit):
            row = entry.to_table_row()
            status = f"{row['icon']} {row['status']}"
            lines.append(
                f" {row['time']:<10} │ {row['node']:<5} │ {row['operation']:<20} │ {status:<7} │ {row['latency']:>8} │"
            )

        lines.extend([
            f"{'─' * 75}",
            f" Total: {self.total_entries} entries | Success Rate: {self.success_rate:.1f}% | Avg Latency: {self.average_latency_ms:.0f}ms",
            f"{'═' * 75}",
        ])

        return "\n".join(lines)
