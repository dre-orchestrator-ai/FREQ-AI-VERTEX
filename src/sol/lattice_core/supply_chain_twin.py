"""
Supply Chain Twin Client for Lattice Core

Interface to Google Cloud Supply Chain Twin backed by Manufacturing Data Engine.
Replaces Azure Digital Twin with GCP-native digital mirror architecture.

API Reference: Google Cloud Supply Chain Twin API
Data Engine: Manufacturing Data Engine (MDE)
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class EntityType(Enum):
    """Supply Chain Twin entity types for maritime operations."""
    VESSEL = "VESSEL"
    BARGE = "BARGE"
    CARGO = "CARGO"
    SENSOR = "SENSOR"
    PORT = "PORT"
    ROUTE = "ROUTE"


class OperationalState(Enum):
    """Operational states for vessels."""
    IDLE = "IDLE"
    LOADING = "LOADING"
    LOADED = "LOADED"
    IN_TRANSIT = "IN_TRANSIT"
    UNLOADING = "UNLOADING"
    MAINTENANCE = "MAINTENANCE"
    EMERGENCY = "EMERGENCY"


@dataclass
class TwinSchema:
    """
    Schema definition for a Supply Chain Twin entity.

    Maps legacy Azure Digital Twin DTDL models to GCP Supply Chain Twin schema.
    """
    entity_type: EntityType
    schema_version: str = "1.0.0"
    properties: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    measurements: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    relationships: List[Dict[str, str]] = field(default_factory=list)

    def to_mde_schema(self) -> Dict[str, Any]:
        """Convert to Manufacturing Data Engine schema format."""
        return {
            "schemaVersion": self.schema_version,
            "entityType": self.entity_type.value,
            "properties": self.properties,
            "measurements": self.measurements,
            "relationships": self.relationships,
        }


@dataclass
class TwinEntity:
    """
    A single entity in the Supply Chain Twin.

    Represents a barge, sensor, or other trackable asset.
    """
    entity_id: str
    entity_type: EntityType
    name: str = ""
    schema: Optional[TwinSchema] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    measurements: Dict[str, Any] = field(default_factory=dict)
    state: OperationalState = OperationalState.IDLE
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def update_measurement(self, key: str, value: Any, unit: str = "") -> None:
        """Update a measurement value."""
        self.measurements[key] = {
            "value": value,
            "unit": unit,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        self.updated_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "entityId": self.entity_id,
            "entityType": self.entity_type.value,
            "name": self.name,
            "properties": self.properties,
            "measurements": self.measurements,
            "state": self.state.value,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class SupplyChainTwinClient:
    """
    Client for Google Cloud Supply Chain Twin.

    Provides interface to Manufacturing Data Engine for:
    - Entity management (create, read, update, delete)
    - Measurement streaming
    - Relationship mapping
    - Query operations

    This replaces Azure Digital Twin with a GCP-native solution.

    Configuration:
        Project: Startup Program GCP Project
        Dataset: barge_intelligence
        API: Supply Chain Twin API (via MDE)

    Usage:
        client = SupplyChainTwinClient(project_id="my-project")

        # Create a barge twin
        barge = client.create_entity(
            entity_id="BARGE-DELTA-001",
            entity_type=EntityType.BARGE,
            name="Delta Pioneer",
            properties={
                "lengthMeters": 76.2,
                "beamMeters": 10.7,
                "maxDraftMeters": 3.8,
            }
        )

        # Update measurements
        client.update_measurements(
            "BARGE-DELTA-001",
            {
                "draft.forward": {"value": 2.45, "unit": "meters"},
                "draft.midship": {"value": 2.52, "unit": "meters"},
                "draft.aft": {"value": 2.58, "unit": "meters"},
            }
        )
    """

    # Pre-defined schemas for maritime entities
    BARGE_SCHEMA = TwinSchema(
        entity_type=EntityType.BARGE,
        schema_version="1.0.0",
        properties={
            "vesselId": {"type": "STRING", "required": True},
            "vesselName": {"type": "STRING", "required": True},
            "vesselType": {"type": "STRING", "default": "CARGO_BARGE"},
            "lengthMeters": {"type": "FLOAT64", "required": True},
            "beamMeters": {"type": "FLOAT64", "required": True},
            "depthMeters": {"type": "FLOAT64"},
            "maxDraftMeters": {"type": "FLOAT64", "required": True},
            "maxCargoTons": {"type": "FLOAT64", "required": True},
            "homePort": {"type": "STRING"},
            "registration": {"type": "STRING"},
            "hullCoefficients": {"type": "JSON"},
        },
        measurements={
            "draft.forward": {"type": "FLOAT64", "unit": "meters"},
            "draft.midship": {"type": "FLOAT64", "unit": "meters"},
            "draft.aft": {"type": "FLOAT64", "unit": "meters"},
            "trim": {"type": "FLOAT64", "unit": "meters"},
            "list": {"type": "FLOAT64", "unit": "degrees"},
            "cargo.weight": {"type": "FLOAT64", "unit": "tons"},
            "cargo.type": {"type": "STRING"},
            "environment.waterTemperature": {"type": "FLOAT64", "unit": "celsius"},
            "environment.salinity": {"type": "FLOAT64", "unit": "ppt"},
            "position.latitude": {"type": "FLOAT64", "unit": "degrees"},
            "position.longitude": {"type": "FLOAT64", "unit": "degrees"},
        },
        relationships=[
            {"name": "hasSensor", "target": "SENSOR"},
            {"name": "carriesCargo", "target": "CARGO"},
            {"name": "dockedAt", "target": "PORT"},
        ],
    )

    SENSOR_SCHEMA = TwinSchema(
        entity_type=EntityType.SENSOR,
        schema_version="1.0.0",
        properties={
            "sensorId": {"type": "STRING", "required": True},
            "sensorType": {"type": "STRING", "required": True},
            "position": {"type": "STRING"},
            "manufacturer": {"type": "STRING"},
            "model": {"type": "STRING"},
            "accuracyMm": {"type": "FLOAT64"},
            "calibrationDate": {"type": "TIMESTAMP"},
        },
        measurements={
            "reading": {"type": "FLOAT64"},
            "qualityScore": {"type": "FLOAT64"},
            "temperature": {"type": "FLOAT64", "unit": "celsius"},
            "status": {"type": "STRING"},
        },
        relationships=[
            {"name": "installedOn", "target": "BARGE"},
        ],
    )

    def __init__(
        self,
        project_id: str = "",
        location: str = "us-central1",
        dataset_id: str = "barge_intelligence"
    ):
        """
        Initialize Supply Chain Twin client.

        Args:
            project_id: GCP project ID
            location: GCP region
            dataset_id: BigQuery dataset for MDE
        """
        self.project_id = project_id
        self.location = location
        self.dataset_id = dataset_id
        self._entities: Dict[str, TwinEntity] = {}
        self._relationships: List[Dict[str, str]] = []
        self._is_connected = False

    @property
    def endpoint(self) -> str:
        """Get the Supply Chain Twin API endpoint."""
        return f"https://{self.location}-supplychaintwin.googleapis.com/v1"

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._is_connected

    def connect(self) -> Dict[str, Any]:
        """
        Establish connection to Supply Chain Twin API.

        Returns:
            Connection status dictionary
        """
        # In production, this would authenticate via Application Default Credentials
        self._is_connected = True
        return {
            "status": "connected",
            "project_id": self.project_id,
            "endpoint": self.endpoint,
            "dataset": self.dataset_id,
        }

    def create_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
        name: str,
        properties: Dict[str, Any],
        schema: Optional[TwinSchema] = None
    ) -> TwinEntity:
        """
        Create a new entity in the Supply Chain Twin.

        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity
            name: Human-readable name
            properties: Entity properties
            schema: Optional schema (uses default if not provided)

        Returns:
            Created TwinEntity
        """
        if schema is None:
            if entity_type == EntityType.BARGE:
                schema = self.BARGE_SCHEMA
            elif entity_type == EntityType.SENSOR:
                schema = self.SENSOR_SCHEMA

        entity = TwinEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            schema=schema,
            properties=properties,
        )

        self._entities[entity_id] = entity
        return entity

    def get_entity(self, entity_id: str) -> Optional[TwinEntity]:
        """Get an entity by ID."""
        return self._entities.get(entity_id)

    def update_entity(
        self,
        entity_id: str,
        properties: Optional[Dict[str, Any]] = None,
        state: Optional[OperationalState] = None
    ) -> Optional[TwinEntity]:
        """
        Update an existing entity.

        Args:
            entity_id: Entity to update
            properties: Properties to update
            state: New operational state

        Returns:
            Updated entity or None if not found
        """
        entity = self._entities.get(entity_id)
        if not entity:
            return None

        if properties:
            entity.properties.update(properties)

        if state:
            entity.state = state

        entity.updated_at = datetime.utcnow().isoformat() + "Z"
        return entity

    def update_measurements(
        self,
        entity_id: str,
        measurements: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Update measurements for an entity.

        Args:
            entity_id: Entity to update
            measurements: Dictionary of measurement updates
                         Format: {"key": {"value": x, "unit": "y"}}

        Returns:
            True if successful
        """
        entity = self._entities.get(entity_id)
        if not entity:
            return False

        for key, data in measurements.items():
            entity.update_measurement(
                key,
                data.get("value"),
                data.get("unit", "")
            )

        return True

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity."""
        if entity_id in self._entities:
            del self._entities[entity_id]
            return True
        return False

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str
    ) -> Dict[str, str]:
        """
        Create a relationship between entities.

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relationship_type: Type of relationship

        Returns:
            Relationship details
        """
        relationship = {
            "sourceId": source_id,
            "targetId": target_id,
            "type": relationship_type,
            "createdAt": datetime.utcnow().isoformat() + "Z",
        }
        self._relationships.append(relationship)
        return relationship

    def query_entities(
        self,
        entity_type: Optional[EntityType] = None,
        state: Optional[OperationalState] = None
    ) -> List[TwinEntity]:
        """
        Query entities with optional filters.

        Args:
            entity_type: Filter by entity type
            state: Filter by operational state

        Returns:
            List of matching entities
        """
        results = list(self._entities.values())

        if entity_type:
            results = [e for e in results if e.entity_type == entity_type]

        if state:
            results = [e for e in results if e.state == state]

        return results

    def get_entity_measurements(
        self,
        entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get all measurements for an entity."""
        entity = self._entities.get(entity_id)
        if not entity:
            return None
        return entity.measurements

    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of Supply Chain Twin status."""
        entity_counts = {}
        for entity in self._entities.values():
            key = entity.entity_type.value
            entity_counts[key] = entity_counts.get(key, 0) + 1

        return {
            "connected": self._is_connected,
            "project_id": self.project_id,
            "location": self.location,
            "dataset": self.dataset_id,
            "entity_count": len(self._entities),
            "entity_counts_by_type": entity_counts,
            "relationship_count": len(self._relationships),
        }

    def export_to_bigquery_schema(self) -> Dict[str, str]:
        """
        Generate BigQuery DDL for Supply Chain Twin tables.

        Returns:
            Dictionary of table names to DDL statements
        """
        ddl = {}

        # Entity master table
        ddl["twin_entities"] = f"""
