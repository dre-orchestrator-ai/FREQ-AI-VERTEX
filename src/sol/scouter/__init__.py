"""
FREQ SOL Executor Scouter Module (VECTOR DELTA)

Autonomous partnership development agent for the Sophisticated Operational Lattice.
Handles LinkedIn/social media automation, investor outreach, and MFSIN scouting.

Components:
- ExecScouter: LatticeNode for partnership operations
- LinkedInBridge: MCP integration for LinkedIn automation
- PitchGenerator: Dynamic pitch generation from FREQ docs
- OutreachEngine: Multi-touch outreach sequence management
"""

from .node import ExecScouter, Prospect, ProspectTier, OutreachStatus
from .linkedin_bridge import LinkedInBridge, LinkedInConfig, LinkedInAction
from .pitch_generator import PitchGenerator, PitchOutput, PitchType, InvestorContext
from .outreach_engine import OutreachEngine, OutreachSequence, Touchpoint

__all__ = [
    # Core Node
    "ExecScouter",
    "Prospect",
    "ProspectTier",
    "OutreachStatus",
    # LinkedIn Bridge
    "LinkedInBridge",
    "LinkedInConfig",
    "LinkedInAction",
    # Pitch Generator
    "PitchGenerator",
    "PitchOutput",
    "PitchType",
    "InvestorContext",
    # Outreach Engine
    "OutreachEngine",
    "OutreachSequence",
    "Touchpoint",
]
