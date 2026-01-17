"""
FREQ AI Platform Abstraction Layer (PAL)

Multi-provider support for AI model access with automatic failover.
Supports AWS Bedrock, Anthropic Direct, Google Vertex AI, and Azure Foundry.
"""

from .providers import (
    BaseProvider,
    AWSBedrockProvider,
    AnthropicDirectProvider,
    VertexAIProvider,
    AzureFoundryProvider,
)
from .unified_model import UnifiedModelInterface
from .config import PlatformConfig, ProviderPriority

__all__ = [
    "BaseProvider",
    "AWSBedrockProvider",
    "AnthropicDirectProvider",
    "VertexAIProvider",
    "AzureFoundryProvider",
    "UnifiedModelInterface",
    "PlatformConfig",
    "ProviderPriority",
]
