"""
Base Lattice Node Definition

All lattice nodes in the SOL system inherit from LatticeNode,
providing common functionality for FREQ LAW compliance, 
quorum participation, and audit logging.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import uuid


class NodeType(Enum):
    """Types of nodes in the Sophisticated Operational Lattice."""
    
    STRATEGIC_OP = "strategic_op"          # Mission-level coordination
    SPCI = "spci"                          # Continuous improvement cycles
    LEGACY_ARCHITECT = "legacy_architect"  # Legacy system translation
    GOV_ENGINE = "gov_engine"              # FREQ LAW compliance, VETO authority
    EXEC_AUTOMATE = "exec_automate"        # Workflow execution
    OPTIMAL_INTEL = "optimal_intel"        # Analytics and decision support
    ELEMENT_DESIGN = "element_design"      # Schema and artifact generation


@dataclass
class NodeMessage:
    """Message passed between lattice nodes."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_node: str = ""
    target_node: str = ""
    operation: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    requires_quorum: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "operation": self.operation,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "requires_quorum": self.requires_quorum
        }


@dataclass
class NodeResponse:
    """Response from a lattice node operation."""
    
    message_id: str
    node_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "node_id": self.node_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp
        }


class LatticeNode(ABC):
    """
    Base class for all SOL lattice nodes.
    
    Each node in the Sophisticated Operational Lattice implements
    specific functionality while adhering to FREQ LAW governance.
    """
    
    def __init__(self, node_id: Optional[str] = None):
        self.node_id = node_id or str(uuid.uuid4())
        self._message_history: List[NodeMessage] = []
        self._response_history: List[NodeResponse] = []
        self._connected_nodes: Dict[str, 'LatticeNode'] = {}
    
    @property
    @abstractmethod
    def node_type(self) -> NodeType:
        """Return the type of this lattice node."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of this node's role."""
        pass
    
    @abstractmethod
    def process_message(self, message: NodeMessage) -> NodeResponse:
        """
        Process an incoming message and return a response.
        
        Args:
            message: Incoming NodeMessage to process
            
        Returns:
            NodeResponse with operation result
        """
        pass
    
    def connect_node(self, node: 'LatticeNode') -> None:
        """Connect to another lattice node for communication."""
        self._connected_nodes[node.node_id] = node
    
    def disconnect_node(self, node_id: str) -> bool:
        """Disconnect from a lattice node."""
        if node_id in self._connected_nodes:
            del self._connected_nodes[node_id]
            return True
        return False
    
    def send_message(self, target_node_id: str, operation: str, 
                     payload: Dict[str, Any], requires_quorum: bool = True) -> Optional[NodeResponse]:
        """
        Send a message to a connected node.
        
        Args:
            target_node_id: ID of the target node
            operation: Operation to perform
            payload: Data payload for the operation
            requires_quorum: Whether operation requires k=3 quorum
            
        Returns:
            NodeResponse from target node, or None if not connected
        """
        if target_node_id not in self._connected_nodes:
            return None
        
        message = NodeMessage(
            source_node=self.node_id,
            target_node=target_node_id,
            operation=operation,
            payload=payload,
            requires_quorum=requires_quorum
        )
        
        self._message_history.append(message)
        target_node = self._connected_nodes[target_node_id]
        response = target_node.process_message(message)
        self._response_history.append(response)
        
        return response
    
    def get_node_info(self) -> Dict[str, Any]:
        """Get information about this node."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "description": self.description,
            "connected_nodes": list(self._connected_nodes.keys()),
            "message_count": len(self._message_history),
            "response_count": len(self._response_history)
        }
    
    def get_audit_data(self) -> Dict[str, Any]:
        """Get audit data for BigQuery logging."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "messages": [m.to_dict() for m in self._message_history],
            "responses": [r.to_dict() for r in self._response_history],
            "timestamp": datetime.utcnow().isoformat()
        }
