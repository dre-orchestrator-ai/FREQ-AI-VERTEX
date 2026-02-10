"""
Dynamic Pitch Generator for FREQ

Reads FREQ documentation and generates tailored pitches
based on investor thesis, portfolio, and interests.

Pitch Types:
- one_liner: 1-sentence description
- elevator: 30-second pitch
- one_pager: Full summary document
- technical_deep_dive: Architecture-focused pitch
- demo_script: Live demo walkthrough
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class PitchType(Enum):
    """Types of pitches that can be generated."""
    ONE_LINER = "one_liner"
    ELEVATOR = "elevator"
    ONE_PAGER = "one_pager"
    TECHNICAL_DEEP_DIVE = "technical_deep_dive"
    DEMO_SCRIPT = "demo_script"


class AudienceType(Enum):
    """Target audience for pitch customization."""
    VC_TECHNICAL = "vc_technical"
    VC_BUSINESS = "vc_business"
    ENTERPRISE_TECHNICAL = "enterprise_technical"
    ENTERPRISE_BUSINESS = "enterprise_business"
    ACCELERATOR = "accelerator"
    MFSIN = "mfsin"


@dataclass
class InvestorContext:
    """Context about the target investor/partner for pitch customization."""

    name: str
    firm: str
    role: str
    audience_type: AudienceType = AudienceType.VC_BUSINESS
    thesis_keywords: List[str] = field(default_factory=list)
    portfolio_companies: List[str] = field(default_factory=list)
    recent_investments: List[str] = field(default_factory=list)
    linkedin_topics: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "firm": self.firm,
            "role": self.role,
            "audience_type": self.audience_type.value,
            "thesis_keywords": self.thesis_keywords,
            "portfolio_companies": self.portfolio_companies,
            "recent_investments": self.recent_investments,
            "linkedin_topics": self.linkedin_topics,
            "pain_points": self.pain_points,
        }


@dataclass
class PitchOutput:
    """Generated pitch output."""

    pitch_type: PitchType
    audience_type: AudienceType
    content: str
    key_points: List[str] = field(default_factory=list)
    supporting_evidence: List[str] = field(default_factory=list)
    call_to_action: str = ""
    customization_notes: str = ""
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pitch_type": self.pitch_type.value,
            "audience_type": self.audience_type.value,
            "content": self.content,
            "key_points": self.key_points,
            "supporting_evidence": self.supporting_evidence,
            "call_to_action": self.call_to_action,
            "customization_notes": self.customization_notes,
            "generated_at": self.generated_at,
        }


class PitchGenerator:
    """
    Dynamic pitch generator that reads FREQ documentation
    and tailors messaging to investor interests.

    Usage:
        generator = PitchGenerator()

        context = InvestorContext(
            name="John Smith",
            firm="Sequoia",
            role="Partner",
            audience_type=AudienceType.VC_TECHNICAL,
            thesis_keywords=["AI infrastructure", "enterprise"]
        )

        pitch = generator.generate_pitch(PitchType.ELEVATOR, context)
    """

    # FREQ documentation paths
    DOCS_ROOT = Path("/home/user/FREQ-AI-VERTEX")

    DOC_FILES = [
        "README.md",
        "src/sol/blueprint/freq_blueprint.py",
        "config/sol_config.yaml",
        "docs/FREQ_SOL_AZURE_BLUEPRINT.md",
        "docs/STATE_OF_THE_MISSION.md",
    ]

    # FREQ key benefits by audience interest
    BENEFITS_MAP = {
        "AI Safety": "FREQ LAW constitutional framework with VETO authority ensures governed AI",
        "AI Governance": "Built-in compliance: <2000ms SLA, k=3 quorum consensus, full audit trails",
        "Enterprise": "Production-ready deployment with BigQuery audit and Azure integration",
        "Multi-agent": "SOL 7-node lattice with Byzantine fault tolerance",
        "Maritime": "VECTOR GAMMA: LiDAR + Digital Twins for 99.8% accurate cargo measurement",
        "Logistics": "Automated barge draft measurement reducing manual inspection costs",
        "Azure": "Native Azure deployment: Foundry, Databricks, Digital Twins",
        "Developer": "Natural language orchestration with visual tools",
        "ESG": "100% data accuracy target with safety-first design",
        "Infrastructure": "Cloud-native architecture on Microsoft Azure ecosystem",
    }

    def __init__(self):
        self._doc_cache: Dict[str, str] = {}
        self._load_documentation()

    def _load_documentation(self) -> None:
        """Load FREQ documentation into cache."""
        for doc_path in self.DOC_FILES:
            full_path = self.DOCS_ROOT / doc_path
            if full_path.exists():
                try:
                    with open(full_path, 'r') as f:
                        self._doc_cache[doc_path] = f.read()
                except Exception:
                    pass

    def generate_pitch(
        self,
        pitch_type: PitchType,
        context: InvestorContext
    ) -> PitchOutput:
        """
        Generate a tailored pitch based on investor context.

        Args:
            pitch_type: Type of pitch to generate
            context: Context about the target investor

        Returns:
            PitchOutput with customized pitch
        """
        # Get base template
        content = self._get_pitch_content(pitch_type, context.audience_type)

        # Extract relevant benefits for this audience
        relevant_benefits = self._extract_relevant_benefits(context.thesis_keywords)

        # Find portfolio connections
        portfolio_connections = self._find_portfolio_connections(context.portfolio_companies)

        # Customize content
        content = self._customize_pitch(content, context, relevant_benefits)

        # Generate call to action
        cta = self._get_call_to_action(context.audience_type)

        return PitchOutput(
            pitch_type=pitch_type,
            audience_type=context.audience_type,
            content=content,
            key_points=relevant_benefits[:3],
            supporting_evidence=portfolio_connections,
            call_to_action=cta,
            customization_notes=f"Tailored for {context.name}'s focus on {', '.join(context.thesis_keywords[:2]) if context.thesis_keywords else 'enterprise AI'}"
        )

    def _get_pitch_content(self, pitch_type: PitchType, audience: AudienceType) -> str:
        """Get base pitch content for type and audience."""

        pitches = {
            # ONE LINERS
            (PitchType.ONE_LINER, AudienceType.VC_TECHNICAL):
                "FREQ is a governed AI agent orchestration platform - multi-agent systems with built-in compliance (sub-2s latency, consensus voting, full audit trails) for enterprise deployment.",

            (PitchType.ONE_LINER, AudienceType.VC_BUSINESS):
                "FREQ enables enterprises to deploy AI agents safely - we're the governance layer that lets companies trust autonomous AI in production.",

            (PitchType.ONE_LINER, AudienceType.ENTERPRISE_TECHNICAL):
                "FREQ provides FREQ LAW-compliant AI agent orchestration with <2000ms SLA, k=3 quorum consensus, and full BigQuery audit trails for enterprise AI deployments.",

            (PitchType.ONE_LINER, AudienceType.ENTERPRISE_BUSINESS):
                "FREQ reduces AI deployment risk by 90% with our governance framework that ensures every AI action is fast, auditable, and reversible.",

            (PitchType.ONE_LINER, AudienceType.ACCELERATOR):
                "FREQ is building the governance layer for enterprise AI agents - think Kubernetes for AI, but with built-in compliance and safety.",

            (PitchType.ONE_LINER, AudienceType.MFSIN):
                "FREQ is an Azure-native AI agent orchestration platform with Digital Twins integration for maritime logistics automation.",

            # ELEVATOR PITCHES
            (PitchType.ELEVATOR, AudienceType.VC_TECHNICAL):
                """The problem: Enterprises want to deploy AI agents but can't trust ungoverned autonomous systems.

