"""
BigQuery Bridge for Lattice Core

Pipes sensor data from IoT Core into BigQuery barge_intelligence dataset.
Replaces Azure Digital Twin telemetry with real-time BigQuery streaming.

Target Dataset: barge_intelligence
Tables:
    - sensor_telemetry: Raw sensor readings
    - draft_measurements: Computed draft readings
    - barge_state: Current vessel state snapshots
    - stability_events: Alerts and anomalies
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from enum import Enum


class MeasurementType(Enum):
    """Types of measurements in the telemetry stream."""
    DRAFT_FORWARD = "DRAFT_FORWARD"
    DRAFT_MIDSHIP = "DRAFT_MIDSHIP"
    DRAFT_AFT = "DRAFT_AFT"
    TRIM = "TRIM"
    LIST = "LIST"
    CARGO_WEIGHT = "CARGO_WEIGHT"
    WATER_TEMP = "WATER_TEMP"
    SALINITY = "SALINITY"
    GPS_POSITION = "GPS_POSITION"


class StabilityStatus(Enum):
    """Vessel stability classification."""
    STABLE = "STABLE"
    CAUTION = "CAUTION"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class TelemetryRecord:
    """
    Single telemetry record for BigQuery streaming insert.

    Maps to barge_intelligence.sensor_telemetry table.
    """
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    barge_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    sensor_id: str = ""
    measurement_type: MeasurementType = MeasurementType.DRAFT_MIDSHIP
    value: float = 0.0
    unit: str = ""
    quality_score: float = 1.0
    source: str = "IOT_CORE"

    def to_bigquery_row(self) -> Dict[str, Any]:
        """Convert to BigQuery row format."""
        return {
            "record_id": self.record_id,
            "barge_id": self.barge_id,
            "timestamp": self.timestamp,
            "sensor_id": self.sensor_id,
            "measurement_type": self.measurement_type.value,
            "value": self.value,
            "unit": self.unit,
            "quality_score": self.quality_score,
            "source": self.source,
        }


@dataclass
class BargeState:
    """
    Current state of a barge in the Lattice.

    Maps to barge_intelligence.barge_state table.
    """
    barge_id: str = ""
    vessel_name: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    # Draft measurements
    forward_draft_m: float = 0.0
    midship_draft_m: float = 0.0
    aft_draft_m: float = 0.0

    # Computed values
    trim_m: float = 0.0
    list_deg: float = 0.0

    # Cargo
    cargo_tons: float = 0.0
    cargo_type: str = "UNKNOWN"

    # Environment
    water_temp_c: float = 20.0
    salinity_ppt: float = 32.0

    # Position
    latitude: float = 0.0
    longitude: float = 0.0

    # Status
    stability_status: StabilityStatus = StabilityStatus.STABLE
    operational_mode: str = "IDLE"

    # Vessel specs
    max_draft_m: float = 3.8
    max_cargo_tons: float = 2200.0

    @property
    def draft_percentage(self) -> float:
        """Percentage of max draft being used."""
        if self.max_draft_m <= 0:
            return 0.0
        return (self.midship_draft_m / self.max_draft_m) * 100

    @property
    def cargo_percentage(self) -> float:
        """Percentage of cargo capacity being used."""
        if self.max_cargo_tons <= 0:
            return 0.0
        return (self.cargo_tons / self.max_cargo_tons) * 100

    @property
    def health_score(self) -> float:
        """
        Compute overall health score (0-100).

        Based on:
        - Draft safety margin
        - Trim within limits
        - List within limits
        """
        score = 100.0

        # Draft penalty: reduce score as we approach max
        if self.draft_percentage > 90:
            score -= (self.draft_percentage - 90) * 2

        # Trim penalty: each 0.1m over 0.2m reduces score
        if abs(self.trim_m) > 0.2:
            score -= (abs(self.trim_m) - 0.2) * 50

        # List penalty: each 0.5 deg over 1.0 deg reduces score
        if abs(self.list_deg) > 1.0:
            score -= (abs(self.list_deg) - 1.0) * 20

        return max(0.0, min(100.0, score))

    def compute_stability_status(self) -> StabilityStatus:
        """Determine stability status from current state."""
        health = self.health_score

        if health >= 85:
            return StabilityStatus.STABLE
        elif health >= 70:
            return StabilityStatus.CAUTION
        elif health >= 50:
            return StabilityStatus.WARNING
        else:
            return StabilityStatus.CRITICAL

    def to_bigquery_row(self) -> Dict[str, Any]:
        """Convert to BigQuery row format."""
        return {
            "barge_id": self.barge_id,
            "vessel_name": self.vessel_name,
            "timestamp": self.timestamp,
            "forward_draft_m": self.forward_draft_m,
            "midship_draft_m": self.midship_draft_m,
            "aft_draft_m": self.aft_draft_m,
            "trim_m": self.trim_m,
            "list_deg": self.list_deg,
            "cargo_tons": self.cargo_tons,
            "cargo_type": self.cargo_type,
            "water_temp_c": self.water_temp_c,
            "salinity_ppt": self.salinity_ppt,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "stability_status": self.stability_status.value,
            "operational_mode": self.operational_mode,
            "draft_percentage": self.draft_percentage,
            "cargo_percentage": self.cargo_percentage,
            "health_score": self.health_score,
        }

    def to_telemetry_json(self) -> str:
        """Convert to JSON for dashboard streaming."""
        return json.dumps({
            **self.to_bigquery_row(),
            "max_draft_m": self.max_draft_m,
            "max_cargo_tons": self.max_cargo_tons,
        })


class BigQueryBridge:
    """
    Bridge for streaming sensor data to BigQuery barge_intelligence dataset.

    Provides:
    - Real-time telemetry streaming
    - Batch upload for historical data
    - State snapshot management
    - Event detection and alerting

    Usage:
        bridge = BigQueryBridge(project_id="my-gcp-project")
        bridge.initialize_tables()

        # Stream telemetry
        bridge.stream_telemetry(TelemetryRecord(
            barge_id="BARGE-DELTA-001",
            measurement_type=MeasurementType.DRAFT_MIDSHIP,
            value=2.85,
            unit="meters"
        ))

        # Update barge state
        bridge.update_barge_state(barge_state)
    """

    # BigQuery schema definitions
    TELEMETRY_SCHEMA = [
        {"name": "record_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "barge_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "sensor_id", "type": "STRING", "mode": "NULLABLE"},
        {"name": "measurement_type", "type": "STRING", "mode": "REQUIRED"},
        {"name": "value", "type": "FLOAT64", "mode": "REQUIRED"},
        {"name": "unit", "type": "STRING", "mode": "REQUIRED"},
        {"name": "quality_score", "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "source", "type": "STRING", "mode": "NULLABLE"},
    ]

    BARGE_STATE_SCHEMA = [
        {"name": "barge_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "vessel_name", "type": "STRING", "mode": "NULLABLE"},
        {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "forward_draft_m", "type": "FLOAT64", "mode": "REQUIRED"},
        {"name": "midship_draft_m", "type": "FLOAT64", "mode": "REQUIRED"},
        {"name": "aft_draft_m", "type": "FLOAT64", "mode": "REQUIRED"},
        {"name": "trim_m", "type": "FLOAT64", "mode": "REQUIRED"},
        {"name": "list_deg", "type": "FLOAT64", "mode": "REQUIRED"},
        {"name": "cargo_tons", "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "cargo_type", "type": "STRING", "mode": "NULLABLE"},
        {"name": "water_temp_c", "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "salinity_ppt", "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "latitude", "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "longitude", "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "stability_status", "type": "STRING", "mode": "REQUIRED"},
        {"name": "operational_mode", "type": "STRING", "mode": "NULLABLE"},
        {"name": "draft_percentage", "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "cargo_percentage", "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "health_score", "type": "FLOAT64", "mode": "NULLABLE"},
    ]

    def __init__(
        self,
        project_id: str = "",
        dataset_id: str = "barge_intelligence",
        location: str = "US"
    ):
        """
        Initialize BigQuery Bridge.

        Args:
            project_id: GCP project ID (uses default if empty)
            dataset_id: BigQuery dataset ID
            location: BigQuery dataset location
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.location = location
        self._client = None
        self._buffer: List[TelemetryRecord] = []
        self._buffer_size = 100
        self._barge_states: Dict[str, BargeState] = {}
        self._callbacks: Dict[str, List[Callable]] = {
            "on_telemetry": [],
            "on_state_change": [],
            "on_stability_alert": [],
        }

    @property
    def full_dataset_id(self) -> str:
        """Get fully qualified dataset ID."""
        return f"{self.project_id}.{self.dataset_id}"

    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for bridge events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit(self, event: str, *args, **kwargs) -> None:
        """Emit event to registered callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass

    def initialize_tables(self) -> Dict[str, str]:
        """
        Generate DDL for creating BigQuery tables.

        Returns:
            Dictionary of table names to DDL statements
        """
        ddl_statements = {}

        # Sensor telemetry table
        ddl_statements["sensor_telemetry"] = f"""
