"""
GOV Engine Node

FREQ LAW compliance node with absolute VETO authority
over all lattice operations.
"""

import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import LatticeNode, NodeType, NodeMessage, NodeResponse
from ..governance.freq_law import FreqLaw, FreqLawConstraints
from ..governance.veto import VetoAuthority, VetoDecision


class GOVEngine(LatticeNode):
    """
    Governance Engine Node
    
    Central governance node with FREQ LAW compliance and VETO authority:
    - FREQ LAW enforcement (Fast, Robust, Evolutionary, Quantified)
    - k=3 quorum consensus validation
    - Absolute VETO authority over non-compliant operations
    - Audit trail management for BigQuery
    """
    
    def __init__(self, node_id: str = None, constraints: Optional[FreqLawConstraints] = None):
        super().__init__(node_id)
        self._freq_law = FreqLaw(constraints)
        self._veto_authority = VetoAuthority()
        self._compliance_log: List[Dict[str, Any]] = []
        self._pending_quorum_requests: Dict[str, Dict[str, Any]] = {}
    
    @property
    def node_type(self) -> NodeType:
        return NodeType.GOV_ENGINE
    
    @property
    def description(self) -> str:
        return "FREQ LAW compliance and absolute VETO authority"
    
    def process_message(self, message: NodeMessage) -> NodeResponse:
        """Process governance messages."""
        start_time = time.time()
        
        try:
            operation = message.operation
            payload = message.payload
            
            if operation == "validate_operation":
                result = self._validate_operation(payload)
            elif operation == "request_quorum":
                result = self._request_quorum(payload)
            elif operation == "submit_quorum_vote":
                result = self._submit_quorum_vote(payload)
            elif operation == "check_compliance":
                result = self._check_compliance(payload)
            elif operation == "exercise_veto":
                result = self._exercise_veto(payload)
            elif operation == "get_veto_history":
                result = self._get_veto_history()
            elif operation == "get_audit_log":
                result = self._get_audit_log()
            else:
                result = {"error": f"Unknown operation: {operation}"}
            
            execution_time = (time.time() - start_time) * 1000
            
            # Log all operations for audit
            self._log_compliance(operation, payload, execution_time)
            
            return NodeResponse(
                message_id=message.id,
                node_id=self.node_id,
                success=True,
                result=result,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return NodeResponse(
                message_id=message.id,
                node_id=self.node_id,
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    def _validate_operation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an operation against FREQ LAW constraints."""
        operation_name = payload.get("operation")
        node_id = payload.get("node_id")
        response_time_ms = payload.get("response_time_ms")
        quorum_count = payload.get("quorum_count")
        has_audit_trail = payload.get("has_audit_trail", True)
        
        decision = self._veto_authority.evaluate_operation(
            operation=operation_name,
            node_id=node_id,
            response_time_ms=response_time_ms,
            quorum_count=quorum_count,
            has_audit_trail=has_audit_trail
        )
        
        return decision.to_dict()
    
    def _request_quorum(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Request quorum consensus for an operation."""
        import uuid
        request_id = str(uuid.uuid4())
        
        request = {
            "id": request_id,
            "operation": payload.get("operation"),
            "requesting_node": payload.get("requesting_node"),
            "votes": [],
            "required_votes": 3,  # k=3 quorum
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self._pending_quorum_requests[request_id] = request
        
        return {"request_id": request_id, "status": "pending", "required_votes": 3}
    
    def _submit_quorum_vote(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a vote for a quorum request."""
        request_id = payload.get("request_id")
        voting_node = payload.get("voting_node")
        vote = payload.get("vote")  # "approve" or "reject"
        
        if request_id not in self._pending_quorum_requests:
            return {"error": "Quorum request not found"}
        
        request = self._pending_quorum_requests[request_id]
        
        # Check for duplicate votes
        existing_voters = [v["node"] for v in request["votes"]]
        if voting_node in existing_voters:
            return {"error": "Node has already voted"}
        
        request["votes"].append({
            "node": voting_node,
            "vote": vote,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Check if quorum is reached
        approvals = sum(1 for v in request["votes"] if v["vote"] == "approve")
        quorum_check = self._freq_law.check_quorum_requirement(approvals)
        
        if quorum_check["has_quorum"]:
            request["status"] = "approved"
        elif len(request["votes"]) >= request["required_votes"] and not quorum_check["has_quorum"]:
            request["status"] = "rejected"
        
        return {
            "request_id": request_id,
            "current_votes": len(request["votes"]),
            "approvals": approvals,
            "status": request["status"],
            "has_quorum": quorum_check["has_quorum"]
        }
    
    def _check_compliance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Check FREQ LAW compliance for a completed operation."""
        start_time = payload.get("start_time")
        operation = payload.get("operation")
        
        if start_time:
            timing_result = self._freq_law.validate_response_time(start_time, operation)
        else:
            timing_result = {"warning": "No start_time provided for timing validation"}
        
        return {
            "operation": operation,
            "timing_compliance": timing_result,
            "freq_law_version": "1.0"
        }
    
    def _exercise_veto(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Exercise manual VETO authority."""
        operation = payload.get("operation")
        node_id = payload.get("node_id")
        reason = payload.get("reason")
        
        decision = self._veto_authority.exercise_manual_veto(
            operation=operation,
            node_id=node_id,
            explanation=reason
        )
        
        return decision.to_dict()
    
    def _get_veto_history(self) -> Dict[str, Any]:
        """Get the history of all VETO decisions."""
        return {
            "history": self._veto_authority.get_veto_history(),
            "active_vetoes": self._veto_authority.get_active_vetoes()
        }
    
    def _get_audit_log(self) -> Dict[str, Any]:
        """Get the compliance audit log."""
        return {
            "log": self._compliance_log,
            "pending_audits": self._freq_law.get_pending_audits()
        }
    
    def _log_compliance(self, operation: str, payload: Dict[str, Any], 
                        execution_time_ms: float) -> None:
        """Log operation for compliance audit."""
        entry = {
            "operation": operation,
            "payload_summary": {k: type(v).__name__ for k, v in payload.items()},
            "execution_time_ms": execution_time_ms,
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": self.node_id
        }
        self._compliance_log.append(entry)
