"""
Lattice Status Aggregator for Lattice Core

Provides real-time status aggregation and health monitoring
for the entire fleet and Lattice Core system.

Designed for dashboard integration and REQ presentation.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from .bigquery_bridge import BargeState, StabilityStatus


class HealthIndicator(Enum):
    """System-wide health indicator."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    IMPAIRED = "IMPAIRED"
    CRITICAL = "CRITICAL"


@dataclass
class FleetMetrics:
    """Aggregated metrics for the entire fleet."""
    total_vessels: int = 0
    active_vessels: int = 0
    idle_vessels: int = 0

    stable_count: int = 0
    caution_count: int = 0
    warning_count: int = 0
    critical_count: int = 0

    total_cargo_tons: float = 0.0
    total_capacity_tons: float = 0.0
    average_health_score: float = 100.0
    average_draft_percentage: float = 0.0

    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @property
    def capacity_utilization(self) -> float:
        """Calculate fleet capacity utilization percentage."""
        if self.total_capacity_tons <= 0:
            return 0.0
        return (self.total_cargo_tons / self.total_capacity_tons) * 100

    @property
    def fleet_health_indicator(self) -> HealthIndicator:
        """Determine overall fleet health."""
        if self.critical_count > 0:
            return HealthIndicator.CRITICAL
        elif self.warning_count > 0:
            return HealthIndicator.IMPAIRED
        elif self.caution_count > 0:
            return HealthIndicator.DEGRADED
        return HealthIndicator.HEALTHY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "totalVessels": self.total_vessels,
            "activeVessels": self.active_vessels,
            "idleVessels": self.idle_vessels,
            "stableCount": self.stable_count,
            "cautionCount": self.caution_count,
            "warningCount": self.warning_count,
            "criticalCount": self.critical_count,
            "totalCargoTons": round(self.total_cargo_tons, 1),
            "totalCapacityTons": round(self.total_capacity_tons, 1),
            "capacityUtilization": round(self.capacity_utilization, 1),
            "averageHealthScore": round(self.average_health_score, 1),
            "averageDraftPercentage": round(self.average_draft_percentage, 1),
            "fleetHealthIndicator": self.fleet_health_indicator.value,
            "timestamp": self.timestamp,
        }


@dataclass
class SystemStatus:
    """Status of Lattice Core system components."""
    bigquery_connected: bool = False
    supply_chain_twin_connected: bool = False
    iot_core_connected: bool = False
    simulation_running: bool = False

    telemetry_buffer_size: int = 0
    telemetry_rate_per_sec: float = 0.0
    last_telemetry_timestamp: str = ""

    uptime_seconds: float = 0.0
    error_count: int = 0
    last_error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bigqueryConnected": self.bigquery_connected,
            "supplyChainTwinConnected": self.supply_chain_twin_connected,
            "iotCoreConnected": self.iot_core_connected,
            "simulationRunning": self.simulation_running,
            "telemetryBufferSize": self.telemetry_buffer_size,
            "telemetryRatePerSec": round(self.telemetry_rate_per_sec, 2),
            "lastTelemetryTimestamp": self.last_telemetry_timestamp,
            "uptimeSeconds": round(self.uptime_seconds, 1),
            "errorCount": self.error_count,
            "lastError": self.last_error,
        }


