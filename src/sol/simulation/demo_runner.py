#!/usr/bin/env python3
"""
SOL Maritime Barge Drafting — Demonstration Runner

Executes the full SCAN > PROCESS > REPORT simulation and renders
a presentation-ready output for the Google Cloud Startup Program.

Usage:
    python -m src.sol.simulation.demo_runner
"""

import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))

from sol.simulation.maritime_barge import MaritimeBargeSimulation


# --- Terminal formatting helpers ---

def _header(text: str, char: str = "=", width: int = 80) -> str:
    return f"\n{char * width}\n  {text}\n{char * width}"


def _subheader(text: str) -> str:
    return f"\n  --- {text} ---"


def _kv(key: str, value, indent: int = 4) -> str:
    pad = " " * indent
    return f"{pad}{key:<36} {value}"


def _status_badge(ok: bool) -> str:
    return "[ PASS ]" if ok else "[ FAIL ]"


def _bar(value: float, max_val: float, width: int = 30) -> str:
    filled = int((value / max_val) * width) if max_val > 0 else 0
    return "[" + "#" * filled + "-" * (width - filled) + "]"


# --- Main renderer ---

def render_demo(results: dict) -> str:
    """Render simulation results as a presentation-ready terminal report."""
    lines = []

    lines.append(_header("SOL LATTICE — MARITIME BARGE DRAFTING OPERATIONS", "="))
    lines.append(_kv("Codename:", "Antigravity"))
    lines.append(_kv("Mission Vector:", "vector_gamma — Maritime Barge Drafting"))
    lines.append(_kv("Governance:", "FREQ LAW (Fast, Robust, Evolutionary, Quantified)"))
    lines.append(_kv("Infrastructure:", "Google Cloud Vertex AI"))
    lines.append(_kv("Sovereign Intent Originator:", "Chief Dre"))

    # --- Mission ---
    mission = results.get("mission", {})
    lines.append(_header("PHASE 1: MISSION INITIALIZATION", "-"))
    lines.append(_kv("Mission ID:", mission.get("mission_id", "N/A")))
    lines.append(_kv("Status:", mission.get("status", "N/A")))

    # --- Vessel ---
    vessel_data = results.get("vessel", {})
    spec = vessel_data.get("spec", {})
    lines.append(_header("PHASE 2: VESSEL REGISTRATION", "-"))
    lines.append(_kv("Vessel ID:", spec.get("vessel_id", "N/A")))
    lines.append(_kv("Name:", spec.get("name", "N/A")))
    lines.append(_kv("LOA:", f"{spec.get('loa_m', 0):.2f} m ({spec.get('loa_m', 0) * 3.281:.0f} ft)"))
    lines.append(_kv("Beam:", f"{spec.get('beam_m', 0):.2f} m ({spec.get('beam_m', 0) * 3.281:.0f} ft)"))
    lines.append(_kv("Depth:", f"{spec.get('depth_m', 0):.2f} m ({spec.get('depth_m', 0) * 3.281:.0f} ft)"))
    lines.append(_kv("Light Draft:", f"{spec.get('light_draft_m', 0):.2f} m"))
    lines.append(_kv("Max Draft:", f"{spec.get('max_draft_m', 0):.2f} m"))
    lines.append(_kv("Deadweight:", f"{spec.get('deadweight_t', 0):.0f} MT"))
    lines.append(_kv("Ballast Tanks:", f"{spec.get('ballast_tanks', 0)} x {spec.get('tank_capacity_m3', 0):.0f} m3"))

    # --- SCAN ---
    scan = results.get("scan", {})
    lines.append(_header("PHASE 3: SCAN — IoT SENSOR INGESTION", "-"))
    lines.append(_kv("Sensor Readings Ingested:", scan.get("readings_ingested", 0)))
    lines.append(_kv("Sensor Type:", "Ultrasonic Draft Sensors (x6)"))
    lines.append(_kv("Positions:", "Fore (PS/SB), Midship (PS/SB), Aft (PS/SB)"))
    lines.append(_kv("Data Pipeline:", "IoT Gateway > Cloud Run > Maritime Ops Node"))
    lines.append(_kv("Status:", scan.get("status", "N/A")))

    # --- PROCESS: Draft Survey ---
    survey_result = results.get("draft_survey", {})
    survey = survey_result.get("survey", {})
    lines.append(_header("PHASE 4: PROCESS — DRAFT SURVEY COMPUTATION", "-"))
    lines.append(_kv("Survey ID:", survey.get("survey_id", "N/A")[:16] + "..."))
    lines.append("")
    lines.append(_subheader("Draft Readings"))
    lines.append(_kv("Fore Draft:", f"{survey.get('fore_draft_m', 0):.3f} m"))
    lines.append(_kv("Midship Draft:", f"{survey.get('mid_draft_m', 0):.3f} m"))
    lines.append(_kv("Aft Draft:", f"{survey.get('aft_draft_m', 0):.3f} m"))
    lines.append(_kv("Mean Draft (Simpson):", f"{survey.get('mean_draft_m', 0):.3f} m"))
    lines.append(_kv("Trim:", f"{survey.get('trim_m', 0):.3f} m ({'by stern' if survey.get('trim_m', 0) > 0 else 'by bow'})"))

    lines.append("")
    lines.append(_subheader("Displacement & Cargo"))
    lines.append(_kv("Water Density:", f"{survey.get('water_density_kg_m3', 0):.2f} kg/m3"))
    lines.append(_kv("Block Coefficient:", f"{survey.get('block_coefficient', 0):.4f}"))
    lines.append(_kv("Displacement:", f"{survey.get('displacement_t', 0):.1f} MT"))
    lines.append(_kv("Cargo Weight:", f"{survey.get('cargo_weight_t', 0):.1f} MT"))

    lines.append("")
    lines.append(_subheader("Safety Metrics"))
    max_draft = spec.get("max_draft_m", 3.05)
    mean_draft = survey.get("mean_draft_m", 0)
    lines.append(_kv("Freeboard:", f"{survey.get('freeboard_m', 0):.3f} m"))
    lines.append(_kv("Under-Keel Clearance:", f"{survey.get('under_keel_clearance_m', 0):.3f} m"))
    lines.append(_kv("Metacentric Height (GM):", f"{survey.get('stability_gm_m', 0):.3f} m"))
    lines.append(_kv("Draft Utilization:", f"{_bar(mean_draft, max_draft)} {mean_draft:.2f}/{max_draft:.2f} m"))

    lines.append("")
    lines.append(_subheader("Compliance"))
    lines.append(_kv("Status:", _status_badge(survey.get("is_compliant", False))))
    for note in survey.get("compliance_notes", []):
        lines.append(f"      > {note}")

    # --- Ballast ---
    ballast_result = results.get("ballast", {})
    plan = ballast_result.get("plan", {})
    lines.append(_header("PHASE 5: BALLAST OPTIMIZATION", "-"))
    lines.append(_kv("Target Trim:", f"{plan.get('target_trim_m', 0):.3f} m"))
    lines.append(_kv("Achieved Trim:", f"{plan.get('achieved_trim_m', 0):.3f} m"))
    lines.append(_kv("Total Ballast:", f"{plan.get('total_ballast_m3', 0):.1f} m3"))
    lines.append(_kv("Pumping Cost:", f"${plan.get('estimated_cost_usd', 0):.2f}"))
    lines.append("")
    lines.append(_subheader("Tank Distribution"))
    for tank, level in plan.get("tank_levels", {}).items():
        pct = int(level * 100)
        lines.append(f"      {tank:<12}  {_bar(level, 1.0, 20)}  {pct}%")

    # --- Stability ---
    stability = results.get("stability", {})
    lines.append(_header("PHASE 6: STABILITY ASSESSMENT", "-"))
    lines.append(_kv("Metacentric Height (GM):", f"{stability.get('metacentric_height_m', 0):.3f} m"))
    lines.append(_kv("Risk Level:", stability.get("risk_level", "N/A")))
    lines.append(_kv("GZ at 10 deg:", f"{stability.get('gz_at_10_deg', 0):.4f} m"))
    lines.append(_kv("Vanishing Stability:", f"{stability.get('angle_of_vanishing_stability_deg', 0):.1f} deg"))
    lines.append(_kv("Assessment:", stability.get("recommendation", "N/A")))

    # --- Governance ---
    gov = results.get("governance", {})
    consensus = gov.get("consensus", {})
    veto = gov.get("veto", {})
    lines.append(_header("PHASE 7: GOVERNANCE — FREQ LAW VALIDATION", "-"))
    lines.append(_subheader("Consensus (k=3 Quorum)"))
    lines.append(_kv("Required Votes:", consensus.get("required_k", 3)))
    lines.append(_kv("Quorum Achieved:", _status_badge(consensus.get("has_quorum", False))))
    lines.append(_kv("Consensus Status:", consensus.get("status", "N/A")))

    lines.append("")
    lines.append(_subheader("VETO Authority (GOVEngine)"))
    lines.append(_kv("VETO Exercised:", "NO" if not veto.get("vetoed") else "YES"))
    lines.append(_kv("Status:", veto.get("status", "N/A")))

    lines.append("")
    lines.append(_kv("GOVERNANCE DECISION:", gov.get("overall_status", "N/A")))

    # --- Cost Analysis ---
    cost = results.get("cost_analysis", {})
    manual = cost.get("traditional_manual", {})
    drone = cost.get("drone_survey", {})
    sol = cost.get("sol_autonomous", {})
    lines.append(_header("PHASE 8: COST ANALYSIS — SOL vs TRADITIONAL", "-"))
    lines.append(_kv("Analysis Period:", f"{cost.get('analysis_period_months', 0)} months"))
    lines.append(_kv("Surveys:", f"{cost.get('surveys_per_month', 0)}/month x {cost.get('analysis_period_months', 0)} months = {cost.get('total_surveys', 0)} total"))

    lines.append("")
    lines.append(_subheader("Annual Cost Comparison"))
    max_cost = max(manual.get("annual_cost_usd", 1), drone.get("annual_cost_usd", 1), sol.get("annual_cost_usd", 1))
    lines.append(_kv("Manual Surveyor:", f"${manual.get('annual_cost_usd', 0):>12,.2f}  {_bar(manual.get('annual_cost_usd', 0), max_cost, 25)}"))
    lines.append(_kv("Drone Survey:", f"${drone.get('annual_cost_usd', 0):>12,.2f}  {_bar(drone.get('annual_cost_usd', 0), max_cost, 25)}"))
    lines.append(_kv("SOL Autonomous:", f"${sol.get('annual_cost_usd', 0):>12,.2f}  {_bar(sol.get('annual_cost_usd', 0), max_cost, 25)}"))

    lines.append("")
    lines.append(_subheader("Savings"))
    lines.append(_kv("vs Manual Surveyor:", f"${cost.get('savings_vs_manual_usd', 0):>12,.2f}  ({cost.get('savings_vs_manual_pct', 0):.1f}% reduction)"))
    lines.append(_kv("vs Drone Survey:", f"${cost.get('savings_vs_drone_usd', 0):>12,.2f}  ({cost.get('savings_vs_drone_pct', 0):.1f}% reduction)"))

    lines.append("")
    lines.append(_subheader("SOL Advantages"))
    for adv in sol.get("advantages", []):
        lines.append(f"      + {adv}")

    # --- Summary ---
    summary = results.get("simulation_summary", {})
    lines.append(_header("SIMULATION SUMMARY", "="))
    lines.append(_kv("Simulation ID:", summary.get("simulation_id", "N/A")[:16] + "..."))
    lines.append(_kv("Total Execution Time:", f"{summary.get('total_execution_time_ms', 0):.2f} ms"))
    lines.append(_kv("FREQ LAW Compliant:", _status_badge(summary.get("freq_law_compliant", False))))
    lines.append(_kv("Lattice Nodes Active:", summary.get("lattice_nodes_active", 0)))
    lines.append(_kv("Events Logged:", summary.get("events_logged", 0)))
    lines.append(_kv("Audit Trail Entries:", summary.get("audit_entries", 0)))
    lines.append(_kv("Governance Status:", summary.get("governance_status", "N/A")))

    lines.append("")
    lines.append(_header("GCP SERVICES UTILIZED", "-"))
    lines.append(_kv("Vertex AI Agent Builder:", "Multi-agent orchestration (Gemini substrates)"))
    lines.append(_kv("BigQuery:", "Audit trail + operational analytics"))
    lines.append(_kv("Cloud Run:", "IoT sensor ingestion service"))
    lines.append(_kv("Cloud Logging:", "Real-time observability (JSON structured)"))
    lines.append(_kv("Dialogflow CX:", "Agent playbook execution"))
    lines.append(_kv("Cloud IoT:", "Sensor device management"))

    lines.append("")
    lines.append(_header("CREDIT REQUEST: $350,000 GCP CREDITS", "-"))
    lines.append(_kv("Phase 3 Objective:", "First Mission Simulation & Deployment"))
    lines.append(_kv("Hardware Integration:", "IoT draft sensor array (6-unit cluster)"))
    lines.append(_kv("Vertex AI Workload:", "Multi-agent lattice at production scale"))
    lines.append(_kv("BigQuery Analytics:", "12-month operational data warehouse"))
    lines.append(_kv("Target Market:", "Gulf of Mexico inland barge operators"))
    lines.append(_kv("Unit Economics:", f"${sol.get('annual_cost_usd', 0):,.2f}/yr vs ${manual.get('annual_cost_usd', 0):,.2f}/yr manual"))

    lines.append("")
    lines.append("=" * 80)
    lines.append("  SOL LATTICE — Sophisticated Operational Lattice")
    lines.append("  \"Replacing physical surveys with intelligence.\"")
    lines.append("=" * 80)
    lines.append("")

    return "\n".join(lines)


def main():
    """Run the demonstration."""
    print("\nInitializing SOL Lattice simulation...")
    print("Connecting lattice nodes...")
    print("Activating vector_gamma: Maritime Barge Drafting...\n")

    sim = MaritimeBargeSimulation()
    results = sim.run()

    # Render the demo output
    output = render_demo(results)
    print(output)

    # Also dump raw JSON for technical review
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_output.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Raw JSON output saved to: {json_path}")
    print("")


if __name__ == "__main__":
    main()
