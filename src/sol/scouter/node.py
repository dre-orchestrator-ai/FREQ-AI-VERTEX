"""
Executor Scouter Node (VECTOR DELTA)

Partnership scouting and outreach automation node for the SOL lattice.
Implements autonomous investor/partner engagement with FREQ LAW compliance.

Capabilities:
1. MFSIN Partner Scouting - Scan for Microsoft for Startups investors
2. LinkedIn Automation - Profile optimization, connections, engagement
3. Warm Intro Mapping - Relationship intelligence and intro requests
4. Targeted Communication - Industry/role-based message adaptation
5. Dynamic Pitch Generation - Tailored pitches from FREQ documentation
"""

import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid

from ..nodes.base import LatticeNode, NodeType, NodeMessage, NodeResponse


class OutreachStatus(Enum):
    """Status of an outreach campaign or sequence."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ProspectTier(Enum):
    """Investor/partner prospect prioritization tiers."""
    TIER_1 = "tier_1"  # Perfect thesis fit, warm connection available
    TIER_2 = "tier_2"  # Good fit, cold outreach required
    TIER_3 = "tier_3"  # Potential fit, needs qualification
    NURTURE = "nurture"  # Long-term relationship building


class ProspectType(Enum):
    """Type of prospect."""
    VC_TECHNICAL = "vc_technical"
    VC_BUSINESS = "vc_business"
    ENTERPRISE_TECHNICAL = "enterprise_technical"
    ENTERPRISE_BUSINESS = "enterprise_business"
    ACCELERATOR = "accelerator"
    MFSIN = "mfsin"
    ANGEL = "angel"
    STRATEGIC = "strategic"


@dataclass
class Prospect:
    """Represents a potential investor or partner."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    organization: str = ""
    role: str = ""
    prospect_type: ProspectType = ProspectType.VC_BUSINESS
    platform: str = "linkedin"
    profile_url: str = ""
    email: Optional[str] = None
    tier: ProspectTier = ProspectTier.TIER_2
    thesis_alignment: float = 0.5  # 0.0 - 1.0
    warm_intro_path: Optional[List[str]] = None
    tags: List[str] = field(default_factory=list)
    last_interaction: Optional[str] = None
    interaction_count: int = 0
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "organization": self.organization,
            "role": self.role,
            "prospect_type": self.prospect_type.value,
            "platform": self.platform,
            "profile_url": self.profile_url,
            "email": self.email,
            "tier": self.tier.value,
            "thesis_alignment": self.thesis_alignment,
            "warm_intro_path": self.warm_intro_path,
            "tags": self.tags,
            "last_interaction": self.last_interaction,
            "interaction_count": self.interaction_count,
            "notes": self.notes,
            "created_at": self.created_at,
        }


