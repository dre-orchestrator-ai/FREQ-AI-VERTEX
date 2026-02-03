"""
LinkedIn MCP Integration Bridge for FREQ SOL

Bridges data flow between Executor Scouter and LinkedIn via MCP protocol.
Handles profile optimization, connection management, and engagement automation.

Data Flow:
    ExecScouter → LinkedInBridge → MCP Server → LinkedIn API
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import asyncio


class LinkedInActionType(Enum):
    """Types of LinkedIn actions."""
    PROFILE_VIEW = "profile_view"
    CONNECTION_REQUEST = "connection_request"
    MESSAGE_SEND = "message_send"
    POST_CREATE = "post_create"
    POST_ENGAGE = "post_engage"
    PROFILE_UPDATE = "profile_update"
    SEARCH = "search"


class EngagementType(Enum):
    """Types of post engagement."""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    REPOST = "repost"


@dataclass
class LinkedInConfig:
    """Configuration for LinkedIn MCP bridge."""

    mcp_server_url: str = "http://localhost:3100"
    mcp_auth_token: Optional[str] = None

    # Rate limits (LinkedIn's unofficial limits)
    daily_connection_limit: int = 10
    daily_message_limit: int = 25
    daily_profile_view_limit: int = 100
    daily_post_limit: int = 2
    daily_engagement_limit: int = 30

    # Timing (FREQ LAW compliant)
    min_action_interval_ms: int = 2000  # <2000ms per operation
    engagement_delay_range: tuple = (30, 120)  # seconds between engagements

    # Safety
    require_personalization: bool = True
    min_connection_note_length: int = 50
    min_comment_length: int = 20
    max_message_length: int = 300

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mcp_server_url": self.mcp_server_url,
            "daily_connection_limit": self.daily_connection_limit,
            "daily_message_limit": self.daily_message_limit,
            "daily_post_limit": self.daily_post_limit,
            "min_action_interval_ms": self.min_action_interval_ms,
            "require_personalization": self.require_personalization,
        }


@dataclass
class LinkedInAction:
    """Result of a LinkedIn action."""

    action_type: LinkedInActionType
    target_url: str
    status: str  # success, failed, rate_limited, pending, queued
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    response_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type.value,
            "target_url": self.target_url,
            "status": self.status,
            "timestamp": self.timestamp,
            "response_data": self.response_data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
        }


@dataclass
class LinkedInProfile:
    """LinkedIn profile data."""

    profile_url: str
    name: str = ""
    headline: str = ""
    company: str = ""
    role: str = ""
    location: str = ""
    connections: int = 0
    is_connection: bool = False
    mutual_connections: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_url": self.profile_url,
            "name": self.name,
            "headline": self.headline,
            "company": self.company,
            "role": self.role,
            "location": self.location,
            "connections": self.connections,
            "is_connection": self.is_connection,
            "mutual_connections": self.mutual_connections,
        }


class LinkedInBridge:
    """
    LinkedIn MCP Integration Bridge.

    Connects Executor Scouter to LinkedIn via Model Context Protocol server.
    Manages rate limiting, personalization requirements, and engagement timing.

    Usage:
        config = LinkedInConfig(mcp_server_url="http://localhost:3100")
        bridge = LinkedInBridge(config)

        # Send personalized connection request
        result = await bridge.send_connection_request(
            profile_url="https://linkedin.com/in/investor-name",
            note="Hi [Name], I noticed your investment in [Company]..."
        )
    """

    def __init__(self, config: Optional[LinkedInConfig] = None):
        self.config = config or LinkedInConfig()
        self._mcp_client = None
        self._action_history: List[LinkedInAction] = []
        self._daily_counts: Dict[str, int] = {
            "connections": 0,
            "messages": 0,
            "profile_views": 0,
            "posts": 0,
            "engagements": 0,
        }
        self._last_action_time: Optional[datetime] = None
        self._last_reset_date: datetime = datetime.utcnow()
        self._callbacks: Dict[str, List[Callable]] = {
            "on_action_complete": [],
            "on_rate_limit": [],
            "on_error": [],
        }

    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for bridge events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit(self, event: str, *args, **kwargs) -> None:
        """Emit event to registered callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass

    def _check_daily_reset(self) -> None:
        """Reset daily counters if new day."""
        now = datetime.utcnow()
        if now.date() > self._last_reset_date.date():
            self._daily_counts = {k: 0 for k in self._daily_counts}
            self._last_reset_date = now

    def _check_rate_limit(self, action_type: str) -> bool:
        """Check if action is within rate limits."""
        self._check_daily_reset()

        limits = {
            "connections": self.config.daily_connection_limit,
            "messages": self.config.daily_message_limit,
            "profile_views": self.config.daily_profile_view_limit,
            "posts": self.config.daily_post_limit,
            "engagements": self.config.daily_engagement_limit,
        }

        if action_type not in limits:
            return True

        return self._daily_counts[action_type] < limits[action_type]

    def _validate_personalization(self, text: str, min_length: int) -> tuple:
        """Validate text meets personalization requirements."""
        if len(text) < min_length:
            return False, f"Text must be at least {min_length} characters"

        # Check for unfilled placeholders
        placeholders = ["{", "[Name]", "[Company]", "{{", "}}"]
        for placeholder in placeholders:
            if placeholder in text:
                return False, f"Text contains unfilled placeholder: {placeholder}"

        return True, None

    async def send_connection_request(
        self,
        profile_url: str,
        note: str,
        prospect_context: Optional[Dict[str, Any]] = None
    ) -> LinkedInAction:
        """
        Send a connection request with personalized note.

        Args:
            profile_url: LinkedIn profile URL
            note: Personalized connection note (min 50 chars)
            prospect_context: Additional context for logging

        Returns:
            LinkedInAction with result
        """
        start_time = datetime.utcnow()

        # Check rate limit
        if not self._check_rate_limit("connections"):
            action = LinkedInAction(
                action_type=LinkedInActionType.CONNECTION_REQUEST,
                target_url=profile_url,
                status="rate_limited",
                error=f"Daily limit reached: {self.config.daily_connection_limit}"
            )
            self._emit("on_rate_limit", action)
            return action

        # Validate personalization
        if self.config.require_personalization:
            is_valid, error = self._validate_personalization(
                note, self.config.min_connection_note_length
            )
            if not is_valid:
                return LinkedInAction(
                    action_type=LinkedInActionType.CONNECTION_REQUEST,
                    target_url=profile_url,
                    status="failed",
                    error=error
                )

        # Enforce message length
        if len(note) > self.config.max_message_length:
            note = note[:self.config.max_message_length - 3] + "..."

        # Queue for MCP execution
        try:
            # In production, call MCP server
            # response = await self._call_mcp("linkedin.connect", {...})

            self._daily_counts["connections"] += 1
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            action = LinkedInAction(
                action_type=LinkedInActionType.CONNECTION_REQUEST,
                target_url=profile_url,
                status="queued",
                response_data={
                    "note_length": len(note),
                    "daily_remaining": self.config.daily_connection_limit - self._daily_counts["connections"],
                    "context": prospect_context
                },
                execution_time_ms=execution_time
            )

        except Exception as e:
            action = LinkedInAction(
                action_type=LinkedInActionType.CONNECTION_REQUEST,
                target_url=profile_url,
                status="failed",
                error=str(e)
            )
            self._emit("on_error", action)

        self._action_history.append(action)
        self._emit("on_action_complete", action)
        return action

    async def send_message(
        self,
        profile_url: str,
        message: str,
        is_inmail: bool = False
    ) -> LinkedInAction:
        """
        Send a message to a LinkedIn connection.

        Args:
            profile_url: LinkedIn profile URL
            message: Message content
            is_inmail: Whether this is an InMail (non-connection)

        Returns:
            LinkedInAction with result
        """
        if not self._check_rate_limit("messages"):
            return LinkedInAction(
                action_type=LinkedInActionType.MESSAGE_SEND,
                target_url=profile_url,
                status="rate_limited",
                error=f"Daily message limit reached: {self.config.daily_message_limit}"
            )

        # Validate message
        if len(message) < 20:
            return LinkedInAction(
                action_type=LinkedInActionType.MESSAGE_SEND,
                target_url=profile_url,
                status="failed",
                error="Message must be at least 20 characters"
            )

        self._daily_counts["messages"] += 1

        return LinkedInAction(
            action_type=LinkedInActionType.MESSAGE_SEND,
            target_url=profile_url,
            status="queued",
            response_data={
                "message_length": len(message),
                "is_inmail": is_inmail,
                "daily_remaining": self.config.daily_message_limit - self._daily_counts["messages"]
            }
        )

    async def engage_with_post(
        self,
        post_url: str,
        engagement_type: EngagementType,
        comment_text: Optional[str] = None
    ) -> LinkedInAction:
        """
        Engage with a LinkedIn post (like, comment, share).

        Args:
            post_url: URL of the post
            engagement_type: Type of engagement
            comment_text: Comment text if engagement_type is COMMENT

        Returns:
            LinkedInAction with result
        """
        if not self._check_rate_limit("engagements"):
            return LinkedInAction(
                action_type=LinkedInActionType.POST_ENGAGE,
                target_url=post_url,
                status="rate_limited",
                error="Daily engagement limit reached"
            )

        # Validate comment if required
        if engagement_type == EngagementType.COMMENT:
            if not comment_text or len(comment_text) < self.config.min_comment_length:
                return LinkedInAction(
                    action_type=LinkedInActionType.POST_ENGAGE,
                    target_url=post_url,
                    status="failed",
                    error=f"Comment must be at least {self.config.min_comment_length} characters"
                )

        self._daily_counts["engagements"] += 1

        return LinkedInAction(
            action_type=LinkedInActionType.POST_ENGAGE,
            target_url=post_url,
            status="queued",
            response_data={
                "engagement_type": engagement_type.value,
                "comment_length": len(comment_text) if comment_text else 0,
                "daily_remaining": self.config.daily_engagement_limit - self._daily_counts["engagements"]
            }
        )

    async def create_post(
        self,
        content: str,
        hashtags: Optional[List[str]] = None,
        scheduled_time: Optional[str] = None
    ) -> LinkedInAction:
        """
        Create a LinkedIn post.

        Args:
            content: Post content
            hashtags: List of hashtags to include
            scheduled_time: ISO timestamp for scheduled posting

        Returns:
            LinkedInAction with result
        """
        if not self._check_rate_limit("posts"):
            return LinkedInAction(
                action_type=LinkedInActionType.POST_CREATE,
                target_url="linkedin://feed",
                status="rate_limited",
                error=f"Daily post limit reached: {self.config.daily_post_limit}"
            )

        if len(content) < 100:
            return LinkedInAction(
                action_type=LinkedInActionType.POST_CREATE,
                target_url="linkedin://feed",
                status="failed",
                error="Post content must be at least 100 characters"
            )

        # Append hashtags if provided
        if hashtags:
            content = content + "\n\n" + " ".join(hashtags)

        self._daily_counts["posts"] += 1

        return LinkedInAction(
            action_type=LinkedInActionType.POST_CREATE,
            target_url="linkedin://feed",
            status="scheduled" if scheduled_time else "queued",
            response_data={
                "content_length": len(content),
                "hashtags": hashtags or [],
                "scheduled_time": scheduled_time,
                "daily_remaining": self.config.daily_post_limit - self._daily_counts["posts"]
            }
        )

    async def view_profile(self, profile_url: str) -> LinkedInAction:
        """View a LinkedIn profile (for research)."""
        if not self._check_rate_limit("profile_views"):
            return LinkedInAction(
                action_type=LinkedInActionType.PROFILE_VIEW,
                target_url=profile_url,
                status="rate_limited",
                error="Daily profile view limit reached"
            )

        self._daily_counts["profile_views"] += 1

        return LinkedInAction(
            action_type=LinkedInActionType.PROFILE_VIEW,
            target_url=profile_url,
            status="queued",
            response_data={
                "daily_remaining": self.config.daily_profile_view_limit - self._daily_counts["profile_views"]
            }
        )

    def get_daily_usage(self) -> Dict[str, Any]:
        """Get current daily usage statistics."""
        self._check_daily_reset()

        return {
            "counts": self._daily_counts.copy(),
            "limits": {
                "connections": self.config.daily_connection_limit,
                "messages": self.config.daily_message_limit,
                "profile_views": self.config.daily_profile_view_limit,
                "posts": self.config.daily_post_limit,
                "engagements": self.config.daily_engagement_limit,
            },
            "remaining": {
                "connections": self.config.daily_connection_limit - self._daily_counts["connections"],
                "messages": self.config.daily_message_limit - self._daily_counts["messages"],
                "profile_views": self.config.daily_profile_view_limit - self._daily_counts["profile_views"],
                "posts": self.config.daily_post_limit - self._daily_counts["posts"],
                "engagements": self.config.daily_engagement_limit - self._daily_counts["engagements"],
            },
            "last_reset": self._last_reset_date.isoformat()
        }

    def get_action_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent action history."""
        return [a.to_dict() for a in self._action_history[-limit:]]

    def get_status_summary(self) -> Dict[str, Any]:
        """Get bridge status summary."""
        return {
            "config": self.config.to_dict(),
            "daily_usage": self.get_daily_usage(),
            "total_actions": len(self._action_history),
            "last_action": self._action_history[-1].to_dict() if self._action_history else None,
            "mcp_connected": self._mcp_client is not None
        }
