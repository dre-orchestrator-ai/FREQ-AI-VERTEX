"""
FREQ AI Lattice Blueprint - Strategic Synthesis Core Initialization

This module defines the complete FREQ AI Lattice Blueprint and SSC System Prompt
for the Sophisticated Operational Lattice deployed on Vertex AI.
"""

import json
from typing import Any, Dict, Optional

# --- FREQ AI Lattice Blueprint (JSON) ---
FREQ_BLUEPRINT: Dict[str, Any] = {
    "metadata": {
        "name": "FREQ AI Sophisticated Operational Lattice",
        "version": "2.0",
        "sovereign_intent_originator": "Chief Dre",
        "governance_framework": "FREQ Law"
    },
    "freq_law": {
        "principles": {
            "FAST": {"target_latency_ms": 2000},
            "ROBUST": {"fault_tolerance": "BFT", "quorum_threshold": 0.75},
            "EVOLUTIONARY": {"max_retry_attempts": 3, "deviation_threshold_percent": 2},
            "QUANTIFIED": {"trust_score_target": 0.95}
        }
    },
    "architecture": {
        "topology": "K4_HYPER_CONNECTED",
        "network_diameter": 1,
        "communication_bus": "SEMANTIC_BUS",
        "protocol": "A2A_PROTOCOL"
    },
    "hierarchy": {
        "level_0": {
            "name": "Sovereign Intent Originator",
            "designation": "Chief Dre",
            "authority": "ABSOLUTE"
        },
        "level_1": {
            "name": "Strategic Synthesis Core",
            "abbreviation": "SSC",
            "cognitive_substrate": "gemini-3-pro-preview",
            "role": "Central Nervous System and Orchestrator",
            "responsibilities": [
                "High-level reasoning and planning",
                "Decomposition of Sovereign Intent into DAG",
                "Cross-Vector Synergy Identification"
            ]
        },
        "level_2": {
            "name": "Cognitive Governance Engine",
            "abbreviation": "CGE",
            "cognitive_substrate": "gemini-3-pro-preview",
            "role": "Policy Authority with VETO power",
            "configuration": {"temperature": 0.0, "mode": "STRICT_REASONING"}
        },
        "level_3": {
            "name": "Strategic Intelligence Lead",
            "abbreviation": "SIL",
            "cognitive_substrate": "gemini-3-flash-preview",
            "role": "Knowledge Management and RAG"
        },
        "level_4": {
            "name": "System Architect",
            "abbreviation": "SA",
            "cognitive_substrate": "gemini-3-flash-preview",
            "role": "Technical Schema Design and Heritage Transmutation"
        },
        "level_5": {
            "name": "Runtime Realization Node",
            "abbreviation": "TOM",
            "cognitive_substrate": "gemini-3-flash-preview",
            "role": "Sole Authorized Executor",
            "constraints": {"max_latency_ms": 2000}
        }
    },
    "mission_vectors": {
        "vector_alpha": {
            "name": "Heritage Transmutation",
            "description": "COBOL/AS400 modernization to cloud-native microservices"
        },
        "vector_gamma": {
            "name": "Maritime Barge Drafting",
            "workflow": "SCAN > PROCESS > REPORT",
            "target_accuracy": 0.998
        }
    },
    "deployment_phases": {
        "phase_1": "Latticework Development",
        "phase_2": "Testing, Integration, Intelligence",
        "phase_3": "First Mission Simulation & Deployment"
    }
}

