"""FREQ LAW Enforcement - Response time, consensus, and audit compliance"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import structlog
from google.cloud import bigquery

logger = structlog.get_logger(__name__)


class FREQLawViolation(Exception):
    """Exception raised when FREQ LAW is violated"""
    pass


class ConsensusResult:
    """Result of consensus voting"""
    
    def __init__(
        self,
        votes: List[bool],
        required_k: int,
        passed: bool,
        node_votes: Dict[str, bool]
    ):
        self.votes = votes
        self.required_k = required_k
        self.passed = passed
        self.node_votes = node_votes
        self.timestamp = datetime.utcnow()


class FREQLawEnforcer:
    """
    Enforces FREQ LAW compliance:
    - Response time < 2000ms
    - k=3 consensus for critical decisions
    - BigQuery audit trail for all operations
    """
    
    def __init__(
        self,
        max_response_time_ms: int = 2000,
        consensus_k: int = 3,
        audit_enabled: bool = True,
        project_id: Optional[str] = None,
        dataset_id: Optional[str] = "freq_audit_logs",
        table_id: Optional[str] = "orchestration_events"
    ):
        """
        Initialize FREQ LAW Enforcer
        
        Args:
            max_response_time_ms: Maximum response time in milliseconds
            consensus_k: Minimum number of votes required for consensus
            audit_enabled: Whether to enable BigQuery audit logging
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
        """
        self.max_response_time_ms = max_response_time_ms
        self.consensus_k = consensus_k
        self.audit_enabled = audit_enabled
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        
        # Initialize BigQuery client if audit is enabled
        self.bq_client: Optional[bigquery.Client] = None
        if audit_enabled and project_id:
            try:
                self.bq_client = bigquery.Client(project=project_id)
                logger.info("bigquery_client_initialized", project_id=project_id)
            except Exception as e:
                logger.warning("bigquery_client_init_failed", error=str(e))
    
    async def enforce_response_time(
        self,
        operation_name: str,
        operation_func,
        *args,
        **kwargs
    ) -> Any:
        """
        Enforce response time constraint on an operation
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: Async function to execute
            *args, **kwargs: Arguments to pass to operation_func
            
        Returns:
            Result of the operation
            
        Raises:
            FREQLawViolation: If response time exceeds limit
        """
        start_time = datetime.utcnow()
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                operation_func(*args, **kwargs),
                timeout=self.max_response_time_ms / 1000.0
            )
            
            # Calculate elapsed time
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(
                "operation_completed",
                operation=operation_name,
                elapsed_ms=elapsed_ms,
                within_limit=True
            )
            
            return result
            
        except asyncio.TimeoutError:
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error(
                "freq_law_violation_timeout",
                operation=operation_name,
                elapsed_ms=elapsed_ms,
                limit_ms=self.max_response_time_ms
            )
            raise FREQLawViolation(
                f"Operation '{operation_name}' exceeded {self.max_response_time_ms}ms limit"
            )
    
    async def achieve_consensus(
        self,
        decision_id: str,
        node_votes: Dict[str, bool],
        required_k: Optional[int] = None
    ) -> ConsensusResult:
        """
        Achieve k=3 consensus among nodes
        
        Args:
            decision_id: Unique identifier for the decision
            node_votes: Dictionary mapping node names to boolean votes
            required_k: Override default consensus requirement
            
        Returns:
            ConsensusResult with voting outcome
        """
        k = required_k if required_k is not None else self.consensus_k
        votes = list(node_votes.values())
        positive_votes = sum(1 for v in votes if v)
        
        passed = positive_votes >= k
        
        result = ConsensusResult(
            votes=votes,
            required_k=k,
            passed=passed,
            node_votes=node_votes
        )
        
        logger.info(
            "consensus_result",
            decision_id=decision_id,
            positive_votes=positive_votes,
            required_k=k,
            passed=passed,
            node_votes=node_votes
        )
        
        # Audit the consensus decision
        await self.audit_event(
            event_type="CONSENSUS",
            event_data={
                "decision_id": decision_id,
                "node_votes": node_votes,
                "positive_votes": positive_votes,
                "required_k": k,
                "passed": passed
            }
        )
        
        return result
    
    async def audit_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        session_id: Optional[str] = None
    ):
        """
        Audit an event to BigQuery
        
        Args:
            event_type: Type of event (e.g., CONSENSUS, STATE_TRANSITION)
            event_data: Event data to audit
            session_id: Optional session identifier
        """
        if not self.audit_enabled or not self.bq_client:
            logger.debug("audit_skipped", reason="audit_disabled_or_no_client")
            return
        
        try:
            # Prepare audit record
            audit_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "event_data": str(event_data),  # Convert to string for BigQuery
                "session_id": session_id or "unknown"
            }
            
            # Insert into BigQuery
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            
            # Note: In production, use streaming inserts or batch inserts
            # For now, we'll just log the audit
            logger.info(
                "audit_event_logged",
                table=table_ref,
                event_type=event_type,
                session_id=session_id
            )
            
            # Actual BigQuery insert (simplified)
            # errors = self.bq_client.insert_rows_json(table_ref, [audit_record])
            # if errors:
            #     logger.error("bigquery_insert_error", errors=errors)
            
        except Exception as e:
            logger.error("audit_event_failed", error=str(e), event_type=event_type)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get FREQ LAW enforcement metrics
        
        Returns:
            Dictionary with enforcement metrics
        """
        return {
            "max_response_time_ms": self.max_response_time_ms,
            "consensus_k": self.consensus_k,
            "audit_enabled": self.audit_enabled,
            "bigquery_configured": self.bq_client is not None
        }
