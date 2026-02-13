"""Tests for Maritime Barge Drafting Operations — vector_gamma"""

import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import pytest

from sol.nodes.base import NodeMessage, NodeType
from sol.nodes.maritime_ops import (
    MaritimeBargeOps,
    BargeSpec,
    DraftReading,
    DraftSurveyResult,
    BallastPlan,
)
from sol.simulation.maritime_barge import MaritimeBargeSimulation


# --- Domain Model Tests ---

class TestBargeSpec:
    """Tests for BargeSpec data model."""

    def test_barge_spec_creation(self):
        spec = BargeSpec(
            vessel_id="TEST-001",
            name="Test Barge",
            loa_m=60.0,
            beam_m=18.0,
            depth_m=4.5,
            light_draft_m=1.2,
            max_draft_m=3.8,
            displacement_t=1200.0,
            deadweight_t=3500.0,
            ballast_tanks=6,
            tank_capacity_m3=85.0,
        )
        assert spec.vessel_id == "TEST-001"
        assert spec.loa_m == 60.0
        d = spec.to_dict()
        assert d["name"] == "Test Barge"
        assert d["ballast_tanks"] == 6

    def test_barge_spec_to_dict_completeness(self):
        spec = BargeSpec(
            vessel_id="V1", name="B1", loa_m=50, beam_m=15,
            depth_m=4, light_draft_m=1.0, max_draft_m=3.5,
            displacement_t=900, deadweight_t=3000,
            ballast_tanks=4, tank_capacity_m3=70,
        )
        d = spec.to_dict()
        expected_keys = {"vessel_id", "name", "loa_m", "beam_m", "depth_m",
                         "light_draft_m", "max_draft_m", "displacement_t",
                         "deadweight_t", "ballast_tanks", "tank_capacity_m3"}
        assert set(d.keys()) == expected_keys


class TestDraftReading:
    """Tests for DraftReading data model."""

    def test_draft_reading_creation(self):
        reading = DraftReading(
            sensor_id="S1", position="fore",
            draft_m=2.5, water_temp_c=22.0, salinity_ppt=35.0,
        )
        assert reading.position == "fore"
        assert reading.draft_m == 2.5
        assert reading.timestamp is not None

    def test_draft_reading_to_dict(self):
        reading = DraftReading(
            sensor_id="S2", position="aft",
            draft_m=2.8, water_temp_c=21.0, salinity_ppt=33.0,
        )
        d = reading.to_dict()
        assert d["sensor_id"] == "S2"
        assert d["position"] == "aft"
        assert d["draft_m"] == 2.8


# --- Maritime Barge Ops Node Tests ---

