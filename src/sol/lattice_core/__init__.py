"""
Lattice Core - Data-Driven Digital Mirror for Maritime Operations

Replaces Azure Digital Twin with Google Cloud Supply Chain Twin architecture.
Provides real-time barge telemetry ingestion via BigQuery and IoT Core.

Architecture:
    IoT Sensors → IoT Core → BigQuery (barge_intelligence) → Lattice Core → Dashboard

Components:
    - BigQueryBridge: Data pipeline from sensors to BigQuery
    - SupplyChainTwinClient: Interface to GCP Supply Chain Twin API
    - TelemetrySimulator: Mock data generator for demonstration
    - LatticeStatus: Real-time status aggregation
"""

from .bigquery_bridge import BigQueryBridge, TelemetryRecord, BargeState
from .supply_chain_twin import SupplyChainTwinClient, TwinSchema
from .telemetry_simulator import TelemetrySimulator, SimulationConfig
from .lattice_status import LatticeStatus, HealthIndicator

__all__ = [
    "BigQueryBridge",
    "TelemetryRecord",
    "BargeState",
    "SupplyChainTwinClient",
    "TwinSchema",
    "TelemetrySimulator",
    "SimulationConfig",
    "LatticeStatus",
    "HealthIndicator",
]

__version__ = "1.0.0"
__author__ = "FREQ SOL Lattice"
