"""
Exec Automate Node

Workflow execution node responsible for automating
complex multi-step workflows across the lattice.
"""

import time
from typing import Any, Dict, List
from datetime import datetime
from enum import Enum
from .base import LatticeNode, NodeType, NodeMessage, NodeResponse


class WorkflowStatus(Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecAutomate(LatticeNode):
    """
    Execution Automation Node
    
    Handles workflow execution across the SOL lattice:
    - Multi-step workflow orchestration
    - Parallel and sequential execution patterns
    - Error handling and retry logic
    - Workflow state management
    """
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self._workflows: Dict[str, Dict[str, Any]] = {}
        self._execution_history: List[Dict[str, Any]] = []
    
    @property
    def node_type(self) -> NodeType:
        return NodeType.EXEC_AUTOMATE
    
    @property
    def description(self) -> str:
        return "Workflow execution and automation"
    
    def process_message(self, message: NodeMessage) -> NodeResponse:
        """Process workflow execution messages."""
        start_time = time.time()
        
        try:
            operation = message.operation
            payload = message.payload
            
            if operation == "create_workflow":
                result = self._create_workflow(payload)
            elif operation == "execute_workflow":
                result = self._execute_workflow(payload)
            elif operation == "pause_workflow":
                result = self._pause_workflow(payload)
            elif operation == "resume_workflow":
                result = self._resume_workflow(payload)
            elif operation == "cancel_workflow":
                result = self._cancel_workflow(payload)
            elif operation == "get_workflow_status":
                result = self._get_workflow_status(payload)
            elif operation == "list_workflows":
                result = self._list_workflows()
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
    
    def _create_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow definition."""
        import uuid
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "id": workflow_id,
            "name": payload.get("name"),
            "description": payload.get("description"),
            "steps": payload.get("steps", []),
            "triggers": payload.get("triggers", []),
            "status": WorkflowStatus.PENDING.value,
            "created_at": datetime.utcnow().isoformat(),
            "execution_count": 0
        }
        
        self._workflows[workflow_id] = workflow
        
        return {"workflow_id": workflow_id, "status": "created"}
    
    def _execute_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow."""
        workflow_id = payload.get("workflow_id")
        
        if workflow_id not in self._workflows:
            return {"error": "Workflow not found"}
        
        workflow = self._workflows[workflow_id]
        workflow["status"] = WorkflowStatus.RUNNING.value
        workflow["execution_count"] += 1
        workflow["last_execution"] = datetime.utcnow().isoformat()
        
        # Record execution
        execution = {
            "workflow_id": workflow_id,
            "execution_number": workflow["execution_count"],
            "started_at": datetime.utcnow().isoformat(),
            "status": "running",
            "steps_completed": 0,
            "total_steps": len(workflow["steps"])
        }
        self._execution_history.append(execution)
        
        # Simulate step execution
        for i, step in enumerate(workflow["steps"]):
            execution["steps_completed"] = i + 1
        
        workflow["status"] = WorkflowStatus.COMPLETED.value
        execution["status"] = "completed"
        execution["completed_at"] = datetime.utcnow().isoformat()
        
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "steps_executed": len(workflow["steps"])
        }
    
    def _pause_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Pause a running workflow."""
        workflow_id = payload.get("workflow_id")
        
        if workflow_id not in self._workflows:
            return {"error": "Workflow not found"}
        
        workflow = self._workflows[workflow_id]
        if workflow["status"] != WorkflowStatus.RUNNING.value:
            return {"error": "Workflow is not running"}
        
        workflow["status"] = WorkflowStatus.PAUSED.value
        
        return {"workflow_id": workflow_id, "status": "paused"}
    
    def _resume_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Resume a paused workflow."""
        workflow_id = payload.get("workflow_id")
        
        if workflow_id not in self._workflows:
            return {"error": "Workflow not found"}
        
        workflow = self._workflows[workflow_id]
        if workflow["status"] != WorkflowStatus.PAUSED.value:
            return {"error": "Workflow is not paused"}
        
        workflow["status"] = WorkflowStatus.RUNNING.value
        
        return {"workflow_id": workflow_id, "status": "running"}
    
    def _cancel_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a workflow."""
        workflow_id = payload.get("workflow_id")
        
        if workflow_id not in self._workflows:
            return {"error": "Workflow not found"}
        
        self._workflows[workflow_id]["status"] = WorkflowStatus.CANCELLED.value
        
        return {"workflow_id": workflow_id, "status": "cancelled"}
    
    def _get_workflow_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get the status of a workflow."""
        workflow_id = payload.get("workflow_id")
        
        if workflow_id not in self._workflows:
            return {"error": "Workflow not found"}
        
        return self._workflows[workflow_id]
    
    def _list_workflows(self) -> Dict[str, Any]:
        """List all workflows."""
        return {
            "workflows": list(self._workflows.values()),
            "total_count": len(self._workflows)
        }
