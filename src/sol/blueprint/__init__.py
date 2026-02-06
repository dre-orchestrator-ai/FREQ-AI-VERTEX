"""
FREQ AI Blueprint Module

Exports the FREQ Blueprint and SSC System Prompt for lattice initialization.

Blueprint Version: 3.0
Current Phase: PHASE_3_ACTIVE
Pivot: Digital Twin → Virtual Drafting & Flash LiDAR
"""

from .freq_blueprint import (
    FREQ_BLUEPRINT,
    SSC_SYSTEM_PROMPT,
    get_blueprint,
    get_ssc_system_prompt,
    get_architecture,
    get_hierarchy_level,
    get_freq_law_principles,
    get_mission_vector,
    get_deployment_phase,
    validate_blueprint,
    format_blueprint_summary,
    # Phase 3 specific
    get_phase3_config,
    get_vds_config,
    get_heritage_mode_config,
)

__all__ = [
    "FREQ_BLUEPRINT",
    "SSC_SYSTEM_PROMPT",
    "get_blueprint",
    "get_ssc_system_prompt",
    "get_architecture",
    "get_hierarchy_level",
    "get_freq_law_principles",
    "get_mission_vector",
    "get_deployment_phase",
    "validate_blueprint",
    "format_blueprint_summary",
    # Phase 3 specific
    "get_phase3_config",
    "get_vds_config",
    "get_heritage_mode_config",
]
