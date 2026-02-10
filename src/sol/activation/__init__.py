"""
FREQ AI Activation Module

Provides activation and verification protocols for lattice deployment phases.

Phase 2: Testing, Integration, Intelligence - COMPLETED
Phase 3: Virtual Drafting & Flash LiDAR - ACTIVE
"""

from .phase2_verification import (
    Phase2Verifier,
    run_phase2_verification,
)

from .phase3_activation import (
    Phase3Activator,
    Phase3Milestone,
    Phase3ReadinessStatus,
    run_phase3_activation,
    get_phase3_status_summary,
)

__all__ = [
    # Phase 2
    "Phase2Verifier",
    "run_phase2_verification",
    # Phase 3
    "Phase3Activator",
    "Phase3Milestone",
    "Phase3ReadinessStatus",
    "run_phase3_activation",
    "get_phase3_status_summary",
]
