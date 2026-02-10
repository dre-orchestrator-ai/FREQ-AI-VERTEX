"""
Outreach Engine for FREQ SOL Executor Scouter

Manages multi-touch outreach sequences for partnership development.
Orchestrates cold, warm intro, and follow-up sequences with timing and personalization.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import uuid


class TouchpointChannel(Enum):
    """Channels for outreach touchpoints."""
    LINKEDIN_CONNECTION = "linkedin_connection"
    LINKEDIN_MESSAGE = "linkedin_message"
    LINKEDIN_COMMENT = "linkedin_comment"
    LINKEDIN_POST_ENGAGE = "linkedin_post_engage"
    EMAIL = "email"
    TWITTER_FOLLOW = "twitter_follow"
    TWITTER_REPLY = "twitter_reply"


class SequenceStatus(Enum):
    """Status of an outreach sequence instance."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"  # Manual stop
    ARCHIVED = "archived"  # No response after all touchpoints


@dataclass
class Touchpoint:
    """Single touchpoint in an outreach sequence."""

    day: int  # Days from sequence start
    channel: TouchpointChannel
    template_key: str
    template_variables: Dict[str, str] = field(default_factory=dict)
    fallback_template_key: Optional[str] = None
    requires_response_to_previous: bool = False
    max_wait_days: int = 7
    condition: Optional[str] = None  # e.g., "connected", "opened_previous"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "channel": self.channel.value,
            "template_key": self.template_key,
            "template_variables": self.template_variables,
            "fallback_template_key": self.fallback_template_key,
            "requires_response_to_previous": self.requires_response_to_previous,
            "max_wait_days": self.max_wait_days,
            "condition": self.condition,
        }


@dataclass
class OutreachSequence:
    """Definition of a multi-touch outreach sequence."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    touchpoints: List[Touchpoint] = field(default_factory=list)
    success_criteria: str = ""
    abort_criteria: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "touchpoints": [t.to_dict() for t in self.touchpoints],
            "success_criteria": self.success_criteria,
            "abort_criteria": self.abort_criteria,
            "tags": self.tags,
        }


@dataclass
class SequenceInstance:
    """Instance of a sequence being executed for a specific prospect."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sequence_id: str = ""
    prospect_id: str = ""
    prospect_name: str = ""
    status: SequenceStatus = SequenceStatus.PENDING
    current_touchpoint: int = 0
    started_at: Optional[str] = None
    last_touchpoint_at: Optional[str] = None
    next_touchpoint_at: Optional[str] = None
    completed_at: Optional[str] = None
    touchpoint_results: List[Dict[str, Any]] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sequence_id": self.sequence_id,
            "prospect_id": self.prospect_id,
            "prospect_name": self.prospect_name,
            "status": self.status.value,
            "current_touchpoint": self.current_touchpoint,
            "started_at": self.started_at,
            "last_touchpoint_at": self.last_touchpoint_at,
            "next_touchpoint_at": self.next_touchpoint_at,
            "completed_at": self.completed_at,
            "touchpoint_results": self.touchpoint_results,
            "notes": self.notes,
        }


