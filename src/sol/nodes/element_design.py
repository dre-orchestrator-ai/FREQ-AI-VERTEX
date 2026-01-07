"""
Element Design Node

Schema and artifact generation node responsible for
creating structured outputs and design elements.
"""

import time
from typing import Any, Dict, List
from datetime import datetime
from .base import LatticeNode, NodeType, NodeMessage, NodeResponse


class ElementDesign(LatticeNode):
    """
    Element Design Node
    
    Handles schema and artifact generation:
    - Schema definition and validation
    - Artifact generation (configs, templates, etc.)
    - Design pattern implementation
    - Output formatting and structuring
    """
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._artifacts: Dict[str, Dict[str, Any]] = {}
        self._templates: Dict[str, str] = {}
    
    @property
    def node_type(self) -> NodeType:
        return NodeType.ELEMENT_DESIGN
    
    @property
    def description(self) -> str:
        return "Schema and artifact generation"
    
    def process_message(self, message: NodeMessage) -> NodeResponse:
        """Process design and generation messages."""
        start_time = time.time()
        
        try:
            operation = message.operation
            payload = message.payload
            
            if operation == "create_schema":
                result = self._create_schema(payload)
            elif operation == "validate_schema":
                result = self._validate_schema(payload)
            elif operation == "generate_artifact":
                result = self._generate_artifact(payload)
            elif operation == "register_template":
                result = self._register_template(payload)
            elif operation == "apply_template":
                result = self._apply_template(payload)
            elif operation == "list_schemas":
                result = self._list_schemas()
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
    
    def _create_schema(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new schema definition."""
        import uuid
        schema_id = str(uuid.uuid4())
        
        schema = {
            "id": schema_id,
            "name": payload.get("name"),
            "version": payload.get("version", "1.0.0"),
            "type": payload.get("type", "object"),
            "properties": payload.get("properties", {}),
            "required": payload.get("required", []),
            "created_at": datetime.utcnow().isoformat()
        }
        
        self._schemas[schema_id] = schema
        
        return {"schema_id": schema_id, "status": "created"}
    
    def _validate_schema(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against a schema."""
        schema_id = payload.get("schema_id")
        data = payload.get("data", {})
        
        if schema_id not in self._schemas:
            return {"valid": False, "error": "Schema not found"}
        
        schema = self._schemas[schema_id]
        errors = []
        
        # Check required fields
        for field in schema.get("required", []):
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check property types
        for prop_name, prop_def in schema.get("properties", {}).items():
            if prop_name in data:
                expected_type = prop_def.get("type")
                actual_type = type(data[prop_name]).__name__
                
                type_mapping = {
                    "string": "str",
                    "integer": "int",
                    "number": ("int", "float"),
                    "boolean": "bool",
                    "array": "list",
                    "object": "dict"
                }
                
                expected = type_mapping.get(expected_type, expected_type)
                if isinstance(expected, tuple):
                    if actual_type not in expected:
                        errors.append(f"Field {prop_name}: expected {expected_type}, got {actual_type}")
                elif actual_type != expected:
                    errors.append(f"Field {prop_name}: expected {expected_type}, got {actual_type}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "schema_id": schema_id
        }
    
    def _generate_artifact(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an artifact based on specifications."""
        import uuid
        artifact_id = str(uuid.uuid4())
        
        artifact = {
            "id": artifact_id,
            "type": payload.get("type"),
            "name": payload.get("name"),
            "content": payload.get("content", {}),
            "metadata": payload.get("metadata", {}),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        self._artifacts[artifact_id] = artifact
        
        return {
            "artifact_id": artifact_id,
            "status": "generated",
            "artifact": artifact
        }
    
    def _register_template(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register a template for artifact generation."""
        template_name = payload.get("name")
        template_content = payload.get("content")
        
        self._templates[template_name] = template_content
        
        return {
            "template_name": template_name,
            "status": "registered"
        }
    
    def _apply_template(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a template with provided variables."""
        template_name = payload.get("template_name")
        variables = payload.get("variables", {})
        
        if template_name not in self._templates:
            return {"error": "Template not found"}
        
        template = self._templates[template_name]
        
        # Simple variable substitution
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        
        return {
            "template_name": template_name,
            "result": result,
            "variables_applied": list(variables.keys())
        }
    
    def _list_schemas(self) -> Dict[str, Any]:
        """List all registered schemas."""
        return {
            "schemas": [
                {"id": s["id"], "name": s["name"], "version": s["version"]}
                for s in self._schemas.values()
            ],
            "total_count": len(self._schemas)
        }