CREATE TABLE IF NOT EXISTS `{self.project_id}.{self.dataset_id}.twin_entities` (
    entity_id STRING NOT NULL,
    entity_type STRING NOT NULL,
    name STRING,
    properties JSON,
    state STRING,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY entity_type
OPTIONS(
    description='Supply Chain Twin entity master table'
);
"""

        # Measurements time-series table
        ddl["twin_measurements"] = f"""
CREATE TABLE IF NOT EXISTS `{self.project_id}.{self.dataset_id}.twin_measurements` (
    entity_id STRING NOT NULL,
    measurement_key STRING NOT NULL,
    value FLOAT64,
    unit STRING,
    timestamp TIMESTAMP NOT NULL
)
PARTITION BY DATE(timestamp)
CLUSTER BY entity_id, measurement_key
OPTIONS(
    description='Supply Chain Twin measurements time-series'
);
"""

        # Relationships table
        ddl["twin_relationships"] = f"""
CREATE TABLE IF NOT EXISTS `{self.project_id}.{self.dataset_id}.twin_relationships` (
    source_id STRING NOT NULL,
    target_id STRING NOT NULL,
    relationship_type STRING NOT NULL,
    created_at TIMESTAMP NOT NULL
)
OPTIONS(
    description='Supply Chain Twin entity relationships'
);
"""

        return ddl


def create_barge_twin_from_legacy(
    client: SupplyChainTwinClient,
    legacy_config: Dict[str, Any]
) -> TwinEntity:
    """
    Create a barge twin from legacy hull displacement configuration.

    Args:
        client: SupplyChainTwinClient instance
        legacy_config: Legacy configuration from hull_displacement_config.json

    Returns:
        Created TwinEntity
    """
    barge_id = legacy_config.get("barge_id", "")
    vessel_name = legacy_config.get("vessel_name", "")
    dimensions = legacy_config.get("dimensions", {})
    displacement = legacy_config.get("displacement", {})
    hull_coefficients = legacy_config.get("hull_coefficients", {})

    properties = {
        "vesselId": barge_id,
        "vesselName": vessel_name,
        "vesselType": legacy_config.get("vessel_type", "CARGO_BARGE"),
        "lengthMeters": dimensions.get("length_m", 0),
        "beamMeters": dimensions.get("beam_m", 0),
        "depthMeters": dimensions.get("depth_m", 0),
        "maxDraftMeters": dimensions.get("max_draft_m", 0),
        "maxCargoTons": displacement.get("max_cargo_tons", 0),
        "lightDisplacementTons": displacement.get("light_displacement_tons", 0),
        "deadweightTons": displacement.get("deadweight_tons", 0),
        "homePort": legacy_config.get("home_port", ""),
        "registration": legacy_config.get("registration", ""),
        "hullCoefficients": json.dumps(hull_coefficients),
    }

    return client.create_entity(
        entity_id=barge_id,
        entity_type=EntityType.BARGE,
        name=vessel_name,
        properties=properties,
    )
