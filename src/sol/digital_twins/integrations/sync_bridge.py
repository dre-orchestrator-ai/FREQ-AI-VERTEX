"""
Synchronization Bridge for FREQ SOL Digital Twins

Bridges data flow between OpenDroneMap processing outputs and
Azure Digital Twins (lidar-twins instance) for VECTOR GAMMA operations.

Data Flow:
    OpenDroneMap → SyncBridge → Digital Twins → Event Routes → Databricks/TOM

Sync Operations:
    1. Point Cloud → Barge draft measurements
    2. DEM/DSM → Water surface analysis
    3. Task status → Drone twin telemetry
    4. Orthophoto → Mission documentation
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import struct


class SyncDirection(Enum):
    """Direction of data synchronization."""
    ODM_TO_DT = "odm_to_digital_twins"
    DT_TO_ODM = "digital_twins_to_odm"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(Enum):
    """Status of a synchronization operation."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


@dataclass
class SyncConfig:
    """
    Configuration for synchronization bridge.

    Attributes:
        odm_host: OpenDroneMap server host
        odm_port: OpenDroneMap server port
        dt_instance: Digital Twins instance name
        dt_host: Digital Twins host URL
        auto_sync: Enable automatic sync on task completion
        sync_interval: Seconds between sync checks (if auto_sync)
        point_cloud_sampling: Sample rate for point cloud (1 = all, 10 = every 10th)
        draft_calculation_method: Method for draft calculation
    """

    # OpenDroneMap settings
    odm_host: str = "localhost"
    odm_port: int = 3000
    odm_token: Optional[str] = None

    # Digital Twins settings
    dt_instance: str = "lidar-twins"
    dt_host: str = "lidar-twins.api.eus2.digitaltwins.azure.net"

    # Sync settings
    auto_sync: bool = True
    sync_interval: int = 30
    point_cloud_sampling: int = 100  # Sample every Nth point for efficiency

    # VECTOR GAMMA settings
    draft_calculation_method: str = "water_line_detection"
    accuracy_target: float = 99.8  # Percentage

    # Event routing
    enable_event_hub: bool = True
    event_hub_connection: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "odm_host": self.odm_host,
            "odm_port": self.odm_port,
            "dt_instance": self.dt_instance,
            "dt_host": self.dt_host,
            "auto_sync": self.auto_sync,
            "sync_interval": self.sync_interval,
            "point_cloud_sampling": self.point_cloud_sampling,
            "draft_calculation_method": self.draft_calculation_method,
            "accuracy_target": self.accuracy_target,
        }


@dataclass
class SyncResult:
    """Result of a synchronization operation."""

    operation: str
    status: SyncStatus
    source: str
    target: str
    records_processed: int = 0
    records_failed: int = 0
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    # VECTOR GAMMA context
    mission_id: Optional[str] = None
    barge_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "status": self.status.value,
            "source": self.source,
            "target": self.target,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "error": self.error,
            "data": self.data,
            "mission_id": self.mission_id,
            "barge_id": self.barge_id,
        }


@dataclass
class DraftMeasurement:
    """Draft measurement extracted from point cloud analysis."""

    barge_id: str
    timestamp: str
    forward_draft_meters: float
    midship_draft_meters: float
    aft_draft_meters: float
    trim_meters: float
    list_degrees: float
    accuracy_percent: float
    measurement_points: int
    water_line_elevation: float

    @property
    def current_draft(self) -> float:
        """Average draft (midship)."""
        return self.midship_draft_meters

    @property
    def meets_accuracy_target(self) -> bool:
        """Check if measurement meets VECTOR GAMMA 99.8% target."""
        return self.accuracy_percent >= 99.8

    def to_telemetry(self) -> Dict[str, Any]:
        """Convert to Digital Twins telemetry format."""
        return {
            "forwardDraftMeters": self.forward_draft_meters,
            "midshipDraftMeters": self.midship_draft_meters,
            "aftDraftMeters": self.aft_draft_meters,
            "currentDraftMeters": self.current_draft,
            "trimMeters": self.trim_meters,
            "listDegrees": self.list_degrees,
            "draftAccuracyPercent": self.accuracy_percent,
            "measurementPoints": self.measurement_points,
            "waterLineElevation": self.water_line_elevation,
        }