class TestMaritimeBargeOpsNode:
    """Tests for MaritimeBargeOps lattice node."""

    def setup_method(self):
        self.node = MaritimeBargeOps(node_id="test-maritime-001")

    def test_node_type(self):
        assert self.node.node_type == NodeType.MARITIME_BARGE_OPS
        assert self.node.node_type.value == "maritime_barge_ops"

    def test_node_description(self):
        assert "maritime" in self.node.description.lower()

    def test_register_vessel(self):
        msg = NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="register_vessel",
            payload={
                "vessel_id": "BARGE-001",
                "name": "Test Runner",
                "loa_m": 60.0,
                "beam_m": 18.0,
                "depth_m": 4.5,
                "light_draft_m": 1.2,
                "max_draft_m": 3.8,
                "displacement_t": 1200.0,
                "deadweight_t": 3500.0,
                "ballast_tanks": 6,
                "tank_capacity_m3": 85.0,
            },
        )
        response = self.node.process_message(msg)
        assert response.success is True
        assert response.result["vessel_id"] == "BARGE-001"
        assert response.result["status"] == "registered"

    def test_ingest_sensor_data(self):
        # First register a vessel
        self._register_default_vessel()

        msg = NodeMessage(
            source_node="iot",
            target_node=self.node.node_id,
            operation="ingest_sensor_data",
            payload={
                "vessel_id": "BARGE-001",
                "readings": [
                    {"sensor_id": "S1", "position": "fore", "draft_m": 2.1, "water_temp_c": 22.0, "salinity_ppt": 35.0},
                    {"sensor_id": "S2", "position": "midship", "draft_m": 2.4, "water_temp_c": 22.0, "salinity_ppt": 35.0},
                    {"sensor_id": "S3", "position": "aft", "draft_m": 2.7, "water_temp_c": 22.0, "salinity_ppt": 35.0},
                ],
            },
        )
        response = self.node.process_message(msg)
        assert response.success is True
        assert response.result["readings_ingested"] == 3
        assert response.result["status"] == "scan_complete"

    def test_ingest_unregistered_vessel(self):
        msg = NodeMessage(
            source_node="iot",
            target_node=self.node.node_id,
            operation="ingest_sensor_data",
            payload={"vessel_id": "NO-SUCH-VESSEL", "readings": []},
        )
        response = self.node.process_message(msg)
        assert response.success is True
        assert "error" in response.result

    def test_compute_draft_survey(self):
        self._register_default_vessel()
        self._ingest_default_readings()

        msg = NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="compute_draft_survey",
            payload={"vessel_id": "BARGE-001", "water_depth_m": 12.0},
        )
        response = self.node.process_message(msg)
        assert response.success is True
        survey = response.result["survey"]
        assert survey["fore_draft_m"] > 0
        assert survey["mid_draft_m"] > 0
        assert survey["aft_draft_m"] > 0
        assert survey["mean_draft_m"] > 0
        assert survey["displacement_t"] > 0
        assert survey["cargo_weight_t"] >= 0
        assert survey["water_density_kg_m3"] > 1000
        assert survey["is_compliant"] is True

    def test_draft_survey_compliance_violation(self):
        """Test that overloaded vessel triggers compliance failure."""
        self.node.process_message(NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="register_vessel",
            payload={
                "vessel_id": "OVERLOADED-001",
                "name": "Overloaded Barge",
                "loa_m": 60.0, "beam_m": 18.0, "depth_m": 4.5,
                "light_draft_m": 1.2, "max_draft_m": 2.0,  # Very low max draft
                "displacement_t": 1200.0, "deadweight_t": 3500.0,
                "ballast_tanks": 6, "tank_capacity_m3": 85.0,
            },
        ))
        self.node.process_message(NodeMessage(
            source_node="iot",
            target_node=self.node.node_id,
            operation="ingest_sensor_data",
            payload={
                "vessel_id": "OVERLOADED-001",
                "readings": [
                    {"sensor_id": "S1", "position": "fore", "draft_m": 2.5, "water_temp_c": 22.0, "salinity_ppt": 35.0},
                    {"sensor_id": "S2", "position": "midship", "draft_m": 2.8, "water_temp_c": 22.0, "salinity_ppt": 35.0},
                    {"sensor_id": "S3", "position": "aft", "draft_m": 3.1, "water_temp_c": 22.0, "salinity_ppt": 35.0},
                ],
            },
        ))
        response = self.node.process_message(NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="compute_draft_survey",
            payload={"vessel_id": "OVERLOADED-001", "water_depth_m": 12.0},
        ))
        assert response.success is True
        survey = response.result["survey"]
        assert survey["is_compliant"] is False
        assert any("VIOLATION" in note for note in survey["compliance_notes"])

    def test_optimize_ballast(self):
        self._register_default_vessel()
        self._ingest_default_readings()
        self._compute_default_survey()

        msg = NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="optimize_ballast",
            payload={"vessel_id": "BARGE-001", "target_trim_m": 0.0},
        )
        response = self.node.process_message(msg)
        assert response.success is True
        plan = response.result["plan"]
        assert plan["total_ballast_m3"] > 0
        assert plan["estimated_cost_usd"] >= 0
        assert len(plan["tank_levels"]) == 6

    def test_assess_stability(self):
        self._register_default_vessel()
        self._ingest_default_readings()
        survey_result = self._compute_default_survey()
        survey_id = survey_result["survey_id"]

        msg = NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="assess_stability",
            payload={"survey_id": survey_id},
        )
        response = self.node.process_message(msg)
        assert response.success is True
        assert response.result["metacentric_height_m"] > 0
        assert response.result["is_stable"] is True
        assert response.result["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")

    def test_check_compliance(self):
        self._register_default_vessel()
        self._ingest_default_readings()
        survey_result = self._compute_default_survey()
        survey_id = survey_result["survey_id"]

        msg = NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="check_compliance",
            payload={"survey_id": survey_id},
        )
        response = self.node.process_message(msg)
        assert response.success is True
        assert response.result["overall_compliant"] is True
        assert response.result["checks_total"] == 4
        assert response.result["regulatory_authority"] == "USCG / IMO"

    def test_generate_report(self):
        self._register_default_vessel()
        self._ingest_default_readings()
        self._compute_default_survey()

        msg = NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="generate_report",
            payload={"vessel_id": "BARGE-001"},
        )
        response = self.node.process_message(msg)
        assert response.success is True
        report = response.result
        assert report["report_type"] == "Maritime Barge Draft Survey Report"
        assert report["vessel"]["vessel_id"] == "BARGE-001"
        assert report["sensor_summary"]["total_readings"] > 0
        assert report["draft_survey"] is not None

    def test_get_cost_analysis(self):
        msg = NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="get_cost_analysis",
            payload={"surveys_per_month": 30, "months": 12},
        )
        response = self.node.process_message(msg)
        assert response.success is True
        cost = response.result
        assert cost["total_surveys"] == 360
        # SOL should be dramatically cheaper than alternatives
        assert cost["sol_autonomous"]["annual_cost_usd"] < cost["traditional_manual"]["annual_cost_usd"]
        assert cost["sol_autonomous"]["annual_cost_usd"] < cost["drone_survey"]["annual_cost_usd"]
        assert cost["savings_vs_manual_pct"] > 90  # >90% cheaper than manual
        assert cost["savings_vs_drone_pct"] > 95   # >95% cheaper than drones

    def test_unknown_operation(self):
        msg = NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="nonexistent_operation",
            payload={},
        )
        response = self.node.process_message(msg)
        assert response.success is True
        assert "error" in response.result

    def test_water_density_calculation(self):
        """Test UNESCO water density formula."""
        # Freshwater at 4C should be ~1000 kg/m3
        density_fw = MaritimeBargeOps._calculate_water_density(4.0, 0.0)
        assert 999.5 < density_fw < 1000.5

        # Seawater at 15C, 35 ppt should be ~1025-1026 kg/m3
        density_sw = MaritimeBargeOps._calculate_water_density(15.0, 35.0)
        assert 1024.0 < density_sw < 1027.0

        # Warmer water should be less dense
        density_warm = MaritimeBargeOps._calculate_water_density(30.0, 35.0)
        assert density_warm < density_sw

    def test_execution_time_tracked(self):
        """Verify all responses track execution time."""
        msg = NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="get_cost_analysis",
            payload={"surveys_per_month": 10, "months": 1},
        )
        response = self.node.process_message(msg)
        assert response.execution_time_ms >= 0
        assert response.execution_time_ms < 2000  # FREQ LAW compliant

    # --- Helpers ---

    def _register_default_vessel(self):
        self.node.process_message(NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="register_vessel",
            payload={
                "vessel_id": "BARGE-001",
                "name": "Test Runner",
                "loa_m": 60.0, "beam_m": 18.0, "depth_m": 4.5,
                "light_draft_m": 1.2, "max_draft_m": 3.8,
                "displacement_t": 1200.0, "deadweight_t": 3500.0,
                "ballast_tanks": 6, "tank_capacity_m3": 85.0,
            },
        ))

    def _ingest_default_readings(self):
        self.node.process_message(NodeMessage(
            source_node="iot",
            target_node=self.node.node_id,
            operation="ingest_sensor_data",
            payload={
                "vessel_id": "BARGE-001",
                "readings": [
                    {"sensor_id": "S1", "position": "fore", "draft_m": 2.1, "water_temp_c": 22.0, "salinity_ppt": 35.0},
                    {"sensor_id": "S2", "position": "midship", "draft_m": 2.4, "water_temp_c": 22.0, "salinity_ppt": 35.0},
                    {"sensor_id": "S3", "position": "aft", "draft_m": 2.7, "water_temp_c": 22.0, "salinity_ppt": 35.0},
                ],
            },
        ))

    def _compute_default_survey(self):
        response = self.node.process_message(NodeMessage(
            source_node="test",
            target_node=self.node.node_id,
            operation="compute_draft_survey",
            payload={"vessel_id": "BARGE-001", "water_depth_m": 12.0},
        ))
        return response.result


