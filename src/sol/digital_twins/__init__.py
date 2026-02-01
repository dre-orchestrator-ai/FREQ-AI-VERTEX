"""
FREQ SOL Digital Twins Module

Azure Digital Twins integration for the Sophisticated Operational Lattice.
Provides spatial intelligence for VECTOR GAMMA maritime operations.

Instance: lidar-twins
Host: lidar-twins.api.eus2.digitaltwins.azure.net
"""

from .client import DigitalTwinsClient, TwinOperationResult
from .models_registry import ModelsRegistry, DTDLModel

__all__ = [
    "DigitalTwinsClient",
    "TwinOperationResult",
    "ModelsRegistry",
    "DTDLModel",
]
