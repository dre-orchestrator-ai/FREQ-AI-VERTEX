"""
SPCI Node

Continuous Improvement Cycles node implementing the
Systematic Process Continuous Improvement framework.
"""

import time
from typing import Any, Dict, List
from datetime import datetime
from .base import LatticeNode, NodeType, NodeMessage, NodeResponse


class SPCI(LatticeNode):
    """
    Systematic Process Continuous Improvement Node
    
    Manages continuous improvement cycles across the SOL lattice:
    - Performance metric collection and analysis
    - Improvement opportunity identification
    - A/B testing and experimentation
    - Learning loop integration
    """
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self._improvement_cycles: List[Dict[str, Any]] = []
        self._metrics: Dict[str, List[float]] = {}
        self._experiments: Dict[str, Dict[str, Any]] = {}
    
    @property
    def node_type(self) -> NodeType:
        return NodeType.SPCI
    
    @property
    def description(self) -> str:
        return "Continuous improvement cycles and evolutionary optimization"
    
    def process_message(self, message: NodeMessage) -> NodeResponse:
        """Process continuous improvement messages."""
        start_time = time.time()
        
        try:
            operation = message.operation
            payload = message.payload
            
            if operation == "record_metric":
                result = self._record_metric(payload)
            elif operation == "analyze_performance":
                result = self._analyze_performance(payload)
            elif operation == "start_experiment":
                result = self._start_experiment(payload)
            elif operation == "end_experiment":
                result = self._end_experiment(payload)
            elif operation == "get_improvement_suggestions":
                result = self._get_improvement_suggestions()
            elif operation == "create_improvement_cycle":
                result = self._create_improvement_cycle(payload)
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
    
    def _record_metric(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Record a performance metric."""
        metric_name = payload.get("name")
        value = payload.get("value")
        
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        
        self._metrics[metric_name].append(value)
        
        return {
            "metric": metric_name,
            "recorded_value": value,
            "total_samples": len(self._metrics[metric_name])
        }
    
    def _analyze_performance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics."""
        metric_name = payload.get("name")
        
        if metric_name not in self._metrics or not self._metrics[metric_name]:
            return {"error": f"No data for metric: {metric_name}"}
        
        values = self._metrics[metric_name]
        
        return {
            "metric": metric_name,
            "sample_count": len(values),
            "min": min(values),
            "max": max(values),
            "average": sum(values) / len(values),
            "latest": values[-1]
        }
    
    def _start_experiment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Start an A/B experiment."""
        import uuid
        experiment_id = str(uuid.uuid4())
        
        experiment = {
            "id": experiment_id,
            "name": payload.get("name"),
            "hypothesis": payload.get("hypothesis"),
            "variants": payload.get("variants", ["control", "treatment"]),
            "start_time": datetime.utcnow().isoformat(),
            "status": "running",
            "results": {}
        }
        
        self._experiments[experiment_id] = experiment
        
        return {"experiment_id": experiment_id, "status": "started"}
    
    def _end_experiment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """End an experiment and analyze results."""
        experiment_id = payload.get("experiment_id")
        
        if experiment_id not in self._experiments:
            return {"error": "Experiment not found"}
        
        experiment = self._experiments[experiment_id]
        experiment["status"] = "completed"
        experiment["end_time"] = datetime.utcnow().isoformat()
        
        return {
            "experiment_id": experiment_id,
            "status": "completed",
            "results": experiment.get("results", {})
        }
    
    def _get_improvement_suggestions(self) -> Dict[str, Any]:
        """Generate improvement suggestions based on collected metrics."""
        suggestions = []
        
        for metric_name, values in self._metrics.items():
            if len(values) >= 5:
                avg = sum(values) / len(values)
                recent_avg = sum(values[-5:]) / 5
                
                if recent_avg > avg * 1.1:
                    suggestions.append({
                        "metric": metric_name,
                        "type": "degradation_warning",
                        "message": f"Recent {metric_name} values are 10% above average"
                    })
        
        return {
            "suggestions": suggestions,
            "total_metrics_analyzed": len(self._metrics)
        }
    
    def _create_improvement_cycle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new improvement cycle."""
        import uuid
        
        cycle = {
            "id": str(uuid.uuid4()),
            "name": payload.get("name"),
            "focus_area": payload.get("focus_area"),
            "baseline_metrics": payload.get("baseline_metrics", {}),
            "target_metrics": payload.get("target_metrics", {}),
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self._improvement_cycles.append(cycle)
        
        return {"cycle_id": cycle["id"], "status": "created"}