# --- Full Simulation Tests ---

class TestMaritimeBargeSimulation:
    """Tests for the end-to-end maritime simulation."""

    def test_simulation_runs_successfully(self):
        sim = MaritimeBargeSimulation()
        results = sim.run()

        assert "mission" in results
        assert "vessel" in results
        assert "scan" in results
        assert "draft_survey" in results
        assert "ballast" in results
        assert "stability" in results
        assert "governance" in results
        assert "report" in results
        assert "cost_analysis" in results
        assert "simulation_summary" in results

    def test_simulation_freq_law_compliant(self):
        """Entire simulation must complete in <2000ms."""
        sim = MaritimeBargeSimulation()
        results = sim.run()
        summary = results["simulation_summary"]
        assert summary["freq_law_compliant"] is True
        assert summary["total_execution_time_ms"] < 2000

    def test_simulation_governance_approved(self):
        sim = MaritimeBargeSimulation()
        results = sim.run()
        gov = results["governance"]
        assert gov["consensus"]["has_quorum"] is True
        assert gov["veto"]["vetoed"] is False
        assert gov["overall_status"] == "GOVERNANCE APPROVED"

    def test_simulation_audit_trail(self):
        sim = MaritimeBargeSimulation()
        results = sim.run()
        assert results["simulation_summary"]["audit_entries"] > 0
        assert results["simulation_summary"]["events_logged"] > 0

    def test_simulation_cost_savings(self):
        sim = MaritimeBargeSimulation()
        results = sim.run()
        cost = results["cost_analysis"]
        assert cost["savings_vs_manual_usd"] > 0
        assert cost["savings_vs_drone_usd"] > 0

    def test_simulation_vessel_data(self):
        sim = MaritimeBargeSimulation()
        results = sim.run()
        vessel = results["vessel"]
        assert vessel["spec"]["vessel_id"] == "BARGE-GOM-2026-001"
        assert vessel["spec"]["name"] == "Gulf Runner 1"

    def test_simulation_draft_survey_has_data(self):
        sim = MaritimeBargeSimulation()
        results = sim.run()
        survey = results["draft_survey"]["survey"]
        assert survey["mean_draft_m"] > 0
        assert survey["displacement_t"] > 0
        assert survey["is_compliant"] is True