@dataclass
class OutreachCampaign:
    """Represents an outreach campaign with multiple prospects."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    status: OutreachStatus = OutreachStatus.DRAFT
    sequence_type: str = "cold_vc"
    prospects: List[str] = field(default_factory=list)  # Prospect IDs
    current_touchpoint: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metrics: Dict[str, int] = field(default_factory=lambda: {
        "sent": 0,
        "delivered": 0,
        "opened": 0,
        "replied": 0,
        "meetings_scheduled": 0,
    })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "sequence_type": self.sequence_type,
            "prospects": self.prospects,
            "current_touchpoint": self.current_touchpoint,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metrics": self.metrics,
        }


class ExecScouter(LatticeNode):
    """
    Executor Scouter Node (VECTOR DELTA)

    Handles autonomous partnership development for FREQ:
    - MFSIN and VC firm scouting
    - LinkedIn/Instagram automation
    - Warm intro relationship mapping
    - Dynamic pitch generation

    All operations comply with FREQ LAW:
    - FAST: <2000ms per operation
    - ROBUST: Graceful degradation on rate limits
    - EVOLUTIONARY: Learn from engagement metrics
    - QUANTIFIED: Full audit trail to BigQuery
    """

    # Daily rate limits (LinkedIn ToS compliance)
    DAILY_LIMITS = {
        "linkedin_connections": 10,
        "linkedin_messages": 25,
        "linkedin_comments": 30,
        "linkedin_posts": 2,
        "instagram_follows": 30,
        "instagram_dms": 10,
    }

    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self._prospects: Dict[str, Prospect] = {}
        self._campaigns: Dict[str, OutreachCampaign] = {}
        self._scheduled_posts: List[Dict[str, Any]] = []
        self._daily_usage: Dict[str, int] = {k: 0 for k in self.DAILY_LIMITS}
        self._last_reset: datetime = datetime.utcnow()
        self._interaction_log: List[Dict[str, Any]] = []

    @property
    def node_type(self) -> NodeType:
        return NodeType.EXEC_SCOUTER

    @property
    def description(self) -> str:
        return "Partnership scouting and outreach automation (VECTOR DELTA)"

    def process_message(self, message: NodeMessage) -> NodeResponse:
        """Process scouting and outreach messages."""
        start_time = time.time()

        # Reset daily limits if new day
        self._check_daily_reset()

        try:
            operation = message.operation
            payload = message.payload

            # --- Prospect Management ---
            if operation == "add_prospect":
                result = self._add_prospect(payload)
            elif operation == "update_prospect":
                result = self._update_prospect(payload)
            elif operation == "get_prospect":
                result = self._get_prospect(payload)
            elif operation == "list_prospects":
                result = self._list_prospects(payload)
            elif operation == "qualify_prospect":
                result = self._qualify_prospect(payload)
            elif operation == "remove_prospect":
                result = self._remove_prospect(payload)

            # --- Outreach Campaign Management ---
            elif operation == "create_campaign":
                result = self._create_campaign(payload)
            elif operation == "start_campaign":
                result = self._start_campaign(payload)
            elif operation == "pause_campaign":
                result = self._pause_campaign(payload)
            elif operation == "resume_campaign":
                result = self._resume_campaign(payload)
            elif operation == "get_campaign_status":
                result = self._get_campaign_status(payload)

            # --- LinkedIn Operations ---
            elif operation == "send_connection_request":
                result = self._send_connection_request(payload)
            elif operation == "send_message":
                result = self._send_message(payload)
            elif operation == "engage_post":
                result = self._engage_post(payload)
            elif operation == "schedule_post":
                result = self._schedule_post(payload)
            elif operation == "optimize_profile":
                result = self._optimize_profile(payload)

            # --- Pitch Generation ---
            elif operation == "generate_pitch":
                result = self._generate_pitch(payload)
            elif operation == "generate_intro_request":
                result = self._generate_intro_request(payload)

            # --- MFSIN Scouting ---
            elif operation == "scan_mfsin":
                result = self._scan_mfsin(payload)
            elif operation == "scan_vc_portfolio":
                result = self._scan_vc_portfolio(payload)

            # --- Relationship Mapping ---
            elif operation == "find_warm_intro_path":
                result = self._find_warm_intro_path(payload)
            elif operation == "map_network":
                result = self._map_network(payload)

            # --- Status and Metrics ---
            elif operation == "get_daily_limits":
                result = self._get_daily_limits()
            elif operation == "get_metrics":
                result = self._get_metrics()
            elif operation == "get_status":
                result = self._get_status()

            else:
                result = {"error": f"Unknown operation: {operation}"}

            execution_time = (time.time() - start_time) * 1000

            # Log interaction for audit
            self._log_interaction(operation, payload, result, execution_time)

            # FREQ LAW compliance check
            if execution_time > 2000:
                result["freq_law_warning"] = f"FAST violation: {execution_time:.1f}ms > 2000ms"

            return NodeResponse(
                message_id=message.id,
                node_id=self.node_id,
                success="error" not in result,
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

    def _check_daily_reset(self):
        """Reset daily usage counters if it's a new day."""
        now = datetime.utcnow()
        if now.date() > self._last_reset.date():
            self._daily_usage = {k: 0 for k in self.DAILY_LIMITS}
            self._last_reset = now

    def _check_rate_limit(self, action_type: str) -> bool:
        """Check if action is within rate limits."""
        if action_type not in self.DAILY_LIMITS:
            return True
        return self._daily_usage[action_type] < self.DAILY_LIMITS[action_type]

    def _increment_usage(self, action_type: str):
        """Increment daily usage counter."""
        if action_type in self._daily_usage:
            self._daily_usage[action_type] += 1

    def _log_interaction(self, operation: str, payload: Dict, result: Dict, execution_time: float):
        """Log interaction for audit trail."""
        self._interaction_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "payload_keys": list(payload.keys()) if payload else [],
            "success": "error" not in result,
            "execution_time_ms": execution_time,
        })

    # --- Prospect Management Implementation ---

    def _add_prospect(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new prospect."""
        prospect = Prospect(
            name=payload.get("name", ""),
            organization=payload.get("organization", ""),
            role=payload.get("role", ""),
            prospect_type=ProspectType(payload.get("prospect_type", "vc_business")),
            platform=payload.get("platform", "linkedin"),
            profile_url=payload.get("profile_url", ""),
            email=payload.get("email"),
            tier=ProspectTier(payload.get("tier", "tier_2")),
            thesis_alignment=payload.get("thesis_alignment", 0.5),
            tags=payload.get("tags", []),
            notes=payload.get("notes", ""),
        )

        self._prospects[prospect.id] = prospect

        return {
            "prospect_id": prospect.id,
            "message": f"Added prospect: {prospect.name} at {prospect.organization}",
            "prospect": prospect.to_dict()
        }

    def _update_prospect(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing prospect."""
        prospect_id = payload.get("prospect_id")
        if prospect_id not in self._prospects:
            return {"error": f"Prospect not found: {prospect_id}"}

        prospect = self._prospects[prospect_id]

        # Update fields if provided
        for field in ["name", "organization", "role", "profile_url", "email",
                      "thesis_alignment", "tags", "notes"]:
            if field in payload:
                setattr(prospect, field, payload[field])

        if "tier" in payload:
            prospect.tier = ProspectTier(payload["tier"])
        if "prospect_type" in payload:
            prospect.prospect_type = ProspectType(payload["prospect_type"])

        return {
            "prospect_id": prospect_id,
            "message": "Prospect updated",
            "prospect": prospect.to_dict()
        }

    def _get_prospect(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get a prospect by ID."""
        prospect_id = payload.get("prospect_id")
        if prospect_id not in self._prospects:
            return {"error": f"Prospect not found: {prospect_id}"}

        return {"prospect": self._prospects[prospect_id].to_dict()}

    def _list_prospects(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """List prospects with optional filtering."""
        tier_filter = payload.get("tier")
        type_filter = payload.get("prospect_type")
        tag_filter = payload.get("tag")

        prospects = list(self._prospects.values())

        if tier_filter:
            prospects = [p for p in prospects if p.tier.value == tier_filter]
        if type_filter:
            prospects = [p for p in prospects if p.prospect_type.value == type_filter]
        if tag_filter:
            prospects = [p for p in prospects if tag_filter in p.tags]

        return {
            "count": len(prospects),
            "prospects": [p.to_dict() for p in prospects]
        }

    def _qualify_prospect(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Qualify a prospect based on thesis alignment."""
        prospect_id = payload.get("prospect_id")
        if prospect_id not in self._prospects:
            return {"error": f"Prospect not found: {prospect_id}"}

        prospect = self._prospects[prospect_id]

        # Calculate qualification score
        score = prospect.thesis_alignment

        # Adjust based on warm intro availability
        if prospect.warm_intro_path:
            score += 0.2

        # Determine tier
        if score >= 0.8:
            new_tier = ProspectTier.TIER_1
        elif score >= 0.5:
            new_tier = ProspectTier.TIER_2
        elif score >= 0.3:
            new_tier = ProspectTier.TIER_3
        else:
            new_tier = ProspectTier.NURTURE

        prospect.tier = new_tier

        return {
            "prospect_id": prospect_id,
            "qualification_score": score,
            "tier": new_tier.value,
            "recommendation": self._get_tier_recommendation(new_tier)
        }

    def _get_tier_recommendation(self, tier: ProspectTier) -> str:
        """Get outreach recommendation based on tier."""
        recommendations = {
            ProspectTier.TIER_1: "High priority - pursue warm intro immediately",
            ProspectTier.TIER_2: "Good fit - start cold outreach sequence",
            ProspectTier.TIER_3: "Needs qualification - research further before outreach",
            ProspectTier.NURTURE: "Long-term nurture - add to content engagement list",
        }
        return recommendations.get(tier, "Unknown tier")

    def _remove_prospect(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a prospect."""
        prospect_id = payload.get("prospect_id")
        if prospect_id not in self._prospects:
            return {"error": f"Prospect not found: {prospect_id}"}

        del self._prospects[prospect_id]
        return {"message": f"Prospect {prospect_id} removed"}

    # --- Campaign Management Implementation ---

    def _create_campaign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new outreach campaign."""
        campaign = OutreachCampaign(
            name=payload.get("name", ""),
            description=payload.get("description", ""),
            sequence_type=payload.get("sequence_type", "cold_vc"),
            prospects=payload.get("prospects", []),
        )

        self._campaigns[campaign.id] = campaign

        return {
            "campaign_id": campaign.id,
            "message": f"Created campaign: {campaign.name}",
            "campaign": campaign.to_dict()
        }

    def _start_campaign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Start an outreach campaign."""
        campaign_id = payload.get("campaign_id")
        if campaign_id not in self._campaigns:
            return {"error": f"Campaign not found: {campaign_id}"}

        campaign = self._campaigns[campaign_id]
        campaign.status = OutreachStatus.ACTIVE
        campaign.started_at = datetime.utcnow().isoformat()

        return {
            "campaign_id": campaign_id,
            "status": campaign.status.value,
            "message": "Campaign started"
        }

    def _pause_campaign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Pause an active campaign."""
        campaign_id = payload.get("campaign_id")
        if campaign_id not in self._campaigns:
            return {"error": f"Campaign not found: {campaign_id}"}

        campaign = self._campaigns[campaign_id]
        campaign.status = OutreachStatus.PAUSED

        return {
            "campaign_id": campaign_id,
            "status": campaign.status.value,
            "message": "Campaign paused"
        }

    def _resume_campaign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Resume a paused campaign."""
        campaign_id = payload.get("campaign_id")
        if campaign_id not in self._campaigns:
            return {"error": f"Campaign not found: {campaign_id}"}

        campaign = self._campaigns[campaign_id]
        campaign.status = OutreachStatus.ACTIVE

        return {
            "campaign_id": campaign_id,
            "status": campaign.status.value,
            "message": "Campaign resumed"
        }

    def _get_campaign_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get campaign status and metrics."""
        campaign_id = payload.get("campaign_id")
        if campaign_id not in self._campaigns:
            return {"error": f"Campaign not found: {campaign_id}"}

        campaign = self._campaigns[campaign_id]
        return {"campaign": campaign.to_dict()}

    # --- LinkedIn Operations Implementation ---

    def _send_connection_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a LinkedIn connection request."""
        if not self._check_rate_limit("linkedin_connections"):
            return {
                "error": "Daily connection limit reached",
                "limit": self.DAILY_LIMITS["linkedin_connections"],
                "used": self._daily_usage["linkedin_connections"]
            }

        profile_url = payload.get("profile_url")
        note = payload.get("note", "")

        # Validate personalization
        if len(note) < 50:
            return {"error": "Connection note must be at least 50 characters (personalization required)"}

        if "{" in note or "[Name]" in note:
            return {"error": "Connection note contains unfilled template placeholders"}

        # In production, this would call the LinkedIn MCP bridge
        self._increment_usage("linkedin_connections")

        return {
            "status": "queued",
            "profile_url": profile_url,
            "note_length": len(note),
            "daily_remaining": self.DAILY_LIMITS["linkedin_connections"] - self._daily_usage["linkedin_connections"],
            "message": "Connection request queued for sending"
        }

    def _send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a LinkedIn message."""
        if not self._check_rate_limit("linkedin_messages"):
            return {
                "error": "Daily message limit reached",
                "limit": self.DAILY_LIMITS["linkedin_messages"],
                "used": self._daily_usage["linkedin_messages"]
            }

        profile_url = payload.get("profile_url")
        message = payload.get("message", "")

        if len(message) < 20:
            return {"error": "Message must be at least 20 characters"}

        # In production, this would call the LinkedIn MCP bridge
        self._increment_usage("linkedin_messages")

        return {
            "status": "queued",
            "profile_url": profile_url,
            "message_length": len(message),
            "daily_remaining": self.DAILY_LIMITS["linkedin_messages"] - self._daily_usage["linkedin_messages"]
        }

    def _engage_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Engage with a LinkedIn post (like/comment)."""
        if not self._check_rate_limit("linkedin_comments"):
            return {"error": "Daily engagement limit reached"}

        post_url = payload.get("post_url")
        action = payload.get("action", "like")  # like, comment
        comment_text = payload.get("comment", "")

        if action == "comment" and len(comment_text) < 20:
            return {"error": "Comment must be at least 20 characters (meaningful engagement required)"}

        self._increment_usage("linkedin_comments")

        return {
            "status": "queued",
            "post_url": post_url,
            "action": action,
            "message": f"Post {action} queued"
        }

    def _schedule_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a LinkedIn post."""
        if not self._check_rate_limit("linkedin_posts"):
            return {"error": "Daily post limit reached"}

        content = payload.get("content", "")
        scheduled_time = payload.get("scheduled_time")
        hashtags = payload.get("hashtags", [])

        if len(content) < 100:
            return {"error": "Post content must be at least 100 characters"}

        post = {
            "id": str(uuid.uuid4()),
            "content": content,
            "hashtags": hashtags,
            "scheduled_time": scheduled_time or datetime.utcnow().isoformat(),
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }

        self._scheduled_posts.append(post)
        self._increment_usage("linkedin_posts")

        return {
            "post_id": post["id"],
            "status": "scheduled",
            "scheduled_time": post["scheduled_time"],
            "message": "Post scheduled successfully"
        }

    def _optimize_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate profile optimization suggestions."""
        current_headline = payload.get("current_headline", "")
        current_summary = payload.get("current_summary", "")

        # Target keywords for investor visibility
        target_keywords = [
            "AI agents", "Enterprise AI", "Azure", "Multi-agent systems",
            "AI governance", "Founder", "Startup", "Maritime", "Digital twins"
        ]

        suggestions = {
            "headline": {
                "current": current_headline,
                "suggested": "Building governed AI agents for enterprise | Founder @ FREQ | Azure + Claude + GPT",
                "keywords_to_add": [kw for kw in target_keywords if kw.lower() not in current_headline.lower()]
            },
            "summary_keywords": [kw for kw in target_keywords if kw.lower() not in current_summary.lower()],
            "recommendations": [
                "Add 'AI agents' or 'agentic AI' to headline",
                "Mention Azure/Microsoft partnership pursuit",
                "Include FREQ LAW governance framework",
                "Add maritime/logistics vertical focus",
            ]
        }

        return suggestions

    # --- Pitch Generation Implementation ---

    def _generate_pitch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a tailored pitch."""
        pitch_type = payload.get("pitch_type", "elevator")
        investor_name = payload.get("investor_name", "")
        investor_firm = payload.get("investor_firm", "")
        thesis_keywords = payload.get("thesis_keywords", [])

        # Delegate to PitchGenerator (imported in actual use)
        # For now, return template structure
        pitches = {
            "one_liner": "FREQ is a governed AI agent orchestration platform - multi-agent systems with built-in compliance for enterprise deployment.",
            "elevator": f"""Enterprises want to deploy AI agents but can't trust ungoverned autonomous systems.

FREQ solves this with the Sophisticated Operational Lattice - a multi-agent architecture where every operation is fast (sub-2000ms guaranteed), robust (Byzantine fault tolerant with k=3 quorum), and quantified (full audit trail).

Our first vertical is maritime logistics - using LiDAR and Azure Digital Twins for automated cargo measurement with 99.8% accuracy.

We're looking for investors who understand enterprise AI infrastructure.""",
            "one_pager": "Full one-pager available via PitchGenerator module"
        }

        return {
            "pitch_type": pitch_type,
            "content": pitches.get(pitch_type, pitches["elevator"]),
            "customization": {
                "investor": investor_name,
                "firm": investor_firm,
                "thesis_match": thesis_keywords
            }
        }

    def _generate_intro_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a warm intro request message."""
        connector_name = payload.get("connector_name", "")
        target_name = payload.get("target_name", "")
        target_company = payload.get("target_company", "")
        relationship_type = payload.get("relationship_type", "investor")

        message = f"""Hi {connector_name},

Hope you're doing well! Quick ask:

I noticed you're connected to {target_name} at {target_company}. I'm building FREQ (AI agent orchestration for enterprise) and {target_company} would be a perfect {relationship_type}.

Would you be comfortable making an intro? Happy to send you a forwardable blurb.

No pressure if it's not a good fit. Appreciate you either way.

Dre"""

        return {
            "message": message,
            "connector": connector_name,
            "target": target_name,
            "target_company": target_company
        }

    # --- MFSIN Scouting Implementation ---

    def _scan_mfsin(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Scan Microsoft for Startups Investor Network."""
        # In production, this would use web search to find MFSIN investors
        return {
            "status": "scan_initiated",
            "target": "Microsoft for Startups Investor Network",
            "message": "Use web search to identify MFSIN-affiliated investors",
            "search_queries": [
                "Microsoft for Startups Investor Network VCs",
                "MFSIN portfolio companies investors",
                "Microsoft Founders Hub investor partners"
            ]
        }

    def _scan_vc_portfolio(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Scan a VC firm's portfolio for thesis alignment."""
        firm_name = payload.get("firm_name", "")

        return {
            "status": "scan_initiated",
            "firm": firm_name,
            "search_queries": [
                f"{firm_name} portfolio companies AI",
                f"{firm_name} recent investments enterprise",
                f"{firm_name} partners investors"
            ]
        }

    # --- Relationship Mapping Implementation ---

    def _find_warm_intro_path(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Find warm intro path to a target."""
        target_name = payload.get("target_name", "")
        target_company = payload.get("target_company", "")

        # In production, this would analyze LinkedIn connections
        return {
            "target": target_name,
            "company": target_company,
            "status": "analysis_required",
            "message": "Check LinkedIn for mutual connections",
            "search_strategy": [
                f"LinkedIn mutual connections with {target_name}",
                f"2nd degree connections at {target_company}",
                f"Common groups or events"
            ]
        }

    def _map_network(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Map network for investor proximity."""
        return {
            "status": "mapping_initiated",
            "segments": ["VCs", "Founders", "Enterprise", "Accelerators"],
            "message": "Categorize LinkedIn connections by investor proximity"
        }

    # --- Status and Metrics ---

    def _get_daily_limits(self) -> Dict[str, Any]:
        """Get current daily usage and limits."""
        return {
            "limits": self.DAILY_LIMITS,
            "usage": self._daily_usage,
            "remaining": {k: self.DAILY_LIMITS[k] - self._daily_usage[k] for k in self.DAILY_LIMITS},
            "reset_at": (self._last_reset + timedelta(days=1)).isoformat()
        }

    def _get_metrics(self) -> Dict[str, Any]:
        """Get scouter performance metrics."""
        return {
            "prospects_count": len(self._prospects),
            "campaigns_count": len(self._campaigns),
            "active_campaigns": sum(1 for c in self._campaigns.values() if c.status == OutreachStatus.ACTIVE),
            "scheduled_posts": len(self._scheduled_posts),
            "daily_usage": self._daily_usage,
            "interaction_count": len(self._interaction_log)
        }

    def _get_status(self) -> Dict[str, Any]:
        """Get overall scouter status."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "description": self.description,
            "metrics": self._get_metrics(),
            "daily_limits": self._get_daily_limits(),
            "connected_nodes": list(self._connected_nodes.keys())
        }
