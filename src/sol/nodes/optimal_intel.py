"""
Optimal Intel Node

Analytics and decision support node providing
intelligence and insights across the lattice.
"""

import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import LatticeNode, NodeType, NodeMessage, NodeResponse


class OptimalIntel(LatticeNode):
    """
    Optimal Intelligence Node
    
    Provides analytics and decision support:
    - Data aggregation and analysis
    - Predictive modeling support
    - Decision recommendations
    - Performance dashboards
    """
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self._data_sources: Dict[str, Dict[str, Any]] = {}
        self._analyses: List[Dict[str, Any]] = []
        self._recommendations: List[Dict[str, Any]] = []
    
    @property
    def node_type(self) -> NodeType:
        return NodeType.OPTIMAL_INTEL
    
    @property
    def description(self) -> str:
        return "Analytics and decision support"
    
    def process_message(self, message: NodeMessage) -> NodeResponse:
        """Process analytics and intelligence messages."""
        start_time = time.time()
        
        try:
            operation = message.operation
            payload = message.payload
            
            if operation == "register_data_source":
                result = self._register_data_source(payload)
            elif operation == "run_analysis":
                result = self._run_analysis(payload)
            elif operation == "get_recommendation":
                result = self._get_recommendation(payload)
            elif operation == "aggregate_metrics":
                result = self._aggregate_metrics(payload)
            elif operation == "generate_report":
                result = self._generate_report(payload)
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
    
    def _register_data_source(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register a data source for analytics."""
        import uuid
        source_id = str(uuid.uuid4())
        
        source = {
            "id": source_id,
            "name": payload.get("name"),
            "type": payload.get("type"),  # e.g., "bigquery", "api", "node"
            "connection": payload.get("connection"),
            "refresh_interval": payload.get("refresh_interval", 3600),
            "registered_at": datetime.utcnow().isoformat()
        }
        
        self._data_sources[source_id] = source
        
        return {"source_id": source_id, "status": "registered"}
    
    def _run_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run an analysis on provided data."""
        import uuid
        analysis_id = str(uuid.uuid4())
        
        analysis = {
            "id": analysis_id,
            "type": payload.get("analysis_type"),
            "data_source": payload.get("data_source"),
            "parameters": payload.get("parameters", {}),
            "started_at": datetime.utcnow().isoformat(),
            "status": "completed",
            "results": self._simulate_analysis(payload)
        }
        
        self._analyses.append(analysis)
        
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "results": analysis["results"]
        }
    
    def _simulate_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate analysis results."""
        analysis_type = payload.get("analysis_type", "general")
        
        return {
            "type": analysis_type,
            "summary": f"Analysis completed for {analysis_type}",
            "metrics": {
                "data_points_analyzed": 1000,
                "confidence_score": 0.95,
                "processing_time_ms": 150
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_recommendation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get a decision recommendation."""
        import uuid
        
        context = payload.get("context", {})
        options = payload.get("options", [])
        
        recommendation = {
            "id": str(uuid.uuid4()),
            "context": context,
            "recommendation": options[0] if options else "No recommendation available",
            "confidence": 0.85,
            "reasoning": "Based on historical data and current context",
            "alternatives": options[1:] if len(options) > 1 else [],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        self._recommendations.append(recommendation)
        
        return recommendation
    
    def _aggregate_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate metrics from multiple sources."""
        metrics = payload.get("metrics", [])
        aggregation_type = payload.get("aggregation_type", "sum")
        
        values = [m.get("value", 0) for m in metrics if isinstance(m, dict)]
        
        if aggregation_type == "sum":
            result = sum(values)
        elif aggregation_type == "avg":
            result = sum(values) / len(values) if values else 0
        elif aggregation_type == "min":
            result = min(values) if values else 0
        elif aggregation_type == "max":
            result = max(values) if values else 0
        else:
            result = sum(values)
        
        return {
            "aggregation_type": aggregation_type,
            "input_count": len(values),
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an analytics report."""
        import uuid
        
        report = {
            "id": str(uuid.uuid4()),
            "title": payload.get("title", "Analytics Report"),
            "period": payload.get("period", "last_24_hours"),
            "sections": [
                {
                    "name": "Data Sources",
                    "count": len(self._data_sources)
                },
                {
                    "name": "Analyses Run",
                    "count": len(self._analyses)
                },
                {
                    "name": "Recommendations Generated",
                    "count": len(self._recommendations)
                }
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report