# --- Blueprint Integration Tests ---

class TestBlueprintVectorGamma:
    """Tests for vector_gamma configuration in the FREQ Blueprint."""

    def test_vector_gamma_exists(self):
        from sol.blueprint import get_mission_vector
        gamma = get_mission_vector("vector_gamma")
        assert gamma.get("name") == "Maritime Barge Drafting"
        assert gamma.get("target_accuracy") == 0.998
        assert gamma.get("workflow") == "SCAN > PROCESS > REPORT"

    def test_vector_gamma_has_sub_operations(self):
        from sol.blueprint import get_mission_vector
        gamma = get_mission_vector("vector_gamma")
        subs = gamma.get("sub_operations", [])
        assert "draft_calculation" in subs
        assert "ballast_optimization" in subs
        assert "regulatory_compliance" in subs

    def test_vector_gamma_required_nodes(self):
        from sol.blueprint import get_mission_vector
        gamma = get_mission_vector("vector_gamma")
        nodes = gamma.get("required_nodes", [])
        assert "maritime_barge_ops" in nodes
        assert "gov_engine" in nodes

    def test_vector_gamma_gcp_services(self):
        from sol.blueprint import get_mission_vector
        gamma = get_mission_vector("vector_gamma")
        services = gamma.get("gcp_services", [])
        assert "vertex_ai_agent_builder" in services
        assert "bigquery" in services


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