class OutreachEngine:
    """
    Outreach sequence execution engine.

    Manages the lifecycle of outreach sequences:
    - Sequence definition and storage
    - Instance creation and execution
    - Timing and scheduling
    - Response tracking and status updates

    Usage:
        engine = OutreachEngine()

        # Load predefined sequences
        engine.register_sequence(COLD_VC_SEQUENCE)

        # Start sequence for a prospect
        instance = engine.start_sequence("cold_vc", prospect_id="abc123")

        # Execute next touchpoint
        result = engine.execute_next_touchpoint(instance.id)

        # Handle response
        engine.record_response(instance.id, "replied", "Interested in a call")
    """

    def __init__(self):
        self._sequences: Dict[str, OutreachSequence] = {}
        self._instances: Dict[str, SequenceInstance] = {}
        self._callbacks: Dict[str, List[Callable]] = {
            "on_touchpoint_executed": [],
            "on_sequence_completed": [],
            "on_response_received": [],
        }

        # Load default sequences
        self._load_default_sequences()

    def _load_default_sequences(self) -> None:
        """Load predefined outreach sequences."""

        # Cold VC Outreach (4 touchpoints over 14 days)
        cold_vc = OutreachSequence(
            name="cold_vc",
            description="Cold outreach to VCs with AI/enterprise thesis",
            touchpoints=[
                Touchpoint(
                    day=0,
                    channel=TouchpointChannel.LINKEDIN_COMMENT,
                    template_key="vc_post_comment",
                ),
                Touchpoint(
                    day=3,
                    channel=TouchpointChannel.LINKEDIN_CONNECTION,
                    template_key="vc_connection_request",
                ),
                Touchpoint(
                    day=7,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="vc_intro_message",
                    condition="connected",
                ),
                Touchpoint(
                    day=14,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="vc_followup_message",
                    requires_response_to_previous=False,
                    max_wait_days=14,
                ),
            ],
            success_criteria="Positive response or referral to colleague",
            abort_criteria="Explicit decline or no response after touchpoint 4",
            tags=["vc", "cold", "ai_thesis"],
        )

        # Cold Enterprise Outreach
        cold_enterprise = OutreachSequence(
            name="cold_enterprise",
            description="Cold outreach to enterprise partnership targets",
            touchpoints=[
                Touchpoint(
                    day=0,
                    channel=TouchpointChannel.LINKEDIN_COMMENT,
                    template_key="enterprise_post_comment",
                ),
                Touchpoint(
                    day=2,
                    channel=TouchpointChannel.LINKEDIN_CONNECTION,
                    template_key="enterprise_connection_request",
                ),
                Touchpoint(
                    day=7,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="enterprise_intro_message",
                    condition="connected",
                ),
            ],
            success_criteria="Demo scheduled or referral to decision maker",
            abort_criteria="No response after 3 touchpoints",
            tags=["enterprise", "cold", "partnership"],
        )

        # Warm Intro Request
        warm_intro = OutreachSequence(
            name="warm_intro",
            description="Request for warm introduction via mutual connection",
            touchpoints=[
                Touchpoint(
                    day=0,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="warm_intro_request",
                ),
                Touchpoint(
                    day=3,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="warm_intro_followup",
                    requires_response_to_previous=False,
                ),
            ],
            success_criteria="Intro made or clear timeline provided",
            abort_criteria="Explicit decline to make intro",
            tags=["warm", "intro_request"],
        )

        # Post-Meeting Follow-up
        post_meeting = OutreachSequence(
            name="post_meeting",
            description="Follow-up sequence after initial meeting",
            touchpoints=[
                Touchpoint(
                    day=0,
                    channel=TouchpointChannel.EMAIL,
                    template_key="meeting_recap_email",
                ),
                Touchpoint(
                    day=7,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="meeting_followup_linkedin",
                    requires_response_to_previous=False,
                ),
                Touchpoint(
                    day=14,
                    channel=TouchpointChannel.EMAIL,
                    template_key="meeting_second_followup",
                    requires_response_to_previous=False,
                ),
            ],
            success_criteria="Next meeting scheduled or clear next step agreed",
            abort_criteria="Two consecutive no-responses",
            tags=["follow_up", "post_meeting"],
        )

        # MFSIN Application Follow-up
        mfsin_followup = OutreachSequence(
            name="mfsin_followup",
            description="Follow-up on Microsoft for Startups application",
            touchpoints=[
                Touchpoint(
                    day=7,
                    channel=TouchpointChannel.EMAIL,
                    template_key="mfsin_application_followup",
                ),
                Touchpoint(
                    day=14,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="mfsin_linkedin_followup",
                ),
            ],
            success_criteria="Application status update or interview scheduled",
            abort_criteria="Application rejected",
            tags=["mfsin", "microsoft", "application"],
        )

        # Connection Accepted - VC Leadership
        connection_accepted_vc = OutreachSequence(
            name="connection_accepted_vc",
            description="Warm follow-up when VC/investor accepts connection request",
            touchpoints=[
                Touchpoint(
                    day=0,  # Same day, but delay 4-8 hours in execution
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_vc_leadership",
                ),
                Touchpoint(
                    day=5,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_followup_value",
                    requires_response_to_previous=False,
                ),
                Touchpoint(
                    day=10,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_followup_ask",
                    requires_response_to_previous=False,
                    max_wait_days=7,
                ),
            ],
            success_criteria="Positive response, referral, or meeting scheduled",
            abort_criteria="Explicit decline or no response after touchpoint 3",
            tags=["warm", "connection_accepted", "vc", "leadership"],
        )

        # Connection Accepted - Enterprise Leadership
        connection_accepted_enterprise = OutreachSequence(
            name="connection_accepted_enterprise",
            description="Warm follow-up when enterprise leader accepts connection request",
            touchpoints=[
                Touchpoint(
                    day=0,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_enterprise_leadership",
                ),
                Touchpoint(
                    day=5,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_followup_value",
                    requires_response_to_previous=False,
                ),
                Touchpoint(
                    day=12,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_followup_ask",
                    requires_response_to_previous=False,
                ),
            ],
            success_criteria="Demo scheduled or referral to decision maker",
            abort_criteria="Explicit decline or no response",
            tags=["warm", "connection_accepted", "enterprise", "leadership"],
        )

        # Connection Accepted - Ecosystem (Google/Microsoft)
        connection_accepted_ecosystem = OutreachSequence(
            name="connection_accepted_ecosystem",
            description="Warm follow-up when ecosystem contact accepts",
            touchpoints=[
                Touchpoint(
                    day=0,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_ecosystem",
                ),
                Touchpoint(
                    day=7,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_followup_ask",
                    requires_response_to_previous=False,
                ),
            ],
            success_criteria="Program referral or partnership conversation",
            abort_criteria="No response after 2 touchpoints",
            tags=["warm", "connection_accepted", "ecosystem", "google", "microsoft"],
        )

        # Connection Accepted - General Leadership
        connection_accepted_general = OutreachSequence(
            name="connection_accepted_general",
            description="Warm follow-up for general leadership connections",
            touchpoints=[
                Touchpoint(
                    day=0,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_general_leadership",
                ),
                Touchpoint(
                    day=7,
                    channel=TouchpointChannel.LINKEDIN_MESSAGE,
                    template_key="connection_accepted_followup_value",
                    requires_response_to_previous=False,
                ),
            ],
            success_criteria="Engagement or conversation started",
            abort_criteria="No response after 2 touchpoints",
            tags=["warm", "connection_accepted", "general"],
        )

        # Register all sequences
        for seq in [
            cold_vc, cold_enterprise, warm_intro, post_meeting, mfsin_followup,
            connection_accepted_vc, connection_accepted_enterprise,
            connection_accepted_ecosystem, connection_accepted_general
        ]:
            self._sequences[seq.name] = seq

    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for engine events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit(self, event: str, *args, **kwargs) -> None:
        """Emit event to registered callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass

    def register_sequence(self, sequence: OutreachSequence) -> None:
        """Register a new outreach sequence."""
        self._sequences[sequence.name] = sequence

    def get_sequence(self, name: str) -> Optional[OutreachSequence]:
        """Get a sequence by name."""
        return self._sequences.get(name)

    def list_sequences(self) -> List[Dict[str, Any]]:
        """List all registered sequences."""
        return [seq.to_dict() for seq in self._sequences.values()]

    def start_sequence(
        self,
        sequence_name: str,
        prospect_id: str,
        prospect_name: str = "",
        variables: Optional[Dict[str, str]] = None
    ) -> SequenceInstance:
        """
        Start an outreach sequence for a prospect.

        Args:
            sequence_name: Name of the sequence to start
            prospect_id: ID of the target prospect
            prospect_name: Name of the prospect (for display)
            variables: Template variables for personalization

        Returns:
            SequenceInstance tracking the sequence execution
        """
        sequence = self._sequences.get(sequence_name)
        if not sequence:
            raise ValueError(f"Unknown sequence: {sequence_name}")

        now = datetime.utcnow()

        # Calculate first touchpoint time
        first_touchpoint = sequence.touchpoints[0] if sequence.touchpoints else None
        next_touchpoint_at = now + timedelta(days=first_touchpoint.day) if first_touchpoint else None

        instance = SequenceInstance(
            sequence_id=sequence.name,
            prospect_id=prospect_id,
            prospect_name=prospect_name,
            status=SequenceStatus.ACTIVE,
            current_touchpoint=0,
            started_at=now.isoformat(),
            next_touchpoint_at=next_touchpoint_at.isoformat() if next_touchpoint_at else None,
        )

        self._instances[instance.id] = instance
        return instance

    def get_instance(self, instance_id: str) -> Optional[SequenceInstance]:
        """Get a sequence instance by ID."""
        return self._instances.get(instance_id)

    def list_active_instances(self) -> List[Dict[str, Any]]:
        """List all active sequence instances."""
        return [
            inst.to_dict()
            for inst in self._instances.values()
            if inst.status == SequenceStatus.ACTIVE
        ]

    def list_due_touchpoints(self) -> List[Dict[str, Any]]:
        """List all touchpoints that are due for execution."""
        now = datetime.utcnow()
        due = []

        for instance in self._instances.values():
            if instance.status != SequenceStatus.ACTIVE:
                continue

            if instance.next_touchpoint_at:
                next_time = datetime.fromisoformat(instance.next_touchpoint_at)
                if next_time <= now:
                    sequence = self._sequences.get(instance.sequence_id)
                    if sequence and instance.current_touchpoint < len(sequence.touchpoints):
                        touchpoint = sequence.touchpoints[instance.current_touchpoint]
                        due.append({
                            "instance_id": instance.id,
                            "prospect_id": instance.prospect_id,
                            "prospect_name": instance.prospect_name,
                            "sequence": instance.sequence_id,
                            "touchpoint_index": instance.current_touchpoint,
                            "touchpoint": touchpoint.to_dict(),
                            "scheduled_for": instance.next_touchpoint_at,
                        })

        return due

    def execute_touchpoint(
        self,
        instance_id: str,
        result: str = "sent",
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Mark a touchpoint as executed and advance the sequence.

        Args:
            instance_id: Sequence instance ID
            result: Result of execution (sent, failed, skipped)
            notes: Additional notes

        Returns:
            Updated instance status
        """
        instance = self._instances.get(instance_id)
        if not instance:
            return {"error": f"Instance not found: {instance_id}"}

        sequence = self._sequences.get(instance.sequence_id)
        if not sequence:
            return {"error": f"Sequence not found: {instance.sequence_id}"}

        now = datetime.utcnow()

        # Record touchpoint result
        touchpoint_result = {
            "index": instance.current_touchpoint,
            "result": result,
            "executed_at": now.isoformat(),
            "notes": notes,
        }
        instance.touchpoint_results.append(touchpoint_result)
        instance.last_touchpoint_at = now.isoformat()

        # Advance to next touchpoint
        instance.current_touchpoint += 1

        # Check if sequence is complete
        if instance.current_touchpoint >= len(sequence.touchpoints):
            instance.status = SequenceStatus.COMPLETED
            instance.completed_at = now.isoformat()
            instance.next_touchpoint_at = None
            self._emit("on_sequence_completed", instance)
        else:
            # Schedule next touchpoint
            next_touchpoint = sequence.touchpoints[instance.current_touchpoint]
            next_time = now + timedelta(days=next_touchpoint.day - sequence.touchpoints[instance.current_touchpoint - 1].day)
            instance.next_touchpoint_at = next_time.isoformat()

        self._emit("on_touchpoint_executed", instance, touchpoint_result)

        return {
            "instance_id": instance_id,
            "touchpoint_executed": instance.current_touchpoint - 1,
            "status": instance.status.value,
            "next_touchpoint_at": instance.next_touchpoint_at,
        }

    def record_response(
        self,
        instance_id: str,
        response_type: str,
        response_content: str = ""
    ) -> Dict[str, Any]:
        """
        Record a response from the prospect.

        Args:
            instance_id: Sequence instance ID
            response_type: Type of response (replied, meeting_scheduled, declined, etc.)
            response_content: Content of the response

        Returns:
            Updated instance status
        """
        instance = self._instances.get(instance_id)
        if not instance:
            return {"error": f"Instance not found: {instance_id}"}

        now = datetime.utcnow()

        # Record response
        response_record = {
            "type": response_type,
            "content": response_content,
            "received_at": now.isoformat(),
            "touchpoint_index": instance.current_touchpoint - 1,
        }

        # Update last touchpoint result with response
        if instance.touchpoint_results:
            instance.touchpoint_results[-1]["response"] = response_record

        # Handle response type
        if response_type in ["meeting_scheduled", "positive_reply"]:
            instance.status = SequenceStatus.COMPLETED
            instance.completed_at = now.isoformat()
            instance.notes = f"Success: {response_type}"
        elif response_type == "declined":
            instance.status = SequenceStatus.STOPPED
            instance.completed_at = now.isoformat()
            instance.notes = f"Stopped: {response_type}"

        self._emit("on_response_received", instance, response_record)

        return {
            "instance_id": instance_id,
            "response_recorded": response_type,
            "status": instance.status.value,
        }

    def pause_instance(self, instance_id: str) -> Dict[str, Any]:
        """Pause a sequence instance."""
        instance = self._instances.get(instance_id)
        if not instance:
            return {"error": f"Instance not found: {instance_id}"}

        instance.status = SequenceStatus.PAUSED
        return {"instance_id": instance_id, "status": "paused"}

    def resume_instance(self, instance_id: str) -> Dict[str, Any]:
        """Resume a paused sequence instance."""
        instance = self._instances.get(instance_id)
        if not instance:
            return {"error": f"Instance not found: {instance_id}"}

        if instance.status != SequenceStatus.PAUSED:
            return {"error": "Instance is not paused"}

        instance.status = SequenceStatus.ACTIVE
        return {"instance_id": instance_id, "status": "active"}

    def stop_instance(self, instance_id: str, reason: str = "") -> Dict[str, Any]:
        """Stop a sequence instance."""
        instance = self._instances.get(instance_id)
        if not instance:
            return {"error": f"Instance not found: {instance_id}"}

        instance.status = SequenceStatus.STOPPED
        instance.completed_at = datetime.utcnow().isoformat()
        instance.notes = f"Stopped: {reason}"
        return {"instance_id": instance_id, "status": "stopped", "reason": reason}

    def select_connection_accepted_sequence(
        self,
        prospect_segment: str,
        prospect_title: Optional[str] = None,
        prospect_company: Optional[str] = None
    ) -> str:
        """
        Select the appropriate connection_accepted sequence based on prospect segment.

        Args:
            prospect_segment: One of 'vc', 'enterprise', 'ecosystem', 'general'
            prospect_title: Optional title for better matching
            prospect_company: Optional company for better matching

        Returns:
            Name of the sequence to use
        """
        # Direct segment mapping
        segment_map = {
            "vc": "connection_accepted_vc",
            "investor": "connection_accepted_vc",
            "partner_vc": "connection_accepted_vc",
            "enterprise": "connection_accepted_enterprise",
            "enterprise_leader": "connection_accepted_enterprise",
            "ecosystem": "connection_accepted_ecosystem",
            "google": "connection_accepted_ecosystem",
            "microsoft": "connection_accepted_ecosystem",
            "general": "connection_accepted_general",
        }

        # Check direct mapping
        if prospect_segment.lower() in segment_map:
            return segment_map[prospect_segment.lower()]

        # Title-based inference
        if prospect_title:
            title_lower = prospect_title.lower()
            if any(t in title_lower for t in ["partner", "principal", "investor", "vc", "venture"]):
                return "connection_accepted_vc"
            if any(t in title_lower for t in ["vp", "director", "head", "chief", "cto", "ceo", "coo"]):
                return "connection_accepted_enterprise"
            if any(t in title_lower for t in ["program", "startup", "advocate", "ecosystem"]):
                return "connection_accepted_ecosystem"

        # Company-based inference
        if prospect_company:
            company_lower = prospect_company.lower()
            if any(c in company_lower for c in ["venture", "capital", "partners", "a16z", "sequoia", "greylock"]):
                return "connection_accepted_vc"
            if any(c in company_lower for c in ["google", "microsoft", "azure", "gcp"]):
                return "connection_accepted_ecosystem"

        # Default to general
        return "connection_accepted_general"

    def get_metrics(self) -> Dict[str, Any]:
        """Get outreach engine metrics."""
        total = len(self._instances)
        by_status = {}
        by_sequence = {}

        for instance in self._instances.values():
            status = instance.status.value
            by_status[status] = by_status.get(status, 0) + 1

            seq = instance.sequence_id
            by_sequence[seq] = by_sequence.get(seq, 0) + 1

        return {
            "total_instances": total,
            "by_status": by_status,
            "by_sequence": by_sequence,
            "sequences_registered": len(self._sequences),
            "due_touchpoints": len(self.list_due_touchpoints()),
        }
