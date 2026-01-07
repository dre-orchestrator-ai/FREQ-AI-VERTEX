"""Tests for SOL - Sophisticated Operational Lattice"""

import os
import sys
import time

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

import pytest

from sol.governance.freq_law import FreqLaw, FreqLawConstraints
from sol.governance.veto import VetoAuthority, VetoReason
from sol.consensus.quorum import QuorumConsensus, VoteType
from sol.audit.bigquery import BigQueryAuditTrail, AuditEntry
from sol.nodes.base import NodeMessage
from sol.nodes.strategic_op import StrategicOP
from sol.nodes.spci import SPCI
from sol.nodes.legacy_architect import LegacyArchitect
from sol.nodes.gov_engine import GOVEngine
from sol.nodes.exec_automate import ExecAutomate
from sol.nodes.optimal_intel import OptimalIntel
from sol.nodes.element_design import ElementDesign


class TestFreqLaw:
    """Tests for FREQ LAW governance."""
    
    def test_default_constraints(self):
        """Test default FREQ LAW constraints."""
        constraints = FreqLawConstraints()
        assert constraints.max_response_time_ms == 2000
        assert constraints.quorum_k == 3
        assert constraints.require_audit_trail is True
        assert constraints.enable_veto_authority is True
    
    def test_response_time_validation_compliant(self):
        """Test response time validation for compliant operation."""
        freq_law = FreqLaw()
        start_time = time.time() - 0.001  # 1ms ago
        result = freq_law.validate_response_time(start_time, "test_operation")
        assert result["is_compliant"] is True
        assert result["elapsed_ms"] < 2000
    
    def test_response_time_validation_non_compliant(self):
        """Test response time validation for non-compliant operation."""
        freq_law = FreqLaw()
        start_time = time.time() - 3  # 3 seconds ago
        result = freq_law.validate_response_time(start_time, "slow_operation")
        assert result["is_compliant"] is False
        assert result["elapsed_ms"] >= 2000
    
    def test_quorum_requirement_met(self):
        """Test quorum check with sufficient approvals."""
        freq_law = FreqLaw()
        result = freq_law.check_quorum_requirement(3)
        assert result["has_quorum"] is True
        assert result["approvals"] == 3
        assert result["required"] == 3
    
    def test_quorum_requirement_not_met(self):
        """Test quorum check with insufficient approvals."""
        freq_law = FreqLaw()
        result = freq_law.check_quorum_requirement(2)
        assert result["has_quorum"] is False
    
    def test_audit_entry_creation(self):
        """Test audit entry creation."""
        freq_law = FreqLaw()
        entry = freq_law.create_audit_entry(
            operation="test_op",
            node="test_node",
            result={"status": "success"},
            metadata={"key": "value"}
        )
        assert entry["operation"] == "test_op"
        assert entry["node"] == "test_node"
        assert entry["freq_law_version"] == "1.0"


class TestVetoAuthority:
    """Tests for GOV Engine VETO authority."""
    
    def test_operation_approved(self):
        """Test operation approval when compliant."""
        veto = VetoAuthority()
        decision = veto.evaluate_operation(
            operation="compliant_op",
            node_id="node1",
            response_time_ms=500,
            quorum_count=3,
            has_audit_trail=True
        )
        assert decision.vetoed is False
        assert decision.reason is None
    
    def test_veto_response_time_violation(self):
        """Test VETO for response time violation."""
        veto = VetoAuthority()
        decision = veto.evaluate_operation(
            operation="slow_op",
            node_id="node1",
            response_time_ms=2500
        )
        assert decision.vetoed is True
        assert decision.reason == VetoReason.RESPONSE_TIME_VIOLATION
    
    def test_veto_quorum_not_met(self):
        """Test VETO for quorum not met."""
        veto = VetoAuthority()
        decision = veto.evaluate_operation(
            operation="low_quorum_op",
            node_id="node1",
            quorum_count=2
        )
        assert decision.vetoed is True
        assert decision.reason == VetoReason.QUORUM_NOT_MET
    
    def test_veto_missing_audit_trail(self):
        """Test VETO for missing audit trail."""
        veto = VetoAuthority()
        decision = veto.evaluate_operation(
            operation="no_audit_op",
            node_id="node1",
            has_audit_trail=False
        )
        assert decision.vetoed is True
        assert decision.reason == VetoReason.AUDIT_TRAIL_MISSING
    
    def test_manual_veto(self):
        """Test manual VETO exercise."""
        veto = VetoAuthority()
        decision = veto.exercise_manual_veto(
            operation="manual_vetoed_op",
            node_id="node1",
            explanation="Manual governance override"
        )
        assert decision.vetoed is True
        assert decision.reason == VetoReason.GOVERNANCE_OVERRIDE


