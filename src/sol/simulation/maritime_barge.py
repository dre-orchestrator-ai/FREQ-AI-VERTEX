"""
Maritime Barge Drafting Simulation Engine

End-to-end simulation of autonomous maritime barge drafting operations
using the SOL Lattice. Demonstrates the full SCAN > PROCESS > REPORT
workflow defined in vector_gamma of the FREQ Blueprint.
"""

import time
import uuid
from typing import Any, Dict, List
from datetime import datetime

from sol.nodes.base import NodeMessage
from sol.nodes.maritime_ops import MaritimeBargeOps
from sol.nodes.strategic_op import StrategicOP
from sol.nodes.gov_engine import GOVEngine
from sol.nodes.optimal_intel import OptimalIntel
from sol.nodes.exec_automate import ExecAutomate
from sol.consensus.quorum import QuorumConsensus, VoteType
from sol.governance.freq_law import FreqLaw
from sol.governance.veto import VetoAuthority
from sol.audit.bigquery import BigQueryAuditTrail


class MaritimeBargeSimulation:
    """
    Full simulation of maritime barge drafting operations orchestrated
    by the SOL Lattice on Google Cloud Vertex AI.

    Demonstrates:
      1. Lattice node initialization and interconnection
      2. Barge registration with physical specs
      3. IoT sensor data ingestion (SCAN)
      4. AI-driven draft survey computation (PROCESS)
      5. Autonomous ballast optimization
      6. Stability assessment and compliance verification
      7. Governance validation via GOVEngine (FREQ LAW + VETO)
      8. k=3 consensus quorum for safety-critical operations
      9. BigQuery audit trail logging
      10. Cost analysis vs traditional methods (REPORT)
    """

    def __init__(self, project_id: str = "freq-ai-vertex"):
        self.project_id = project_id
        self.simulation_id = str(uuid.uuid4())
        self.start_time = None
        self.events: List[Dict[str, Any]] = []

        # Initialize lattice nodes
        self.maritime_ops = MaritimeBargeOps(node_id="maritime-ops-001")
        self.strategic_op = StrategicOP(node_id="strategic-op-001")
        self.gov_engine = GOVEngine(node_id="gov-engine-001")
        self.optimal_intel = OptimalIntel(node_id="optimal-intel-001")
        self.exec_automate = ExecAutomate(node_id="exec-automate-001")

        # Initialize governance components
        self.freq_law = FreqLaw()
        self.veto_authority = VetoAuthority()
        self.consensus = QuorumConsensus()
        self.audit = BigQueryAuditTrail(project_id=project_id)

        # Wire up lattice connections
        self.strategic_op.connect_node(self.maritime_ops)
        self.strategic_op.connect_node(self.gov_engine)
        self.strategic_op.connect_node(self.optimal_intel)
        self.maritime_ops.connect_node(self.gov_engine)
        self.maritime_ops.connect_node(self.optimal_intel)
        self.maritime_ops.connect_node(self.exec_automate)

        # Register consensus voters
        self.consensus.register_voter(self.strategic_op.node_id)
        self.consensus.register_voter(self.gov_engine.node_id)
        self.consensus.register_voter(self.maritime_ops.node_id)

    def _log_event(self, phase: str, action: str, details: Dict[str, Any],
                   execution_time_ms: float = 0.0) -> None:
        """Log a simulation event."""
        event = {
            "simulation_id": self.simulation_id,
            "phase": phase,
            "action": action,
            "details": details,
            "execution_time_ms": round(execution_time_ms, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.events.append(event)

    def run(self) -> Dict[str, Any]:
        """Execute the full maritime barge drafting simulation."""
        self.start_time = time.time()
        results = {}

        # === PHASE 1: MISSION INITIALIZATION ===
        results["mission"] = self._phase_mission_init()

        # === PHASE 2: SCAN — Sensor Data Ingestion ===
        results["vessel"] = self._phase_register_vessel()
        results["scan"] = self._phase_scan()

        # === PHASE 3: PROCESS — Draft Survey + Ballast + Stability ===
        results["draft_survey"] = self._phase_compute_survey()
        results["ballast"] = self._phase_optimize_ballast()
        results["stability"] = self._phase_assess_stability(results["draft_survey"]["survey_id"])

        # === PHASE 4: GOVERNANCE — FREQ LAW + Consensus + VETO ===
        results["governance"] = self._phase_governance(results["draft_survey"])

        # === PHASE 5: REPORT — Final Report + Cost Analysis ===
        results["report"] = self._phase_report()
        results["cost_analysis"] = self._phase_cost_analysis()

        # === Finalize ===
        total_time = (time.time() - self.start_time) * 1000
        results["simulation_summary"] = {
            "simulation_id": self.simulation_id,
            "total_execution_time_ms": round(total_time, 2),
            "freq_law_compliant": total_time < 2000,
            "events_logged": len(self.events),
            "audit_entries": self.audit.get_buffer_size(),
            "lattice_nodes_active": 5,
            "governance_status": "APPROVED",
            "timestamp": datetime.utcnow().isoformat(),
        }

        self._log_event("COMPLETE", "simulation_finished", results["simulation_summary"], total_time)
        return results

    def _phase_mission_init(self) -> Dict[str, Any]:
        """Initialize the maritime barge drafting mission."""
        t = time.time()
        msg = NodeMessage(
            source_node="simulation",
            target_node=self.strategic_op.node_id,
            operation="create_mission",
            payload={
                "name": "Maritime Barge Draft Survey — Autonomous Operations",
                "objectives": [
                    "Execute autonomous draft survey via IoT sensors",
                    "Compute displacement and cargo weight",
                    "Optimize ballast for even keel",
                    "Validate USCG/IMO regulatory compliance",
                    "Generate cost comparison vs traditional methods",
                ],
                "priority": "critical",
                "vector": "vector_gamma",
            },
        )
        response = self.strategic_op.process_message(msg)
        elapsed = (time.time() - t) * 1000
        self._log_event("INIT", "mission_created", response.result, elapsed)

        self.audit.log_operation(
            operation="create_mission",
            node_id=self.strategic_op.node_id,
            node_type="strategic_op",
            request_payload=msg.payload,
            response_payload=response.result,
            execution_time_ms=elapsed,
        )
        return response.result

    def _phase_register_vessel(self) -> Dict[str, Any]:
        """Register a barge with realistic Gulf of Mexico specs."""
        t = time.time()
        msg = NodeMessage(
            source_node=self.strategic_op.node_id,
            target_node=self.maritime_ops.node_id,
            operation="register_vessel",
            payload={
                "vessel_id": "BARGE-GOM-2026-001",
                "name": "Gulf Runner 1",
                "loa_m": 60.96,          # 200 ft deck barge
                "beam_m": 18.29,         # 60 ft beam
                "depth_m": 3.66,         # 12 ft depth
                "light_draft_m": 0.91,   # 3 ft light draft
                "max_draft_m": 3.05,     # 10 ft loaded draft
                "displacement_t": 850.0,
                "deadweight_t": 3200.0,
                "ballast_tanks": 6,
                "tank_capacity_m3": 75.0,
            },
        )
        response = self.maritime_ops.process_message(msg)
        elapsed = (time.time() - t) * 1000
        self._log_event("INIT", "vessel_registered", response.result, elapsed)
        return response.result

    def _phase_scan(self) -> Dict[str, Any]:
        """Simulate IoT sensor data ingestion from 6 ultrasonic draft sensors."""
        t = time.time()

        # Simulate sensor readings at 3 positions (fore, midship, aft) x 2 sides
        readings = [
            {"sensor_id": "US-FORE-PS", "position": "fore", "draft_m": 2.15, "water_temp_c": 24.3, "salinity_ppt": 33.5},
            {"sensor_id": "US-FORE-SB", "position": "fore", "draft_m": 2.17, "water_temp_c": 24.2, "salinity_ppt": 33.6},
            {"sensor_id": "US-MID-PS", "position": "midship", "draft_m": 2.42, "water_temp_c": 24.1, "salinity_ppt": 33.4},
            {"sensor_id": "US-MID-SB", "position": "midship", "draft_m": 2.40, "water_temp_c": 24.0, "salinity_ppt": 33.5},
            {"sensor_id": "US-AFT-PS", "position": "aft", "draft_m": 2.68, "water_temp_c": 23.9, "salinity_ppt": 33.3},
            {"sensor_id": "US-AFT-SB", "position": "aft", "draft_m": 2.70, "water_temp_c": 24.1, "salinity_ppt": 33.4},
        ]

        msg = NodeMessage(
            source_node="iot_gateway",
            target_node=self.maritime_ops.node_id,
            operation="ingest_sensor_data",
            payload={
                "vessel_id": "BARGE-GOM-2026-001",
                "readings": readings,
            },
        )
        response = self.maritime_ops.process_message(msg)
        elapsed = (time.time() - t) * 1000
        self._log_event("SCAN", "sensor_data_ingested", response.result, elapsed)

        self.audit.log_operation(
            operation="ingest_sensor_data",
            node_id=self.maritime_ops.node_id,
            node_type="maritime_barge_ops",
            request_payload={"vessel_id": "BARGE-GOM-2026-001", "sensor_count": len(readings)},
            response_payload=response.result,
            execution_time_ms=elapsed,
        )
        return response.result

    def _phase_compute_survey(self) -> Dict[str, Any]:
        """Compute full draft survey from sensor data."""
        t = time.time()
        msg = NodeMessage(
            source_node=self.strategic_op.node_id,
            target_node=self.maritime_ops.node_id,
            operation="compute_draft_survey",
            payload={
                "vessel_id": "BARGE-GOM-2026-001",
                "water_depth_m": 9.14,   # 30 ft channel depth
            },
        )
        response = self.maritime_ops.process_message(msg)
        elapsed = (time.time() - t) * 1000
        self._log_event("PROCESS", "draft_survey_computed", response.result, elapsed)

        self.audit.log_operation(
            operation="compute_draft_survey",
            node_id=self.maritime_ops.node_id,
            node_type="maritime_barge_ops",
            request_payload=msg.payload,
            response_payload=response.result,
            execution_time_ms=elapsed,
        )
        return response.result

    def _phase_optimize_ballast(self) -> Dict[str, Any]:
        """Optimize ballast for even keel."""
        t = time.time()
        msg = NodeMessage(
            source_node=self.optimal_intel.node_id,
            target_node=self.maritime_ops.node_id,
            operation="optimize_ballast",
            payload={
                "vessel_id": "BARGE-GOM-2026-001",
                "target_trim_m": 0.0,
                "target_list_deg": 0.0,
            },
        )
        response = self.maritime_ops.process_message(msg)
        elapsed = (time.time() - t) * 1000
        self._log_event("PROCESS", "ballast_optimized", response.result, elapsed)
        return response.result

    def _phase_assess_stability(self, survey_id: str) -> Dict[str, Any]:
        """Assess vessel stability from survey results."""
        t = time.time()
        msg = NodeMessage(
            source_node=self.gov_engine.node_id,
            target_node=self.maritime_ops.node_id,
            operation="assess_stability",
            payload={"survey_id": survey_id},
        )
        response = self.maritime_ops.process_message(msg)
        elapsed = (time.time() - t) * 1000
        self._log_event("PROCESS", "stability_assessed", response.result, elapsed)
        return response.result

    def _phase_governance(self, survey_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run FREQ LAW governance: consensus + VETO evaluation."""
        t = time.time()

        # Step 1: Initiate k=3 consensus for safety-critical draft operation
        consensus_round = self.consensus.initiate_consensus(
            operation="approve_draft_survey",
            initiator_node=self.strategic_op.node_id,
        )
        self.consensus.submit_vote(consensus_round.id, self.strategic_op.node_id, VoteType.APPROVE)
        self.consensus.submit_vote(consensus_round.id, self.gov_engine.node_id, VoteType.APPROVE)
        vote_result = self.consensus.submit_vote(consensus_round.id, self.maritime_ops.node_id, VoteType.APPROVE)

        has_quorum = self.consensus.has_quorum(consensus_round.id)

        # Step 2: VETO authority evaluation
        veto_decision = self.veto_authority.evaluate_operation(
            operation="approve_draft_survey",
            node_id=self.maritime_ops.node_id,
            quorum_count=3,
            has_audit_trail=True,
        )

        # Step 3: FREQ LAW compliance check
        freq_check = self.freq_law.check_quorum_requirement(3)

        elapsed = (time.time() - t) * 1000

        governance_result = {
            "consensus": {
                "round_id": consensus_round.id,
                "votes": vote_result,
                "has_quorum": has_quorum,
                "required_k": 3,
                "status": "APPROVED" if has_quorum else "PENDING",
            },
            "veto": {
                "vetoed": veto_decision.vetoed,
                "reason": str(veto_decision.reason) if veto_decision.reason else None,
                "status": "CLEAR" if not veto_decision.vetoed else "VETOED",
            },
            "freq_law": freq_check,
            "overall_status": "GOVERNANCE APPROVED" if (has_quorum and not veto_decision.vetoed) else "GOVERNANCE BLOCKED",
        }

        self._log_event("GOVERNANCE", "governance_validated", governance_result, elapsed)

        self.audit.log_operation(
            operation="governance_validation",
            node_id=self.gov_engine.node_id,
            node_type="gov_engine",
            request_payload={"operation": "approve_draft_survey"},
            response_payload=governance_result,
            execution_time_ms=elapsed,
            quorum_required=True,
            quorum_achieved=has_quorum,
        )

        return governance_result

    def _phase_report(self) -> Dict[str, Any]:
        """Generate final operational report."""
        t = time.time()
        msg = NodeMessage(
            source_node=self.strategic_op.node_id,
            target_node=self.maritime_ops.node_id,
            operation="generate_report",
            payload={"vessel_id": "BARGE-GOM-2026-001"},
        )
        response = self.maritime_ops.process_message(msg)
        elapsed = (time.time() - t) * 1000
        self._log_event("REPORT", "report_generated", response.result, elapsed)
        return response.result

    def _phase_cost_analysis(self) -> Dict[str, Any]:
        """Generate cost comparison analysis."""
        t = time.time()
        msg = NodeMessage(
            source_node=self.optimal_intel.node_id,
            target_node=self.maritime_ops.node_id,
            operation="get_cost_analysis",
            payload={
                "surveys_per_month": 30,
                "months": 12,
            },
        )
        response = self.maritime_ops.process_message(msg)
        elapsed = (time.time() - t) * 1000
        self._log_event("REPORT", "cost_analysis_generated", response.result, elapsed)
        return response.result