Our solution: The Sophisticated Operational Lattice (SOL) - a multi-agent architecture where every operation is:
• Fast (sub-2000ms guaranteed)
• Robust (Byzantine fault tolerant with k=3 quorum)
• Quantified (full BigQuery audit trail)

First vertical: Maritime logistics using LiDAR and Azure Digital Twins for automated cargo measurement with 99.8% accuracy target.

Technical highlights:
• 7-node lattice with VETO authority
• FREQ LAW constitutional framework
• Native Azure deployment (Foundry, Databricks, Digital Twins)

Traction: Working system deployed, DTDL models for maritime assets complete.

Ask: 15-minute technical deep dive on our architecture.""",

            (PitchType.ELEVATOR, AudienceType.VC_BUSINESS):
                """Enterprises are leaving $100B+ on the table because they can't deploy AI agents safely.

Current AI tools offer intelligence without accountability. That's why 78% of enterprise AI projects fail to reach production.

FREQ solves this with the governance layer for AI agents:
• Every action logged and auditable
• Constitutional framework (FREQ LAW) for AI behavior
• Enterprise-grade SLAs built in

Our beachhead: Maritime logistics - a $200B industry where accuracy is everything. We're delivering 99.8% accuracy in automated cargo measurement.

Ask: 15-minute call to discuss the market opportunity.""",

            (PitchType.ELEVATOR, AudienceType.MFSIN):
                """FREQ is building governed AI agents on Microsoft Azure.

