"""
GOV Engine VETO Authority

The GOV Engine holds absolute VETO authority over all lattice operations.
This module implements the VETO mechanism that can halt any operation
that violates FREQ LAW compliance.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class VetoReason(Enum):
    """Standard reasons for VETO exercise."""
    
    RESPONSE_TIME_VIOLATION = "response_time_exceeded_2000ms"
    QUORUM_NOT_MET = "quorum_k3_not_achieved"
    AUDIT_TRAIL_MISSING = "bigquery_audit_required"
    COMPLIANCE_VIOLATION = "freq_law_compliance_failure"
    SECURITY_CONCERN = "security_policy_violation"
    GOVERNANCE_OVERRIDE = "manual_governance_override"


@dataclass
class VetoDecision:
    """Represents a VETO decision from the GOV Engine."""
    
    vetoed: bool
    reason: Optional[VetoReason]
    explanation: str
    timestamp: str
    node_id: str
    operation: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "vetoed": self.vetoed,
            "reason": self.reason.value if self.reason else None,
            "explanation": self.explanation,
            "timestamp": self.timestamp,
            "node_id": self.node_id,
            "operation": self.operation
        }


class VetoAuthority:
    """
    GOV Engine VETO Authority Implementation
    
    Provides absolute VETO power over lattice operations to ensure
    FREQ LAW compliance. All operations must pass through VETO
    authority before execution.
    """
    
    def __init__(self):
        self._veto_history: List[VetoDecision] = []
        self._active_vetoes: Dict[str, VetoDecision] = {}
    
    def evaluate_operation(
        self, 
        operation: str,
        node_id: str,
        response_time_ms: Optional[float] = None,
        quorum_count: Optional[int] = None,
        has_audit_trail: bool = True,
        custom_checks: Optional[Dict[str, bool]] = None
    ) -> VetoDecision:
        """
        Evaluate an operation for VETO.
        
        Args:
            operation: Name of the operation to evaluate
            node_id: ID of the node requesting execution
            response_time_ms: Estimated/actual response time
            quorum_count: Number of quorum approvals
            has_audit_trail: Whether audit logging is configured
            custom_checks: Additional custom compliance checks
            
        Returns:
            VetoDecision indicating whether operation is vetoed
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Check response time constraint
        if response_time_ms is not None and response_time_ms >= 2000:
            decision = VetoDecision(
                vetoed=True,
                reason=VetoReason.RESPONSE_TIME_VIOLATION,
                explanation=f"Response time {response_time_ms}ms exceeds 2000ms limit",
                timestamp=timestamp,
                node_id=node_id,
                operation=operation
            )
            self._record_veto(decision)
            return decision
        
        # Check quorum requirement
        if quorum_count is not None and quorum_count < 3:
            decision = VetoDecision(
                vetoed=True,
                reason=VetoReason.QUORUM_NOT_MET,
                explanation=f"Quorum count {quorum_count} is below required k=3",
                timestamp=timestamp,
                node_id=node_id,
                operation=operation
            )
            self._record_veto(decision)
            return decision
        
        # Check audit trail requirement
        if not has_audit_trail:
            decision = VetoDecision(
                vetoed=True,
                reason=VetoReason.AUDIT_TRAIL_MISSING,
                explanation="BigQuery audit trail is required for all operations",
                timestamp=timestamp,
                node_id=node_id,
                operation=operation
            )
            self._record_veto(decision)
            return decision
        
        # Check custom compliance rules
        if custom_checks:
            for check_name, passed in custom_checks.items():
                if not passed:
                    decision = VetoDecision(
                        vetoed=True,
                        reason=VetoReason.COMPLIANCE_VIOLATION,
                        explanation=f"Custom check failed: {check_name}",
                        timestamp=timestamp,
                        node_id=node_id,
                        operation=operation
                    )
                    self._record_veto(decision)
                    return decision
        
        # Operation approved
        return VetoDecision(
            vetoed=False,
            reason=None,
            explanation="Operation approved by GOV Engine",
            timestamp=timestamp,
            node_id=node_id,
            operation=operation
        )
    
    def exercise_manual_veto(
        self, 
        operation: str, 
        node_id: str, 
        explanation: str
    ) -> VetoDecision:
        """
        Exercise manual VETO authority for governance override.
        
        Args:
            operation: Operation to veto
            node_id: Node associated with the operation
            explanation: Reason for manual veto
            
        Returns:
            VetoDecision with manual override
        """
        decision = VetoDecision(
            vetoed=True,
            reason=VetoReason.GOVERNANCE_OVERRIDE,
            explanation=explanation,
            timestamp=datetime.utcnow().isoformat(),
            node_id=node_id,
            operation=operation
        )
        self._record_veto(decision)
        return decision
    
    def _record_veto(self, decision: VetoDecision) -> None:
        """Record a VETO decision in history."""
        self._veto_history.append(decision)
        if decision.vetoed:
            key = f"{decision.node_id}:{decision.operation}"
            self._active_vetoes[key] = decision
    
    def get_veto_history(self) -> List[Dict[str, Any]]:
        """Get full VETO history for audit purposes."""
        return [v.to_dict() for v in self._veto_history]
    
    def get_active_vetoes(self) -> Dict[str, Dict[str, Any]]:
        """Get currently active VETOs."""
        return {k: v.to_dict() for k, v in self._active_vetoes.items()}
    
    def clear_veto(self, node_id: str, operation: str) -> bool:
        """Clear an active VETO after issue resolution."""
        key = f"{node_id}:{operation}"
        if key in self._active_vetoes:
            del self._active_vetoes[key]
            return True
        return False
