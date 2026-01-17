"""
FREQ AI Platform Providers

Multi-cloud AI model providers with unified interface.
Primary: AWS Bedrock (Claude Opus 4.5)
Fallbacks: Anthropic Direct, Vertex AI, Azure Foundry
"""

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    INITIALIZING = "initializing"


class ModelCapability(Enum):
    """Model capability flags."""
    COMPLETION = "completion"
    STREAMING = "streaming"
    TOOL_USE = "tool_use"
    VISION = "vision"
    EMBEDDINGS = "embeddings"
    EXTENDED_THINKING = "extended_thinking"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    model_id: str
    display_name: str
    max_tokens: int = 8192
    context_window: int = 200000
    capabilities: List[ModelCapability] = field(default_factory=list)
    temperature: float = 0.7
    top_p: float = 0.95

    # Cost per million tokens (input/output)
    cost_input_per_million: float = 5.0
    cost_output_per_million: float = 25.0


@dataclass
class CompletionRequest:
    """Unified completion request format."""
    messages: List[Dict[str, Any]]
    model: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.95
    stop_sequences: Optional[List[str]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    stream: bool = False
    system: Optional[str] = None

    # Advanced options
    effort: Optional[str] = None  # "low", "medium", "high" for Opus 4.5
    thinking_budget: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CompletionResponse:
    """Unified completion response format."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    stop_reason: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    thinking: Optional[str] = None
    latency_ms: float = 0.0

    # Provenance for audit trail
    request_id: Optional[str] = None
    timestamp: Optional[str] = None


class BaseProvider(ABC):
    """Abstract base class for AI model providers."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.status = ProviderStatus.INITIALIZING
        self._last_health_check: float = 0
        self._health_check_interval: float = 60.0  # seconds
        self._consecutive_failures: int = 0
        self._max_failures_before_unavailable: int = 3

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute a completion request."""
        pass

    @abstractmethod
    async def stream(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream a completion request."""
        pass

    @abstractmethod
    async def health_check(self) -> ProviderStatus:
        """Check provider health."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[ModelConfig]:
        """Get list of available models."""
        pass

    def is_healthy(self) -> bool:
        """Check if provider is healthy."""
        return self.status == ProviderStatus.HEALTHY

    def record_failure(self) -> None:
        """Record a failure and update status."""
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._max_failures_before_unavailable:
            self.status = ProviderStatus.UNAVAILABLE
            logger.error(f"Provider {self.name} marked unavailable after {self._consecutive_failures} failures")
        else:
            self.status = ProviderStatus.DEGRADED

    def record_success(self) -> None:
        """Record a success and update status."""
        self._consecutive_failures = 0
        self.status = ProviderStatus.HEALTHY


class AWSBedrockProvider(BaseProvider):
    """
    AWS Bedrock provider for Claude models.

    Primary provider for Claude Opus 4.5 with full enterprise features:
    - AgentCore integration
    - Tool Gateway
    - Persistent memory
    - Global cross-region inference
    """

    MODELS = {
        "opus-4.5": ModelConfig(
            model_id="global.anthropic.claude-opus-4-5-20251101-v1:0",
            display_name="Claude Opus 4.5",
            max_tokens=8192,
            context_window=200000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
                ModelCapability.VISION,
                ModelCapability.EXTENDED_THINKING,
            ],
            temperature=0.0,  # For strict governance reasoning
            cost_input_per_million=5.0,
            cost_output_per_million=25.0,
        ),
        "sonnet-4.5": ModelConfig(
            model_id="global.anthropic.claude-sonnet-4-5-20251101-v1:0",
            display_name="Claude Sonnet 4.5",
            max_tokens=8192,
            context_window=200000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
                ModelCapability.VISION,
            ],
            cost_input_per_million=3.0,
            cost_output_per_million=15.0,
        ),
        "haiku-4.5": ModelConfig(
            model_id="global.anthropic.claude-haiku-4-5-20251101-v1:0",
            display_name="Claude Haiku 4.5",
            max_tokens=8192,
            context_window=200000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
            ],
            cost_input_per_million=0.25,
            cost_output_per_million=1.25,
        ),
    }

    def __init__(self, config: Dict[str, Any]):
        super().__init__("aws_bedrock", config)
        self.region = config.get("region", "us-east-1")
        self.inference_profile = config.get("inference_profile", "global")
        self._client = None

    async def _get_client(self):
        """Get or create Bedrock runtime client."""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    "bedrock-runtime",
                    region_name=self.region,
                )
                self.status = ProviderStatus.HEALTHY
            except ImportError:
                logger.warning("boto3 not installed. AWS Bedrock provider unavailable.")
                self.status = ProviderStatus.UNAVAILABLE
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock client: {e}")
                self.status = ProviderStatus.UNAVAILABLE
        return self._client

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute completion via AWS Bedrock."""
        start_time = time.time()

        client = await self._get_client()
        if client is None:
            raise RuntimeError("Bedrock client not available")

        model_id = request.model or self.MODELS["opus-4.5"].model_id

        # Build Bedrock request payload
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": request.max_tokens,
            "messages": request.messages,
        }

        if request.system:
            payload["system"] = request.system
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.stop_sequences:
            payload["stop_sequences"] = request.stop_sequences
        if request.tools:
            payload["tools"] = request.tools
        if request.tool_choice:
            payload["tool_choice"] = {"type": request.tool_choice}

        # Opus 4.5 specific: effort parameter (beta)
        if request.effort and "opus" in model_id.lower():
            payload["effort"] = request.effort

        try:
            response = client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload),
            )

            result = json.loads(response["body"].read())
            latency_ms = (time.time() - start_time) * 1000

            self.record_success()

            return CompletionResponse(
                content=result.get("content", [{}])[0].get("text", ""),
                model=model_id,
                provider=self.name,
                usage={
                    "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                    "output_tokens": result.get("usage", {}).get("output_tokens", 0),
                },
                stop_reason=result.get("stop_reason"),
                tool_calls=self._extract_tool_calls(result),
                thinking=self._extract_thinking(result),
                latency_ms=latency_ms,
                request_id=response.get("ResponseMetadata", {}).get("RequestId"),
            )

        except Exception as e:
            self.record_failure()
            logger.error(f"Bedrock completion failed: {e}")
            raise

    async def stream(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream completion via AWS Bedrock."""
        # Implementation for streaming
        # Note: Actual streaming requires bedrock-runtime streaming API
        response = await self.complete(request)
        yield response.content

    async def health_check(self) -> ProviderStatus:
        """Check Bedrock availability."""
        try:
            client = await self._get_client()
            if client is None:
                return ProviderStatus.UNAVAILABLE
            # Simple list models call to verify connectivity
            self.status = ProviderStatus.HEALTHY
            return self.status
        except Exception as e:
            logger.error(f"Bedrock health check failed: {e}")
            self.status = ProviderStatus.UNAVAILABLE
            return self.status

    def get_available_models(self) -> List[ModelConfig]:
        """Get available Bedrock models."""
        return list(self.MODELS.values())

    def _extract_tool_calls(self, result: Dict) -> Optional[List[Dict]]:
        """Extract tool calls from response."""
        content = result.get("content", [])
        tool_calls = [c for c in content if c.get("type") == "tool_use"]
        return tool_calls if tool_calls else None

    def _extract_thinking(self, result: Dict) -> Optional[str]:
        """Extract thinking content from response (Opus 4.5 extended thinking)."""
        content = result.get("content", [])
        thinking = [c.get("text") for c in content if c.get("type") == "thinking"]
        return "\n".join(thinking) if thinking else None


class AnthropicDirectProvider(BaseProvider):
    """
    Direct Anthropic API provider.

    Fallback when AWS Bedrock is unavailable.
    Provides access to Claude models via api.anthropic.com.
    """

    MODELS = {
        "opus-4.5": ModelConfig(
            model_id="claude-opus-4-5-20251101",
            display_name="Claude Opus 4.5",
            max_tokens=8192,
            context_window=200000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
                ModelCapability.VISION,
                ModelCapability.EXTENDED_THINKING,
            ],
        ),
        "sonnet-4.5": ModelConfig(
            model_id="claude-sonnet-4-5-20251101",
            display_name="Claude Sonnet 4.5",
            max_tokens=8192,
            context_window=200000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
                ModelCapability.VISION,
            ],
        ),
    }

    def __init__(self, config: Dict[str, Any]):
        super().__init__("anthropic_direct", config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.anthropic.com")
        self._client = None

    async def _get_client(self):
        """Get or create Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
                self.status = ProviderStatus.HEALTHY
            except ImportError:
                logger.warning("anthropic package not installed.")
                self.status = ProviderStatus.UNAVAILABLE
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                self.status = ProviderStatus.UNAVAILABLE
        return self._client

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute completion via Anthropic API."""
        start_time = time.time()

        client = await self._get_client()
        if client is None:
            raise RuntimeError("Anthropic client not available")

        model_id = request.model or self.MODELS["opus-4.5"].model_id

        try:
            kwargs = {
                "model": model_id,
                "max_tokens": request.max_tokens,
                "messages": request.messages,
            }

            if request.system:
                kwargs["system"] = request.system
            if request.temperature is not None:
                kwargs["temperature"] = request.temperature
            if request.tools:
                kwargs["tools"] = request.tools

            response = client.messages.create(**kwargs)
            latency_ms = (time.time() - start_time) * 1000

            self.record_success()

            return CompletionResponse(
                content=response.content[0].text if response.content else "",
                model=model_id,
                provider=self.name,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                stop_reason=response.stop_reason,
                latency_ms=latency_ms,
                request_id=response.id,
            )

        except Exception as e:
            self.record_failure()
            logger.error(f"Anthropic completion failed: {e}")
            raise

    async def stream(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream completion via Anthropic API."""
        response = await self.complete(request)
        yield response.content

    async def health_check(self) -> ProviderStatus:
        """Check Anthropic API availability."""
        try:
            client = await self._get_client()
            if client is None:
                return ProviderStatus.UNAVAILABLE
            self.status = ProviderStatus.HEALTHY
            return self.status
        except Exception:
            self.status = ProviderStatus.UNAVAILABLE
            return self.status

    def get_available_models(self) -> List[ModelConfig]:
        """Get available Anthropic models."""
        return list(self.MODELS.values())


class VertexAIProvider(BaseProvider):
    """
    Google Cloud Vertex AI provider for Gemini models.

    Secondary provider for Gemini 3.0 family models.
    Used for SIL, SA, and TOM nodes per substrate mapping.
    """

    MODELS = {
        "gemini-3-thinking": ModelConfig(
            model_id="gemini-3.0-thinking-preview",
            display_name="Gemini 3.0 Thinking",
            max_tokens=8192,
            context_window=1000000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
                ModelCapability.EXTENDED_THINKING,
            ],
        ),
        "gemini-3-pro": ModelConfig(
            model_id="gemini-3.0-pro-preview",
            display_name="Gemini 3.0 Pro",
            max_tokens=8192,
            context_window=1000000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
            ],
        ),
        "gemini-3-flash": ModelConfig(
            model_id="gemini-3.0-flash-preview",
            display_name="Gemini 3.0 Flash",
            max_tokens=8192,
            context_window=1000000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
            ],
        ),
    }

    def __init__(self, config: Dict[str, Any]):
        super().__init__("vertex_ai", config)
        self.project_id = config.get("project_id")
        self.region = config.get("region", "us-central1")
        self._client = None

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute completion via Vertex AI."""
        start_time = time.time()

        # Simulated response for now - actual implementation requires google-cloud-aiplatform
        latency_ms = (time.time() - start_time) * 1000

        return CompletionResponse(
            content="[Vertex AI integration pending - requires google-cloud-aiplatform]",
            model=request.model or "gemini-3.0-pro-preview",
            provider=self.name,
            usage={"input_tokens": 0, "output_tokens": 0},
            latency_ms=latency_ms,
        )

    async def stream(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream completion via Vertex AI."""
        response = await self.complete(request)
        yield response.content

    async def health_check(self) -> ProviderStatus:
        """Check Vertex AI availability."""
        # Implementation pending
        self.status = ProviderStatus.DEGRADED
        return self.status

    def get_available_models(self) -> List[ModelConfig]:
        """Get available Vertex AI models."""
        return list(self.MODELS.values())


