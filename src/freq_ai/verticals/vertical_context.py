"""Vertical Domain Support for FREQ AI SOL"""

from typing import Dict, Any, Optional
from enum import Enum


class Vertical(Enum):
    """Supported vertical domains"""
    MARITIME = "maritime"
    AGRICULTURE = "agriculture"
    MANUFACTURING = "manufacturing"
    HEALTHCARE = "healthcare"
    CONSTRUCTION = "construction"


class VerticalContext:
    """Context and metadata for vertical domains"""
    
    VERTICAL_METADATA = {
        Vertical.MARITIME: {
            "description": "Maritime operations and logistics",
            "key_concerns": [
                "Vessel tracking and management",
                "Port operations optimization",
                "Cargo logistics and handling",
                "Maritime safety regulations",
                "Weather and route optimization",
                "International shipping compliance"
            ],
            "regulations": ["IMO", "SOLAS", "MARPOL", "ISM Code"],
            "typical_operations": [
                "Fleet management",
                "Route planning",
                "Cargo tracking",
                "Port coordination"
            ]
        },
        Vertical.AGRICULTURE: {
            "description": "Agricultural operations and supply chain",
            "key_concerns": [
                "Crop management and monitoring",
                "Supply chain optimization",
                "Equipment maintenance",
                "Weather and seasonal planning",
                "Food safety and quality",
                "Sustainability practices"
            ],
            "regulations": ["FDA", "USDA", "GAP", "Organic standards"],
            "typical_operations": [
                "Harvest planning",
                "Inventory management",
                "Distribution logistics",
                "Quality control"
            ]
        },
        Vertical.MANUFACTURING: {
            "description": "Manufacturing processes and optimization",
            "key_concerns": [
                "Production line efficiency",
                "Quality control and assurance",
                "Supply chain coordination",
                "Equipment maintenance",
                "Waste reduction",
                "Worker safety"
            ],
            "regulations": ["ISO 9001", "OSHA", "Industry-specific standards"],
            "typical_operations": [
                "Production scheduling",
                "Quality inspection",
                "Maintenance planning",
                "Inventory optimization"
            ]
        },
        Vertical.HEALTHCARE: {
            "description": "Healthcare systems and compliance",
            "key_concerns": [
                "Patient data privacy",
                "Clinical workflow optimization",
                "Medical equipment management",
                "Regulatory compliance",
                "Patient safety",
                "Interoperability standards"
            ],
            "regulations": ["HIPAA", "FDA", "HITECH", "HL7", "FHIR"],
            "typical_operations": [
                "Patient scheduling",
                "EHR management",
                "Clinical decision support",
                "Compliance monitoring"
            ]
        },
        Vertical.CONSTRUCTION: {
            "description": "Construction project management and safety",
            "key_concerns": [
                "Project scheduling and tracking",
                "Resource allocation",
                "Safety compliance",
                "Budget management",
                "Quality control",
                "Regulatory permits"
            ],
            "regulations": ["OSHA", "Building codes", "Environmental regulations"],
            "typical_operations": [
                "Project planning",
                "Resource scheduling",
                "Safety inspections",
                "Progress tracking"
            ]
        }
    }
    
    @classmethod
    def get_context(cls, vertical: Vertical) -> Dict[str, Any]:
        """
        Get context for a vertical domain
        
        Args:
            vertical: Target vertical
            
        Returns:
            Dictionary with vertical metadata
        """
        return cls.VERTICAL_METADATA.get(vertical, {})
    
    @classmethod
    def get_description(cls, vertical: Vertical) -> str:
        """Get vertical description"""
        return cls.VERTICAL_METADATA.get(vertical, {}).get("description", "")
    
    @classmethod
    def get_regulations(cls, vertical: Vertical) -> list:
        """Get applicable regulations for vertical"""
        return cls.VERTICAL_METADATA.get(vertical, {}).get("regulations", [])
    
    @classmethod
    def from_string(cls, vertical_str: str) -> Optional[Vertical]:
        """
        Convert string to Vertical enum
        
        Args:
            vertical_str: Vertical name as string
            
        Returns:
            Vertical enum or None if invalid
        """
        try:
            return Vertical(vertical_str.lower())
        except (ValueError, AttributeError):
            return None