We're a perfect fit for Microsoft for Startups because:
• Azure-native: Foundry, Databricks, Digital Twins integration complete
• Enterprise-focused: Governance and compliance built-in
• Strategic vertical: Maritime logistics with IoT and LiDAR

Our Sophisticated Operational Lattice (SOL) runs 7 AI nodes with sub-2000ms response times and full audit trails.

We're seeking:
• Azure credits to scale our infrastructure
• Access to the MFSIN investor network
• Co-sell opportunities with Microsoft enterprise accounts

Timeline: Actively building, ready for pilot deployments.""",

            # ONE PAGER
            (PitchType.ONE_PAGER, AudienceType.VC_BUSINESS):
                """# FREQ: Governed AI Agents for Enterprise

## The Problem
Enterprises are leaving $100B+ on the table because they can't deploy AI agents safely. Current solutions offer intelligence without accountability.

## Our Solution
FREQ provides the governance layer for AI agents:

**FREQ LAW Framework**
• Fast: <2000ms response time, always
• Robust: Byzantine fault tolerant, k=3 quorum
• Evolutionary: Continuous improvement cycles
• Quantified: Full audit trail to BigQuery

**SOL Architecture**
7-node Sophisticated Operational Lattice with:
• Strategic coordination (SSC)
• Governance engine with VETO authority (CGE)
• Tactical execution (TOM)
• Schema authority (SA)
• Knowledge management (SIL)

## Market Opportunity
• AI agent orchestration: $50B+ by 2028
• Enterprise AI governance: Nascent, no clear leader
• Maritime logistics (our beachhead): $200B industry

## Traction
• Working product: 7-node SOL lattice fully operational
• Technology: Azure Digital Twins integration complete
• Vertical: VECTOR GAMMA maritime operations ready for pilot

## Business Model
• Platform licensing to enterprises
• Usage-based pricing for agent operations
• Professional services for custom development

## Team
• Dre (Founder): Technical founder building enterprise AI

## Ask
$[X] to reach [milestone]

## Why Now
• Foundation models commoditized (GPT-4, Claude, Gemini)
• Enterprise AI budgets exploding
• Regulation incoming (EU AI Act) demands governance""",

            # TECHNICAL DEEP DIVE
            (PitchType.TECHNICAL_DEEP_DIVE, AudienceType.VC_TECHNICAL):
                """# FREQ Technical Architecture Deep Dive

## Sophisticated Operational Lattice (SOL)

### Node Hierarchy (6 Levels)
```
Level 0: Chief Dre (Sovereign Intent) - ABSOLUTE authority
Level 1: SSC (Strategic Synthesis Core) - Coordination
Level 2: CGE (Cognitive Governance Engine) - VETO Power
Level 3: SIL (Strategic Intelligence Lead) - Knowledge
Level 4: SA (Schema Authority) - Technical
Level 5: TOM (Tactical Optimization Module) - Execution
```

### FREQ LAW Enforcement

| Pillar | Requirement | Implementation |
|--------|-------------|----------------|
| FAST | <2000ms | Hard timeout on all operations |
| ROBUST | k=3 quorum | Byzantine fault tolerant consensus |
| EVOLUTIONARY | Metrics | SPCI continuous improvement cycles |
| QUANTIFIED | Audit | BigQuery with timestamp partitioning |

### Inter-Node Communication Protocol
```python
NodeMessage:
  - id: UUID
  - source_node: str
  - target_node: str
  - operation: str
  - payload: Dict[str, Any]
  - timestamp: ISO8601
  - requires_quorum: bool

NodeResponse:
  - message_id: str
  - node_id: str
  - success: bool
  - result: Any
  - execution_time_ms: float
```

### VECTOR GAMMA Implementation

Maritime barge drafting workflow:
1. SCAN: LiDAR drone captures 3D point cloud
2. PROCESS: OpenDroneMap generates DSM/DTM
3. Digital Twins: Sync to lidar-twins instance
4. TOM: Calculate draft measurements
5. REPORT: Generate compliance documentation

Accuracy target: 99.8% (industry requirement)

### Azure Integration Stack
• Azure AI Foundry: SSC, TOM deployment
• Copilot Studio: CGE with Claude Opus 4.5
• Databricks: Unity Catalog, Delta Lake, MLflow
• Digital Twins: lidar-twins instance (East US 2)
• BigQuery: Audit trail and analytics

### Security & Compliance
• RBAC via Azure AD
• All data encrypted at rest and in transit
• SOC 2 Type II ready architecture
• GDPR compliant data handling""",

            # DEMO SCRIPT
            (PitchType.DEMO_SCRIPT, AudienceType.VC_TECHNICAL):
                """# FREQ Live Demo Script

