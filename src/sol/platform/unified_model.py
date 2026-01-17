"""
FREQ AI Unified Model Interface (UMI)

Provides a single interface for all AI model interactions across providers.
Implements automatic failover, load balancing, and provider health management.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

from .providers import (
    BaseProvider,
    AWSBedrockProvider,
    AnthropicDirectProvider,
    VertexAIProvider,
    AzureFoundryProvider,
    CompletionRequest,
    CompletionResponse,
    ProviderStatus,
)

logger = logging.getLogger(__name__)


class FailoverStrategy(Enum):
    """Strategy for handling provider failures."""
    PRIORITY = "priority"  # Try providers in priority order
    ROUND_ROBIN = "round_robin"  # Rotate through healthy providers
    FASTEST = "fastest"  # Use fastest responding provider


class LatticeLevel(Enum):
    """FREQ AI Lattice hierarchy levels."""
    L0_SOVEREIGN = 0
    L1_SSC = 1
    L2_CGE = 2
    L3_SIL = 3
    L4_SA = 4
    L5_TOM = 5


@dataclass
class SubstrateMapping:
    """Maps lattice levels to preferred model substrates."""
    level: LatticeLevel
    primary_provider: str
    primary_model: str
    fallback_provider: str
    fallback_model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    strict_mode: bool = False  # For CGE governance decisions


# Default substrate mappings per blueprint specification
DEFAULT_SUBSTRATE_MAPPINGS = {
    LatticeLevel.L1_SSC: SubstrateMapping(
        level=LatticeLevel.L1_SSC,
        primary_provider="aws_bedrock",
        primary_model="opus-4.5",
        fallback_provider="vertex_ai",
        fallback_model="gemini-3-thinking",
        max_tokens=8192,
    ),
    LatticeLevel.L2_CGE: SubstrateMapping(
        level=LatticeLevel.L2_CGE,
        primary_provider="aws_bedrock",
        primary_model="opus-4.5",
        fallback_provider="vertex_ai",
        fallback_model="gemini-3-pro",
        temperature=0.0,  # Deterministic for governance
        strict_mode=True,
    ),
    LatticeLevel.L3_SIL: SubstrateMapping(
        level=LatticeLevel.L3_SIL,
        primary_provider="vertex_ai",
        primary_model="gemini-3-flash",
        fallback_provider="anthropic_direct",
        fallback_model="sonnet-4.5",
    ),
    LatticeLevel.L4_SA: SubstrateMapping(
        level=LatticeLevel.L4_SA,
        primary_provider="vertex_ai",
        primary_model="gemini-3-pro",
        fallback_provider="anthropic_direct",
        fallback_model="sonnet-4.5",
    ),
    LatticeLevel.L5_TOM: SubstrateMapping(
        level=LatticeLevel.L5_TOM,
        primary_provider="vertex_ai",
        primary_model="gemini-3-flash",
        fallback_provider="aws_bedrock",
        fallback_model="haiku-4.5",
        max_tokens=2048,  # Fast responses for runtime
    ),
}


@dataclass
class ProviderMetrics:
    """Metrics for a provider."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    average_latency_ms: float = 0.0
    last_request_time: float = 0.0
    uptime_percentage: float = 100.0