CREATE TABLE IF NOT EXISTS `{self.full_dataset_id}.sensor_telemetry` (
    record_id STRING NOT NULL,
    barge_id STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    sensor_id STRING,
    measurement_type STRING NOT NULL,
    value FLOAT64 NOT NULL,
    unit STRING NOT NULL,
    quality_score FLOAT64,
    source STRING
)
PARTITION BY DATE(timestamp)
CLUSTER BY barge_id, measurement_type
OPTIONS(
    description='Real-time sensor telemetry from IoT Core',
    labels=[('system', 'lattice_core'), ('data_type', 'telemetry')]
);
"""

        # Barge state table
        ddl_statements["barge_state"] = f"""
CREATE TABLE IF NOT EXISTS `{self.full_dataset_id}.barge_state` (
    barge_id STRING NOT NULL,
    vessel_name STRING,
    timestamp TIMESTAMP NOT NULL,
    forward_draft_m FLOAT64 NOT NULL,
    midship_draft_m FLOAT64 NOT NULL,
    aft_draft_m FLOAT64 NOT NULL,
    trim_m FLOAT64 NOT NULL,
    list_deg FLOAT64 NOT NULL,
    cargo_tons FLOAT64,
    cargo_type STRING,
    water_temp_c FLOAT64,
    salinity_ppt FLOAT64,
    latitude FLOAT64,
    longitude FLOAT64,
    stability_status STRING NOT NULL,
    operational_mode STRING,
    draft_percentage FLOAT64,
    cargo_percentage FLOAT64,
    health_score FLOAT64
)
PARTITION BY DATE(timestamp)
CLUSTER BY barge_id, stability_status
OPTIONS(
    description='Barge state snapshots for Lattice Core',
    labels=[('system', 'lattice_core'), ('data_type', 'state')]
);
"""

        # Stability events table
        ddl_statements["stability_events"] = f"""