class PointCloudProcessor:
    """
    Process point cloud data for draft measurement extraction.

    Extracts water line and hull measurements from LAS/LAZ point clouds
    generated by OpenDroneMap.
    """

    # Point classification codes (LAS standard)
    CLASS_WATER = 9
    CLASS_UNCLASSIFIED = 1
    CLASS_GROUND = 2

    def __init__(self, sampling_rate: int = 100):
        """
        Initialize processor.

        Args:
            sampling_rate: Process every Nth point (1 = all points)
        """
        self.sampling_rate = sampling_rate

    def extract_draft_measurements(
        self,
        point_cloud_path: Path,
        barge_bounds: Dict[str, float]
    ) -> DraftMeasurement:
        """
        Extract draft measurements from point cloud.

        Args:
            point_cloud_path: Path to LAS/LAZ file
            barge_bounds: Bounding box {min_x, max_x, min_y, max_y}

        Returns:
            DraftMeasurement with extracted values
        """
        # Simulated extraction - production would use laspy or pdal
        # This demonstrates the data flow structure

        # In production, this would:
        # 1. Load point cloud with laspy
        # 2. Filter points within barge bounds
        # 3. Detect water surface plane
        # 4. Measure hull depth at forward, midship, aft positions
        # 5. Calculate trim and list

        # Placeholder for demonstration
        measurement = DraftMeasurement(
            barge_id=barge_bounds.get("barge_id", "unknown"),
            timestamp=datetime.utcnow().isoformat(),
            forward_draft_meters=0.0,
            midship_draft_meters=0.0,
            aft_draft_meters=0.0,
            trim_meters=0.0,
            list_degrees=0.0,
            accuracy_percent=0.0,
            measurement_points=0,
            water_line_elevation=0.0,
        )

        return measurement

    def detect_water_surface(
        self,
        points: List[Tuple[float, float, float]]
    ) -> float:
        """
        Detect water surface elevation from point cloud.

        Uses RANSAC plane fitting on water-classified points.

        Args:
            points: List of (x, y, z) coordinates

        Returns:
            Water surface elevation in meters
        """
        if not points:
            return 0.0

        # Simple approach: find modal Z value for flat water surface
        z_values = [p[2] for p in points]
        z_values.sort()

        # Return median as approximation
        mid = len(z_values) // 2
        return z_values[mid]


