"""Core FSM State Management for FREQ AI SOL"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
import structlog

logger = structlog.get_logger(__name__)


class FSMState(Enum):
    """Finite State Machine states for FREQ AI orchestration"""
    IDLE = "IDLE"
    DIRECTIVE = "DIRECTIVE"
    VALIDATION = "VALIDATION"
    QUORUM = "QUORUM"
    EXECUTION = "EXECUTION"
    AUDIT = "AUDIT"
    COMPLETE = "COMPLETE"
    VETO = "VETO"


class FSMTransition:
    """Represents a state transition with metadata"""
    
    def __init__(
        self,
        from_state: FSMState,
        to_state: FSMState,
        timestamp: datetime,
        context: Optional[Dict[str, Any]] = None
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.timestamp = timestamp
        self.context = context or {}


class FSMController:
    """
    Finite State Machine controller for FREQ AI orchestration flow
    
    State Flow:
    IDLE → DIRECTIVE → VALIDATION → QUORUM → EXECUTION → AUDIT → COMPLETE
                                                              ↓
                                                            VETO
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        FSMState.IDLE: [FSMState.DIRECTIVE],
        FSMState.DIRECTIVE: [FSMState.VALIDATION, FSMState.VETO],
        FSMState.VALIDATION: [FSMState.QUORUM, FSMState.VETO],
        FSMState.QUORUM: [FSMState.EXECUTION, FSMState.VETO],
        FSMState.EXECUTION: [FSMState.AUDIT, FSMState.VETO],
        FSMState.AUDIT: [FSMState.COMPLETE, FSMState.VETO],
        FSMState.COMPLETE: [FSMState.IDLE],
        FSMState.VETO: [FSMState.IDLE],
    }
    
    def __init__(self, timeout_ms: int = 30000):
        """
        Initialize FSM Controller
        
        Args:
            timeout_ms: Maximum time allowed for a complete cycle (default 30 seconds)
        """
        self.current_state = FSMState.IDLE
        self.timeout_ms = timeout_ms
        self.transition_history: List[FSMTransition] = []
        self.start_time: Optional[datetime] = None
        self.context: Dict[str, Any] = {}
        
    def can_transition(self, to_state: FSMState) -> bool:
        """
        Check if transition to target state is valid
        
        Args:
            to_state: Target state to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_next_states = self.VALID_TRANSITIONS.get(self.current_state, [])
        return to_state in valid_next_states
    
    async def transition(
        self,
        to_state: FSMState,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Transition to a new state
        
        Args:
            to_state: Target state to transition to
            context: Optional context data for the transition
            
        Returns:
            True if transition successful, False otherwise
        """
        if not self.can_transition(to_state):
            logger.error(
                "invalid_state_transition",
                from_state=self.current_state.value,
                to_state=to_state.value
            )
            return False
        
        # Record transition
        transition = FSMTransition(
            from_state=self.current_state,
            to_state=to_state,
            timestamp=datetime.utcnow(),
            context=context
        )
        self.transition_history.append(transition)
        
        # Update state
        previous_state = self.current_state
        self.current_state = to_state
        
        # Update context
        if context:
            self.context.update(context)
        
        # Set start time on first transition from IDLE
        if previous_state == FSMState.IDLE and to_state == FSMState.DIRECTIVE:
            self.start_time = datetime.utcnow()
        
        logger.info(
            "state_transition",
            from_state=previous_state.value,
            to_state=to_state.value,
            context=context
        )
        
        return True
    
    def get_elapsed_time_ms(self) -> Optional[int]:
        """
        Get elapsed time since orchestration started
        
        Returns:
            Elapsed time in milliseconds, or None if not started
        """
        if not self.start_time:
            return None
        
        elapsed = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        return int(elapsed)
    
    def is_timeout(self) -> bool:
        """
        Check if orchestration has exceeded timeout
        
        Returns:
            True if timeout exceeded, False otherwise
        """
        elapsed = self.get_elapsed_time_ms()
        if elapsed is None:
            return False
        return elapsed > self.timeout_ms
    
    def reset(self):
        """Reset FSM to initial state"""
        self.current_state = FSMState.IDLE
        self.transition_history = []
        self.start_time = None
        self.context = {}
        logger.info("fsm_reset")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get summary of current FSM state
        
        Returns:
            Dictionary with state summary
        """
        return {
            "current_state": self.current_state.value,
            "elapsed_time_ms": self.get_elapsed_time_ms(),
            "is_timeout": self.is_timeout(),
            "transition_count": len(self.transition_history),
            "context": self.context
        }