CREATE TABLE IF NOT EXISTS `{self.full_dataset_id}.stability_events` (
    event_id STRING NOT NULL,
    barge_id STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    event_type STRING NOT NULL,
    severity STRING NOT NULL,
    previous_status STRING,
    new_status STRING,
    health_score FLOAT64,
    message STRING,
    metadata JSON
)
PARTITION BY DATE(timestamp)
CLUSTER BY barge_id, severity
OPTIONS(
    description='Stability alerts and events for Lattice Core',
    labels=[('system', 'lattice_core'), ('data_type', 'events')]
);
"""

        return ddl_statements

    def stream_telemetry(self, record: TelemetryRecord) -> str:
        """
        Stream a telemetry record to BigQuery.

        Args:
            record: TelemetryRecord to stream

        Returns:
            Record ID
        """
        self._buffer.append(record)
        self._emit("on_telemetry", record)

        # Auto-flush if buffer is full
        if len(self._buffer) >= self._buffer_size:
            self.flush_buffer()

        return record.record_id

    def stream_batch(self, records: List[TelemetryRecord]) -> int:
        """
        Stream a batch of telemetry records.

        Args:
            records: List of TelemetryRecords

        Returns:
            Number of records streamed
        """
        for record in records:
            self.stream_telemetry(record)
        return len(records)

    def flush_buffer(self) -> int:
        """
        Flush buffered records to BigQuery.

        Returns:
            Number of records flushed
        """
        if not self._buffer:
            return 0

        count = len(self._buffer)
        rows = [r.to_bigquery_row() for r in self._buffer]

        # In production, this would stream to BigQuery:
        # errors = self._client.insert_rows_json(table, rows)

        self._buffer = []
        return count

    def update_barge_state(self, state: BargeState) -> None:
        """
        Update the current state of a barge.

        Triggers stability alerts if status changes.

        Args:
            state: New BargeState
        """
        previous_state = self._barge_states.get(state.barge_id)

        # Compute stability status
        state.stability_status = state.compute_stability_status()

        # Check for status change
        if previous_state and previous_state.stability_status != state.stability_status:
            self._emit(
                "on_stability_alert",
                state.barge_id,
                previous_state.stability_status,
                state.stability_status,
                state.health_score
            )

        self._barge_states[state.barge_id] = state
        self._emit("on_state_change", state)

    def get_barge_state(self, barge_id: str) -> Optional[BargeState]:
        """Get current state for a barge."""
        return self._barge_states.get(barge_id)

    def get_all_barge_states(self) -> Dict[str, BargeState]:
        """Get all current barge states."""
        return self._barge_states.copy()

    def get_fleet_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for the entire fleet.

        Returns:
            Dictionary with fleet-wide metrics
        """
        states = list(self._barge_states.values())

        if not states:
            return {
                "total_vessels": 0,
                "stable_count": 0,
                "caution_count": 0,
                "warning_count": 0,
                "critical_count": 0,
                "average_health_score": 0.0,
                "total_cargo_tons": 0.0,
            }

        status_counts = {
            StabilityStatus.STABLE: 0,
            StabilityStatus.CAUTION: 0,
            StabilityStatus.WARNING: 0,
            StabilityStatus.CRITICAL: 0,
        }

        total_health = 0.0
        total_cargo = 0.0

        for state in states:
            status_counts[state.stability_status] += 1
            total_health += state.health_score
            total_cargo += state.cargo_tons

        return {
            "total_vessels": len(states),
            "stable_count": status_counts[StabilityStatus.STABLE],
            "caution_count": status_counts[StabilityStatus.CAUTION],
            "warning_count": status_counts[StabilityStatus.WARNING],
            "critical_count": status_counts[StabilityStatus.CRITICAL],
            "average_health_score": total_health / len(states),
            "total_cargo_tons": total_cargo,
        }

    def get_buffer_status(self) -> Dict[str, Any]:
        """Get status of the telemetry buffer."""
        return {
            "buffer_size": len(self._buffer),
            "buffer_capacity": self._buffer_size,
            "barge_count": len(self._barge_states),
        }
