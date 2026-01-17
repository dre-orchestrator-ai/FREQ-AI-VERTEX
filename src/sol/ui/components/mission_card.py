"""
FREQ AI Mission Card Component

Displays status and progress of active missions.
Supports Maritime (Vector Gamma) and Heritage (Vector Alpha) missions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class MissionStatus(Enum):
    """Mission execution status."""
    QUEUED = "queued"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    AWAITING_GOVERNANCE = "awaiting_governance"
    EXECUTING = "executing"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    VETOED = "vetoed"
    CANCELLED = "cancelled"


class MissionVector(Enum):
    """Mission domain/vector."""
    ALPHA = "alpha"  # Heritage Transmutation
    GAMMA = "gamma"  # Maritime Barge Drafting


class MissionPriority(Enum):
    """Mission priority level."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MissionStep:
    """Individual step within a mission."""
    step_id: str
    name: str
    status: MissionStatus = MissionStatus.QUEUED
    progress_percent: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class MissionCard:
    """
    Mission Card Component

    Displays comprehensive mission status including:
    - Mission identification and type
    - Current status and progress
    - Trust score and governance status
    - Estimated time remaining
    - Step-by-step breakdown

    Layout:
    ┌──────────────────────────────────────────┐
    │ ▸ Maritime Barge Draft #2847             │
    │   Vector: GAMMA | Priority: HIGH         │
    │   ─────────────────────────────────────  │
    │   Status: PROCESSING                     │
    │   Progress: ████████░░ 78%               │
    │   ETA: 4m 32s                            │
    │   ─────────────────────────────────────  │
    │   Trust: 0.97 | Quorum: 3/3 | Gov: ✓     │
    └──────────────────────────────────────────┘
    """

    # Mission identity
    mission_id: str
    name: str
    description: str = ""
    vector: MissionVector = MissionVector.GAMMA

    # Status
    status: MissionStatus = MissionStatus.QUEUED
    priority: MissionPriority = MissionPriority.MEDIUM

    # Progress
    progress_percent: float = 0.0
    current_step: Optional[str] = None
    steps: List[MissionStep] = field(default_factory=list)

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration_seconds: int = 360  # 6 minutes default

    # Governance
    trust_score: float = 0.0
    quorum_achieved: bool = False
    quorum_count: int = 0
    quorum_required: int = 3
    governance_approved: bool = False
    veto_reason: Optional[str] = None

    # Results
    result_summary: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def get_eta_seconds(self) -> Optional[int]:
        """Calculate estimated time to completion."""
        if self.status in (
            MissionStatus.COMPLETED,
            MissionStatus.FAILED,
            MissionStatus.VETOED,
            MissionStatus.CANCELLED,
        ):
            return 0

        if self.progress_percent <= 0:
            return self.estimated_duration_seconds

        # Calculate based on progress
        if self.started_at:
            elapsed = (datetime.now() - self.started_at).total_seconds()
            if self.progress_percent > 0:
                total_estimated = elapsed / (self.progress_percent / 100)
                remaining = total_estimated - elapsed
                return max(0, int(remaining))

        return None

    def get_eta_display(self) -> str:
        """Get human-readable ETA string."""
        eta = self.get_eta_seconds()
        if eta is None:
            return "-"
        if eta == 0:
            return "Complete"

        minutes = eta // 60
        seconds = eta % 60

        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def get_status_color(self) -> str:
        """Get semantic color for current status."""
        color_map = {
            MissionStatus.QUEUED: "neutral",
            MissionStatus.INITIALIZING: "info",
            MissionStatus.PROCESSING: "info",
            MissionStatus.AWAITING_GOVERNANCE: "warning",
            MissionStatus.EXECUTING: "info",
            MissionStatus.COMPLETING: "info",
            MissionStatus.COMPLETED: "success",
            MissionStatus.FAILED: "danger",
            MissionStatus.VETOED: "danger",
            MissionStatus.CANCELLED: "neutral",
        }
        return color_map.get(self.status, "neutral")

    def get_progress_bar(self, width: int = 10) -> str:
        """Generate ASCII progress bar."""
        filled = int(self.progress_percent / 100 * width)
        empty = width - filled
        return "█" * filled + "░" * empty

    def update_progress(self, percent: float, step: Optional[str] = None) -> None:
        """Update mission progress."""
        self.progress_percent = min(100, max(0, percent))
        if step:
            self.current_step = step

        if percent > 0 and self.started_at is None:
            self.started_at = datetime.now()

        if percent >= 100:
            self.status = MissionStatus.COMPLETING

    def mark_completed(self, result_summary: str, result_data: Optional[Dict] = None) -> None:
        """Mark mission as completed."""
        self.status = MissionStatus.COMPLETED
        self.progress_percent = 100
        self.completed_at = datetime.now()
        self.result_summary = result_summary
        self.result_data = result_data

    def mark_failed(self, error: str) -> None:
        """Mark mission as failed."""
        self.status = MissionStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error

    def mark_vetoed(self, reason: str) -> None:
        """Mark mission as vetoed by CGE."""
        self.status = MissionStatus.VETOED
        self.completed_at = datetime.now()
        self.veto_reason = reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "missionId": self.mission_id,
            "name": self.name,
            "description": self.description,
            "vector": self.vector.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "progressPercent": self.progress_percent,
            "currentStep": self.current_step,
            "steps": [
                {
                    "stepId": s.step_id,
                    "name": s.name,
                    "status": s.status.value,
                    "progressPercent": s.progress_percent,
                }
                for s in self.steps
            ],
            "timing": {
                "createdAt": self.created_at.isoformat(),
                "startedAt": self.started_at.isoformat() if self.started_at else None,
                "completedAt": self.completed_at.isoformat() if self.completed_at else None,
                "etaSeconds": self.get_eta_seconds(),
                "etaDisplay": self.get_eta_display(),
            },
            "governance": {
                "trustScore": self.trust_score,
                "quorumAchieved": self.quorum_achieved,
                "quorumCount": self.quorum_count,
                "quorumRequired": self.quorum_required,
                "approved": self.governance_approved,
                "vetoReason": self.veto_reason,
            },
            "result": {
                "summary": self.result_summary,
                "data": self.result_data,
                "error": self.error_message,
            },
            "display": {
                "statusColor": self.get_status_color(),
                "progressBar": self.get_progress_bar(),
            },
        }

    def render_text(self) -> str:
        """Render text representation for CLI/logs."""
        vector_name = {
            MissionVector.ALPHA: "Heritage",
            MissionVector.GAMMA: "Maritime",
        }.get(self.vector, "Unknown")

        status_icon = {
            MissionStatus.QUEUED: "○",
            MissionStatus.PROCESSING: "⟳",
            MissionStatus.COMPLETED: "●",
            MissionStatus.FAILED: "✗",
            MissionStatus.VETOED: "⊘",
        }.get(self.status, "○")

        gov_icon = "✓" if self.governance_approved else "○"

        lines = [
            f"┌{'─' * 44}┐",
            f"│ {status_icon} {self.name[:38]:<38} │",
            f"│   Vector: {vector_name:<8} | Priority: {self.priority.value.upper():<8} │",
            f"├{'─' * 44}┤",
            f"│   Status: {self.status.value.upper():<32} │",
            f"│   Progress: {self.get_progress_bar()} {self.progress_percent:>3.0f}%{' ' * 14} │",
            f"│   ETA: {self.get_eta_display():<36} │",
            f"├{'─' * 44}┤",
            f"│   Trust: {self.trust_score:.2f} | Quorum: {self.quorum_count}/{self.quorum_required} | Gov: {gov_icon}    │",
            f"└{'─' * 44}┘",
        ]

        return "\n".join(lines)


@dataclass
class MissionList:
    """Collection of mission cards with filtering."""

    missions: List[MissionCard] = field(default_factory=list)

    def add(self, mission: MissionCard) -> None:
        """Add a mission to the list."""
        self.missions.append(mission)

    def get_by_id(self, mission_id: str) -> Optional[MissionCard]:
        """Get mission by ID."""
        for m in self.missions:
            if m.mission_id == mission_id:
                return m
        return None

    def get_active(self) -> List[MissionCard]:
        """Get all active (non-terminal) missions."""
        terminal = {
            MissionStatus.COMPLETED,
            MissionStatus.FAILED,
            MissionStatus.VETOED,
            MissionStatus.CANCELLED,
        }
        return [m for m in self.missions if m.status not in terminal]

    def get_by_vector(self, vector: MissionVector) -> List[MissionCard]:
        """Get missions by vector type."""
        return [m for m in self.missions if m.vector == vector]

    def get_by_status(self, status: MissionStatus) -> List[MissionCard]:
        """Get missions by status."""
        return [m for m in self.missions if m.status == status]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total": len(self.missions),
            "active": len(self.get_active()),
            "missions": [m.to_dict() for m in self.missions],
        }
