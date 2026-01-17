"""
FREQ AI Compliance Widget

Displays real-time FREQ LAW compliance status.
Shows Fast, Robust, Evolutionary, Quantified metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ComplianceStatus(Enum):
    """Compliance check status."""
    PASSING = "passing"
    WARNING = "warning"
    FAILING = "failing"
    UNKNOWN = "unknown"


@dataclass
class ComplianceMetric:
    """Individual compliance metric."""

    name: str
    description: str
    current_value: Any
    target_value: Any
    unit: str = ""
    status: ComplianceStatus = ComplianceStatus.UNKNOWN
    last_checked: Optional[datetime] = None

    def evaluate(self) -> ComplianceStatus:
        """Evaluate metric status based on current vs target."""
        if self.current_value is None:
            return ComplianceStatus.UNKNOWN

        try:
            if isinstance(self.target_value, (int, float)):
                # Numeric comparison (lower is better for latency, higher for scores)
                if "latency" in self.name.lower() or "time" in self.name.lower():
                    if self.current_value <= self.target_value:
                        return ComplianceStatus.PASSING
                    elif self.current_value <= self.target_value * 1.2:
                        return ComplianceStatus.WARNING
                    return ComplianceStatus.FAILING
                else:
                    if self.current_value >= self.target_value:
                        return ComplianceStatus.PASSING
                    elif self.current_value >= self.target_value * 0.9:
                        return ComplianceStatus.WARNING
                    return ComplianceStatus.FAILING
            elif isinstance(self.target_value, bool):
                return ComplianceStatus.PASSING if self.current_value == self.target_value else ComplianceStatus.FAILING
        except (TypeError, ValueError):
            return ComplianceStatus.UNKNOWN

        return ComplianceStatus.UNKNOWN

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "currentValue": self.current_value,
            "targetValue": self.target_value,
            "unit": self.unit,
            "status": self.status.value,
            "lastChecked": self.last_checked.isoformat() if self.last_checked else None,
        }


@dataclass
class FreqComplianceWidget:
    """
    FREQ LAW Compliance Widget

    Displays compliance with the four FREQ principles:
    - Fast: Response time < 2000ms
    - Robust: BFT active, quorum met
    - Evolutionary: Self-correction active
    - Quantified: Trust score > 0.95

    Layout:
    ┌─────────────────────────────────┐
    │  FREQ COMPLIANCE          [⟳]  │
    │  ─────────────────────────────  │
    │  Fast:    ✓ 1842ms / 2000ms    │
    │  Robust:  ✓ BFT Active (3/3)   │
    │  Evolve:  ✓ 0/3 retries        │
    │  Quant:   ✓ 0.96 / 0.95        │
    │                                 │
    │  Overall: COMPLIANT            │
    └─────────────────────────────────┘
    """

    title: str = "FREQ COMPLIANCE"
    auto_refresh_seconds: int = 10

    # FREQ metrics
    metrics: Dict[str, ComplianceMetric] = field(default_factory=dict)

    # Overall status
    overall_status: ComplianceStatus = ComplianceStatus.UNKNOWN
    last_evaluation: Optional[datetime] = None

    def __post_init__(self):
        """Initialize with default FREQ LAW metrics."""
        if not self.metrics:
            self.metrics = self._create_default_metrics()

    def _create_default_metrics(self) -> Dict[str, ComplianceMetric]:
        """Create default FREQ LAW metrics."""
        return {
            "fast": ComplianceMetric(
                name="FAST",
                description="Response time target",
                current_value=0,
                target_value=2000,
                unit="ms",
            ),
            "robust_bft": ComplianceMetric(
                name="ROBUST (BFT)",
                description="Byzantine Fault Tolerance active",
                current_value=True,
                target_value=True,
            ),
            "robust_quorum": ComplianceMetric(
                name="ROBUST (Quorum)",
                description="Quorum consensus achieved",
                current_value=3,
                target_value=3,
                unit="nodes",
            ),
            "evolutionary": ComplianceMetric(
                name="EVOLUTIONARY",
                description="Reflexion loop retries",
                current_value=0,
                target_value=3,  # Max allowed
                unit="retries",
            ),
            "quantified": ComplianceMetric(
                name="QUANTIFIED",
                description="Trust score threshold",
                current_value=0.95,
                target_value=0.95,
            ),
        }

    def update_metric(self, key: str, current_value: Any) -> None:
        """Update a specific metric value."""
        if key in self.metrics:
            self.metrics[key].current_value = current_value
            self.metrics[key].status = self.metrics[key].evaluate()
            self.metrics[key].last_checked = datetime.now()
            self._evaluate_overall()

    def update_from_lattice_stats(
        self,
        avg_latency_ms: float,
        healthy_nodes: int,
        total_nodes: int,
        retry_count: int,
        trust_score: float,
    ) -> None:
        """Update all metrics from lattice statistics."""
        self.update_metric("fast", avg_latency_ms)
        self.update_metric("robust_quorum", healthy_nodes)
        self.update_metric("evolutionary", retry_count)
        self.update_metric("quantified", trust_score)

    def _evaluate_overall(self) -> None:
        """Evaluate overall compliance status."""
        statuses = [m.evaluate() for m in self.metrics.values()]

        if all(s == ComplianceStatus.PASSING for s in statuses):
            self.overall_status = ComplianceStatus.PASSING
        elif any(s == ComplianceStatus.FAILING for s in statuses):
            self.overall_status = ComplianceStatus.FAILING
        elif any(s == ComplianceStatus.WARNING for s in statuses):
            self.overall_status = ComplianceStatus.WARNING
        else:
            self.overall_status = ComplianceStatus.UNKNOWN

        self.last_evaluation = datetime.now()

    def is_compliant(self) -> bool:
        """Check if system is FREQ LAW compliant."""
        return self.overall_status == ComplianceStatus.PASSING

    def get_violations(self) -> List[ComplianceMetric]:
        """Get list of non-compliant metrics."""
        return [
            m for m in self.metrics.values()
            if m.evaluate() in (ComplianceStatus.FAILING, ComplianceStatus.WARNING)
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert widget state to dictionary."""
        return {
            "title": self.title,
            "autoRefreshSeconds": self.auto_refresh_seconds,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "overallStatus": self.overall_status.value,
            "isCompliant": self.is_compliant(),
            "lastEvaluation": self.last_evaluation.isoformat() if self.last_evaluation else None,
            "violations": [v.to_dict() for v in self.get_violations()],
        }

    def render_text(self) -> str:
        """Render text representation for CLI/logs."""
        lines = [
            f"{'=' * 36}",
            f"  {self.title}",
            f"{'─' * 36}",
        ]

        status_icons = {
            ComplianceStatus.PASSING: "✓",
            ComplianceStatus.WARNING: "⚠",
            ComplianceStatus.FAILING: "✗",
            ComplianceStatus.UNKNOWN: "?",
        }

        for key, metric in self.metrics.items():
            status = metric.evaluate()
            icon = status_icons.get(status, "?")

            if metric.unit:
                value_str = f"{metric.current_value} {metric.unit}"
                target_str = f"{metric.target_value} {metric.unit}"
            else:
                value_str = str(metric.current_value)
                target_str = str(metric.target_value)

            # Format based on metric type
            if isinstance(metric.current_value, bool):
                display = f"{icon} {'Active' if metric.current_value else 'Inactive'}"
            else:
                display = f"{icon} {value_str}"

            lines.append(f"  {metric.name:<12} {display}")

        lines.extend([
            f"{'─' * 36}",
            f"  Overall: {self.overall_status.value.upper()}",
            f"{'=' * 36}",
        ])

        return "\n".join(lines)