class TestQuorumConsensus:
    """Tests for k=3 quorum consensus."""
    
    def test_default_required_votes(self):
        """Test default k=3 requirement."""
        consensus = QuorumConsensus()
        assert consensus.required_votes == 3
    
    def test_initiate_consensus(self):
        """Test consensus round initiation."""
        consensus = QuorumConsensus()
        round = consensus.initiate_consensus("test_operation", "initiator_node")
        assert round.operation == "test_operation"
        assert round.status == "pending"
        assert round.required_votes == 3
    
    def test_submit_votes_reach_quorum(self):
        """Test voting until quorum is reached."""
        consensus = QuorumConsensus()
        consensus.register_voter("node1")
        consensus.register_voter("node2")
        consensus.register_voter("node3")
        
        round = consensus.initiate_consensus("test_op", "initiator")
        
        # Submit 3 approval votes
        consensus.submit_vote(round.id, "node1", VoteType.APPROVE)
        consensus.submit_vote(round.id, "node2", VoteType.APPROVE)
        result = consensus.submit_vote(round.id, "node3", VoteType.APPROVE)
        
        # When quorum is reached, status changes to "approved"
        assert result["status"] == "approved"
        assert result["approvals"] == 3
    
    def test_has_quorum(self):
        """Test quorum check."""
        consensus = QuorumConsensus()
        consensus.register_voter("node1")
        consensus.register_voter("node2")
        consensus.register_voter("node3")
        
        round = consensus.initiate_consensus("test_op", "initiator")
        
        assert consensus.has_quorum(round.id) is False
        
        consensus.submit_vote(round.id, "node1", VoteType.APPROVE)
        consensus.submit_vote(round.id, "node2", VoteType.APPROVE)
        consensus.submit_vote(round.id, "node3", VoteType.APPROVE)
        
        assert consensus.has_quorum(round.id) is True


class TestBigQueryAuditTrail:
    """Tests for BigQuery audit trail."""
    
    def test_log_operation(self):
        """Test operation logging."""
        audit = BigQueryAuditTrail(project_id="test-project")
        entry_id = audit.log_operation(
            operation="test_op",
            node_id="node1",
            node_type="strategic_op",
            request_payload={"key": "value"},
            response_payload={"status": "success"},
            execution_time_ms=150.5
        )
        assert entry_id is not None
        assert audit.get_buffer_size() == 1
    
    def test_flush_buffer(self):
        """Test buffer flush."""
        audit = BigQueryAuditTrail(project_id="test-project")
        audit.log_operation(
            operation="test_op",
            node_id="node1",
            node_type="strategic_op",
            request_payload={},
            response_payload={},
            execution_time_ms=100
        )
        
        count = audit.flush()
        assert count == 1
        assert audit.get_buffer_size() == 0
    
    def test_table_ddl_generation(self):
        """Test DDL generation."""
        audit = BigQueryAuditTrail(
            project_id="test-project",
            dataset_id="sol_audit",
            table_id="operations"
        )
        ddl = audit.create_table_ddl()
        assert "CREATE TABLE IF NOT EXISTS" in ddl
        assert "test-project.sol_audit.operations" in ddl


