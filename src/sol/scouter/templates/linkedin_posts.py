"""
LinkedIn Post Templates for FREQ Founder

Startup founder tone - technical credibility with approachable energy.
Focus: AI agent orchestration, enterprise infrastructure, maritime logistics.
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class PostCategory(Enum):
    """Categories of LinkedIn posts."""
    TECHNICAL_INSIGHT = "technical_insight"
    FOUNDER_JOURNEY = "founder_journey"
    INDUSTRY_COMMENTARY = "industry_commentary"
    MILESTONE_ANNOUNCEMENT = "milestone_announcement"
    THOUGHT_LEADERSHIP = "thought_leadership"
    ENGAGEMENT_HOOK = "engagement_hook"


@dataclass
class PostTemplate:
    """LinkedIn post template."""
    key: str
    category: PostCategory
    title: str
    template: str
    hashtags: List[str] = field(default_factory=list)
    best_posting_times: List[str] = field(default_factory=list)
    engagement_cta: str = ""
    variables: List[str] = field(default_factory=list)


LINKEDIN_POST_TEMPLATES: Dict[str, PostTemplate] = {

    # === TECHNICAL INSIGHT ===

    "lattice_architecture": PostTemplate(
        key="lattice_architecture",
        category=PostCategory.TECHNICAL_INSIGHT,
        title="SOL Architecture Reveal",
        template="""Building AI agents is easy.

Building AI agents that GOVERN themselves? That's the hard part.

Here's what we built at FREQ:

The Sophisticated Operational Lattice (SOL) - a multi-agent system where:
→ Every operation completes in <2000ms (FREQ LAW: Fast)
→ Every decision requires k=3 quorum consensus (FREQ LAW: Robust)
→ Every action has a BigQuery audit trail (FREQ LAW: Quantified)

Why does this matter?

Because when you're deploying AI agents in enterprise environments, you can't have rogue decisions.

{custom_insight}

The future of enterprise AI isn't just intelligent - it's governed.

What governance patterns are you seeing in AI deployments?

