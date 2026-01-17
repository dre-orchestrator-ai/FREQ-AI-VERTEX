"""
FREQ AI API Routes

RESTful API endpoint definitions for the FREQ AI Command Center.
Framework-agnostic route definitions that can be adapted to FastAPI, Flask, etc.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import logging

from .schemas import (
    APIResponse,
    SovereignIntentRequest,
    LatticeStatusResponse,
    MissionResponse,
    ProviderStatusResponse,
    FreqComplianceResponse,
    AuditQueryRequest,
)
from ..ui.components import (
    LatticeStatusWidget,
    FreqComplianceWidget,
    MissionCard,
    MissionList,
    AuditTimeline,
)
from ..platform import UnifiedModelInterface

logger = logging.getLogger(__name__)


@dataclass
class APIRoute:
    """Definition of an API route."""

    method: str  # GET, POST, PUT, DELETE
    path: str
    handler: str  # Handler method name
    description: str
    tags: List[str]
    auth_required: bool = True


class FreqAPIController:
    """
    FREQ AI API Controller

    Provides handlers for all Command Center API endpoints.
    """

    def __init__(
        self,
        model_interface: Optional[UnifiedModelInterface] = None,
        lattice_widget: Optional[LatticeStatusWidget] = None,
        compliance_widget: Optional[FreqComplianceWidget] = None,
        mission_list: Optional[MissionList] = None,
        audit_timeline: Optional[AuditTimeline] = None,
    ):
        self.model_interface = model_interface
        self.lattice_widget = lattice_widget or LatticeStatusWidget()
        self.compliance_widget = compliance_widget or FreqComplianceWidget()
        self.mission_list = mission_list or MissionList()
        self.audit_timeline = audit_timeline or AuditTimeline()

    # =========================================================================
    # INTENT ENDPOINTS
    # =========================================================================

    async def submit_intent(self, request: SovereignIntentRequest) -> APIResponse:
        """
        Submit a Sovereign Intent directive.

        POST /api/v1/intent

        The directive is processed by the Strategic Synthesis Core (SSC)
        and decomposed into a DAG of tasks for execution.
        """
        try:
            # Validate request
            if not request.directive or len(request.directive.strip()) == 0:
                return APIResponse(
                    success=False,
                    error="Directive cannot be empty",
                    error_code="INVALID_DIRECTIVE",
                )

            # Create mission from directive
            mission_id = f"mission-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            mission = MissionCard(
                mission_id=mission_id,
                name=request.directive[:50],
                description=request.directive,
                status="queued",
                priority=request.priority,
            )

            self.mission_list.add(mission)

            # If dry run, return without execution
            if request.dry_run:
                return APIResponse(
                    success=True,
                    data={
                        "missionId": mission_id,
                        "status": "dry_run",
                        "message": "Directive validated successfully (dry run)",
                    },
                    request_id=request.request_id,
                )

            # TODO: Submit to SSC for processing
            # This would invoke the actual lattice orchestration

            return APIResponse(
                success=True,
                data={
                    "missionId": mission_id,
                    "status": "accepted",
                    "message": "Directive submitted for processing",
                },
                request_id=request.request_id,
            )

        except Exception as e:
            logger.error(f"Failed to submit intent: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                error_code="INTENT_SUBMISSION_FAILED",
                request_id=request.request_id,
            )

    # =========================================================================
    # LATTICE ENDPOINTS
    # =========================================================================

    async def get_lattice_status(self) -> APIResponse:
        """
        Get current lattice node statuses.

        GET /api/v1/lattice/status
        """
        try:
            widget_data = self.lattice_widget.to_dict()

            response = LatticeStatusResponse(
                nodes=widget_data["nodes"],
                aggregates=widget_data["aggregates"],
                freq_compliant=widget_data["aggregates"]["freqCompliant"],
            )

            return APIResponse(
                success=True,
                data=response.to_dict(),
            )

        except Exception as e:
            logger.error(f"Failed to get lattice status: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                error_code="LATTICE_STATUS_FAILED",
            )

    async def get_provider_status(self) -> APIResponse:
        """
        Get AI provider statuses.

        GET /api/v1/providers/status
        """
        try:
            if self.model_interface:
                provider_data = self.model_interface.get_provider_status()
            else:
                # Mock data for development
                provider_data = {
                    "aws_bedrock": {
                        "status": "healthy",
                        "is_healthy": True,
                        "available_models": ["Claude Opus 4.5", "Claude Sonnet 4.5"],
                    },
                    "vertex_ai": {
                        "status": "healthy",
                        "is_healthy": True,
                        "available_models": ["Gemini 3.0 Pro", "Gemini 3.0 Flash"],
                    },
                }

            healthy = sum(1 for p in provider_data.values() if p.get("is_healthy"))

            response = ProviderStatusResponse(
                providers=provider_data,
                primary_provider="aws_bedrock",
                healthy_count=healthy,
                total_count=len(provider_data),
            )

            return APIResponse(
                success=True,
                data=response.to_dict(),
            )

        except Exception as e:
            logger.error(f"Failed to get provider status: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                error_code="PROVIDER_STATUS_FAILED",
            )

    # =========================================================================
    # COMPLIANCE ENDPOINTS
    # =========================================================================

    async def get_freq_compliance(self) -> APIResponse:
        """
        Get FREQ LAW compliance status.

        GET /api/v1/compliance
        """
        try:
            widget_data = self.compliance_widget.to_dict()

            response = FreqComplianceResponse(
                metrics=widget_data["metrics"],
                overall_status=widget_data["overallStatus"],
                is_compliant=widget_data["isCompliant"],
                violations=widget_data["violations"],
            )

            return APIResponse(
                success=True,
                data=response.to_dict(),
            )

        except Exception as e:
            logger.error(f"Failed to get compliance status: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                error_code="COMPLIANCE_STATUS_FAILED",
            )

    # =========================================================================
    # MISSION ENDPOINTS
    # =========================================================================

    async def get_missions(
        self,
        status: Optional[str] = None,
        vector: Optional[str] = None,
    ) -> APIResponse:
        """
        Get list of missions.

        GET /api/v1/missions
        """
        try:
            missions = self.mission_list.missions

            if status:
                missions = [m for m in missions if m.status.value == status]
            if vector:
                missions = [m for m in missions if m.vector.value == vector]

            return APIResponse(
                success=True,
                data={
                    "missions": [m.to_dict() for m in missions],
                    "total": len(missions),
                    "active": len(self.mission_list.get_active()),
                },
            )

        except Exception as e:
            logger.error(f"Failed to get missions: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                error_code="MISSIONS_FETCH_FAILED",
            )

    async def get_mission(self, mission_id: str) -> APIResponse:
        """
        Get a specific mission by ID.

        GET /api/v1/missions/{mission_id}
        """
        try:
            mission = self.mission_list.get_by_id(mission_id)

            if not mission:
                return APIResponse(
                    success=False,
                    error=f"Mission not found: {mission_id}",
                    error_code="MISSION_NOT_FOUND",
                )

            return APIResponse(
                success=True,
                data=mission.to_dict(),
            )

        except Exception as e:
            logger.error(f"Failed to get mission {mission_id}: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                error_code="MISSION_FETCH_FAILED",
            )

    async def cancel_mission(self, mission_id: str) -> APIResponse:
        """
        Cancel an active mission.

        POST /api/v1/missions/{mission_id}/cancel
        """
        try:
            mission = self.mission_list.get_by_id(mission_id)

            if not mission:
                return APIResponse(
                    success=False,
                    error=f"Mission not found: {mission_id}",
                    error_code="MISSION_NOT_FOUND",
                )

            # TODO: Implement actual cancellation logic
            mission.status = "cancelled"

            return APIResponse(
                success=True,
                data={"missionId": mission_id, "status": "cancelled"},
            )

        except Exception as e:
            logger.error(f"Failed to cancel mission {mission_id}: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                error_code="MISSION_CANCEL_FAILED",
            )

    # =========================================================================
    # AUDIT ENDPOINTS
    # =========================================================================

    async def query_audit_trail(self, request: AuditQueryRequest) -> APIResponse:
        """
        Query the Cognitive Audit Trail.

        POST /api/v1/audit/query
        """
        try:
            # Convert request to filter
            from ..ui.components.audit_timeline import AuditFilter

            audit_filter = AuditFilter(
                start_time=request.start_time,
                end_time=request.end_time,
                node_types=request.node_types,
                mission_id=request.mission_id,
                success_only=request.success_only,
                vetoed_only=request.vetoed_only,
                min_latency_ms=request.min_latency_ms,
                search_text=request.search_text,
            )

            entries = self.audit_timeline.get_entries(
                filter_criteria=audit_filter,
                page=request.page,
            )

            return APIResponse(
                success=True,
                data={
                    "entries": [e.to_dict() for e in entries],
                    "pagination": {
                        "page": request.page,
                        "pageSize": request.page_size,
                        "totalEntries": self.audit_timeline.total_entries,
                    },
                    "statistics": {
                        "successRate": self.audit_timeline.success_rate,
                        "averageLatencyMs": self.audit_timeline.average_latency_ms,
                    },
                },
            )

        except Exception as e:
            logger.error(f"Failed to query audit trail: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                error_code="AUDIT_QUERY_FAILED",
            )

    async def export_audit_trail(
        self,
        format: str = "json",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> APIResponse:
        """
        Export audit trail data.

        GET /api/v1/audit/export
        """
        try:
            if format == "bigquery":
                data = self.audit_timeline.export_to_bigquery_format()
            else:
                data = self.audit_timeline.to_dict()

            return APIResponse(
                success=True,
                data=data,
            )

        except Exception as e:
            logger.error(f"Failed to export audit trail: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                error_code="AUDIT_EXPORT_FAILED",
            )

    # =========================================================================
    # HEALTH ENDPOINTS
    # =========================================================================

    async def health_check(self) -> APIResponse:
        """
        System health check.

        GET /api/v1/health
        """
        return APIResponse(
            success=True,
            data={
                "status": "healthy",
                "version": "2.0.0",
                "lattice": self.lattice_widget.get_overall_health().value,
                "freqCompliant": self.lattice_widget.is_freq_compliant(),
            },
        )

    async def readiness_check(self) -> APIResponse:
        """
        Kubernetes readiness probe.

        GET /api/v1/ready
        """
        # Check if core components are ready
        is_ready = (
            self.lattice_widget.healthy_nodes >= 3  # Quorum available
            and self.lattice_widget.is_freq_compliant()
        )

        return APIResponse(
            success=is_ready,
            data={"ready": is_ready},
        )


def create_api_routes() -> List[APIRoute]:
    """
    Create the list of API route definitions.

    These can be used to configure any web framework.
    """
    return [
        # Intent
        APIRoute(
            method="POST",
            path="/api/v1/intent",
            handler="submit_intent",
            description="Submit a Sovereign Intent directive",
            tags=["Intent"],
        ),

        # Lattice
        APIRoute(
            method="GET",
            path="/api/v1/lattice/status",
            handler="get_lattice_status",
            description="Get lattice node statuses",
            tags=["Lattice"],
        ),
        APIRoute(
            method="GET",
            path="/api/v1/providers/status",
            handler="get_provider_status",
            description="Get AI provider statuses",
            tags=["Lattice"],
        ),

        # Compliance
        APIRoute(
            method="GET",
            path="/api/v1/compliance",
            handler="get_freq_compliance",
            description="Get FREQ LAW compliance status",
            tags=["Compliance"],
        ),

        # Missions
        APIRoute(
            method="GET",
            path="/api/v1/missions",
            handler="get_missions",
            description="Get list of missions",
            tags=["Missions"],
        ),
        APIRoute(
            method="GET",
            path="/api/v1/missions/{mission_id}",
            handler="get_mission",
            description="Get a specific mission",
            tags=["Missions"],
        ),
        APIRoute(
            method="POST",
            path="/api/v1/missions/{mission_id}/cancel",
            handler="cancel_mission",
            description="Cancel an active mission",
            tags=["Missions"],
        ),

        # Audit
        APIRoute(
            method="POST",
            path="/api/v1/audit/query",
            handler="query_audit_trail",
            description="Query the Cognitive Audit Trail",
            tags=["Audit"],
        ),
        APIRoute(
            method="GET",
            path="/api/v1/audit/export",
            handler="export_audit_trail",
            description="Export audit trail data",
            tags=["Audit"],
        ),

        # Health
        APIRoute(
            method="GET",
            path="/api/v1/health",
            handler="health_check",
            description="System health check",
            tags=["Health"],
            auth_required=False,
        ),
        APIRoute(
            method="GET",
            path="/api/v1/ready",
            handler="readiness_check",
            description="Kubernetes readiness probe",
            tags=["Health"],
            auth_required=False,
        ),
    ]