class UnifiedModelInterface:
    """
    Unified interface for AI model interactions.

    Provides:
    - Multi-provider support with automatic failover
    - Lattice-level substrate routing
    - Health monitoring and metrics
    - Retry logic with exponential backoff
    - Audit trail integration
    """

    def __init__(
        self,
        providers: Optional[Dict[str, BaseProvider]] = None,
        substrate_mappings: Optional[Dict[LatticeLevel, SubstrateMapping]] = None,
        failover_strategy: FailoverStrategy = FailoverStrategy.PRIORITY,
        max_retries: int = 3,
        retry_delay_base: float = 1.0,
    ):
        self.providers: Dict[str, BaseProvider] = providers or {}
        self.substrate_mappings = substrate_mappings or DEFAULT_SUBSTRATE_MAPPINGS
        self.failover_strategy = failover_strategy
        self.max_retries = max_retries
        self.retry_delay_base = retry_delay_base

        # Provider priority (1 = highest)
        self.provider_priority = {
            "aws_bedrock": 1,
            "anthropic_direct": 2,
            "vertex_ai": 3,
            "azure_foundry": 4,
        }

        # Metrics tracking
        self.metrics: Dict[str, ProviderMetrics] = {}

        # Health check task
        self._health_check_task: Optional[asyncio.Task] = None
        self._health_check_interval = 60.0  # seconds

    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize providers from configuration."""
        provider_configs = config.get("providers", {})

        # Initialize AWS Bedrock (Primary)
        if "aws_bedrock" in provider_configs:
            self.providers["aws_bedrock"] = AWSBedrockProvider(
                provider_configs["aws_bedrock"]
            )
            self.metrics["aws_bedrock"] = ProviderMetrics()

        # Initialize Anthropic Direct (Fallback)
        if "anthropic_direct" in provider_configs:
            self.providers["anthropic_direct"] = AnthropicDirectProvider(
                provider_configs["anthropic_direct"]
            )
            self.metrics["anthropic_direct"] = ProviderMetrics()

        # Initialize Vertex AI (Secondary)
        if "vertex_ai" in provider_configs:
            self.providers["vertex_ai"] = VertexAIProvider(
                provider_configs["vertex_ai"]
            )
            self.metrics["vertex_ai"] = ProviderMetrics()

        # Initialize Azure Foundry (Tertiary)
        if "azure_foundry" in provider_configs:
            self.providers["azure_foundry"] = AzureFoundryProvider(
                provider_configs["azure_foundry"]
            )
            self.metrics["azure_foundry"] = ProviderMetrics()

        # Perform initial health checks
        await self._check_all_providers()

        # Start background health monitoring
        self._health_check_task = asyncio.create_task(self._health_monitor())

        logger.info(f"UnifiedModelInterface initialized with {len(self.providers)} providers")

    async def shutdown(self) -> None:
        """Shutdown the interface."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

    async def complete(
        self,
        request: CompletionRequest,
        lattice_level: Optional[LatticeLevel] = None,
    ) -> CompletionResponse:
        """
        Execute a completion request with automatic provider selection and failover.

        Args:
            request: The completion request
            lattice_level: Optional lattice level for substrate routing

        Returns:
            CompletionResponse from the first successful provider
        """
        # Determine provider order based on substrate mapping or priority
        provider_order = self._get_provider_order(lattice_level)

        # Apply substrate-specific configuration if level specified
        if lattice_level and lattice_level in self.substrate_mappings:
            mapping = self.substrate_mappings[lattice_level]
            if mapping.strict_mode:
                request.temperature = 0.0
            if mapping.max_tokens and not request.max_tokens:
                request.max_tokens = mapping.max_tokens

        last_error: Optional[Exception] = None

        for provider_name in provider_order:
            provider = self.providers.get(provider_name)
            if not provider or not provider.is_healthy():
                continue

            for attempt in range(self.max_retries):
                try:
                    response = await provider.complete(request)

                    # Update metrics
                    self._update_metrics(provider_name, response.latency_ms, success=True)

                    return response

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Provider {provider_name} attempt {attempt + 1} failed: {e}"
                    )

                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay_base * (2 ** attempt)
                        await asyncio.sleep(delay)

            # Mark provider as having failed
            self._update_metrics(provider_name, 0, success=False)

        # All providers exhausted
        raise RuntimeError(
            f"All providers failed. Last error: {last_error}"
        )

    async def complete_for_node(
        self,
        request: CompletionRequest,
        node_type: str,
    ) -> CompletionResponse:
        """
        Execute a completion request for a specific lattice node type.

        Maps node types to lattice levels and applies appropriate substrate.
        """
        level_mapping = {
            "SSC": LatticeLevel.L1_SSC,
            "StrategicSynthesisCore": LatticeLevel.L1_SSC,
            "CGE": LatticeLevel.L2_CGE,
            "CognitiveGovernanceEngine": LatticeLevel.L2_CGE,
            "GOVEngine": LatticeLevel.L2_CGE,
            "SIL": LatticeLevel.L3_SIL,
            "StrategicIntelligenceLead": LatticeLevel.L3_SIL,
            "OptimalIntel": LatticeLevel.L3_SIL,
            "SA": LatticeLevel.L4_SA,
            "SystemArchitect": LatticeLevel.L4_SA,
            "ElementDesign": LatticeLevel.L4_SA,
            "TOM": LatticeLevel.L5_TOM,
            "RuntimeRealizationNode": LatticeLevel.L5_TOM,
            "ExecAutomate": LatticeLevel.L5_TOM,
        }

        lattice_level = level_mapping.get(node_type, LatticeLevel.L5_TOM)
        return await self.complete(request, lattice_level)

    async def stream(
        self,
        request: CompletionRequest,
        lattice_level: Optional[LatticeLevel] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion request."""
        provider_order = self._get_provider_order(lattice_level)

        for provider_name in provider_order:
            provider = self.providers.get(provider_name)
            if not provider or not provider.is_healthy():
                continue

            try:
                async for chunk in provider.stream(request):
                    yield chunk
                return
            except Exception as e:
                logger.warning(f"Provider {provider_name} streaming failed: {e}")
                continue

        raise RuntimeError("All providers failed for streaming")

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        status = {}
        for name, provider in self.providers.items():
            metrics = self.metrics.get(name, ProviderMetrics())
            status[name] = {
                "status": provider.status.value,
                "is_healthy": provider.is_healthy(),
                "total_requests": metrics.total_requests,
                "success_rate": (
                    metrics.successful_requests / metrics.total_requests * 100
                    if metrics.total_requests > 0 else 100
                ),
                "average_latency_ms": metrics.average_latency_ms,
                "available_models": [m.display_name for m in provider.get_available_models()],
            }
        return status

    def get_substrate_info(self, lattice_level: LatticeLevel) -> Dict[str, Any]:
        """Get substrate configuration for a lattice level."""
        mapping = self.substrate_mappings.get(lattice_level)
        if not mapping:
            return {}

        return {
            "level": mapping.level.name,
            "primary_provider": mapping.primary_provider,
            "primary_model": mapping.primary_model,
            "fallback_provider": mapping.fallback_provider,
            "fallback_model": mapping.fallback_model,
            "temperature": mapping.temperature,
            "strict_mode": mapping.strict_mode,
        }

    def _get_provider_order(
        self,
        lattice_level: Optional[LatticeLevel] = None,
    ) -> List[str]:
        """Determine provider order based on strategy and level mapping."""
        if lattice_level and lattice_level in self.substrate_mappings:
            mapping = self.substrate_mappings[lattice_level]
            # Start with mapped providers, then fall through to others
            order = [mapping.primary_provider, mapping.fallback_provider]
            for p in sorted(self.provider_priority, key=lambda x: self.provider_priority[x]):
                if p not in order:
                    order.append(p)
            return order

        # Default priority order
        return sorted(
            self.providers.keys(),
            key=lambda x: self.provider_priority.get(x, 99)
        )

    def _update_metrics(
        self,
        provider_name: str,
        latency_ms: float,
        success: bool,
    ) -> None:
        """Update provider metrics."""
        if provider_name not in self.metrics:
            self.metrics[provider_name] = ProviderMetrics()

        metrics = self.metrics[provider_name]
        metrics.total_requests += 1
        metrics.last_request_time = time.time()

        if success:
            metrics.successful_requests += 1
            metrics.total_latency_ms += latency_ms
            metrics.average_latency_ms = (
                metrics.total_latency_ms / metrics.successful_requests
            )
        else:
            metrics.failed_requests += 1

        metrics.uptime_percentage = (
            metrics.successful_requests / metrics.total_requests * 100
        )

    async def _check_all_providers(self) -> None:
        """Check health of all providers."""
        for name, provider in self.providers.items():
            try:
                await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                provider.status = ProviderStatus.UNAVAILABLE

    async def _health_monitor(self) -> None:
        """Background task for periodic health monitoring."""
        while True:
            try:
                await asyncio.sleep(self._health_check_interval)
                await self._check_all_providers()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")


# Factory function for easy initialization
async def create_unified_interface(config: Dict[str, Any]) -> UnifiedModelInterface:
    """Create and initialize a UnifiedModelInterface from configuration."""
    interface = UnifiedModelInterface()
    await interface.initialize(config)
    return interface
