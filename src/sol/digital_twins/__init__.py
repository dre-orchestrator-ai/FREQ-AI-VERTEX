"""
FREQ SOL Digital Twins Module

Azure Digital Twins integration for the Sophisticated Operational Lattice.
Provides spatial intelligence for VECTOR GAMMA maritime operations.

Instance: lidar-twins
Host: lidar-twins.api.eus2.digitaltwins.azure.net

Components:
- DigitalTwinsClient: Azure Digital Twins API client
- ModelsRegistry: DTDL model loader and validator
- OpenDroneMapClient: Photogrammetry processing integration
- SyncBridge: ODM ↔ Digital Twins synchronization
"""

from .client import DigitalTwinsClient, TwinOperationResult
from .models_registry import ModelsRegistry, DTDLModel
from .integrations import (
    OpenDroneMapClient,
    ODMProject,
    ODMTask,
    ProcessingOptions,
    SyncBridge,
    SyncConfig,
    SyncResult,
)

__all__ = [
    # Digital Twins Client
    "DigitalTwinsClient",
    "TwinOperationResult",
    # Models Registry
    "ModelsRegistry",
    "DTDLModel",
    # OpenDroneMap Integration
    "OpenDroneMapClient",
    "ODMProject",
    "ODMTask",
    "ProcessingOptions",
    # Sync Bridge
    "SyncBridge",
    "SyncConfig",
    "SyncResult",
]