class TestLatticeNodes:
    """Tests for lattice nodes."""
    
    def test_strategic_op_node(self):
        """Test Strategic OP node."""
        node = StrategicOP()
        assert node.node_type.value == "strategic_op"
        
        message = NodeMessage(
            source_node="test",
            target_node=node.node_id,
            operation="create_mission",
            payload={"name": "Test Mission", "objectives": ["obj1"]}
        )
        response = node.process_message(message)
        assert response.success is True
        assert "mission_id" in response.result
    
    def test_spci_node(self):
        """Test SPCI node."""
        node = SPCI()
        assert node.node_type.value == "spci"
        
        message = NodeMessage(
            source_node="test",
            target_node=node.node_id,
            operation="record_metric",
            payload={"name": "response_time", "value": 150}
        )
        response = node.process_message(message)
        assert response.success is True
    
    def test_legacy_architect_node(self):
        """Test Legacy Architect node."""
        node = LegacyArchitect()
        assert node.node_type.value == "legacy_architect"
        
        message = NodeMessage(
            source_node="test",
            target_node=node.node_id,
            operation="register_adapter",
            payload={"name": "REST-to-SOAP", "source_protocol": "REST", "target_protocol": "SOAP"}
        )
        response = node.process_message(message)
        assert response.success is True
    
    def test_gov_engine_node(self):
        """Test GOV Engine node."""
        node = GOVEngine()
        assert node.node_type.value == "gov_engine"
        
        message = NodeMessage(
            source_node="test",
            target_node=node.node_id,
            operation="validate_operation",
            payload={
                "operation": "test_op",
                "node_id": "test_node",
                "response_time_ms": 100,
                "quorum_count": 3
            }
        )
        response = node.process_message(message)
        assert response.success is True
        assert response.result["vetoed"] is False
    
    def test_exec_automate_node(self):
        """Test Exec Automate node."""
        node = ExecAutomate()
        assert node.node_type.value == "exec_automate"
        
        message = NodeMessage(
            source_node="test",
            target_node=node.node_id,
            operation="create_workflow",
            payload={"name": "Test Workflow", "steps": [{"name": "step1"}]}
        )
        response = node.process_message(message)
        assert response.success is True
    
    def test_optimal_intel_node(self):
        """Test Optimal Intel node."""
        node = OptimalIntel()
        assert node.node_type.value == "optimal_intel"
        
        message = NodeMessage(
            source_node="test",
            target_node=node.node_id,
            operation="run_analysis",
            payload={"analysis_type": "performance"}
        )
        response = node.process_message(message)
        assert response.success is True
    
    def test_element_design_node(self):
        """Test Element Design node."""
        node = ElementDesign()
        assert node.node_type.value == "element_design"
        
        message = NodeMessage(
            source_node="test",
            target_node=node.node_id,
            operation="create_schema",
            payload={"name": "TestSchema", "properties": {"field1": {"type": "string"}}}
        )
        response = node.process_message(message)
        assert response.success is True
    
    def test_node_communication(self):
        """Test communication between nodes."""
        strategic_op = StrategicOP()
        gov_engine = GOVEngine()
        
        strategic_op.connect_node(gov_engine)
        
        response = strategic_op.send_message(
            target_node_id=gov_engine.node_id,
            operation="validate_operation",
            payload={"operation": "test", "node_id": strategic_op.node_id}
        )
        
        assert response is not None
        assert response.success is True


class TestIntegration:
    """Integration tests for SOL system."""
    
    def test_full_workflow_with_governance(self):
        """Test complete workflow with FREQ LAW governance."""
        # Initialize components
        freq_law = FreqLaw()
        consensus = QuorumConsensus()
        veto = VetoAuthority()
        audit = BigQueryAuditTrail(project_id="test")
        
        # Create nodes
        strategic_op = StrategicOP()
        gov_engine = GOVEngine()
        spci = SPCI()
        
        # Register voters
        consensus.register_voter(strategic_op.node_id)
        consensus.register_voter(gov_engine.node_id)
        consensus.register_voter(spci.node_id)
        
        # Initiate consensus for an operation
        round = consensus.initiate_consensus(
            operation="deploy_workflow",
            initiator_node=strategic_op.node_id
        )
        
        # All nodes vote to approve
        start_time = time.time()
        consensus.submit_vote(round.id, strategic_op.node_id, VoteType.APPROVE)
        consensus.submit_vote(round.id, gov_engine.node_id, VoteType.APPROVE)
        consensus.submit_vote(round.id, spci.node_id, VoteType.APPROVE)
        
        # Verify quorum
        assert consensus.has_quorum(round.id)
        
        # Validate with VETO authority
        decision = veto.evaluate_operation(
            operation="deploy_workflow",
            node_id=strategic_op.node_id,
            quorum_count=3,
            has_audit_trail=True
        )
        assert decision.vetoed is False
        
        # Log to audit trail
        audit.log_operation(
            operation="deploy_workflow",
            node_id=strategic_op.node_id,
            node_type="strategic_op",
            request_payload={"workflow": "test"},
            response_payload={"status": "deployed"},
            execution_time_ms=(time.time() - start_time) * 1000,
            quorum_required=True,
            quorum_achieved=True
        )
        
        # Verify audit was logged
        assert audit.get_buffer_size() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
