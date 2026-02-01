"""
DTDL Models for FREQ SOL Digital Twins

Digital Twin Definition Language (DTDL v3) models for maritime operations.
These models define the structure of digital twins in the lidar-twins instance.

Models:
- MaritimeVessel: Base interface for all vessels
- CargoBarge: Barge with draft measurements (extends MaritimeVessel)
- CargoHold: Individual cargo hold within a barge
- LidarSensor: LiDAR sensor array for scanning
- LidarDrone: Autonomous drone with LiDAR payload
- EnvironmentalZone: Environmental conditions zone
"""

DTDL_MODELS = [
    "maritime_vessel.json",
    "cargo_barge.json",
    "cargo_hold.json",
    "lidar_sensor.json",
    "lidar_drone.json",
    "environmental_zone.json",
]

MODEL_IDS = {
    "MaritimeVessel": "dtmi:freq:lattice:MaritimeVessel;1",
    "CargoBarge": "dtmi:freq:lattice:CargoBarge;1",
    "CargoHold": "dtmi:freq:lattice:CargoHold;1",
    "LidarSensor": "dtmi:freq:lattice:LidarSensor;1",
    "LidarDrone": "dtmi:freq:lattice:LidarDrone;1",
    "EnvironmentalZone": "dtmi:freq:lattice:EnvironmentalZone;1",
}