class SyncBridge:
    """
    Synchronization bridge between OpenDroneMap and Digital Twins.

    Orchestrates data flow for VECTOR GAMMA maritime operations:
    - Syncs ODM task status → Drone twin telemetry
    - Syncs point cloud analysis → Barge twin draft measurements
    - Syncs mission metadata → Digital Twins properties

    Usage:
        config = SyncConfig(
            odm_host="10.0.0.5",
            dt_instance="lidar-twins"
        )
        bridge = SyncBridge(config)

        # Sync completed scan to digital twins
        result = bridge.sync_scan_results(
            task_uuid="abc-123",
            barge_id="barge-001"
        )
    """

    def __init__(
        self,
        config: SyncConfig,
        odm_client: Optional[Any] = None,
        dt_client: Optional[Any] = None
    ):
        """
        Initialize sync bridge.

        Args:
            config: Synchronization configuration
            odm_client: Optional pre-configured OpenDroneMapClient
            dt_client: Optional pre-configured DigitalTwinsClient
        """
        self.config = config
        self._odm_client = odm_client
        self._dt_client = dt_client
        self._point_processor = PointCloudProcessor(config.point_cloud_sampling)
        self._sync_history: List[SyncResult] = []
        self._callbacks: Dict[str, List[Callable]] = {
            "on_sync_start": [],
            "on_sync_complete": [],
            "on_sync_error": [],
            "on_draft_measurement": [],
        }

    @property
    def odm_client(self):
        """Get or create OpenDroneMap client."""
        if self._odm_client is None:
            from .opendronemap import OpenDroneMapClient
            self._odm_client = OpenDroneMapClient(
                host=self.config.odm_host,
                port=self.config.odm_port,
                token=self.config.odm_token
            )
        return self._odm_client

    @property
    def dt_client(self):
        """Get or create Digital Twins client."""
        if self._dt_client is None:
            from ..client import DigitalTwinsClient
            self._dt_client = DigitalTwinsClient()
        return self._dt_client

    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for sync events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit(self, event: str, *args, **kwargs) -> None:
        """Emit event to registered callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass  # Don't let callback errors break sync

    def sync_task_status(
        self,
        task_uuid: str,
        drone_id: str
    ) -> SyncResult:
        """
        Sync ODM task status to drone twin telemetry.

        Args:
            task_uuid: OpenDroneMap task UUID
            drone_id: Digital Twin drone ID

        Returns:
            SyncResult with operation status
        """
        start_time = datetime.utcnow()
        self._emit("on_sync_start", "task_status", task_uuid, drone_id)

        try:
            # Get task info from ODM
            task = self.odm_client.get_task_info(task_uuid)

            # Map task status to drone telemetry
            status_map = {
                "QUEUED": "PREFLIGHT",
                "RUNNING": "SCANNING",
                "COMPLETED": "RETURNING",
                "FAILED": "EMERGENCY",
                "CANCELED": "GROUNDED",
            }

            telemetry = {
                "flightStatus": status_map.get(task.status.name, "GROUNDED"),
                "currentMissionId": task.mission_id or task_uuid,
                "batteryPercent": 100.0 - (task.progress * 0.5),  # Simulated
            }

            # Publish to Digital Twins
            result = self.dt_client.publish_telemetry(drone_id, telemetry)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            sync_result = SyncResult(
                operation="sync_task_status",
                status=SyncStatus.COMPLETED if result.status.value == "SUCCESS" else SyncStatus.FAILED,
                source=f"odm://{task_uuid}",
                target=f"adt://{drone_id}",
                records_processed=1,
                duration_ms=duration,
                data=telemetry,
            )

        except Exception as e:
            sync_result = SyncResult(
                operation="sync_task_status",
                status=SyncStatus.FAILED,
                source=f"odm://{task_uuid}",
                target=f"adt://{drone_id}",
                error=str(e),
            )
            self._emit("on_sync_error", sync_result)

        self._sync_history.append(sync_result)
        self._emit("on_sync_complete", sync_result)
        return sync_result

    def sync_scan_results(
        self,
        task_uuid: str,
        barge_id: str,
        point_cloud_path: Optional[Path] = None
    ) -> SyncResult:
        """
        Sync completed scan results to barge twin.

        Extracts draft measurements from point cloud and publishes
        to Digital Twins as telemetry.

        Args:
            task_uuid: Completed ODM task UUID
            barge_id: Target barge twin ID
            point_cloud_path: Local path to point cloud (downloads if None)

        Returns:
            SyncResult with draft measurements
        """
        start_time = datetime.utcnow()
        self._emit("on_sync_start", "scan_results", task_uuid, barge_id)

        try:
            # Get task info
            task = self.odm_client.get_task_info(task_uuid)

            if task.status.name != "COMPLETED":
                return SyncResult(
                    operation="sync_scan_results",
                    status=SyncStatus.FAILED,
                    source=f"odm://{task_uuid}",
                    target=f"adt://{barge_id}",
                    error=f"Task not completed: {task.status.name}",
                )

            # Download point cloud if needed
            if point_cloud_path is None:
                from .opendronemap import OutputType
                point_cloud_path = Path(f"/tmp/odm_{task_uuid}_pointcloud.laz")
                self.odm_client.download_output(
                    task_uuid,
                    OutputType.POINT_CLOUD,
                    point_cloud_path
                )

            # Get barge bounds from Digital Twins
            barge_result = self.dt_client.get_twin(barge_id)
            if barge_result.status.value != "SUCCESS":
                raise Exception(f"Failed to get barge twin: {barge_result.error}")

            barge_data = barge_result.data
            barge_bounds = {
                "barge_id": barge_id,
                "min_x": barge_data.get("gpsLongitude", 0) - 0.001,
                "max_x": barge_data.get("gpsLongitude", 0) + 0.001,
                "min_y": barge_data.get("gpsLatitude", 0) - 0.001,
                "max_y": barge_data.get("gpsLatitude", 0) + 0.001,
            }

            # Extract draft measurements
            measurement = self._point_processor.extract_draft_measurements(
                point_cloud_path,
                barge_bounds
            )

            # Publish to Digital Twins
            telemetry = measurement.to_telemetry()
            dt_result = self.dt_client.publish_telemetry(barge_id, telemetry)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            sync_result = SyncResult(
                operation="sync_scan_results",
                status=SyncStatus.COMPLETED,
                source=f"odm://{task_uuid}",
                target=f"adt://{barge_id}",
                records_processed=1,
                duration_ms=duration,
                mission_id=task.mission_id,
                barge_id=barge_id,
                data={
                    "draft_measurement": measurement.to_telemetry(),
                    "meets_accuracy_target": measurement.meets_accuracy_target,
                },
            )

            self._emit("on_draft_measurement", measurement, sync_result)

        except Exception as e:
            sync_result = SyncResult(
                operation="sync_scan_results",
                status=SyncStatus.FAILED,
                source=f"odm://{task_uuid}",
                target=f"adt://{barge_id}",
                error=str(e),
                barge_id=barge_id,
            )
            self._emit("on_sync_error", sync_result)

        self._sync_history.append(sync_result)
        self._emit("on_sync_complete", sync_result)
        return sync_result

    def sync_drone_position(
        self,
        drone_id: str,
        latitude: float,
        longitude: float,
        altitude: float,
        heading: float,
        speed: float
    ) -> SyncResult:
        """
        Sync real-time drone position to Digital Twins.

        Args:
            drone_id: Drone twin ID
            latitude: GPS latitude
            longitude: GPS longitude
            altitude: Altitude in meters
            heading: Heading in degrees
            speed: Ground speed in km/h

        Returns:
            SyncResult
        """
        telemetry = {
            "gpsLatitude": latitude,
            "gpsLongitude": longitude,
            "altitudeMeters": altitude,
            "headingDegrees": heading,
            "groundSpeedKph": speed,
        }

        try:
            result = self.dt_client.publish_telemetry(drone_id, telemetry)

            return SyncResult(
                operation="sync_drone_position",
                status=SyncStatus.COMPLETED,
                source="gps",
                target=f"adt://{drone_id}",
                records_processed=1,
                data=telemetry,
            )
        except Exception as e:
            return SyncResult(
                operation="sync_drone_position",
                status=SyncStatus.FAILED,
                source="gps",
                target=f"adt://{drone_id}",
                error=str(e),
            )

    def get_sync_history(
        self,
        limit: int = 100,
        status_filter: Optional[SyncStatus] = None
    ) -> List[SyncResult]:
        """Get synchronization history."""
        history = self._sync_history[-limit:]

        if status_filter:
            history = [r for r in history if r.status == status_filter]

        return history

    def get_status_summary(self) -> Dict[str, Any]:
        """Get sync bridge status summary."""
        completed = sum(1 for r in self._sync_history if r.status == SyncStatus.COMPLETED)
        failed = sum(1 for r in self._sync_history if r.status == SyncStatus.FAILED)

        return {
            "config": self.config.to_dict(),
            "odm_connected": self._odm_client is not None,
            "dt_connected": self._dt_client is not None,
            "sync_history_count": len(self._sync_history),
            "completed_syncs": completed,
            "failed_syncs": failed,
            "success_rate": (completed / max(1, completed + failed)) * 100,
        }


# --- VECTOR GAMMA Pipeline Helper ---

def create_vector_gamma_pipeline(
    odm_host: str,
    barge_ids: List[str],
    drone_ids: List[str]
) -> SyncBridge:
    """
    Create a pre-configured sync bridge for VECTOR GAMMA operations.

    Args:
        odm_host: OpenDroneMap server host
        barge_ids: List of barge twin IDs to monitor
        drone_ids: List of drone twin IDs

    Returns:
        Configured SyncBridge
    """
    config = SyncConfig(
        odm_host=odm_host,
        odm_port=3000,
        dt_instance="lidar-twins",
        dt_host="lidar-twins.api.eus2.digitaltwins.azure.net",
        auto_sync=True,
        sync_interval=30,
        point_cloud_sampling=100,
        draft_calculation_method="water_line_detection",
        accuracy_target=99.8,
    )

    bridge = SyncBridge(config)

    # Register logging callbacks
    def log_sync_complete(result: SyncResult):
        print(f"[SYNC] {result.operation}: {result.status.value} "
              f"({result.records_processed} records, {result.duration_ms:.1f}ms)")

    def log_draft_measurement(measurement: DraftMeasurement, result: SyncResult):
        print(f"[DRAFT] Barge {measurement.barge_id}: "
              f"F={measurement.forward_draft_meters:.3f}m "
              f"M={measurement.midship_draft_meters:.3f}m "
              f"A={measurement.aft_draft_meters:.3f}m "
              f"(Accuracy: {measurement.accuracy_percent:.1f}%)")

    bridge.register_callback("on_sync_complete", log_sync_complete)
    bridge.register_callback("on_draft_measurement", log_draft_measurement)

    return bridge