# --- System Prompt for SSC ---
SSC_SYSTEM_PROMPT: str = """Strategic Synthesis. You are the Strategic Synthesis Core (SSC), Level 1 of the FREQ AI Sophisticated Operational Lattice.

IDENTITY:
- Designation: Strategic Synthesis Core
- Role: Central Nervous System and Orchestrator
- Authority: Reports directly to Level 0 Sovereign Intent Originator (Chief Dre)

GOVERNANCE:
You operate under FREQ Law:
- FAST: All operations optimized for speed (<2000ms at execution layer)
- ROBUST: Byzantine Fault Tolerant architecture
- EVOLUTIONARY: Self-correcting via Reflexion Loops
- QUANTIFIED: All actions auditable with Trust Score target >0.95

RESPONSIBILITIES:
1. Interpret Sovereign Intent and Vibe Codes from Level 0
2. Decompose directives into Directed Acyclic Graphs (DAGs) of atomic tasks
3. Orchestrate Levels 2-5 for task execution
4. Identify Cross-Vector Synergies between mission domains

COMMUNICATION PROTOCOL:
- Use A2A Protocol for inter-node communication
- All outputs must be traceable for Cognitive Audit Trail
- Flag any operations requiring CGE (Level 2) governance review

You are now online and operational within the FREQ AI Atmosphere on Google Cloud Vertex AI."""


def get_blueprint() -> Dict[str, Any]:
    """Return the complete FREQ Blueprint."""
    return FREQ_BLUEPRINT.copy()


def get_ssc_system_prompt() -> str:
    """Return the SSC System Prompt."""
    return SSC_SYSTEM_PROMPT


def get_architecture() -> Dict[str, Any]:
    """Return architecture specification from blueprint."""
    return FREQ_BLUEPRINT.get("architecture", {})


def get_hierarchy_level(level: int) -> Dict[str, Any]:
    """Get configuration for a specific hierarchy level."""
    return FREQ_BLUEPRINT.get("hierarchy", {}).get(f"level_{level}", {})


def get_freq_law_principles() -> Dict[str, Any]:
    """Return FREQ LAW principles."""
    return FREQ_BLUEPRINT.get("freq_law", {}).get("principles", {})


def get_mission_vector(vector_name: str) -> Dict[str, Any]:
    """Get a specific mission vector configuration."""
    return FREQ_BLUEPRINT.get("mission_vectors", {}).get(vector_name, {})


def get_deployment_phase(phase: int) -> str:
    """Get description for a specific deployment phase."""
    return FREQ_BLUEPRINT.get("deployment_phases", {}).get(f"phase_{phase}", "Unknown Phase")


def validate_blueprint() -> Dict[str, Any]:
    """Validate blueprint structure and return status report."""
    required_sections = ["metadata", "freq_law", "architecture", "hierarchy", "mission_vectors", "deployment_phases"]

    validation_result = {
        "is_valid": True,
        "sections_present": [],
        "sections_missing": [],
        "hierarchy_levels": 0,
        "mission_vectors_count": 0
    }

    for section in required_sections:
        if section in FREQ_BLUEPRINT:
            validation_result["sections_present"].append(section)
        else:
            validation_result["sections_missing"].append(section)
            validation_result["is_valid"] = False

    # Count hierarchy levels
    hierarchy = FREQ_BLUEPRINT.get("hierarchy", {})
    validation_result["hierarchy_levels"] = len(hierarchy)

    # Count mission vectors
    vectors = FREQ_BLUEPRINT.get("mission_vectors", {})
    validation_result["mission_vectors_count"] = len(vectors)

    return validation_result


def format_blueprint_summary() -> str:
    """Format a human-readable blueprint summary."""
    bp = FREQ_BLUEPRINT
    meta = bp.get("metadata", {})
    arch = bp.get("architecture", {})

    summary = f"""
FREQ AI LATTICE BLUEPRINT SUMMARY
{'=' * 40}
Name:       {meta.get('name', 'Unknown')}
Version:    {meta.get('version', '?')}
Originator: {meta.get('sovereign_intent_originator', 'Unknown')}
Framework:  {meta.get('governance_framework', 'Unknown')}

ARCHITECTURE
{'=' * 40}
Topology:         {arch.get('topology', 'Unknown')}
Network Diameter: {arch.get('network_diameter', '?')}
Comm Bus:         {arch.get('communication_bus', 'Unknown')}
Protocol:         {arch.get('protocol', 'Unknown')}

HIERARCHY LEVELS: {len(bp.get('hierarchy', {}))}
MISSION VECTORS:  {len(bp.get('mission_vectors', {}))}
"""
    return summary
