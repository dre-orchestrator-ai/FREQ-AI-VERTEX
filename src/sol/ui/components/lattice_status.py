"""
FREQ AI Lattice Status Widget

Displays real-time status of all lattice nodes.
Follows IBM Carbon dashboard widget patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeHealth(Enum):
    """Node health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    INITIALIZING = "initializing"


@dataclass
class NodeStatus:
    """Status information for a single lattice node."""

    # Identity
    node_id: str
    node_name: str
    abbreviation: str
    level: int

    # Health
    health: NodeHealth = NodeHealth.INITIALIZING
    last_heartbeat: Optional[datetime] = None
    uptime_percentage: float = 100.0

    # Performance
    average_latency_ms: float = 0.0
    requests_processed: int = 0
    errors_count: int = 0

    # Substrate
    current_provider: str = ""
    current_model: str = ""

    # Activity
    current_operation: Optional[str] = None
    queue_depth: int = 0

    def get_status_color(self) -> str:
        """Get the semantic color for this status."""
        color_map = {
            NodeHealth.HEALTHY: "success",
            NodeHealth.DEGRADED: "warning",
            NodeHealth.OFFLINE: "danger",
            NodeHealth.INITIALIZING: "info",
        }
        return color_map.get(self.health, "neutral")

    def get_status_icon(self) -> str:
        """Get the icon name for this status."""
        icon_map = {
            NodeHealth.HEALTHY: "checkmark-filled",
            NodeHealth.DEGRADED: "warning-alt-filled",
            NodeHealth.OFFLINE: "close-filled",
            NodeHealth.INITIALIZING: "in-progress",
        }
        return icon_map.get(self.health, "unknown")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "nodeId": self.node_id,
            "nodeName": self.node_name,
            "abbreviation": self.abbreviation,
            "level": self.level,
            "health": self.health.value,
            "lastHeartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "uptimePercentage": self.uptime_percentage,
            "averageLatencyMs": self.average_latency_ms,
            "requestsProcessed": self.requests_processed,
            "errorsCount": self.errors_count,
            "currentProvider": self.current_provider,
            "currentModel": self.current_model,
            "currentOperation": self.current_operation,
            "queueDepth": self.queue_depth,
            "statusColor": self.get_status_color(),
            "statusIcon": self.get_status_icon(),
        }


