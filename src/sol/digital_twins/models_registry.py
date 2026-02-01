"""
DTDL Models Registry for FREQ SOL Digital Twins

Manages loading, validation, and registration of DTDL models
with the Azure Digital Twins instance.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path


@dataclass
class DTDLModel:
    """Represents a DTDL model definition."""

    model_id: str
    display_name: str
    description: str
    contents: List[Dict[str, Any]]
    extends: Optional[str] = None
    raw_definition: Dict[str, Any] = field(default_factory=dict)

    @property
    def properties(self) -> List[Dict[str, Any]]:
        """Get all Property definitions."""
        return [c for c in self.contents if c.get("@type") == "Property"]

    @property
    def telemetry(self) -> List[Dict[str, Any]]:
        """Get all Telemetry definitions."""
        return [c for c in self.contents if c.get("@type") == "Telemetry"]

    @property
    def relationships(self) -> List[Dict[str, Any]]:
        """Get all Relationship definitions."""
        return [c for c in self.contents if c.get("@type") == "Relationship"]

    @property
    def commands(self) -> List[Dict[str, Any]]:
        """Get all Command definitions."""
        return [c for c in self.contents if c.get("@type") == "Command"]


class ModelsRegistry:
    """
    Registry for managing DTDL models.

    Loads models from JSON files and provides methods for
    model validation and Azure Digital Twins registration.
    """

    MODELS_DIR = Path(__file__).parent / "models"

    def __init__(self):
        self._models: Dict[str, DTDLModel] = {}
        self._load_all_models()

    def _load_all_models(self) -> None:
        """Load all DTDL model files from the models directory."""
        if not self.MODELS_DIR.exists():
            return

        for model_file in self.MODELS_DIR.glob("*.json"):
            try:
                model = self._load_model_file(model_file)
                if model:
                    self._models[model.model_id] = model
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Failed to load {model_file}: {e}")

    def _load_model_file(self, file_path: Path) -> Optional[DTDLModel]:
        """Load a single DTDL model from a JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)

        return DTDLModel(
            model_id=data["@id"],
            display_name=data.get("displayName", ""),
            description=data.get("description", ""),
            contents=data.get("contents", []),
            extends=data.get("extends"),
            raw_definition=data
        )

    def get_model(self, model_id: str) -> Optional[DTDLModel]:
        """Get a model by its DTDL ID."""
        return self._models.get(model_id)

    def get_model_by_name(self, name: str) -> Optional[DTDLModel]:
        """Get a model by its display name."""
        for model in self._models.values():
            if model.display_name == name:
                return model
        return None

    def list_models(self) -> List[str]:
        """List all registered model IDs."""
        return list(self._models.keys())

    def get_all_models(self) -> List[DTDLModel]:
        """Get all registered models."""
        return list(self._models.values())

    def get_models_for_upload(self) -> List[Dict[str, Any]]:
        """
        Get all models in the correct order for Azure Digital Twins upload.

        Models are sorted so that base interfaces come before extensions.
        """
        models = list(self._models.values())

        # Sort: models without extends first, then those that extend others
        base_models = [m for m in models if m.extends is None]
        extended_models = [m for m in models if m.extends is not None]

        ordered = base_models + extended_models
        return [m.raw_definition for m in ordered]

    def validate_model(self, model_id: str) -> Dict[str, Any]:
        """
        Validate a model's structure.

        Returns validation result with any issues found.
        """
        model = self.get_model(model_id)
        if not model:
            return {"valid": False, "errors": [f"Model {model_id} not found"]}

        errors = []
        warnings = []

        # Check required fields
        if not model.display_name:
            warnings.append("Missing displayName")

        if not model.description:
            warnings.append("Missing description")

        # Check for duplicate content names
        names = [c.get("name") for c in model.contents if "name" in c]
        duplicates = [n for n in names if names.count(n) > 1]
        if duplicates:
            errors.append(f"Duplicate content names: {set(duplicates)}")

        # Validate relationship targets exist
        for rel in model.relationships:
            target = rel.get("target")
            if target and target not in self._models:
                warnings.append(f"Relationship '{rel.get('name')}' targets unknown model: {target}")

        # Validate extends reference
        if model.extends and model.extends not in self._models:
            errors.append(f"Model extends unknown interface: {model.extends}")

        return {
            "valid": len(errors) == 0,
            "model_id": model_id,
            "errors": errors,
            "warnings": warnings,
            "properties_count": len(model.properties),
            "telemetry_count": len(model.telemetry),
            "relationships_count": len(model.relationships),
            "commands_count": len(model.commands)
        }

    def validate_all(self) -> Dict[str, Any]:
        """Validate all registered models."""
        results = {}
        all_valid = True

        for model_id in self._models:
            result = self.validate_model(model_id)
            results[model_id] = result
            if not result["valid"]:
                all_valid = False

        return {
            "all_valid": all_valid,
            "model_count": len(self._models),
            "results": results
        }

    def get_relationship_graph(self) -> Dict[str, List[str]]:
        """
        Build a graph of relationships between models.

        Returns a dict mapping model IDs to lists of related model IDs.
        """
        graph = {model_id: [] for model_id in self._models}

        for model in self._models.values():
            # Add extends relationship
            if model.extends:
                graph[model.model_id].append(model.extends)

            # Add explicit relationships
            for rel in model.relationships:
                target = rel.get("target")
                if target:
                    graph[model.model_id].append(target)

        return graph

    def format_summary(self) -> str:
        """Format a human-readable summary of all models."""
        lines = [
            "FREQ SOL DTDL Models Registry",
            "=" * 50,
            f"Total Models: {len(self._models)}",
            ""
        ]

        for model in self._models.values():
            lines.append(f"Model: {model.display_name}")
            lines.append(f"  ID: {model.model_id}")
            if model.extends:
                lines.append(f"  Extends: {model.extends}")
            lines.append(f"  Properties: {len(model.properties)}")
            lines.append(f"  Telemetry: {len(model.telemetry)}")
            lines.append(f"  Relationships: {len(model.relationships)}")
            lines.append(f"  Commands: {len(model.commands)}")
            lines.append("")

        return "\n".join(lines)