#AIAgents #EnterpriseAI #CloudArchitecture #AzureAI #Startups""",
        hashtags=["#AIAgents", "#EnterpriseAI", "#CloudArchitecture", "#AzureAI", "#Startups"],
        best_posting_times=["14:00", "09:00"],
        engagement_cta="What governance patterns are you seeing in AI deployments?",
        variables=["custom_insight"],
    ),

    "freq_law_explainer": PostTemplate(
        key="freq_law_explainer",
        category=PostCategory.TECHNICAL_INSIGHT,
        title="FREQ LAW Framework",
        template="""Every AI framework needs a constitution.

Ours is FREQ LAW:

F - Fast (<2000ms response time, always)
R - Robust (Byzantine fault tolerant, k=3 quorum)
E - Evolutionary (continuous improvement via SPCI cycles)
Q - Quantified (every action logged, measured, auditable)

We didn't invent these principles. We borrowed them from:
→ Distributed systems (Paxos, Raft)
→ Financial trading systems (latency requirements)
→ Aviation safety (redundancy requirements)

Then we encoded them into our lattice.

Result? An AI orchestration system that enterprises can actually trust.

{custom_insight}

Building AI for enterprises isn't about moving fast and breaking things.

It's about moving fast AND keeping things working.

#AIGovernance #EnterpriseArchitecture #TrustInAI #AIOps #BuildInPublic""",
        hashtags=["#AIGovernance", "#EnterpriseArchitecture", "#TrustInAI", "#AIOps"],
        best_posting_times=["11:00", "15:00"],
        engagement_cta="How do you think about governance in your AI systems?",
        variables=["custom_insight"],
    ),

    "vector_gamma_intro": PostTemplate(
        key="vector_gamma_intro",
        category=PostCategory.TECHNICAL_INSIGHT,
        title="VECTOR GAMMA Maritime",
        template="""Our first AI mission: VECTOR GAMMA

Target: Maritime barge drafting automation
Accuracy requirement: 99.8%
Industry: $200B+ logistics market

The workflow:
1. SCAN - LiDAR drone captures 3D point cloud
2. PROCESS - OpenDroneMap generates surface models
3. SYNC - Azure Digital Twins updates in real-time
4. REPORT - TOM calculates draft measurements

Why maritime first?

→ High accuracy requirements (perfect for proving governance)
→ Clear ROI (manual inspections are expensive)
→ Regulated industry (compliance is a feature, not a bug)

{custom_insight}

Sometimes the best way to prove your AI works is to pick the hardest problem first.

What vertical would you tackle with governed AI agents?

#Maritime #Logistics #DigitalTwins #LiDAR #AIAgents #AzureAI""",
        hashtags=["#Maritime", "#Logistics", "#DigitalTwins", "#LiDAR", "#AIAgents"],
        best_posting_times=["10:00", "14:00"],
        engagement_cta="What vertical would you tackle with governed AI agents?",
        variables=["custom_insight"],
    ),

    # === FOUNDER JOURNEY ===

    "bootstrap_reality": PostTemplate(
        key="bootstrap_reality",
        category=PostCategory.FOUNDER_JOURNEY,
        title="Bootstrap Reality Check",
        template="""Day {day_count} of building FREQ with $0 in funding.

Today's reality:
→ Learning Azure courses while building
→ Automating partnership outreach (meta: our AI scouts for partnerships)
→ No capital, no contracts... yet

But here's what I have:
→ A working SOL lattice with 7 operational nodes
→ Digital Twins integration for maritime ops
→ A governance framework enterprises will pay for

{personal_insight}

The bottleneck isn't ideas. It's distribution.

Every founder knows: you can build the best product in the world, but if no one knows about it, it doesn't exist.

That's why I'm here. Building in public. Sharing the journey.

Who should I be talking to?

#StartupLife #BuildInPublic #Bootstrapped #AIStartup #Founder""",
        hashtags=["#StartupLife", "#BuildInPublic", "#Bootstrapped", "#AIStartup", "#Founder"],
        best_posting_times=["08:00", "18:00"],
        engagement_cta="Who should I be talking to?",
        variables=["day_count", "personal_insight"],
    ),

    "azure_learning": PostTemplate(
        key="azure_learning",
        category=PostCategory.FOUNDER_JOURNEY,
        title="Azure Learning Journey",
        template="""Currently deep in Azure certifications while simultaneously building on Azure.

The learn-by-building approach:

Week 1: Fundamentals
→ Spun up a Digital Twins instance
→ Connected it to our SOL lattice
→ Learned: pricing models matter more than you think

Week 2: Architecture
→ Set up proper RBAC for our agent system
→ Configured monitoring and alerts
→ Learned: observability isn't optional

{current_learning}

Building without budget forces you to understand costs deeply.

Every $1 in Azure credits is an experiment in efficiency.

Any Azure architects here? Would love to compare notes on:
→ Digital Twins best practices
→ Cost optimization for AI workloads
→ Multi-agent deployment patterns

#Azure #CloudLearning #TechFounder #BuildInPublic""",
        hashtags=["#Azure", "#CloudLearning", "#TechFounder", "#BuildInPublic"],
        best_posting_times=["10:00", "16:00"],
        engagement_cta="Any Azure architects here? Would love to compare notes.",
        variables=["current_learning"],
    ),

    # === MILESTONE ANNOUNCEMENT ===

    "feature_launch": PostTemplate(
        key="feature_launch",
        category=PostCategory.MILESTONE_ANNOUNCEMENT,
        title="Feature Launch",
        template="""SHIPPED: {feature_name}

What it does:
{feature_description}

Why it matters:
{business_impact}

Technical details for the curious:
{technical_details}

Building FREQ one commit at a time.

If you're working on similar problems in {industry}, let's talk.

#Shipped #ProductUpdate #TechStartup #AIEngineering #BuildInPublic""",
        hashtags=["#Shipped", "#ProductUpdate", "#TechStartup", "#AIEngineering"],
        best_posting_times=["12:00", "09:00"],
        engagement_cta="If you're working on similar problems, let's talk.",
        variables=["feature_name", "feature_description", "business_impact", "technical_details", "industry"],
    ),

    "milestone_reached": PostTemplate(
        key="milestone_reached",
        category=PostCategory.MILESTONE_ANNOUNCEMENT,
        title="Milestone Reached",
        template="""Milestone unlocked: {milestone}

What this means:
{significance}

The journey to get here:
{journey_summary}

What's next:
{next_steps}

{personal_reflection}

Grateful for everyone who's been following this journey.

#Milestone #StartupJourney #BuildInPublic #TechStartup""",
        hashtags=["#Milestone", "#StartupJourney", "#BuildInPublic", "#TechStartup"],
        best_posting_times=["11:00", "15:00"],
        engagement_cta="",
        variables=["milestone", "significance", "journey_summary", "next_steps", "personal_reflection"],
    ),

    # === THOUGHT LEADERSHIP ===

    "ai_agents_future": PostTemplate(
        key="ai_agents_future",
        category=PostCategory.THOUGHT_LEADERSHIP,
        title="AI Agents Future",
        template="""Hot take: Most "AI agents" today are just fancy chatbots.

Here's what separates real AI agents:

1. Autonomous goal pursuit (not just responding to prompts)
2. Multi-step planning (not just single-turn inference)
3. Tool orchestration (not just API calls)
4. Self-correction (not just error messages)
5. Governance (not just guardrails)

At FREQ, we're building for #5 specifically.

Because enterprises won't deploy ungoverned agents.

{supporting_argument}

The AI agent market will bifurcate:
→ Consumer: creative, exploratory, ungoverned
→ Enterprise: precise, auditable, governed

We're betting on enterprise.

What's your take - is agent governance a feature or a requirement?

#AIAgents #EnterpriseAI #FutureOfWork #AgenticAI #TechTrends""",
        hashtags=["#AIAgents", "#EnterpriseAI", "#FutureOfWork", "#AgenticAI"],
        best_posting_times=["14:00", "11:00"],
        engagement_cta="Is agent governance a feature or a requirement?",
        variables=["supporting_argument"],
    ),

    "enterprise_ai_reality": PostTemplate(
        key="enterprise_ai_reality",
        category=PostCategory.THOUGHT_LEADERSHIP,
        title="Enterprise AI Reality",
        template="""Unpopular opinion: Enterprise AI adoption is slower than headlines suggest.

Why?

Not because the tech isn't ready.
Because trust isn't there yet.

What enterprises actually need:
→ Audit trails (who did what, when, why)
→ Predictable latency (SLAs matter)
→ Rollback capability (mistakes happen)
→ Human override (always)

What most AI tools offer:
→ "It's really smart"
→ "It usually works"
→ "Trust us"

{enterprise_insight}

The gap between "impressive demo" and "production deployment" is governance.

That's what we're building at FREQ.

#EnterpriseAI #AIAdoption #B2B #TechStrategy""",
        hashtags=["#EnterpriseAI", "#AIAdoption", "#B2B", "#TechStrategy"],
        best_posting_times=["09:00", "14:00"],
        engagement_cta="What's blocking AI adoption at your company?",
        variables=["enterprise_insight"],
    ),

    # === ENGAGEMENT HOOK ===

    "quick_poll": PostTemplate(
        key="quick_poll",
        category=PostCategory.ENGAGEMENT_HOOK,
        title="Quick Poll",
        template="""Quick poll for the AI builders:

When deploying AI agents in production, what's your biggest concern?

🔴 Reliability (will it work consistently?)
🟡 Latency (will it be fast enough?)
🟢 Cost (will it scale affordably?)
🔵 Governance (can I audit and control it?)

Drop your color in the comments.

Building FREQ to solve 🔵 specifically - but curious what's top of mind for others.

#AIAgents #Poll #TechLeadership #EnterpriseAI""",
        hashtags=["#AIAgents", "#Poll", "#TechLeadership", "#EnterpriseAI"],
        best_posting_times=["12:00", "16:00"],
        engagement_cta="Drop your color in the comments.",
        variables=[],
    ),
}


def render_post(template_key: str, variables: Dict[str, Any]) -> str:
    """
    Render a post template with custom variables.

    Args:
        template_key: Key of the template to render
        variables: Dictionary of variable values

    Returns:
        Rendered post content
    """
    if template_key not in LINKEDIN_POST_TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}")

    template = LINKEDIN_POST_TEMPLATES[template_key]

    # Start with template content
    content = template.template

    # Replace variables
    for var_name, var_value in variables.items():
        placeholder = "{" + var_name + "}"
        content = content.replace(placeholder, str(var_value))

    return content


def get_templates_by_category(category: PostCategory) -> List[PostTemplate]:
    """Get all templates in a category."""
    return [t for t in LINKEDIN_POST_TEMPLATES.values() if t.category == category]


def get_template(key: str) -> PostTemplate:
    """Get a template by key."""
    if key not in LINKEDIN_POST_TEMPLATES:
        raise ValueError(f"Unknown template: {key}")
    return LINKEDIN_POST_TEMPLATES[key]
