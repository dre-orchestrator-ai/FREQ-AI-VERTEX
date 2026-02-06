"""
Lattice Core: Data-Driven Digital Mirror for Maritime Operations

The Lattice Core is the central orchestration layer that maintains
a real-time digital representation of vessel operations, enabling
autonomous agents to monitor, analyze, and optimize maritime processes.
"""

__version__ = "0.1.0"
__codename__ = "Antigravity"

from pathlib import Path

LATTICE_ROOT = Path(__file__).parent
MANIFEST_PATH = LATTICE_ROOT / "manifest.json"
