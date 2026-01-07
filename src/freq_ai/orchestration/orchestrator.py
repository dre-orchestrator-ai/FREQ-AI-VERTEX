"""Main SOL Orchestrator - Natural language orchestration system"""

from typing import Optional, Dict, Any, List
import asyncio
import uuid
from datetime import datetime
import structlog

from ..core.fsm import FSMController, FSMState
from ..core.freq_law import FREQLawEnforcer, FREQLawViolation
from ..nodes.gemini_nodes import (
    StrategicOperationsNode,
    SupplyChainIntelligenceNode,
    LegacyArchitectNode,
    GovernanceEngineNode,
    ExecutiveAutomationNode,
    OptimalIntelligenceNode,
    ElementDesignNode
)
from ..verticals.vertical_context import Vertical, VerticalContext

logger = structlog.get_logger(__name__)


class OrchestrationResult:
    """Result of an orchestration session"""
    
    def __init__(
        self,
        session_id: str,
        directive: str,
        vertical: Optional[str],
        success: bool,
        final_state: FSMState,
        elapsed_time_ms: int,
        node_responses: List[Dict[str, Any]],
        consensus_result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        self.session_id = session_id
        self.directive = directive
        self.vertical = vertical
        self.success = success
        self.final_state = final_state
        self.elapsed_time_ms = elapsed_time_ms
        self.node_responses = node_responses
        self.consensus_result = consensus_result
        self.error = error
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "session_id": self.session_id,
            "directive": self.directive,
            "vertical": self.vertical,
            "success": self.success,
            "final_state": self.final_state.value,
            "elapsed_time_ms": self.elapsed_time_ms,
            "node_responses": self.node_responses,
            "consensus_result": self.consensus_result,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


class SOLOrchestrator:
    """
    Sophisticated Operational Lattice (SOL) Orchestrator
    
    Natural language orchestration system with:
    - 7 Gemini nodes for multi-perspective analysis
    - FSM state control (IDLE→DIRECTIVE→VALIDATION→QUORUM→EXECUTION→AUDIT→COMPLETE/VETO)
    - FREQ LAW compliance (<2000ms, k=3 consensus, BigQuery audit)
    - 5 vertical domain support
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        max_response_time_ms: int = 2000,
        consensus_k: int = 3,
        audit_enabled: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize SOL Orchestrator
        
        Args:
            project_id: Google Cloud project ID
            location: GCP location
            max_response_time_ms: Maximum response time (FREQ LAW)
            consensus_k: Consensus requirement (FREQ LAW)
            audit_enabled: Enable BigQuery audit trails
            config: Optional configuration dictionary
        """
        self.project_id = project_id
        self.location = location
        self.config = config or {}
        
        # Initialize FSM controller
        self.fsm = FSMController(timeout_ms=30000)
        
        # Initialize FREQ LAW enforcer
        self.freq_law = FREQLawEnforcer(
            max_response_time_ms=max_response_time_ms,
            consensus_k=consensus_k,
            audit_enabled=audit_enabled,
            project_id=project_id
        )
        
        # Initialize 7 Gemini nodes
        node_kwargs = {
            "project_id": project_id,
            "location": location
        }
        
        self.nodes = {
            "strategic_operations": StrategicOperationsNode(**node_kwargs),
            "supply_chain_intelligence": SupplyChainIntelligenceNode(**node_kwargs),
            "legacy_architect": LegacyArchitectNode(**node_kwargs),
            "governance_engine": GovernanceEngineNode(**node_kwargs),
            "executive_automation": ExecutiveAutomationNode(**node_kwargs),
            "optimal_intelligence": OptimalIntelligenceNode(**node_kwargs),
            "element_design": ElementDesignNode(**node_kwargs)
        }
        
        logger.info(
            "sol_orchestrator_initialized",
            nodes=len(self.nodes),
            project_id=project_id
        )
    
    async def orchestrate(
        self,
        directive: str,
        vertical: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """
        Orchestrate a natural language directive through the SOL
        
        Args:
            directive: Natural language directive to execute
            vertical: Target vertical domain (maritime, agriculture, etc.)
            context: Additional context for processing
            
        Returns:
            OrchestrationResult with execution details
        """
        session_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(
            "orchestration_started",
            session_id=session_id,
            directive=directive[:100],
            vertical=vertical
        )
        
        try:
            # Validate vertical if provided
            vertical_enum = None
            if vertical:
                vertical_enum = VerticalContext.from_string(vertical)
                if not vertical_enum:
                    raise ValueError(f"Invalid vertical: {vertical}")
            
            # IDLE → DIRECTIVE
            await self.fsm.transition(FSMState.DIRECTIVE, {"directive": directive})
            await self.freq_law.audit_event(
                "STATE_TRANSITION",
                {"state": "DIRECTIVE", "directive": directive},
                session_id
            )
            
            # DIRECTIVE → VALIDATION
            await self.fsm.transition(FSMState.VALIDATION)
            node_responses = await self._validate_with_nodes(
                directive, vertical, context
            )
            
            # VALIDATION → QUORUM
            await self.fsm.transition(FSMState.QUORUM)
            consensus_result = await self._achieve_quorum(node_responses, session_id)
            
            if not consensus_result["passed"]:
                # Consensus failed → VETO
                await self.fsm.transition(FSMState.VETO)
                await self.freq_law.audit_event(
                    "VETO",
                    {"reason": "consensus_failed", "votes": consensus_result},
                    session_id
                )
                
                elapsed_ms = self.fsm.get_elapsed_time_ms()
                
                return OrchestrationResult(
                    session_id=session_id,
                    directive=directive,
                    vertical=vertical,
                    success=False,
                    final_state=FSMState.VETO,
                    elapsed_time_ms=elapsed_ms,
                    node_responses=node_responses,
                    consensus_result=consensus_result,
                    error="Consensus not achieved"
                )
            
            # QUORUM → EXECUTION
            await self.fsm.transition(FSMState.EXECUTION)
            execution_result = await self._execute_directive(
                directive, vertical, context, session_id
            )
            
            # EXECUTION → AUDIT
            await self.fsm.transition(FSMState.AUDIT)
            await self._audit_execution(execution_result, session_id)
            
            # AUDIT → COMPLETE
            await self.fsm.transition(FSMState.COMPLETE)
            
            elapsed_ms = self.fsm.get_elapsed_time_ms()
            
            result = OrchestrationResult(
                session_id=session_id,
                directive=directive,
                vertical=vertical,
                success=True,
                final_state=FSMState.COMPLETE,
                elapsed_time_ms=elapsed_ms,
                node_responses=node_responses,
                consensus_result=consensus_result
            )
            
            logger.info(
                "orchestration_completed",
                session_id=session_id,
                elapsed_ms=elapsed_ms,
                final_state="COMPLETE"
            )
            
            # Reset FSM for next orchestration
            self.fsm.reset()
            
            return result
            
        except FREQLawViolation as e:
            logger.error("freq_law_violation", session_id=session_id, error=str(e))
            elapsed_ms = self.fsm.get_elapsed_time_ms() or 0
            self.fsm.reset()
            
            return OrchestrationResult(
                session_id=session_id,
                directive=directive,
                vertical=vertical,
                success=False,
                final_state=self.fsm.current_state,
                elapsed_time_ms=elapsed_ms,
                node_responses=[],
                error=f"FREQ LAW violation: {str(e)}"
            )
            
        except Exception as e:
            logger.error("orchestration_error", session_id=session_id, error=str(e))
            elapsed_ms = self.fsm.get_elapsed_time_ms() or 0
            self.fsm.reset()
            
            return OrchestrationResult(
                session_id=session_id,
                directive=directive,
                vertical=vertical,
                success=False,
                final_state=self.fsm.current_state,
                elapsed_time_ms=elapsed_ms,
                node_responses=[],
                error=str(e)
            )
    
    async def _validate_with_nodes(
        self,
        directive: str,
        vertical: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate directive with all nodes in parallel
        
        Args:
            directive: Natural language directive
            vertical: Target vertical
            context: Additional context
            
        Returns:
            List of node responses
        """
        async def process_with_timeout(node):
            return await self.freq_law.enforce_response_time(
                f"node_{node.node_name}",
                node.process,
                directive,
                context,
                vertical
            )
        
        # Process all nodes in parallel
        tasks = [process_with_timeout(node) for node in self.nodes.values()]
        node_responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error responses
        processed_responses = []
        for i, response in enumerate(node_responses):
            if isinstance(response, Exception):
                node_name = list(self.nodes.values())[i].node_name
                processed_responses.append({
                    "node_name": node_name,
                    "success": False,
                    "error": str(response),
                    "vote": False
                })
            else:
                processed_responses.append(response)
        
        return processed_responses
    
    async def _achieve_quorum(
        self,
        node_responses: List[Dict[str, Any]],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Achieve k=3 consensus from node votes
        
        Args:
            node_responses: List of node responses with votes
            session_id: Session identifier
            
        Returns:
            Dictionary with consensus result
        """
        node_votes = {
            resp["node_name"]: resp.get("vote", False)
            for resp in node_responses
        }
        
        consensus = await self.freq_law.achieve_consensus(
            decision_id=session_id,
            node_votes=node_votes
        )
        
        return {
            "passed": consensus.passed,
            "positive_votes": sum(1 for v in consensus.votes if v),
            "required_k": consensus.required_k,
            "node_votes": consensus.node_votes
        }
    
    async def _execute_directive(
        self,
        directive: str,
        vertical: Optional[str],
        context: Optional[Dict[str, Any]],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute the approved directive
        
        Args:
            directive: Natural language directive
            vertical: Target vertical
            context: Additional context
            session_id: Session identifier
            
        Returns:
            Execution result
        """
        logger.info("executing_directive", session_id=session_id, directive=directive[:100])
        
        # In a real implementation, this would execute the actual directive
        # For now, we'll simulate execution
        await asyncio.sleep(0.1)  # Simulate work
        
        execution_result = {
            "status": "executed",
            "directive": directive,
            "vertical": vertical,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.freq_law.audit_event(
            "EXECUTION",
            execution_result,
            session_id
        )
        
        return execution_result
    
    async def _audit_execution(
        self,
        execution_result: Dict[str, Any],
        session_id: str
    ):
        """
        Audit the execution result
        
        Args:
            execution_result: Result of execution
            session_id: Session identifier
        """
        await self.freq_law.audit_event(
            "AUDIT",
            {
                "execution_result": execution_result,
                "audit_timestamp": datetime.utcnow().isoformat()
            },
            session_id
        )
        
        logger.info("execution_audited", session_id=session_id)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get orchestrator status
        
        Returns:
            Dictionary with status information
        """
        return {
            "nodes": {name: node.get_info() for name, node in self.nodes.items()},
            "fsm_state": self.fsm.get_state_summary(),
            "freq_law": self.freq_law.get_metrics(),
            "verticals": [v.value for v in Vertical]
        }
