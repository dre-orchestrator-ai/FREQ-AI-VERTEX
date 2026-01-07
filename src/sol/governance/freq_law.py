"""
FREQ LAW Governance Protocol

FREQ LAW defines the core operational constraints:
- Fast: All operations must complete within 2000ms
- Robust: System must maintain resilience through quorum consensus
- Evolutionary: Continuous improvement through SPCI cycles
- Quantified: All outputs require measurement and BigQuery audit trail
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime
import time


@dataclass
class FreqLawConstraints:
    """Defines FREQ LAW operational constraints."""
    
    max_response_time_ms: int = 2000
    quorum_k: int = 3
    require_audit_trail: bool = True
    enable_veto_authority: bool = True


class FreqLaw:
    """
    FREQ LAW Governance Engine
    
    Enforces the four pillars of FREQ LAW across all lattice operations:
    - Fast: Response time enforcement
    - Robust: Failure tolerance via quorum
    - Evolutionary: SPCI integration for continuous improvement
    - Quantified: Mandatory audit logging
    """
    
    def __init__(self, constraints: Optional[FreqLawConstraints] = None):
        self.constraints = constraints or FreqLawConstraints()
        self._audit_buffer: list = []
    
    def validate_response_time(self, start_time: float, operation: str) -> Dict[str, Any]:
        """
        Validate that an operation completes within FREQ LAW time constraints.
        
        Args:
            start_time: Unix timestamp when operation started
            operation: Name of the operation being validated
            
        Returns:
            Dict with compliance status and metrics
        """
        elapsed_ms = (time.time() - start_time) * 1000
        is_compliant = elapsed_ms < self.constraints.max_response_time_ms
        
        result = {
            "operation": operation,
            "elapsed_ms": elapsed_ms,
            "max_allowed_ms": self.constraints.max_response_time_ms,
            "is_compliant": is_compliant,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self._audit_buffer.append(result)
        return result
    
    def check_quorum_requirement(self, approvals: int) -> Dict[str, Any]:
        """
        Check if quorum consensus requirement is met.
        
        Args:
            approvals: Number of node approvals received
            
        Returns:
            Dict with quorum status
        """
        has_quorum = approvals >= self.constraints.quorum_k
        
        return {
            "approvals": approvals,
            "required": self.constraints.quorum_k,
            "has_quorum": has_quorum,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def create_audit_entry(self, operation: str, node: str, 
                           result: Any, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create an audit trail entry for BigQuery logging.
        
        Args:
            operation: Name of the operation
            node: Lattice node that performed the operation
            result: Result of the operation
            metadata: Additional context metadata
            
        Returns:
            Formatted audit entry for BigQuery
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "node": node,
            "result": result,
            "metadata": metadata or {},
            "freq_law_version": "1.0"
        }
        
        self._audit_buffer.append(entry)
        return entry
    
    def get_pending_audits(self) -> list:
        """Get all pending audit entries awaiting BigQuery flush."""
        return self._audit_buffer.copy()
    
    def clear_audit_buffer(self) -> int:
        """Clear the audit buffer after successful BigQuery write."""
        count = len(self._audit_buffer)
        self._audit_buffer = []
        return count