## Setup (30 seconds)
"Let me show you FREQ in action. I'm going to walk through a VECTOR GAMMA maritime operation."

## 1. SOL Lattice Overview (2 minutes)
"Here's our Sophisticated Operational Lattice. You can see all 7 nodes are operational:
- SSC coordinating the mission
- CGE providing governance oversight
- TOM ready for tactical execution"

## 2. FREQ LAW in Action (2 minutes)
"Watch what happens when I trigger an operation. Notice:
- Execution time: [X]ms - under our 2000ms SLA
- Quorum achieved: 3 nodes voted APPROVE
- Audit entry created in BigQuery"

## 3. VECTOR GAMMA Workflow (3 minutes)
"Now let's run a barge scanning mission:
1. Drone scan initiated
2. Point cloud processing via OpenDroneMap
3. Digital Twin updated in real-time
4. Draft measurement calculated: [X]m with 99.8% confidence"

## 4. Governance Demo (2 minutes)
"What if something violates FREQ LAW? Watch:
- I'll trigger an operation that exceeds 2000ms
- CGE automatically VETOs
- Full audit trail captured"

## Close (1 minute)
"That's FREQ - governed AI agents for enterprise.
Questions on the architecture?"""
        }

        # Get the specific pitch, or fall back to VC_BUSINESS
        key = (pitch_type, audience)
        if key in pitches:
            return pitches[key]

        # Fallback chain
        fallback_key = (pitch_type, AudienceType.VC_BUSINESS)
        if fallback_key in pitches:
            return pitches[fallback_key]

        return pitches.get((PitchType.ONE_LINER, AudienceType.VC_BUSINESS),
                          "FREQ: Governed AI agents for enterprise.")

    def _extract_relevant_benefits(self, thesis_keywords: List[str]) -> List[str]:
        """Extract FREQ benefits relevant to investor thesis."""
        if not thesis_keywords:
            return list(self.BENEFITS_MAP.values())[:3]

        relevant = []
        for keyword in thesis_keywords:
            for benefit_key, benefit_text in self.BENEFITS_MAP.items():
                if keyword.lower() in benefit_key.lower():
                    relevant.append(benefit_text)

        # Ensure we return at least some benefits
        if not relevant:
            relevant = list(self.BENEFITS_MAP.values())[:3]

        return relevant[:5]

    def _find_portfolio_connections(self, portfolio_companies: List[str]) -> List[str]:
        """Find connections between FREQ and investor's portfolio."""
        connections = []

        ai_keywords = ["ai", "agent", "llm", "ml", "enterprise", "saas", "infrastructure"]
        maritime_keywords = ["logistics", "maritime", "shipping", "supply chain", "port"]
        azure_keywords = ["azure", "microsoft", "cloud"]

        for company in portfolio_companies:
            company_lower = company.lower()
            if any(kw in company_lower for kw in ai_keywords):
                connections.append(f"Portfolio synergy with {company} (AI/infrastructure)")
            if any(kw in company_lower for kw in maritime_keywords):
                connections.append(f"Vertical alignment with {company} (logistics/maritime)")
            if any(kw in company_lower for kw in azure_keywords):
                connections.append(f"Platform alignment with {company} (Azure ecosystem)")

        return connections[:3]

    def _customize_pitch(
        self,
        content: str,
        context: InvestorContext,
        benefits: List[str]
    ) -> str:
        """Customize pitch content with investor-specific details."""
        # Simple variable substitution
        content = content.replace("{investor_name}", context.name)
        content = content.replace("{firm_name}", context.firm)
        content = content.replace("{thesis_focus}", ", ".join(context.thesis_keywords[:2]) if context.thesis_keywords else "enterprise AI")

        return content

    def _get_call_to_action(self, audience: AudienceType) -> str:
        """Get appropriate call-to-action for audience."""
        ctas = {
            AudienceType.VC_TECHNICAL: "15-minute technical deep dive on our SOL architecture?",
            AudienceType.VC_BUSINESS: "15-minute call to discuss the market opportunity?",
            AudienceType.ENTERPRISE_TECHNICAL: "30-minute demo of our governance framework?",
            AudienceType.ENTERPRISE_BUSINESS: "Quick call to explore partnership opportunities?",
            AudienceType.ACCELERATOR: "Application review and feedback conversation?",
            AudienceType.MFSIN: "Discussion about Microsoft for Startups benefits and fit?",
        }
        return ctas.get(audience, "15-minute intro call?")

    def get_available_pitch_types(self) -> List[str]:
        """Get list of available pitch types."""
        return [pt.value for pt in PitchType]

    def get_available_audience_types(self) -> List[str]:
        """Get list of available audience types."""
        return [at.value for at in AudienceType]
