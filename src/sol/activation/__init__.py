"""
FREQ AI Activation Module

Provides activation and verification protocols for lattice deployment phases.
"""

from .phase2_verification import (
    Phase2Verifier,
    run_phase2_verification,
)

__all__ = [
    "Phase2Verifier",
    "run_phase2_verification",
]