@dataclass
class LatticeStatusWidget:
    """
    Lattice Status Widget

    Displays the health and status of all FREQ AI lattice nodes.
    Designed for real-time dashboard display.

    Layout:
    ┌─────────────────────────────────┐
    │  LATTICE STATUS           [⟳]  │
    │  ─────────────────────────────  │
    │  ● SSC    [ACTIVE]     1247ms  │
    │  ● CGE    [ACTIVE]      892ms  │
    │  ● SIL    [ACTIVE]      456ms  │
    │  ● SA     [DEGRADED]   2134ms  │
    │  ● TOM    [ACTIVE]      234ms  │
    │                                 │
    │  Overall: 4/5 Healthy          │
    │  Avg Latency: 993ms            │
    └─────────────────────────────────┘
    """

    # Widget configuration
    title: str = "LATTICE STATUS"
    show_details: bool = True
    auto_refresh_seconds: int = 5

    # Node statuses
    nodes: List[NodeStatus] = field(default_factory=list)

    # Aggregate metrics
    total_nodes: int = 0
    healthy_nodes: int = 0
    overall_latency_ms: float = 0.0

    def __post_init__(self):
        """Initialize with default FREQ AI lattice nodes."""
        if not self.nodes:
            self.nodes = self._create_default_nodes()
        self._update_aggregates()

    def _create_default_nodes(self) -> List[NodeStatus]:
        """Create default node status entries for FREQ AI lattice."""
        return [
            NodeStatus(
                node_id="ssc-001",
                node_name="Strategic Synthesis Core",
                abbreviation="SSC",
                level=1,
                health=NodeHealth.HEALTHY,
                current_provider="aws_bedrock",
                current_model="Claude Opus 4.5",
            ),
            NodeStatus(
                node_id="cge-001",
                node_name="Cognitive Governance Engine",
                abbreviation="CGE",
                level=2,
                health=NodeHealth.HEALTHY,
                current_provider="aws_bedrock",
                current_model="Claude Opus 4.5",
            ),
            NodeStatus(
                node_id="sil-001",
                node_name="Strategic Intelligence Lead",
                abbreviation="SIL",
                level=3,
                health=NodeHealth.HEALTHY,
                current_provider="vertex_ai",
                current_model="Gemini 3.0 Flash",
            ),
            NodeStatus(
                node_id="sa-001",
                node_name="System Architect",
                abbreviation="SA",
                level=4,
                health=NodeHealth.HEALTHY,
                current_provider="vertex_ai",
                current_model="Gemini 3.0 Pro",
            ),
            NodeStatus(
                node_id="tom-001",
                node_name="Runtime Realization Node",
                abbreviation="TOM",
                level=5,
                health=NodeHealth.HEALTHY,
                current_provider="vertex_ai",
                current_model="Gemini 3.0 Flash",
            ),
        ]

    def _update_aggregates(self) -> None:
        """Update aggregate metrics."""
        self.total_nodes = len(self.nodes)
        self.healthy_nodes = sum(
            1 for n in self.nodes if n.health == NodeHealth.HEALTHY
        )

        if self.nodes:
            total_latency = sum(n.average_latency_ms for n in self.nodes)
            self.overall_latency_ms = total_latency / len(self.nodes)

    def update_node(self, node_id: str, **kwargs) -> bool:
        """Update a specific node's status."""
        for node in self.nodes:
            if node.node_id == node_id:
                for key, value in kwargs.items():
                    if hasattr(node, key):
                        setattr(node, key, value)
                self._update_aggregates()
                return True
        return False

    def get_node(self, node_id: str) -> Optional[NodeStatus]:
        """Get a node by ID."""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def get_nodes_by_health(self, health: NodeHealth) -> List[NodeStatus]:
        """Get all nodes with a specific health status."""
        return [n for n in self.nodes if n.health == health]

    def get_overall_health(self) -> NodeHealth:
        """Determine overall lattice health."""
        if all(n.health == NodeHealth.HEALTHY for n in self.nodes):
            return NodeHealth.HEALTHY
        if any(n.health == NodeHealth.OFFLINE for n in self.nodes):
            return NodeHealth.OFFLINE
        if any(n.health == NodeHealth.DEGRADED for n in self.nodes):
            return NodeHealth.DEGRADED
        return NodeHealth.INITIALIZING

    def is_freq_compliant(self) -> bool:
        """Check if lattice meets FREQ LAW requirements."""
        # Fast: All nodes under 2000ms
        if any(n.average_latency_ms > 2000 for n in self.nodes):
            return False

        # Robust: Minimum quorum available
        if self.healthy_nodes < 3:
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert widget state to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "autoRefreshSeconds": self.auto_refresh_seconds,
            "nodes": [n.to_dict() for n in self.nodes],
            "aggregates": {
                "totalNodes": self.total_nodes,
                "healthyNodes": self.healthy_nodes,
                "overallLatencyMs": self.overall_latency_ms,
                "overallHealth": self.get_overall_health().value,
                "freqCompliant": self.is_freq_compliant(),
            },
        }

    def render_text(self) -> str:
        """Render a text representation for CLI/logs."""
        lines = [
            f"{'=' * 40}",
            f"  {self.title}",
            f"{'─' * 40}",
        ]

        for node in sorted(self.nodes, key=lambda n: n.level):
            status_indicator = {
                NodeHealth.HEALTHY: "●",
                NodeHealth.DEGRADED: "◐",
                NodeHealth.OFFLINE: "○",
                NodeHealth.INITIALIZING: "◌",
            }.get(node.health, "?")

            status_text = node.health.value.upper()
            latency = f"{node.average_latency_ms:.0f}ms" if node.average_latency_ms else "-"

            lines.append(
                f"  {status_indicator} {node.abbreviation:<5} [{status_text:<11}] {latency:>8}"
            )

        lines.extend([
            f"{'─' * 40}",
            f"  Overall: {self.healthy_nodes}/{self.total_nodes} Healthy",
            f"  Avg Latency: {self.overall_latency_ms:.0f}ms",
            f"  FREQ Compliant: {'Yes' if self.is_freq_compliant() else 'No'}",
            f"{'=' * 40}",
        ])

        return "\n".join(lines)
