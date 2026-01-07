"""
Legacy Architect Node

Legacy system translation node responsible for bridging
modern AI orchestration with legacy enterprise systems.
"""

import time
from typing import Any, Dict, List
from datetime import datetime
from .base import LatticeNode, NodeType, NodeMessage, NodeResponse


class LegacyArchitect(LatticeNode):
    """
    Legacy Architect Node
    
    Handles legacy system integration and translation:
    - Protocol translation (REST, SOAP, GraphQL, etc.)
    - Data format transformation
    - Legacy API adaptation
    - Migration path planning
    """
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self._adapters: Dict[str, Dict[str, Any]] = {}
        self._transformations: Dict[str, Dict[str, Any]] = {}
        self._migration_plans: List[Dict[str, Any]] = []
    
    @property
    def node_type(self) -> NodeType:
        return NodeType.LEGACY_ARCHITECT
    
    @property
    def description(self) -> str:
        return "Legacy system translation and integration"
    
    def process_message(self, message: NodeMessage) -> NodeResponse:
        """Process legacy integration messages."""
        start_time = time.time()
        
        try:
            operation = message.operation
            payload = message.payload
            
            if operation == "register_adapter":
                result = self._register_adapter(payload)
            elif operation == "translate_protocol":
                result = self._translate_protocol(payload)
            elif operation == "transform_data":
                result = self._transform_data(payload)
            elif operation == "create_migration_plan":
                result = self._create_migration_plan(payload)
            elif operation == "get_adapters":
                result = self._get_adapters()
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
    
    def _register_adapter(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register a legacy system adapter."""
        import uuid
        adapter_id = str(uuid.uuid4())
        
        adapter = {
            "id": adapter_id,
            "name": payload.get("name"),
            "source_protocol": payload.get("source_protocol"),
            "target_protocol": payload.get("target_protocol"),
            "endpoint": payload.get("endpoint"),
            "config": payload.get("config", {}),
            "registered_at": datetime.utcnow().isoformat()
        }
        
        self._adapters[adapter_id] = adapter
        
        return {"adapter_id": adapter_id, "status": "registered"}
    
    def _translate_protocol(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Translate between protocols."""
        source = payload.get("source_protocol")
        target = payload.get("target_protocol")
        data = payload.get("data")
        
        # Simulated protocol translation
        translated = {
            "original_protocol": source,
            "translated_protocol": target,
            "data": data,
            "translation_timestamp": datetime.utcnow().isoformat()
        }
        
        return {"translated": translated, "status": "success"}
    
    def _transform_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data between formats."""
        source_format = payload.get("source_format")
        target_format = payload.get("target_format")
        data = payload.get("data")
        
        # Simulated data transformation
        transformed = {
            "original_format": source_format,
            "transformed_format": target_format,
            "data": data,
            "transformation_timestamp": datetime.utcnow().isoformat()
        }
        
        return {"transformed": transformed, "status": "success"}
    
    def _create_migration_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a migration plan for legacy system."""
        import uuid
        
        plan = {
            "id": str(uuid.uuid4()),
            "legacy_system": payload.get("legacy_system"),
            "target_system": payload.get("target_system"),
            "phases": payload.get("phases", []),
            "estimated_duration": payload.get("estimated_duration"),
            "risk_assessment": payload.get("risk_assessment", "medium"),
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self._migration_plans.append(plan)
        
        return {"plan_id": plan["id"], "status": "created"}
    
    def _get_adapters(self) -> Dict[str, Any]:
        """Get all registered adapters."""
        return {
            "adapters": list(self._adapters.values()),
            "total_count": len(self._adapters)
        }
