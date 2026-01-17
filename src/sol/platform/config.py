"""
FREQ AI Platform Configuration

Defines configuration structures for multi-platform AI provider deployment.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderPriority(Enum):
    """Provider priority levels."""
    PRIMARY = 1
    SECONDARY = 2
    TERTIARY = 3
    FALLBACK = 4


@dataclass
class ProviderConfig:
    """Configuration for a single provider."""
    name: str
    enabled: bool = True
    priority: ProviderPriority = ProviderPriority.FALLBACK

    # Connection settings
    region: Optional[str] = None
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    project_id: Optional[str] = None

    # Performance settings
    timeout_seconds: int = 120
    max_retries: int = 3
    retry_delay_base: float = 1.0

    # Health check settings
    health_check_interval: float = 60.0
    max_consecutive_failures: int = 3


@dataclass
class PlatformConfig:
    """Complete platform configuration."""

    # Provider configurations
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)

    # Failover settings
    enable_failover: bool = True
    failover_timeout_ms: int = 5000

    # Audit settings
    enable_audit_logging: bool = True
    audit_retention_days: int = 90

    # Performance targets (FREQ LAW compliance)
    target_latency_ms: int = 2000
    trust_score_threshold: float = 0.95

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlatformConfig":
        """Create PlatformConfig from dictionary."""
        providers = {}
        for name, pconfig in data.get("providers", {}).items():
            providers[name] = ProviderConfig(
                name=name,
                enabled=pconfig.get("enabled", True),
                priority=ProviderPriority(pconfig.get("priority", 4)),
                region=pconfig.get("region"),
                endpoint=pconfig.get("endpoint"),
                api_key=pconfig.get("api_key"),
                project_id=pconfig.get("project_id"),
                timeout_seconds=pconfig.get("timeout_seconds", 120),
                max_retries=pconfig.get("max_retries", 3),
            )

        return cls(
            providers=providers,
            enable_failover=data.get("enable_failover", True),
            failover_timeout_ms=data.get("failover_timeout_ms", 5000),
            enable_audit_logging=data.get("enable_audit_logging", True),
            target_latency_ms=data.get("target_latency_ms", 2000),
            trust_score_threshold=data.get("trust_score_threshold", 0.95),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "providers": {
                name: {
                    "enabled": p.enabled,
                    "priority": p.priority.value,
                    "region": p.region,
                    "endpoint": p.endpoint,
                    "timeout_seconds": p.timeout_seconds,
                    "max_retries": p.max_retries,
                }
                for name, p in self.providers.items()
            },
            "enable_failover": self.enable_failover,
            "failover_timeout_ms": self.failover_timeout_ms,
            "enable_audit_logging": self.enable_audit_logging,
            "target_latency_ms": self.target_latency_ms,
            "trust_score_threshold": self.trust_score_threshold,
        }


# Default configuration with recommended settings
DEFAULT_PLATFORM_CONFIG = PlatformConfig(
    providers={
        "aws_bedrock": ProviderConfig(
            name="aws_bedrock",
            enabled=True,
            priority=ProviderPriority.PRIMARY,
            region="us-east-1",
            timeout_seconds=120,
            max_retries=3,
        ),
        "anthropic_direct": ProviderConfig(
            name="anthropic_direct",
            enabled=True,
            priority=ProviderPriority.SECONDARY,
            endpoint="https://api.anthropic.com",
            timeout_seconds=120,
            max_retries=3,
        ),
        "vertex_ai": ProviderConfig(
            name="vertex_ai",
            enabled=True,
            priority=ProviderPriority.TERTIARY,
            region="us-central1",
            timeout_seconds=120,
            max_retries=3,
        ),
        "azure_foundry": ProviderConfig(
            name="azure_foundry",
            enabled=False,  # Disabled by default due to restrictions
            priority=ProviderPriority.FALLBACK,
            timeout_seconds=120,
            max_retries=3,
        ),
    },
    enable_failover=True,
    failover_timeout_ms=5000,
    target_latency_ms=2000,
    trust_score_threshold=0.95,
)


def get_provider_for_level(level: int, config: PlatformConfig) -> Optional[str]:
    """Get recommended provider for a lattice level."""
    # Level-to-provider mapping based on blueprint
    level_mapping = {
        1: "aws_bedrock",   # L1 SSC - needs Opus 4.5
        2: "aws_bedrock",   # L2 CGE - needs Opus 4.5 for strict governance
        3: "vertex_ai",     # L3 SIL - Gemini Flash for speed
        4: "vertex_ai",     # L4 SA  - Gemini Pro for design
        5: "vertex_ai",     # L5 TOM - Gemini Flash for runtime
    }

    primary = level_mapping.get(level)
    if primary and primary in config.providers:
        provider_config = config.providers[primary]
        if provider_config.enabled:
            return primary

    # Fallback to any available primary provider
    for name, p in sorted(
        config.providers.items(),
        key=lambda x: x[1].priority.value
    ):
        if p.enabled:
            return name

    return None
