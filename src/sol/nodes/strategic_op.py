"""
Strategic OP Node

Mission-level coordination node responsible for high-level
strategic planning and cross-node orchestration.
"""

import time
from typing import Any, Dict
from .base import LatticeNode, NodeType, NodeMessage, NodeResponse


class StrategicOP(LatticeNode):
    """
    Strategic Operations Node
    
    Handles mission-level coordination across the SOL lattice:
    - Strategic planning and objective setting
    - Cross-node workflow orchestration
    - Priority management and resource allocation
    - Mission status monitoring and reporting
    """
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self._active_missions: Dict[str, Dict[str, Any]] = {}
        self._strategic_objectives: list = []
    
    @property
    def node_type(self) -> NodeType:
        return NodeType.STRATEGIC_OP
    
    @property
    def description(self) -> str:
        return "Mission-level coordination and strategic planning"
    
    def process_message(self, message: NodeMessage) -> NodeResponse:
        """Process strategic coordination messages."""
        start_time = time.time()
        
        try:
            operation = message.operation
            payload = message.payload
            
            if operation == "create_mission":
                result = self._create_mission(payload)
            elif operation == "update_mission":
                result = self._update_mission(payload)
            elif operation == "get_mission_status":
                result = self._get_mission_status(payload.get("mission_id"))
            elif operation == "set_objective":
                result = self._set_objective(payload)
            elif operation == "orchestrate":
                result = self._orchestrate_workflow(payload)
            else:
                result = {"error": f"Unknown operation: {operation}"}
            
            execution_time = (time.time() - start_time) * 1000
            
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
    
    def _create_mission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new strategic mission."""
        import uuid
        mission_id = str(uuid.uuid4())
        mission = {
            "id": mission_id,
            "name": payload.get("name", "Unnamed Mission"),
            "objectives": payload.get("objectives", []),
            "priority": payload.get("priority", "normal"),
            "status": "active",
            "created_at": time.time()
        }
        self._active_missions[mission_id] = mission
        return {"mission_id": mission_id, "status": "created"}
    
    def _update_mission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing mission."""
        mission_id = payload.get("mission_id")
        if mission_id not in self._active_missions:
            return {"error": "Mission not found"}
        
        updates = payload.get("updates", {})
        self._active_missions[mission_id].update(updates)
        return {"mission_id": mission_id, "status": "updated"}
    
    def _get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """Get status of a mission."""
        if mission_id not in self._active_missions:
            return {"error": "Mission not found"}
        return self._active_missions[mission_id]
    
    def _set_objective(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Set a strategic objective."""
        objective = {
            "name": payload.get("name"),
            "description": payload.get("description"),
            "priority": payload.get("priority", "normal"),
            "target_date": payload.get("target_date")
        }
        self._strategic_objectives.append(objective)
        return {"status": "objective_set", "total_objectives": len(self._strategic_objectives)}
    
    def _orchestrate_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a workflow across connected nodes."""
        workflow_id = payload.get("workflow_id")
        steps = payload.get("steps", [])
        
        return {
            "workflow_id": workflow_id,
            "steps_count": len(steps),
            "status": "orchestration_initiated",
            "connected_nodes": list(self._connected_nodes.keys())
        }