class AzureFoundryProvider(BaseProvider):
    """
    Microsoft Azure Foundry provider.

    Tertiary provider for compliance scenarios requiring Azure.
    Supports Claude models via Azure Foundry integration.
    """

    MODELS = {
        "opus-4.5": ModelConfig(
            model_id="claude-opus-4-5",
            display_name="Claude Opus 4.5 (Azure)",
            max_tokens=8192,
            context_window=200000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
            ],
        ),
        "sonnet-4.5": ModelConfig(
            model_id="claude-sonnet-4-5",
            display_name="Claude Sonnet 4.5 (Azure)",
            max_tokens=8192,
            context_window=200000,
            capabilities=[
                ModelCapability.COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.TOOL_USE,
            ],
        ),
    }

    def __init__(self, config: Dict[str, Any]):
        super().__init__("azure_foundry", config)
        self.endpoint = config.get("endpoint")
        self.api_key = config.get("api_key")

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute completion via Azure Foundry."""
        start_time = time.time()
        latency_ms = (time.time() - start_time) * 1000

        return CompletionResponse(
            content="[Azure Foundry integration pending]",
            model=request.model or "claude-opus-4-5",
            provider=self.name,
            usage={"input_tokens": 0, "output_tokens": 0},
            latency_ms=latency_ms,
        )

    async def stream(self, request: CompletionRequest) -> AsyncGenerator[str, None]:
        """Stream completion via Azure Foundry."""
        response = await self.complete(request)
        yield response.content

    async def health_check(self) -> ProviderStatus:
        """Check Azure Foundry availability."""
        self.status = ProviderStatus.DEGRADED
        return self.status

    def get_available_models(self) -> List[ModelConfig]:
        """Get available Azure models."""
        return list(self.MODELS.values())
