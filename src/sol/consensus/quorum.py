"""
Quorum Consensus Implementation

Implements k=3 quorum consensus mechanism for the SOL lattice.
All operations requiring consensus must receive approval from
at least 3 nodes before execution.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import uuid


class VoteType(Enum):
    """Types of votes in quorum consensus."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


@dataclass
class Vote:
    """Represents a single vote in a consensus round."""
    node_id: str
    vote_type: VoteType
    reason: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "vote_type": self.vote_type.value,
            "reason": self.reason,
            "timestamp": self.timestamp
        }


@dataclass
class ConsensusRound:
    """Represents a single consensus round."""
    id: str
    operation: str
    initiator_node: str
    required_votes: int
    votes: List[Vote] = field(default_factory=list)
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "operation": self.operation,
            "initiator_node": self.initiator_node,
            "required_votes": self.required_votes,
            "votes": [v.to_dict() for v in self.votes],
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }


class QuorumConsensus:
    """
    k=3 Quorum Consensus Manager
    
    Manages consensus rounds for operations that require
    distributed agreement across lattice nodes. FREQ LAW
    mandates k=3 quorum for all critical operations.
    """
    
    def __init__(self, required_votes: int = 3):
        self.required_votes = required_votes  # k=3 by default
        self._active_rounds: Dict[str, ConsensusRound] = {}
        self._completed_rounds: List[ConsensusRound] = []
        self._eligible_voters: Set[str] = set()
    
    def register_voter(self, node_id: str) -> None:
        """Register a node as eligible to vote in consensus rounds."""
        self._eligible_voters.add(node_id)
    
    def unregister_voter(self, node_id: str) -> bool:
        """Remove a node from eligible voters."""
        if node_id in self._eligible_voters:
            self._eligible_voters.discard(node_id)
            return True
        return False
    
    def get_eligible_voters(self) -> List[str]:
        """Get list of eligible voter node IDs."""
        return list(self._eligible_voters)
    
    def initiate_consensus(self, operation: str, initiator_node: str,
                           metadata: Optional[Dict[str, Any]] = None) -> ConsensusRound:
        """
        Initiate a new consensus round.
        
        Args:
            operation: Description of the operation requiring consensus
            initiator_node: Node ID initiating the consensus
            metadata: Additional context for voters
            
        Returns:
            ConsensusRound object for tracking
        """
        round_id = str(uuid.uuid4())
        
        consensus_round = ConsensusRound(
            id=round_id,
            operation=operation,
            initiator_node=initiator_node,
            required_votes=self.required_votes
        )
        
        self._active_rounds[round_id] = consensus_round
        
        return consensus_round
    
    def submit_vote(self, round_id: str, node_id: str, 
                    vote_type: VoteType, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit a vote for a consensus round.
        
        Args:
            round_id: ID of the consensus round
            node_id: ID of the voting node
            vote_type: Type of vote (approve, reject, abstain)
            reason: Optional reason for the vote
            
        Returns:
            Dict with vote status and round state
        """
        if round_id not in self._active_rounds:
            return {"error": "Consensus round not found", "round_id": round_id}
        
        consensus_round = self._active_rounds[round_id]
        
        if consensus_round.status != "pending":
            return {"error": "Consensus round is not active", "status": consensus_round.status}
        
        # Check if node has already voted
        existing_voters = {v.node_id for v in consensus_round.votes}
        if node_id in existing_voters:
            return {"error": "Node has already voted in this round"}
        
        # Check if node is eligible to vote
        if self._eligible_voters and node_id not in self._eligible_voters:
            return {"error": "Node is not eligible to vote"}
        
        # Record the vote
        vote = Vote(
            node_id=node_id,
            vote_type=vote_type,
            reason=reason
        )
        consensus_round.votes.append(vote)
        
        # Check if consensus is reached
        self._evaluate_consensus(consensus_round)
        
        return {
            "round_id": round_id,
            "vote_recorded": True,
            "current_votes": len(consensus_round.votes),
            "approvals": self._count_approvals(consensus_round),
            "rejections": self._count_rejections(consensus_round),
            "status": consensus_round.status
        }
    
    def get_round_status(self, round_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a consensus round."""
        if round_id in self._active_rounds:
            return self._active_rounds[round_id].to_dict()
        
        for completed in self._completed_rounds:
            if completed.id == round_id:
                return completed.to_dict()
        
        return None
    
    def get_active_rounds(self) -> List[Dict[str, Any]]:
        """Get all active consensus rounds."""
        return [r.to_dict() for r in self._active_rounds.values()]
    
    def get_completed_rounds(self) -> List[Dict[str, Any]]:
        """Get all completed consensus rounds."""
        return [r.to_dict() for r in self._completed_rounds]
    
    def cancel_round(self, round_id: str, reason: str = "cancelled") -> bool:
        """Cancel an active consensus round."""
        if round_id not in self._active_rounds:
            return False
        
        consensus_round = self._active_rounds[round_id]
        consensus_round.status = "cancelled"
        consensus_round.completed_at = datetime.utcnow().isoformat()
        
        self._completed_rounds.append(consensus_round)
        del self._active_rounds[round_id]
        
        return True
    
    def has_quorum(self, round_id: str) -> bool:
        """Check if a round has achieved quorum."""
        if round_id not in self._active_rounds:
            for completed in self._completed_rounds:
                if completed.id == round_id:
                    return completed.status == "approved"
            return False
        
        consensus_round = self._active_rounds[round_id]
        return self._count_approvals(consensus_round) >= self.required_votes
    
    def _count_approvals(self, consensus_round: ConsensusRound) -> int:
        """Count approval votes in a round."""
        return sum(1 for v in consensus_round.votes if v.vote_type == VoteType.APPROVE)
    
    def _count_rejections(self, consensus_round: ConsensusRound) -> int:
        """Count rejection votes in a round."""
        return sum(1 for v in consensus_round.votes if v.vote_type == VoteType.REJECT)
    
    def _evaluate_consensus(self, consensus_round: ConsensusRound) -> None:
        """Evaluate if consensus has been reached."""
        approvals = self._count_approvals(consensus_round)
        rejections = self._count_rejections(consensus_round)
        
        # Check for approval quorum
        if approvals >= self.required_votes:
            consensus_round.status = "approved"
            consensus_round.completed_at = datetime.utcnow().isoformat()
            self._complete_round(consensus_round)
        
        # Check if approval is impossible (too many rejections)
        elif rejections > len(self._eligible_voters) - self.required_votes:
            consensus_round.status = "rejected"
            consensus_round.completed_at = datetime.utcnow().isoformat()
            self._complete_round(consensus_round)
    
    def _complete_round(self, consensus_round: ConsensusRound) -> None:
        """Move a round from active to completed."""
        if consensus_round.id in self._active_rounds:
            self._completed_rounds.append(consensus_round)
            del self._active_rounds[consensus_round.id]
