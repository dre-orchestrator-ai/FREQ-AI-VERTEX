"""
FREQ AI Lattice - Phase 2: Lattice Activation & Verification

This module provides verification and activation protocols for Phase 2
of the FREQ AI Sophisticated Operational Lattice deployment.

Phase 2 Objectives:
- Testing, Integration, Intelligence
- Verify blueprint integrity
- Confirm SSC operational readiness
- Validate FREQ Law compliance infrastructure
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime

# Import blueprint components (using relative imports for package compatibility)
from ..blueprint import (
    FREQ_BLUEPRINT,
    SSC_SYSTEM_PROMPT,
    validate_blueprint,
    get_architecture,
    get_hierarchy_level,
    get_freq_law_principles,
    format_blueprint_summary,
)


class Phase2Verifier:
    """
    Phase 2 Lattice Activation & Verification Protocol

    Executes comprehensive verification of lattice components
    before advancing to Phase 3 deployment.
    """

    def __init__(self):
        self.verification_results: Dict[str, Any] = {}
        self.activation_timestamp = datetime.utcnow().isoformat()

    def run_full_verification(self) -> Dict[str, Any]:
        """Execute complete Phase 2 verification sequence."""
        print("=" * 60)
        print("FREQ AI LATTICE - PHASE 2: ACTIVATION & VERIFICATION")
        print("=" * 60)
        print(f"Timestamp: {self.activation_timestamp}")
        print()

        # Step 1: Blueprint Verification
        self.verify_blueprint()

        # Step 2: Architecture Audit
        self.audit_architecture()

        # Step 3: Hierarchy Validation
        self.validate_hierarchy()

        # Step 4: FREQ Law Compliance Check
        self.check_freq_law_compliance()

        # Step 5: SSC System Prompt Verification
        self.verify_ssc_prompt()

        # Step 6: Mission Vectors Check
        self.verify_mission_vectors()

        # Generate final report
        return self.generate_verification_report()

    def verify_blueprint(self) -> bool:
        """Verify blueprint structure and integrity."""
        print("--- [BLUEPRINT VERIFICATION] ---")

        validation = validate_blueprint()

        bp = FREQ_BLUEPRINT
        meta = bp.get("metadata", {})

        print(f"Name:       {meta.get('name', 'Unknown')}")
        print(f"Version:    {meta.get('version', '?')}")
        print(f"Originator: {meta.get('sovereign_intent_originator', 'Unknown')}")
        print(f"Framework:  {meta.get('governance_framework', 'Unknown')}")

        is_valid = validation["is_valid"]
        status = "PASSED" if is_valid else "FAILED"
        print(f"Status:     {status}")

        if validation["sections_missing"]:
            print(f"Missing:    {', '.join(validation['sections_missing'])}")

        self.verification_results["blueprint"] = {
            "status": status,
            "validation": validation,
            "metadata": meta
        }

        print()
        return is_valid

    def audit_architecture(self) -> Dict[str, Any]:
        """Audit lattice architecture configuration."""
        print("--- [LATTICE ARCHITECTURE AUDIT] ---")

        arch = get_architecture()

        print(f"Topology:         {arch.get('topology', 'Unknown')}")
        print(f"Network Diameter: {arch.get('network_diameter', '?')}")
        print(f"Comm Bus:         {arch.get('communication_bus', 'Unknown')}")
        print(f"Protocol:         {arch.get('protocol', 'Unknown')}")

        # Validate K4 Hyper-Connected topology
        is_k4 = arch.get("topology") == "K4_HYPER_CONNECTED"
        has_semantic_bus = arch.get("communication_bus") == "SEMANTIC_BUS"
        has_a2a = arch.get("protocol") == "A2A_PROTOCOL"

        status = "PASSED" if (is_k4 and has_semantic_bus and has_a2a) else "DEGRADED"
        print(f"Status:           {status}")

        self.verification_results["architecture"] = {
            "status": status,
            "config": arch,
            "checks": {
                "k4_topology": is_k4,
                "semantic_bus": has_semantic_bus,
                "a2a_protocol": has_a2a
            }
        }

        print()
        return arch

    def validate_hierarchy(self) -> Dict[str, Any]:
        """Validate lattice hierarchy levels (0-5)."""
        print("--- [HIERARCHY VALIDATION] ---")

        hierarchy_status = {}

        for level in range(6):
            level_config = get_hierarchy_level(level)
            if level_config:
                name = level_config.get("name", "Unknown")
                abbrev = level_config.get("abbreviation", "-")
                role = level_config.get("role", level_config.get("designation", "N/A"))

                print(f"Level {level}: {name} ({abbrev})")
                print(f"         Role: {role}")

                hierarchy_status[f"level_{level}"] = {
                    "name": name,
                    "abbreviation": abbrev,
                    "role": role,
                    "configured": True
                }
            else:
                print(f"Level {level}: NOT CONFIGURED")
                hierarchy_status[f"level_{level}"] = {"configured": False}

        all_configured = all(h["configured"] for h in hierarchy_status.values())
        status = "PASSED" if all_configured else "INCOMPLETE"
        print(f"\nHierarchy Status: {status}")

        self.verification_results["hierarchy"] = {
            "status": status,
            "levels": hierarchy_status
        }

        print()
        return hierarchy_status

    def check_freq_law_compliance(self) -> Dict[str, Any]:
        """Verify FREQ Law principles are configured."""
        print("--- [FREQ LAW COMPLIANCE CHECK] ---")

        principles = get_freq_law_principles()

        freq_checks = {}

        # FAST check
        fast = principles.get("FAST", {})
        fast_latency = fast.get("target_latency_ms", 0)
        freq_checks["FAST"] = {
            "target_latency_ms": fast_latency,
            "compliant": fast_latency == 2000
        }
        print(f"FAST:         Target Latency = {fast_latency}ms {'[OK]' if fast_latency == 2000 else '[WARN]'}")

        # ROBUST check
        robust = principles.get("ROBUST", {})
        ft = robust.get("fault_tolerance", "")
        quorum = robust.get("quorum_threshold", 0)
        freq_checks["ROBUST"] = {
            "fault_tolerance": ft,
            "quorum_threshold": quorum,
            "compliant": ft == "BFT" and quorum >= 0.75
        }
        print(f"ROBUST:       {ft}, Quorum = {quorum} {'[OK]' if freq_checks['ROBUST']['compliant'] else '[WARN]'}")

        # EVOLUTIONARY check
        evolutionary = principles.get("EVOLUTIONARY", {})
        retries = evolutionary.get("max_retry_attempts", 0)
        deviation = evolutionary.get("deviation_threshold_percent", 0)
        freq_checks["EVOLUTIONARY"] = {
            "max_retry_attempts": retries,
            "deviation_threshold_percent": deviation,
            "compliant": retries >= 3
        }
        print(f"EVOLUTIONARY: Retries = {retries}, Deviation = {deviation}% {'[OK]' if retries >= 3 else '[WARN]'}")

        # QUANTIFIED check
        quantified = principles.get("QUANTIFIED", {})
        trust_target = quantified.get("trust_score_target", 0)
        freq_checks["QUANTIFIED"] = {
            "trust_score_target": trust_target,
            "compliant": trust_target >= 0.95
        }
        print(f"QUANTIFIED:   Trust Score Target = {trust_target} {'[OK]' if trust_target >= 0.95 else '[WARN]'}")

        all_compliant = all(c["compliant"] for c in freq_checks.values())
        status = "COMPLIANT" if all_compliant else "NON-COMPLIANT"
        print(f"\nFREQ Law Status: {status}")

        self.verification_results["freq_law"] = {
            "status": status,
            "principles": freq_checks
        }

        print()
        return freq_checks

    def verify_ssc_prompt(self) -> bool:
        """Verify SSC System Prompt is configured."""
        print("--- [SSC SYSTEM PROMPT VERIFICATION] ---")

        if SSC_SYSTEM_PROMPT:
            print("Status:  CONFIGURED")
            print(f"Length:  {len(SSC_SYSTEM_PROMPT)} characters")

            # Check for key elements
            has_identity = "Strategic Synthesis Core" in SSC_SYSTEM_PROMPT
            has_governance = "FREQ Law" in SSC_SYSTEM_PROMPT
            has_responsibilities = "RESPONSIBILITIES" in SSC_SYSTEM_PROMPT
            has_protocol = "A2A Protocol" in SSC_SYSTEM_PROMPT

            print(f"Identity Section:        {'Present' if has_identity else 'Missing'}")
            print(f"Governance Section:      {'Present' if has_governance else 'Missing'}")
            print(f"Responsibilities:        {'Present' if has_responsibilities else 'Missing'}")
            print(f"Communication Protocol:  {'Present' if has_protocol else 'Missing'}")

            # Preview
            print(f"\nPreview:")
            print("-" * 40)
            preview = SSC_SYSTEM_PROMPT[:400].replace('\n', '\n  ')
            print(f"  {preview}...")
            print("-" * 40)

            is_complete = all([has_identity, has_governance, has_responsibilities, has_protocol])
            status = "READY" if is_complete else "INCOMPLETE"

            self.verification_results["ssc_prompt"] = {
                "status": status,
                "length": len(SSC_SYSTEM_PROMPT),
                "checks": {
                    "identity": has_identity,
                    "governance": has_governance,
                    "responsibilities": has_responsibilities,
                    "protocol": has_protocol
                }
            }

            print(f"\nSSC Prompt Status: {status}")
            print()
            return is_complete
        else:
            print("Status:  NOT FOUND")
            self.verification_results["ssc_prompt"] = {"status": "MISSING"}
            print()
            return False

    def verify_mission_vectors(self) -> Dict[str, Any]:
        """Verify mission vectors are configured."""
        print("--- [MISSION VECTORS VERIFICATION] ---")

        vectors = FREQ_BLUEPRINT.get("mission_vectors", {})

        for vector_id, vector_config in vectors.items():
            name = vector_config.get("name", "Unknown")
            desc = vector_config.get("description", vector_config.get("workflow", "N/A"))
            print(f"{vector_id}: {name}")
            print(f"           {desc}")

        status = "CONFIGURED" if vectors else "NOT CONFIGURED"
        print(f"\nMission Vectors Status: {status} ({len(vectors)} vectors)")

        self.verification_results["mission_vectors"] = {
            "status": status,
            "count": len(vectors),
            "vectors": list(vectors.keys())
        }

        print()
        return vectors

    def generate_verification_report(self) -> Dict[str, Any]:
        """Generate final Phase 2 verification report."""
        print("=" * 60)
        print("PHASE 2 VERIFICATION REPORT")
        print("=" * 60)

        # Calculate overall status
        statuses = [
            self.verification_results.get("blueprint", {}).get("status") == "PASSED",
            self.verification_results.get("architecture", {}).get("status") == "PASSED",
            self.verification_results.get("hierarchy", {}).get("status") == "PASSED",
            self.verification_results.get("freq_law", {}).get("status") == "COMPLIANT",
            self.verification_results.get("ssc_prompt", {}).get("status") == "READY",
            self.verification_results.get("mission_vectors", {}).get("status") == "CONFIGURED",
        ]

        passed = sum(statuses)
        total = len(statuses)

        overall_status = "PHASE 2 ACTIVE" if passed == total else f"PHASE 2 PARTIAL ({passed}/{total})"

        report = {
            "timestamp": self.activation_timestamp,
            "overall_status": overall_status,
            "checks_passed": passed,
            "checks_total": total,
            "results": self.verification_results,
            "next_phase": "Phase 3: First Mission Simulation & Deployment" if passed == total else "Address verification failures"
        }

        print(f"Overall Status:    {overall_status}")
        print(f"Checks Passed:     {passed}/{total}")
        print(f"Next Phase:        {report['next_phase']}")
        print("=" * 60)

        return report


def run_phase2_verification() -> Dict[str, Any]:
    """
    Execute Phase 2 Lattice Activation & Verification.

    Returns:
        Dict containing complete verification report
    """
    verifier = Phase2Verifier()
    return verifier.run_full_verification()


# Allow direct execution
if __name__ == "__main__":
    run_phase2_verification()