class LatticeStatus:
    """
    Central status aggregator for Lattice Core.

    Collects and exposes:
    - Fleet-wide metrics
    - Individual vessel states
    - System component status
    - Health indicators

    Designed for real-time dashboard streaming.

    Usage:
        status = LatticeStatus()

        # Update vessel states
        status.update_vessel(barge_state)

        # Get aggregated status
        dashboard_data = status.get_dashboard_payload()
    """

    def __init__(self):
        """Initialize Lattice Status aggregator."""
        self._vessel_states: Dict[str, BargeState] = {}
        self._fleet_metrics = FleetMetrics()
        self._system_status = SystemStatus()
        self._start_time = datetime.utcnow()
        self._telemetry_count = 0
        self._last_update = datetime.utcnow()

    def update_vessel(self, state: BargeState) -> None:
        """
        Update state for a vessel.

        Args:
            state: BargeState to update
        """
        self._vessel_states[state.barge_id] = state
        self._last_update = datetime.utcnow()
        self._telemetry_count += 1
        self._recalculate_metrics()

    def remove_vessel(self, barge_id: str) -> None:
        """Remove a vessel from tracking."""
        if barge_id in self._vessel_states:
            del self._vessel_states[barge_id]
            self._recalculate_metrics()

    def _recalculate_metrics(self) -> None:
        """Recalculate fleet-wide metrics."""
        states = list(self._vessel_states.values())

        if not states:
            self._fleet_metrics = FleetMetrics()
            return

        metrics = FleetMetrics()
        metrics.total_vessels = len(states)

        status_counts = {
            StabilityStatus.STABLE: 0,
            StabilityStatus.CAUTION: 0,
            StabilityStatus.WARNING: 0,
            StabilityStatus.CRITICAL: 0,
        }

        total_health = 0.0
        total_draft_pct = 0.0
        active_count = 0

        for state in states:
            status_counts[state.stability_status] += 1
            total_health += state.health_score
            total_draft_pct += state.draft_percentage
            metrics.total_cargo_tons += state.cargo_tons
            metrics.total_capacity_tons += state.max_cargo_tons

            if state.operational_mode not in ("IDLE", "MAINTENANCE"):
                active_count += 1

        metrics.active_vessels = active_count
        metrics.idle_vessels = metrics.total_vessels - active_count
        metrics.stable_count = status_counts[StabilityStatus.STABLE]
        metrics.caution_count = status_counts[StabilityStatus.CAUTION]
        metrics.warning_count = status_counts[StabilityStatus.WARNING]
        metrics.critical_count = status_counts[StabilityStatus.CRITICAL]
        metrics.average_health_score = total_health / len(states)
        metrics.average_draft_percentage = total_draft_pct / len(states)
        metrics.timestamp = datetime.utcnow().isoformat() + "Z"

        self._fleet_metrics = metrics

    def update_system_status(
        self,
        bigquery: bool = None,
        supply_chain_twin: bool = None,
        iot_core: bool = None,
        simulation: bool = None,
        buffer_size: int = None,
        error: str = None
    ) -> None:
        """Update system component status."""
        if bigquery is not None:
            self._system_status.bigquery_connected = bigquery
        if supply_chain_twin is not None:
            self._system_status.supply_chain_twin_connected = supply_chain_twin
        if iot_core is not None:
            self._system_status.iot_core_connected = iot_core
        if simulation is not None:
            self._system_status.simulation_running = simulation
        if buffer_size is not None:
            self._system_status.telemetry_buffer_size = buffer_size
        if error:
            self._system_status.error_count += 1
            self._system_status.last_error = error

        # Calculate uptime and telemetry rate
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        self._system_status.uptime_seconds = uptime

        if uptime > 0:
            self._system_status.telemetry_rate_per_sec = self._telemetry_count / uptime

        self._system_status.last_telemetry_timestamp = self._last_update.isoformat() + "Z"

    def get_vessel_state(self, barge_id: str) -> Optional[BargeState]:
        """Get state for a specific vessel."""
        return self._vessel_states.get(barge_id)

    def get_all_vessel_states(self) -> Dict[str, BargeState]:
        """Get all vessel states."""
        return self._vessel_states.copy()

    def get_fleet_metrics(self) -> FleetMetrics:
        """Get current fleet metrics."""
        return self._fleet_metrics

    def get_system_status(self) -> SystemStatus:
        """Get system component status."""
        return self._system_status

    def get_dashboard_payload(self) -> Dict[str, Any]:
        """
        Get complete dashboard payload for Browser Preview.

        Returns:
            Dictionary suitable for JSON streaming to dashboard
        """
        vessels = [
            {
                "bargeId": state.barge_id,
                "vesselName": state.vessel_name,
                "forwardDraft": round(state.forward_draft_m, 3),
                "midshipDraft": round(state.midship_draft_m, 3),
                "aftDraft": round(state.aft_draft_m, 3),
                "trim": round(state.trim_m, 3),
                "list": round(state.list_deg, 2),
                "cargoTons": round(state.cargo_tons, 1),
                "cargoType": state.cargo_type,
                "draftPercentage": round(state.draft_percentage, 1),
                "cargoPercentage": round(state.cargo_percentage, 1),
                "healthScore": round(state.health_score, 1),
                "stabilityStatus": state.stability_status.value,
                "operationalMode": state.operational_mode,
                "latitude": state.latitude,
                "longitude": state.longitude,
            }
            for state in self._vessel_states.values()
        ]

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "fleetMetrics": self._fleet_metrics.to_dict(),
            "systemStatus": self._system_status.to_dict(),
            "vessels": vessels,
        }

    def get_dashboard_json(self) -> str:
        """Get dashboard payload as JSON string."""
        return json.dumps(self.get_dashboard_payload(), indent=2)

    def get_health_indicator(self) -> HealthIndicator:
        """Get overall system health indicator."""
        # Check system components
        if not self._system_status.bigquery_connected:
            return HealthIndicator.IMPAIRED

        if self._system_status.error_count > 10:
            return HealthIndicator.DEGRADED

        # Check fleet health
        return self._fleet_metrics.fleet_health_indicator
