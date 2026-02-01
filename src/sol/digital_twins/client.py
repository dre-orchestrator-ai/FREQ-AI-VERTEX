"""
Azure Digital Twins Client for FREQ SOL

Provides interface to the lidar-twins Digital Twins instance
for VECTOR GAMMA maritime operations.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from .models_registry import ModelsRegistry, DTDLModel


class TwinOperationStatus(Enum):
    """Status of a Digital Twins operation."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    NOT_FOUND = "NOT_FOUND"


@dataclass
class TwinOperationResult:
    """Result of a Digital Twins operation."""

    operation: str
    status: TwinOperationStatus
    twin_id: Optional[str] = None
    model_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "status": self.status.value,
            "twin_id": self.twin_id,
            "model_id": self.model_id,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp,
            "execution_time_ms": self.execution_time_ms
        }


class DigitalTwinsClient:
    """
    Client for Azure Digital Twins operations.

    Connects to the lidar-twins instance for managing maritime
    digital twins in the FREQ SOL lattice.

    Configuration:
        Instance: lidar-twins
        Host: lidar-twins.api.eus2.digitaltwins.azure.net
        Region: East US 2
    """

    # Azure Digital Twins configuration
    INSTANCE_NAME = "lidar-twins"
    HOST_NAME = "lidar-twins.api.eus2.digitaltwins.azure.net"
    REGION = "eastus2"

    def __init__(self, credential: Optional[Any] = None):
        """
        Initialize the Digital Twins client.

        Args:
            credential: Azure credential for authentication.
                       If None, will use DefaultAzureCredential when available.
        """
        self._credential = credential
        self._client = None  # Azure DigitalTwinsClient instance
        self._models_registry = ModelsRegistry()
        self._twins_cache: Dict[str, Dict[str, Any]] = {}
        self._is_connected = False

    @property
    def endpoint(self) -> str:
        """Get the Digital Twins endpoint URL."""
        return f"https://{self.HOST_NAME}"

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to Azure."""
        return self._is_connected

    @property
    def models_registry(self) -> ModelsRegistry:
        """Get the DTDL models registry."""
        return self._models_registry

    def connect(self) -> TwinOperationResult:
        """
        Establish connection to Azure Digital Twins.

        Requires azure-digitaltwins-core and azure-identity packages.
        """
        try:
            # Import Azure SDK (optional dependency)
            from azure.digitaltwins.core import DigitalTwinsClient as AzureDTClient
            from azure.identity import DefaultAzureCredential

            if self._credential is None:
                self._credential = DefaultAzureCredential()

            self._client = AzureDTClient(self.endpoint, self._credential)
            self._is_connected = True

            return TwinOperationResult(
                operation="connect",
                status=TwinOperationStatus.SUCCESS,
                data={"endpoint": self.endpoint, "instance": self.INSTANCE_NAME}
            )
        except ImportError:
            return TwinOperationResult(
                operation="connect",
                status=TwinOperationStatus.FAILED,
                error="Azure SDK not installed. Run: pip install azure-digitaltwins-core azure-identity"
            )
        except Exception as e:
            return TwinOperationResult(
                operation="connect",
                status=TwinOperationStatus.FAILED,
                error=str(e)
            )

    def upload_models(self) -> TwinOperationResult:
        """
        Upload all DTDL models to Azure Digital Twins.

        Models are uploaded in dependency order (base models first).
        """
        if not self._is_connected:
            return TwinOperationResult(
                operation="upload_models",
                status=TwinOperationStatus.FAILED,
                error="Not connected. Call connect() first."
            )

        try:
            models = self._models_registry.get_models_for_upload()
            created_models = self._client.create_models(models)

            return TwinOperationResult(
                operation="upload_models",
                status=TwinOperationStatus.SUCCESS,
                data={
                    "models_uploaded": len(models),
                    "model_ids": [m["@id"] for m in models]
                }
            )
        except Exception as e:
            return TwinOperationResult(
                operation="upload_models",
                status=TwinOperationStatus.FAILED,
                error=str(e)
            )

    def create_twin(
        self,
        twin_id: str,
        model_id: str,
        properties: Dict[str, Any]
    ) -> TwinOperationResult:
        """
        Create a new digital twin.

        Args:
            twin_id: Unique identifier for the twin
            model_id: DTDL model ID (e.g., "dtmi:freq:lattice:CargoBarge;1")
            properties: Initial property values
        """
        if not self._is_connected:
            return TwinOperationResult(
                operation="create_twin",
                status=TwinOperationStatus.FAILED,
                error="Not connected. Call connect() first."
            )

        try:
            twin_data = {
                "$dtId": twin_id,
                "$metadata": {"$model": model_id},
                **properties
            }

            created_twin = self._client.upsert_digital_twin(twin_id, twin_data)
            self._twins_cache[twin_id] = created_twin

            return TwinOperationResult(
                operation="create_twin",
                status=TwinOperationStatus.SUCCESS,
                twin_id=twin_id,
                model_id=model_id,
                data=created_twin
            )
        except Exception as e:
            return TwinOperationResult(
                operation="create_twin",
                status=TwinOperationStatus.FAILED,
                twin_id=twin_id,
                model_id=model_id,
                error=str(e)
            )

    def get_twin(self, twin_id: str) -> TwinOperationResult:
        """Retrieve a digital twin by ID."""
        if not self._is_connected:
            return TwinOperationResult(
                operation="get_twin",
                status=TwinOperationStatus.FAILED,
                error="Not connected. Call connect() first."
            )

        try:
            twin = self._client.get_digital_twin(twin_id)
            self._twins_cache[twin_id] = twin

            return TwinOperationResult(
                operation="get_twin",
                status=TwinOperationStatus.SUCCESS,
                twin_id=twin_id,
                model_id=twin.get("$metadata", {}).get("$model"),
                data=twin
            )
        except Exception as e:
            if "not found" in str(e).lower():
                return TwinOperationResult(
                    operation="get_twin",
                    status=TwinOperationStatus.NOT_FOUND,
                    twin_id=twin_id,
                    error=f"Twin {twin_id} not found"
                )
            return TwinOperationResult(
                operation="get_twin",
                status=TwinOperationStatus.FAILED,
                twin_id=twin_id,
                error=str(e)
            )

    def update_twin(
        self,
        twin_id: str,
        updates: Dict[str, Any]
    ) -> TwinOperationResult:
        """
        Update a digital twin's properties.

        Args:
            twin_id: ID of the twin to update
            updates: Dictionary of property updates
        """
        if not self._is_connected:
            return TwinOperationResult(
                operation="update_twin",
                status=TwinOperationStatus.FAILED,
                error="Not connected. Call connect() first."
            )

        try:
            # Build JSON Patch operations
            patch = [
                {"op": "replace", "path": f"/{key}", "value": value}
                for key, value in updates.items()
            ]

            self._client.update_digital_twin(twin_id, patch)

            # Refresh cache
            result = self.get_twin(twin_id)

            return TwinOperationResult(
                operation="update_twin",
                status=TwinOperationStatus.SUCCESS,
                twin_id=twin_id,
                data={"updated_properties": list(updates.keys())}
            )
        except Exception as e:
            return TwinOperationResult(
                operation="update_twin",
                status=TwinOperationStatus.FAILED,
                twin_id=twin_id,
                error=str(e)
            )

    def publish_telemetry(
        self,
        twin_id: str,
        telemetry: Dict[str, Any],
        message_id: Optional[str] = None
    ) -> TwinOperationResult:
        """
        Publish telemetry data for a digital twin.

        Args:
            twin_id: ID of the twin
            telemetry: Telemetry data to publish
            message_id: Optional unique message identifier
        """
        if not self._is_connected:
            return TwinOperationResult(
                operation="publish_telemetry",
                status=TwinOperationStatus.FAILED,
                error="Not connected. Call connect() first."
            )

        try:
            self._client.publish_telemetry(
                twin_id,
                telemetry,
                message_id=message_id
            )

            return TwinOperationResult(
                operation="publish_telemetry",
                status=TwinOperationStatus.SUCCESS,
                twin_id=twin_id,
                data=telemetry
            )
        except Exception as e:
            return TwinOperationResult(
                operation="publish_telemetry",
                status=TwinOperationStatus.FAILED,
                twin_id=twin_id,
                error=str(e)
            )

    def create_relationship(
        self,
        source_twin_id: str,
        target_twin_id: str,
        relationship_name: str,
        relationship_id: Optional[str] = None
    ) -> TwinOperationResult:
        """
        Create a relationship between two twins.

        Args:
            source_twin_id: ID of the source twin
            target_twin_id: ID of the target twin
            relationship_name: Name of the relationship (from DTDL)
            relationship_id: Optional unique ID for the relationship
        """
        if not self._is_connected:
            return TwinOperationResult(
                operation="create_relationship",
                status=TwinOperationStatus.FAILED,
                error="Not connected. Call connect() first."
            )

        try:
            if relationship_id is None:
                relationship_id = f"{source_twin_id}-{relationship_name}-{target_twin_id}"

            relationship = {
                "$relationshipId": relationship_id,
                "$sourceId": source_twin_id,
                "$targetId": target_twin_id,
                "$relationshipName": relationship_name
            }

            created = self._client.upsert_relationship(
                source_twin_id,
                relationship_id,
                relationship
            )

            return TwinOperationResult(
                operation="create_relationship",
                status=TwinOperationStatus.SUCCESS,
                data={
                    "relationship_id": relationship_id,
                    "source": source_twin_id,
                    "target": target_twin_id,
                    "name": relationship_name
                }
            )
        except Exception as e:
            return TwinOperationResult(
                operation="create_relationship",
                status=TwinOperationStatus.FAILED,
                error=str(e)
            )

    def query_twins(self, query: str) -> TwinOperationResult:
        """
        Query twins using Azure Digital Twins Query Language.

        Args:
            query: SQL-like query string

        Example queries:
            - "SELECT * FROM digitaltwins"
            - "SELECT * FROM digitaltwins WHERE $dtId = 'barge-001'"
            - "SELECT * FROM digitaltwins T WHERE T.$metadata.$model = 'dtmi:freq:lattice:CargoBarge;1'"
        """
        if not self._is_connected:
            return TwinOperationResult(
                operation="query_twins",
                status=TwinOperationStatus.FAILED,
                error="Not connected. Call connect() first."
            )

        try:
            query_result = self._client.query_twins(query)
            twins = list(query_result)

            return TwinOperationResult(
                operation="query_twins",
                status=TwinOperationStatus.SUCCESS,
                data={"count": len(twins), "twins": twins}
            )
        except Exception as e:
            return TwinOperationResult(
                operation="query_twins",
                status=TwinOperationStatus.FAILED,
                error=str(e)
            )

    # --- VECTOR GAMMA Convenience Methods ---

    def create_cargo_barge(
        self,
        barge_id: str,
        name: str,
        length_meters: float,
        beam_meters: float,
        max_draft_meters: float,
        cargo_capacity_tons: float,
        **additional_properties
    ) -> TwinOperationResult:
        """
        Create a CargoBarge digital twin for VECTOR GAMMA.

        Args:
            barge_id: Unique barge identifier
            name: Barge name
            length_meters: Length of barge
            beam_meters: Beam width
            max_draft_meters: Maximum draft
            cargo_capacity_tons: Cargo capacity
            **additional_properties: Additional barge properties
        """
        properties = {
            "vesselId": barge_id,
            "vesselName": name,
            "vesselType": "BARGE",
            "lengthMeters": length_meters,
            "beamMeters": beam_meters,
            "maxDraftMeters": max_draft_meters,
            "cargoCapacityTons": cargo_capacity_tons,
            "operationalStatus": "IDLE",
            "currentCargoTons": 0.0,
            "cargoType": "EMPTY",
            **additional_properties
        }

        return self.create_twin(
            twin_id=barge_id,
            model_id="dtmi:freq:lattice:CargoBarge;1",
            properties=properties
        )

    def create_lidar_drone(
        self,
        drone_id: str,
        name: str,
        model: str,
        home_latitude: float,
        home_longitude: float,
        **additional_properties
    ) -> TwinOperationResult:
        """
        Create a LidarDrone digital twin.

        Args:
            drone_id: Unique drone identifier
            name: Drone name
            model: Drone model name
            home_latitude: Home base latitude
            home_longitude: Home base longitude
            **additional_properties: Additional drone properties
        """
        properties = {
            "droneId": drone_id,
            "droneName": name,
            "droneModel": model,
            "homeBaseLatitude": home_latitude,
            "homeBaseLongitude": home_longitude,
            "flightStatus": "GROUNDED",
            "batteryPercent": 100.0,
            **additional_properties
        }

        return self.create_twin(
            twin_id=drone_id,
            model_id="dtmi:freq:lattice:LidarDrone;1",
            properties=properties
        )

    def create_lidar_sensor(
        self,
        sensor_id: str,
        model: str,
        sensor_type: str,
        max_range_meters: float,
        accuracy_mm: float,
        **additional_properties
    ) -> TwinOperationResult:
        """
        Create a LidarSensor digital twin.

        Args:
            sensor_id: Unique sensor identifier
            model: Sensor model name
            sensor_type: FIXED, DRONE_MOUNTED, VESSEL_MOUNTED, or SHORE_BASED
            max_range_meters: Maximum sensing range
            accuracy_mm: Measurement accuracy in millimeters
            **additional_properties: Additional sensor properties
        """
        properties = {
            "sensorId": sensor_id,
            "sensorModel": model,
            "sensorType": sensor_type,
            "maxRangeMeters": max_range_meters,
            "accuracyMillimeters": accuracy_mm,
            "operationalStatus": "ONLINE",
            **additional_properties
        }

        return self.create_twin(
            twin_id=sensor_id,
            model_id="dtmi:freq:lattice:LidarSensor;1",
            properties=properties
        )

    def publish_draft_reading(
        self,
        barge_id: str,
        forward_draft: float,
        midship_draft: float,
        aft_draft: float,
        accuracy_percent: float = 99.8
    ) -> TwinOperationResult:
        """
        Publish draft telemetry for a barge (VECTOR GAMMA SCAN phase).

        Args:
            barge_id: ID of the barge twin
            forward_draft: Forward draft in meters
            midship_draft: Midship draft in meters
            aft_draft: Aft draft in meters
            accuracy_percent: Measurement accuracy (target: 99.8%)
        """
        trim = forward_draft - aft_draft
        current_draft = midship_draft

        telemetry = {
            "forwardDraftMeters": forward_draft,
            "midshipDraftMeters": midship_draft,
            "aftDraftMeters": aft_draft,
            "currentDraftMeters": current_draft,
            "trimMeters": trim,
            "draftAccuracyPercent": accuracy_percent
        }

        return self.publish_telemetry(barge_id, telemetry)

    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the Digital Twins client status."""
        return {
            "instance": self.INSTANCE_NAME,
            "endpoint": self.endpoint,
            "region": self.REGION,
            "connected": self._is_connected,
            "models_loaded": len(self._models_registry.list_models()),
            "twins_cached": len(self._twins_cache),
            "model_ids": self._models_registry.list_models()
        }
