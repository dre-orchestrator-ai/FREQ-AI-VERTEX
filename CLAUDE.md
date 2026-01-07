# CLAUDE.md - AI Assistant Guide for FREQ-AI-VERTEX

**Version:** 0.1.0
**Last Updated:** 2026-01-07
**Purpose:** Comprehensive guide for AI assistants working on the Sophisticated Operational Lattice (SOL) system

---

## Table of Contents

1. [System Identity & Overview](#system-identity--overview)
2. [Architecture & Core Concepts](#architecture--core-concepts)
3. [Directory Structure](#directory-structure)
4. [Development Environment](#development-environment)
5. [Code Conventions & Style](#code-conventions--style)
6. [Testing Practices](#testing-practices)
7. [FREQ LAW Governance](#freq-law-governance)
8. [Key Files Reference](#key-files-reference)
9. [Common Development Tasks](#common-development-tasks)
10. [Deployment & Configuration](#deployment--configuration)
11. [Important Guidelines for AI Assistants](#important-guidelines-for-ai-assistants)

---

## System Identity & Overview

### What is SOL?

**SOL (Sophisticated Operational Lattice)** is a distributed AI orchestration system deployed on Google Cloud Vertex AI Agent Builder using Gemini substrates. It's designed for legacy modernization across regulated industries with strict governance requirements.

### Key Characteristics

- **Architecture:** Distributed lattice of 7 specialized nodes with message-passing communication
- **Governance:** Rigid FREQ LAW enforcement with VETO authority
- **Consensus:** k=3 quorum voting for critical operations
- **Compliance:** All operations logged to BigQuery with full audit trail
- **Tech Stack:** Pure Python 3.9+ with Google Cloud Platform integration
- **Status:** Alpha (v0.1.0), actively developing

### Repository Information

- **GitHub:** https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX
- **Package Name:** freq-ai-sol
- **License:** MIT
- **Python Versions:** 3.9, 3.10, 3.11, 3.12

---

## Architecture & Core Concepts

### The 7 Lattice Nodes

Each node is a specialized component with distinct responsibilities:

| Node | Type | Purpose | Key Methods |
|------|------|---------|-------------|
| **StrategicOP** | Mission Coordination | High-level strategic planning, cross-node orchestration, priority management | `set_mission()`, `get_mission_status()`, `coordinate_nodes()` |
| **SPCI** | Continuous Improvement | Performance metrics, A/B testing, learning loops, evolutionary optimization | `track_metric()`, `analyze_performance()`, `run_experiment()` |
| **LegacyArchitect** | System Translation | Protocol translation, data transformation, legacy API adaptation, migration planning | `translate_protocol()`, `adapt_legacy_api()`, `plan_migration()` |
| **GOVEngine** | Governance & Compliance | FREQ LAW enforcement, k=3 quorum validation, absolute VETO authority | `validate_compliance()`, `exercise_veto()`, `check_freq_law()` |
| **ExecAutomate** | Workflow Execution | Multi-step workflows, parallel/sequential execution, error handling | `execute_workflow()`, `add_step()`, `get_status()` |
| **OptimalIntel** | Decision Support | Data aggregation, predictive modeling, recommendations, dashboards | `aggregate_data()`, `generate_recommendation()`, `create_dashboard()` |
| **ElementDesign** | Artifact Generation | Schema definition, artifact generation, template management | `define_schema()`, `generate_artifact()`, `apply_template()` |

### Core Architectural Patterns

#### 1. Message-Passing Communication

```python
# Message structure
@dataclass
class NodeMessage:
    id: str                      # UUID for tracking
    source_node: str             # Sender node ID
    target_node: str             # Receiver node ID
    operation: str               # Operation name
    payload: Dict[str, Any]      # Data payload
    timestamp: str               # ISO 8601 timestamp
    requires_quorum: bool        # Whether k=3 quorum needed
```

**Pattern:** Nodes communicate through immutable messages, maintaining history for audit trails.

#### 2. Response Protocol

```python
@dataclass
class NodeResponse:
    message_id: str              # Links to originating message
    node_id: str                 # Responding node
    success: bool                # Operation outcome
    result: Any                  # Response data
    error: Optional[str]         # Error details if failed
    execution_time_ms: float     # For FREQ LAW validation
    timestamp: str               # ISO 8601 timestamp
```

**Pattern:** Every operation returns a structured response with execution timing for FREQ LAW compliance.

#### 3. Consensus Mechanism (k=3 Quorum)

```python
# Consensus voting
class QuorumConsensus:
    def initiate_consensus(self, operation: str, context: Dict) -> ConsensusRound
    def submit_vote(self, consensus_id: str, voter_id: str, vote: Vote) -> None
    def check_consensus(self, consensus_id: str) -> Optional[ConsensusResult]
```

**Pattern:** Critical operations require approval from at least 3 nodes before execution.

#### 4. VETO Authority

```python
class VetoAuthority:
    def evaluate_operation(self, operation: Dict[str, Any],
                          freq_law: FreqLaw) -> VetoDecision
    def exercise_veto(self, operation_id: str, reason: VetoReason) -> VetoDecision
```

**Pattern:** GOV Engine can veto any operation violating FREQ LAW constraints.

#### 5. Audit Trail

```python
@dataclass
class AuditEntry:
    operation: str
    node_id: str
    node_type: str
    request_payload: Dict[str, Any]
    response_payload: Dict[str, Any]
    execution_time_ms: float
    quorum_achieved: bool
    veto_exercised: bool
    timestamp: str
```

**Pattern:** All operations logged to BigQuery with comprehensive context.

### FSM State Machine

Operations follow a finite state machine:

```
IDLE → DIRECTIVE_RECEIVED → VALIDATION → QUORUM → EXECUTION → AUDIT → COMPLETE/VETO
```

| State | Description | Transition Trigger |
|-------|-------------|-------------------|
| **IDLE** | Awaiting directive | Operator input received |
| **DIRECTIVE_RECEIVED** | Intent classification active | Parse complete |
| **VALIDATION** | GOV Engine compliance check | Schema validated |
| **QUORUM** | k=3 node consensus polling | Consensus achieved |
| **EXECUTION** | Distributed task processing | Workflow triggered |
| **AUDIT** | BigQuery trail logging | Execution complete |
| **COMPLETE/VETO** | Terminal state | Governance outcome |

---

## Directory Structure

```
FREQ-AI-VERTEX/
├── README.md                              # Project overview and quick start
├── CLAUDE.md                              # This file - AI assistant guide
├── .gitignore                             # Git ignore patterns
├── pyproject.toml                         # Python package configuration
│
├── src/                                   # Main source code
│   └── sol/                               # Sophisticated Operational Lattice package
│       ├── __init__.py                    # Package exports (v0.1.0)
│       │
│       ├── nodes/                         # Lattice node implementations
│       │   ├── __init__.py                # Node exports
│       │   ├── base.py                    # LatticeNode ABC, NodeMessage, NodeResponse
│       │   ├── strategic_op.py            # StrategicOP - Mission coordination
│       │   ├── spci.py                    # SPCI - Continuous improvement
│       │   ├── legacy_architect.py        # LegacyArchitect - Legacy translation
│       │   ├── gov_engine.py              # GOVEngine - FREQ LAW & VETO
│       │   ├── exec_automate.py           # ExecAutomate - Workflow execution
│       │   ├── optimal_intel.py           # OptimalIntel - Analytics
│       │   └── element_design.py          # ElementDesign - Schema generation
│       │
│       ├── governance/                    # FREQ LAW governance layer
│       │   ├── __init__.py                # Governance exports
│       │   ├── freq_law.py                # FreqLaw engine & constraints
│       │   └── veto.py                    # VetoAuthority & VetoDecision
│       │
│       ├── consensus/                     # Consensus mechanisms
│       │   ├── __init__.py                # Consensus exports
│       │   └── quorum.py                  # QuorumConsensus (k=3 voting)
│       │
│       └── audit/                         # Audit trail management
│           ├── __init__.py                # Audit exports
│           └── bigquery.py                # BigQueryAuditTrail & AuditEntry
│
├── config/                                # Configuration files
│   ├── sol_config.yaml                    # SOL runtime configuration
│   └── vertex_ai_agent.yaml               # Vertex AI Agent Builder config
│
├── tests/                                 # Test suite
│   ├── __init__.py                        # Test package
│   └── test_sol.py                        # Comprehensive test suite
│
└── .github/                               # GitHub configuration
    └── agents/
        └── strategic-opus-code.md         # GitHub Copilot agent config
```

**Total Codebase:** ~2,380 lines of Python across 18 files

---

## Development Environment

### Prerequisites

- **Python:** 3.9 or higher (3.9, 3.10, 3.11, 3.12 supported)
- **pip:** Latest version recommended
- **Git:** For version control
- **Google Cloud SDK:** (Optional) For GCP deployment

### Installation

#### 1. Base Installation

```bash
# Clone repository
git clone https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX.git
cd FREQ-AI-VERTEX

# Install in development mode
pip install -e .
```

#### 2. With GCP Dependencies

```bash
pip install -e ".[gcp]"
```

Includes:
- `google-cloud-bigquery>=3.0.0`
- `google-cloud-aiplatform>=1.38.0`

#### 3. With Development Tools

```bash
pip install -e ".[dev]"
```

Includes:
- `pytest>=7.0.0` - Test framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `black>=23.0.0` - Code formatter
- `ruff>=0.1.0` - Linter
- `mypy>=1.0.0` - Type checker

#### 4. Full Development Setup

```bash
pip install -e ".[gcp,dev]"
```

### Verifying Installation

```bash
# Run tests
pytest

# Check code formatting
black --check src tests

# Run linter
ruff check src tests

# Type checking
mypy src
```

---

## Code Conventions & Style

### Python Style Guide

**Formatter:** Black (v23.0.0+)
- **Line Length:** 100 characters
- **Target Versions:** Python 3.9-3.12
- **Configuration:** `[tool.black]` in `pyproject.toml`

**Linter:** Ruff (v0.1.0+)
- **Rules Enabled:**
  - `E` - PEP 8 errors
  - `F` - Pyflakes checks
  - `W` - PEP 8 warnings
  - `I` - isort import sorting
  - `UP` - Modern Python syntax
- **Configuration:** `[tool.ruff]` in `pyproject.toml`

**Type Checker:** MyPy (v1.0.0+)
- **Python Version:** 3.9
- **Strict Settings:** `warn_return_any=true`, `warn_unused_configs=true`
- **Import Policy:** `ignore_missing_imports=true` (for non-typed packages)

### Code Structure Conventions

#### 1. Class Definitions

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import uuid

class LatticeNode(ABC):
    """
    Base class with clear docstring.

    Describe purpose, behavior, and constraints.
    """

    def __init__(self, node_id: Optional[str] = None):
        # Public attribute
        self.node_id = node_id or str(uuid.uuid4())
        # Private attributes with underscore prefix
        self._message_history: List[NodeMessage] = []
        self._connected_nodes: Dict[str, 'LatticeNode'] = {}
```

**Conventions:**
- Use `ABC` for abstract base classes
- Type hints on all method signatures
- Docstrings for all public classes and methods
- Private attributes prefixed with `_`
- Use `Optional[T]` for nullable parameters

#### 2. Dataclasses for Structured Data

```python
@dataclass
class NodeMessage:
    """Message passed between lattice nodes."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_node: str = ""
    target_node: str = ""
    operation: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    requires_quorum: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "source_node": self.source_node,
            # ... all fields
        }
```

**Conventions:**
- Use `@dataclass` for data structures
- Provide default factories for mutable defaults
- Include `to_dict()` method for serialization
- ISO 8601 timestamps (`datetime.utcnow().isoformat()`)
- UUID generation with `uuid.uuid4()`

#### 3. Enums for Type Safety

```python
from enum import Enum

class NodeType(Enum):
    """Types of nodes in the Sophisticated Operational Lattice."""

    STRATEGIC_OP = "strategic_op"
    SPCI = "spci"
    LEGACY_ARCHITECT = "legacy_architect"
    # ...
```

**Conventions:**
- Use `Enum` for fixed sets of constants
- String values for serialization compatibility
- Descriptive docstrings

#### 4. Method Signatures

```python
def send_message(
    self,
    target_node_id: str,
    operation: str,
    payload: Dict[str, Any],
    requires_quorum: bool = True
) -> Optional[NodeResponse]:
    """
    Send a message to a connected node.

    Args:
        target_node_id: ID of the target node
        operation: Operation to perform
        payload: Data payload for the operation
        requires_quorum: Whether operation requires k=3 quorum

    Returns:
        NodeResponse from target node, or None if not connected
    """
    # Implementation
```

**Conventions:**
- Type hints on all parameters and return values
- Google-style docstrings with Args and Returns sections
- Optional parameters with defaults at the end
- Use `Optional[T]` for potentially None returns

### Import Organization

```python
# Standard library imports
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

# Third-party imports
import yaml
from google.cloud import bigquery

# Local imports
from sol.nodes.base import LatticeNode, NodeMessage, NodeResponse
from sol.governance import FreqLaw
```

**Conventions:**
- Three groups: standard library, third-party, local
- Alphabetically sorted within groups (enforced by `ruff` rule `I`)
- Use explicit imports, avoid `import *`

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| **Classes** | PascalCase | `LatticeNode`, `FreqLaw`, `NodeMessage` |
| **Functions/Methods** | snake_case | `send_message()`, `check_consensus()` |
| **Constants** | SCREAMING_SNAKE_CASE | `MAX_RESPONSE_TIME_MS = 2000` |
| **Private attributes** | _snake_case | `_message_history`, `_connected_nodes` |
| **Module names** | snake_case | `freq_law.py`, `quorum.py` |
| **Package names** | lowercase | `sol`, `governance`, `nodes` |

---

## Testing Practices

### Test Framework: Pytest

**Configuration:** `[tool.pytest.ini_options]` in `pyproject.toml`
- **Test Paths:** `tests/`
- **File Pattern:** `test_*.py`
- **Function Pattern:** `test_*`
- **Options:** `-v --tb=short` (verbose with short tracebacks)

### Test Structure

**File:** `tests/test_sol.py` (~425 lines)

#### Test Classes

```python
class TestFreqLaw:
    """Test FREQ LAW governance validation."""

    def test_default_constraints(self):
        """Test default FREQ LAW constraints."""
        # Arrange
        freq_law = FreqLaw()

        # Assert
        assert freq_law.max_response_time_ms == 2000
        assert freq_law.required_quorum == 3
        # ...

    def test_response_time_validation(self):
        """Test response time validation."""
        # Test both compliant and non-compliant cases
```

**Test Classes (6 total):**
1. `TestFreqLaw` - Governance constraints
2. `TestVetoAuthority` - VETO decisions
3. `TestQuorumConsensus` - k=3 voting
4. `TestBigQueryAuditTrail` - Audit logging
5. `TestLatticeNodes` - Individual node behavior
6. `TestIntegration` - End-to-end workflows

### Testing Conventions

#### 1. Test Method Naming

```python
def test_<what_is_being_tested>_<expected_outcome>(self):
    """Descriptive docstring explaining the test."""
```

Examples:
- `test_response_time_validation_passes_for_compliant_time()`
- `test_veto_exercised_for_insufficient_quorum()`
- `test_consensus_reached_after_k_votes()`

#### 2. Arrange-Act-Assert Pattern

```python
def test_example(self):
    """Test example behavior."""
    # Arrange - Set up test conditions
    freq_law = FreqLaw()
    operation = {"execution_time_ms": 1500}

    # Act - Execute the behavior
    result = freq_law.validate_response_time(operation)

    # Assert - Verify the outcome
    assert result is True
```

#### 3. Test All Edge Cases

```python
def test_veto_authority():
    """Test VETO for all violation types."""
    veto = VetoAuthority()
    freq_law = FreqLaw()

    # Test 1: Response time violation
    operation_slow = {"execution_time_ms": 2500, "quorum": 3, "audit_trail": True}
    decision = veto.evaluate_operation(operation_slow, freq_law)
    assert decision.veto is True
    assert decision.reason == VetoReason.RESPONSE_TIME_VIOLATION

    # Test 2: Quorum violation
    operation_no_quorum = {"execution_time_ms": 1000, "quorum": 2, "audit_trail": True}
    decision = veto.evaluate_operation(operation_no_quorum, freq_law)
    assert decision.veto is True
    assert decision.reason == VetoReason.QUORUM_NOT_MET

    # Test 3: Audit trail violation
    # ...
```

#### 4. Integration Tests

```python
def test_full_workflow_with_governance():
    """Test complete workflow from directive to audit."""
    # Create all components
    strategic_op = StrategicOP()
    gov_engine = GOVEngine()
    consensus = QuorumConsensus(required_votes=3)
    audit_trail = BigQueryAuditTrail(project_id="test", dataset_id="test")

    # Execute full workflow
    # 1. Strategic OP receives directive
    # 2. Consensus initiated
    # 3. Votes collected
    # 4. VETO evaluation
    # 5. Audit logging

    # Verify end-to-end behavior
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test class
pytest tests/test_sol.py::TestFreqLaw

# Run specific test
pytest tests/test_sol.py::TestFreqLaw::test_default_constraints

# Run with coverage
pytest --cov=sol --cov-report=html

# Run with verbose output
pytest -vv

# Run with specific markers (if defined)
pytest -m integration
```

### Test Coverage Goals

- **Target:** 80%+ coverage for all modules
- **Critical Paths:** 100% coverage for governance, consensus, and veto logic
- **Edge Cases:** All FREQ LAW violation scenarios tested

---

## FREQ LAW Governance

### The Four Pillars

FREQ LAW is the foundational governance protocol enforcing system reliability:

| Pillar | Requirement | Validation Method | Enforcement |
|--------|-------------|-------------------|-------------|
| **F**ast | Response time < 2000ms | `execution_time_ms` field validation | GOV Engine timing check |
| **R**obust | Resilient to failures | k=3 quorum consensus | QuorumConsensus voting |
| **E**volutionary | Continuous improvement | SPCI integration | Performance tracking |
| **Q**uantified | Measured and logged | Audit trail required | BigQuery logging |

### Implementation

#### 1. FreqLaw Class

**Location:** `src/sol/governance/freq_law.py`

```python
class FreqLaw:
    """
    FREQ LAW governance engine.

    Enforces Fast, Robust, Evolutionary, Quantified principles.
    """

    def __init__(
        self,
        max_response_time_ms: int = 2000,
        required_quorum: int = 3,
        require_audit_trail: bool = True,
        enable_veto_authority: bool = True
    ):
        self.max_response_time_ms = max_response_time_ms
        self.required_quorum = required_quorum
        self.require_audit_trail = require_audit_trail
        self.enable_veto_authority = enable_veto_authority

    def validate_response_time(self, operation: Dict[str, Any]) -> bool:
        """Validate operation meets Fast requirement."""
        execution_time = operation.get("execution_time_ms", 0)
        return execution_time < self.max_response_time_ms

    def validate_quorum(self, operation: Dict[str, Any]) -> bool:
        """Validate operation meets Robust requirement."""
        quorum = operation.get("quorum", 0)
        return quorum >= self.required_quorum

    def validate_audit_trail(self, operation: Dict[str, Any]) -> bool:
        """Validate operation meets Quantified requirement."""
        return operation.get("audit_trail", False)
```

#### 2. VETO Authority

**Location:** `src/sol/governance/veto.py`

```python
class VetoReason(Enum):
    """Reasons for VETO decisions."""

    RESPONSE_TIME_VIOLATION = "response_time_violation"
    QUORUM_NOT_MET = "quorum_not_met"
    AUDIT_TRAIL_MISSING = "audit_trail_missing"
    GOVERNANCE_OVERRIDE = "governance_override"

@dataclass
class VetoDecision:
    """VETO decision with rationale."""

    veto: bool
    reason: Optional[VetoReason]
    operation_id: str
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)

class VetoAuthority:
    """GOV Engine VETO authority."""

    def evaluate_operation(
        self,
        operation: Dict[str, Any],
        freq_law: FreqLaw
    ) -> VetoDecision:
        """
        Evaluate operation for FREQ LAW compliance.

        Returns VetoDecision with veto=True if non-compliant.
        """
        operation_id = operation.get("id", str(uuid.uuid4()))

        # Check response time (Fast)
        if not freq_law.validate_response_time(operation):
            return VetoDecision(
                veto=True,
                reason=VetoReason.RESPONSE_TIME_VIOLATION,
                operation_id=operation_id,
                timestamp=datetime.utcnow().isoformat(),
                details={"execution_time_ms": operation.get("execution_time_ms")}
            )

        # Check quorum (Robust)
        if not freq_law.validate_quorum(operation):
            return VetoDecision(
                veto=True,
                reason=VetoReason.QUORUM_NOT_MET,
                operation_id=operation_id,
                timestamp=datetime.utcnow().isoformat(),
                details={"quorum": operation.get("quorum")}
            )

        # Check audit trail (Quantified)
        if not freq_law.validate_audit_trail(operation):
            return VetoDecision(
                veto=True,
                reason=VetoReason.AUDIT_TRAIL_MISSING,
                operation_id=operation_id,
                timestamp=datetime.utcnow().isoformat()
            )

        # Operation compliant
        return VetoDecision(
            veto=False,
            reason=None,
            operation_id=operation_id,
            timestamp=datetime.utcnow().isoformat()
        )
```

#### 3. Quorum Consensus

**Location:** `src/sol/consensus/quorum.py`

```python
class VoteType(Enum):
    """Vote types for consensus."""

    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"

@dataclass
class Vote:
    """Individual vote in consensus round."""

    voter_id: str
    vote_type: VoteType
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    rationale: str = ""

class QuorumConsensus:
    """k=3 quorum consensus mechanism."""

    def __init__(self, required_votes: int = 3):
        self.required_votes = required_votes  # k=3 by default
        self._eligible_voters: List[str] = []
        self._consensus_rounds: Dict[str, ConsensusRound] = {}

    def register_voter(self, voter_id: str) -> None:
        """Register a node as eligible voter."""
        if voter_id not in self._eligible_voters:
            self._eligible_voters.append(voter_id)

    def initiate_consensus(
        self,
        operation: str,
        context: Dict[str, Any]
    ) -> ConsensusRound:
        """Initiate new consensus round."""
        round_id = str(uuid.uuid4())
        consensus_round = ConsensusRound(
            id=round_id,
            operation=operation,
            context=context,
            required_votes=self.required_votes
        )
        self._consensus_rounds[round_id] = consensus_round
        return consensus_round

    def submit_vote(
        self,
        consensus_id: str,
        voter_id: str,
        vote: Vote
    ) -> None:
        """Submit vote for consensus round."""
        if consensus_id not in self._consensus_rounds:
            raise ValueError(f"Consensus round {consensus_id} not found")

        if voter_id not in self._eligible_voters:
            raise ValueError(f"Voter {voter_id} not eligible")

        consensus_round = self._consensus_rounds[consensus_id]
        consensus_round.add_vote(vote)

        # Check if consensus reached
        if len(consensus_round.votes) >= self.required_votes:
            consensus_round.evaluate_consensus()
```

### Configuration

**File:** `config/sol_config.yaml`

```yaml
freq_law:
  max_response_time_ms: 2000
  required_quorum: 3
  require_audit_trail: true
  enable_veto_authority: true

consensus:
  required_votes: 3
  timeout_seconds: 30
  eligible_nodes:
    - strategic_op
    - gov_engine
    - spci
```

### Usage in Code

```python
from sol.governance import FreqLaw, VetoAuthority
from sol.consensus import QuorumConsensus

# Initialize governance
freq_law = FreqLaw()
veto_authority = VetoAuthority()
consensus = QuorumConsensus(required_votes=3)

# Register voters
consensus.register_voter("strategic_op_node_id")
consensus.register_voter("gov_engine_node_id")
consensus.register_voter("spci_node_id")

# Execute operation with governance
operation = {
    "id": "op_123",
    "execution_time_ms": 1500,
    "quorum": 3,
    "audit_trail": True
}

# Evaluate with VETO authority
decision = veto_authority.evaluate_operation(operation, freq_law)

if decision.veto:
    print(f"Operation vetoed: {decision.reason}")
else:
    print("Operation approved by governance")
```

---

## Key Files Reference

### Critical Files to Understand

#### 1. `src/sol/nodes/base.py` (179 lines)

**Purpose:** Foundation of entire SOL architecture

**Key Components:**
- `NodeType` enum - All 7 node types
- `NodeMessage` dataclass - Message structure
- `NodeResponse` dataclass - Response structure
- `LatticeNode` ABC - Base class for all nodes

**Why Critical:** Every node inherits from `LatticeNode`. Understanding this file is essential for working with any node implementation.

**Key Methods:**
```python
@abstractmethod
def process_message(self, message: NodeMessage) -> NodeResponse
    """Override this in each node to define behavior."""

def connect_node(self, node: 'LatticeNode') -> None
    """Build lattice topology."""

def send_message(self, target_node_id: str, operation: str,
                 payload: Dict[str, Any]) -> Optional[NodeResponse]
    """Inter-node communication."""
```

#### 2. `src/sol/governance/freq_law.py`

**Purpose:** FREQ LAW enforcement engine

**Key Components:**
- `FreqLaw` class - Constraint validation
- Response time checking (<2000ms)
- Quorum requirement checking (k=3)
- Audit trail validation

**Why Critical:** Governs all operations in SOL. Any change to governance rules must go through this file.

#### 3. `src/sol/governance/veto.py`

**Purpose:** VETO authority implementation

**Key Components:**
- `VetoReason` enum - Veto reasons
- `VetoDecision` dataclass - Decision structure
- `VetoAuthority` class - Decision engine

**Why Critical:** GOV Engine's absolute VETO power. Understanding veto logic is essential for compliance.

#### 4. `src/sol/consensus/quorum.py`

**Purpose:** k=3 consensus mechanism

**Key Components:**
- `VoteType` enum - Vote types
- `Vote` dataclass - Vote structure
- `ConsensusRound` dataclass - Round tracking
- `QuorumConsensus` class - Voting engine

**Why Critical:** Critical operations require consensus. This implements the Robust pillar of FREQ LAW.

#### 5. `config/sol_config.yaml`

**Purpose:** Runtime configuration

**Sections:**
- `freq_law` - Governance settings
- `nodes` - Node enable/disable/priority
- `consensus` - Quorum settings
- `audit` - BigQuery configuration
- `vertex_ai` - Model settings
- `logging` - Log configuration

**Why Critical:** Single source of truth for system behavior. Changes here affect entire system.

#### 6. `tests/test_sol.py` (425 lines)

**Purpose:** Comprehensive test suite

**Test Classes:**
- `TestFreqLaw` - Governance validation
- `TestVetoAuthority` - VETO logic
- `TestQuorumConsensus` - Consensus voting
- `TestBigQueryAuditTrail` - Audit logging
- `TestLatticeNodes` - Node behavior
- `TestIntegration` - End-to-end workflows

**Why Critical:** Defines expected behavior. Read tests to understand how components should work.

### Node Implementation Files

Each node follows the same structure:

```python
from sol.nodes.base import LatticeNode, NodeType, NodeMessage, NodeResponse

class SpecificNode(LatticeNode):
    """Node-specific docstring."""

    def __init__(self, node_id: Optional[str] = None):
        super().__init__(node_id)
        # Node-specific state

    @property
    def node_type(self) -> NodeType:
        return NodeType.SPECIFIC_NODE

    @property
    def description(self) -> str:
        return "Node-specific description"

    def process_message(self, message: NodeMessage) -> NodeResponse:
        """
        Process messages specific to this node.

        Implements node-specific operations.
        """
        # Implementation
```

**Files:**
- `src/sol/nodes/strategic_op.py` - StrategicOP
- `src/sol/nodes/spci.py` - SPCI
- `src/sol/nodes/legacy_architect.py` - LegacyArchitect
- `src/sol/nodes/gov_engine.py` - GOVEngine
- `src/sol/nodes/exec_automate.py` - ExecAutomate
- `src/sol/nodes/optimal_intel.py` - OptimalIntel
- `src/sol/nodes/element_design.py` - ElementDesign

---

## Common Development Tasks

### Adding a New Node Method

**Example:** Add `get_mission_priority()` to StrategicOP

1. **Edit the node file:**

```python
# src/sol/nodes/strategic_op.py

def get_mission_priority(self, mission_id: str) -> Optional[int]:
    """
    Get priority level for a mission.

    Args:
        mission_id: ID of the mission

    Returns:
        Priority level (1-10), or None if not found
    """
    mission = self._missions.get(mission_id)
    if mission:
        return mission.get("priority")
    return None
```

2. **Add test:**

```python
# tests/test_sol.py

def test_strategic_op_mission_priority(self):
    """Test mission priority retrieval."""
    node = StrategicOP()

    # Set mission with priority
    node.set_mission("mission_1", "Test mission", priority=5)

    # Get priority
    priority = node.get_mission_priority("mission_1")

    assert priority == 5
```

3. **Run tests:**

```bash
pytest tests/test_sol.py::test_strategic_op_mission_priority
```

4. **Format and lint:**

```bash
black src/sol/nodes/strategic_op.py tests/test_sol.py
ruff check src/sol/nodes/strategic_op.py
```

### Modifying FREQ LAW Constraints

**Example:** Change response time limit to 1500ms

1. **Update default in FreqLaw:**

```python
# src/sol/governance/freq_law.py

def __init__(
    self,
    max_response_time_ms: int = 1500,  # Changed from 2000
    # ...
):
```

2. **Update configuration:**

```yaml
# config/sol_config.yaml

freq_law:
  max_response_time_ms: 1500  # Changed from 2000
```

3. **Update tests:**

```python
# tests/test_sol.py

def test_default_constraints(self):
    freq_law = FreqLaw()
    assert freq_law.max_response_time_ms == 1500  # Changed from 2000
```

4. **Update documentation:**

```markdown
# README.md

| **F**ast | Response time < 1500ms | GOV Engine timing validation |
```

### Adding a New Consensus Voter

**Example:** Register ExecAutomate as voter

```python
from sol.nodes import ExecAutomate
from sol.consensus import QuorumConsensus

# Create consensus engine
consensus = QuorumConsensus(required_votes=3)

# Create node
exec_node = ExecAutomate()

# Register as voter
consensus.register_voter(exec_node.node_id)

# Node can now participate in consensus rounds
```

### Creating an Integration Test

**Example:** Test full workflow with all governance checks

```python
# tests/test_sol.py

class TestIntegration:
    """Integration tests for full workflows."""

    def test_full_governance_workflow(self):
        """Test complete workflow with FREQ LAW governance."""
        # Arrange - Create all components
        strategic_op = StrategicOP()
        gov_engine = GOVEngine()
        spci = SPCI()

        freq_law = FreqLaw()
        veto_authority = VetoAuthority()
        consensus = QuorumConsensus(required_votes=3)

        # Register voters
        consensus.register_voter(strategic_op.node_id)
        consensus.register_voter(gov_engine.node_id)
        consensus.register_voter(spci.node_id)

        # Connect nodes
        strategic_op.connect_node(gov_engine)
        strategic_op.connect_node(spci)

        # Act - Execute workflow
        # 1. Strategic OP sets mission
        strategic_op.set_mission("mission_1", "Test mission")

        # 2. Initiate consensus
        round = consensus.initiate_consensus(
            operation="execute_mission",
            context={"mission_id": "mission_1"}
        )

        # 3. Collect votes
        from sol.consensus.quorum import Vote, VoteType
        consensus.submit_vote(round.id, strategic_op.node_id,
                            Vote(strategic_op.node_id, VoteType.APPROVE))
        consensus.submit_vote(round.id, gov_engine.node_id,
                            Vote(gov_engine.node_id, VoteType.APPROVE))
        consensus.submit_vote(round.id, spci.node_id,
                            Vote(spci.node_id, VoteType.APPROVE))

        # 4. Evaluate VETO
        operation = {
            "id": "op_123",
            "execution_time_ms": 1500,
            "quorum": 3,
            "audit_trail": True
        }
        decision = veto_authority.evaluate_operation(operation, freq_law)

        # Assert - Verify outcomes
        assert round.consensus_reached
        assert decision.veto is False
        assert strategic_op.get_mission_status("mission_1") is not None
```

### Deploying to Vertex AI

**Prerequisites:**
- Google Cloud Project with Vertex AI enabled
- Service account with required permissions
- `gcloud` CLI authenticated

**Steps:**

1. **Install GCP dependencies:**

```bash
pip install -e ".[gcp]"
```

2. **Configure Vertex AI:**

```yaml
# config/vertex_ai_agent.yaml

# Already configured with:
# - Agent name: sol-orchestrator
# - Model: gemini-1.5-pro
# - Playbooks for each node
# - Tools for governance
```

3. **Deploy agent:**

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Deploy to Vertex AI Agent Builder
# (Deployment scripts would go here - currently manual via console)
```

4. **Create BigQuery dataset:**

```bash
# Create dataset
bq mk --dataset YOUR_PROJECT_ID:sol_audit

# Create table (DDL generated by BigQueryAuditTrail.get_table_ddl())
bq query --use_legacy_sql=false < audit_table_ddl.sql
```

---

## Deployment & Configuration

### Configuration Files

#### 1. `config/sol_config.yaml`

**Full Structure:**

```yaml
freq_law:
  max_response_time_ms: 2000
  required_quorum: 3
  require_audit_trail: true
  enable_veto_authority: true

nodes:
  strategic_op:
    enabled: true
    priority: 10
  spci:
    enabled: true
    priority: 8
  legacy_architect:
    enabled: true
    priority: 7
  gov_engine:
    enabled: true
    priority: 10
  exec_automate:
    enabled: true
    priority: 8
  optimal_intel:
    enabled: true
    priority: 6
  element_design:
    enabled: true
    priority: 6

consensus:
  required_votes: 3
  timeout_seconds: 30
  eligible_nodes:
    - strategic_op
    - gov_engine
    - spci

audit:
  bigquery:
    project_id: your-gcp-project
    dataset_id: sol_audit
    table_id: operations
    partitioning:
      type: DAY
      field: timestamp
    clustering:
      - node_type
      - operation

vertex_ai:
  model: gemini-1.5-pro
  temperature: 0.1
  max_output_tokens: 8192
  top_p: 0.95
  top_k: 40

logging:
  level: INFO
  format: json
  include_timestamp: true
```

#### 2. `config/vertex_ai_agent.yaml`

**Key Sections:**

```yaml
displayName: sol-orchestrator
defaultLanguageCode: en
timeZone: America/New_York

securitySettings:
  redactionStrategy: REDACT_WITH_SERVICE
  redactionScope:
    - REDACT_DISK_STORAGE

generativeSettings:
  name: gemini-1.5-pro
  safety_settings:
    - category: HARM_CATEGORY_HARASSMENT
      threshold: BLOCK_MEDIUM_AND_ABOVE
    - category: HARM_CATEGORY_HATE_SPEECH
      threshold: BLOCK_MEDIUM_AND_ABOVE
    # ...

playbooks:
  - displayName: strategic-op-playbook
    goal: "Mission-level coordination and strategic planning"
    steps:
      - step_1: "Receive operator directive"
      - step_2: "Parse intent and objectives"
      - step_3: "Coordinate with lattice nodes"
      - step_4: "Track mission progress"

  # ... playbooks for all 7 nodes

tools:
  - name: freq_law_validator
    description: "Validate operations against FREQ LAW constraints"
  - name: quorum_consensus
    description: "Initiate and track k=3 consensus voting"
  - name: bigquery_audit_logger
    description: "Log operations to BigQuery audit trail"
```

### Environment Variables

```bash
# Google Cloud
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# BigQuery
export BIGQUERY_DATASET="sol_audit"
export BIGQUERY_TABLE="operations"

# SOL Configuration
export SOL_CONFIG_PATH="/path/to/sol_config.yaml"
export FREQ_LAW_MAX_TIME_MS=2000
export FREQ_LAW_QUORUM_K=3
```

### Docker Deployment (Optional)

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY config/ config/

RUN pip install -e ".[gcp]"

CMD ["python", "-m", "sol"]
```

**Build and Run:**

```bash
# Build image
docker build -t freq-ai-sol:latest .

# Run container
docker run -e GCP_PROJECT_ID=your-project \
           -e GOOGLE_APPLICATION_CREDENTIALS=/creds/sa.json \
           -v /path/to/creds:/creds \
           freq-ai-sol:latest
```

---

## Important Guidelines for AI Assistants

### 1. Understand FREQ LAW Before Making Changes

**FREQ LAW is non-negotiable.** Every change must comply:

- **Fast:** Will this change affect execution time? If so, ensure <2000ms.
- **Robust:** Does this require consensus? If so, implement k=3 voting.
- **Evolutionary:** Is this improving the system? Consider SPCI integration.
- **Quantified:** Is this logged? Add audit trail entries.

### 2. Read Before Writing

**Always read existing code before modifying:**

```bash
# Before editing any node
Read: src/sol/nodes/base.py          # Understand foundation
Read: src/sol/nodes/<specific>.py    # Understand current implementation
Read: tests/test_sol.py              # Understand expected behavior
```

### 3. Preserve Architecture Patterns

**Do NOT:**
- Break message-passing communication
- Bypass VETO authority
- Skip quorum consensus for critical operations
- Remove audit logging
- Change node types without updating all references

**Do:**
- Follow existing patterns in `base.py`
- Use dataclasses for structured data
- Include type hints on all methods
- Write tests for new functionality
- Update documentation when changing behavior

### 4. Test Thoroughly

**Before committing:**

```bash
# Run full test suite
pytest

# Check coverage
pytest --cov=sol --cov-report=term-missing

# Verify no regressions
pytest tests/test_sol.py::TestIntegration

# Format code
black src tests

# Lint
ruff check src tests

# Type check
mypy src
```

### 5. Operator Interface

**Remember the operator context:**

From `strategic-opus-code.md`:

> You are interfacing with the Context Architect of FREQ AI. This operator works through verbal orchestration and intent-based synthesis—not traditional coding. Translate all natural language directives into executable architecture without requiring the operator to write code directly.

**When implementing features:**
- Accept natural language directives
- Translate intent into architectural operations
- Explain what you're building, why it aligns with FREQ LAW, and how it integrates
- Use the Response Protocol: What, Why, How

### 6. Version Control

**Git Workflow:**

```bash
# Current branch
claude/claude-md-mk4gmamup71q5idj-UEw4z

# Making changes
git status
git add <files>
git commit -m "Clear description following FREQ LAW principles"

# Push to branch
git push -u origin claude/claude-md-mk4gmamup71q5idj-UEw4z
```

**Commit Message Format:**

```
<type>: <subject>

<body explaining why and how it aligns with FREQ LAW>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `config`

### 7. When to Ask for Clarification

**Ask the operator when:**
- A directive conflicts with FREQ LAW constraints
- Multiple architectural approaches are valid
- A change would require modifying core governance logic
- You need to understand legacy system context
- A feature requires new external dependencies

### 8. Documentation Standards

**When adding new functionality:**

1. **Code docstrings:**
   ```python
   def new_method(self, param: str) -> bool:
       """
       One-line summary.

       Detailed explanation of behavior, FREQ LAW implications,
       and integration with lattice topology.

       Args:
           param: Description

       Returns:
           Description
       """
   ```

2. **Update README.md** if:
   - Adding new lattice node
   - Changing FREQ LAW constraints
   - Adding new external dependencies
   - Changing deployment process

3. **Update CLAUDE.md** (this file) if:
   - Changing architectural patterns
   - Adding new development workflows
   - Modifying testing approaches
   - Changing configuration structure

### 9. Performance Considerations

**Always measure execution time:**

```python
from time import time

start = time()
# ... operation ...
execution_time_ms = (time() - start) * 1000

# Validate FREQ LAW Fast pillar
assert execution_time_ms < 2000, "FREQ LAW violation: response too slow"
```

**Include timing in responses:**

```python
response = NodeResponse(
    message_id=message.id,
    node_id=self.node_id,
    success=True,
    result=result,
    execution_time_ms=execution_time_ms,  # Always include
    timestamp=datetime.utcnow().isoformat()
)
```

### 10. Security and Compliance

**This system is designed for regulated industries:**

- **Data Sensitivity:** Assume all payloads contain PII/PHI
- **Audit Trail:** NEVER skip audit logging
- **VETO Authority:** GOV Engine can stop any operation
- **Quorum Consensus:** Critical operations require k=3 approval
- **BigQuery:** All operations logged for compliance review

**When handling data:**
- Use secure serialization (JSON, not pickle)
- Validate inputs before processing
- Log security-relevant events
- Respect redaction settings in Vertex AI config

---

## Quick Reference

### Essential Commands

```bash
# Development
pip install -e ".[dev]"
pytest
black src tests
ruff check src tests
mypy src

# Testing
pytest tests/test_sol.py::TestFreqLaw
pytest --cov=sol
pytest -v --tb=short

# Git
git status
git add .
git commit -m "feat: description"
git push -u origin <branch>

# Configuration
cat config/sol_config.yaml
cat config/vertex_ai_agent.yaml
```

### Key Concepts

- **SOL:** Sophisticated Operational Lattice
- **FREQ LAW:** Fast, Robust, Evolutionary, Quantified
- **k=3:** Quorum consensus requiring 3 votes
- **VETO:** GOV Engine's absolute authority to block operations
- **Lattice Node:** Base component in distributed system
- **Message-Passing:** Inter-node communication pattern
- **Audit Trail:** BigQuery logging for all operations

### File Locations

```
src/sol/nodes/base.py              # Start here to understand architecture
src/sol/governance/freq_law.py     # FREQ LAW implementation
src/sol/governance/veto.py         # VETO authority
src/sol/consensus/quorum.py        # k=3 consensus
config/sol_config.yaml             # Runtime configuration
tests/test_sol.py                  # Test specifications
```

### Contact & Resources

- **GitHub:** https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX
- **Issues:** https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX/issues
- **Documentation:** https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX#readme
- **Package:** freq-ai-sol (PyPI - not yet published)

---

## Changelog

### v0.1.0 - 2026-01-07

- Initial CLAUDE.md creation
- Documented full SOL architecture
- Added comprehensive development guidelines
- Included FREQ LAW governance protocols
- Provided testing and deployment instructions

---

**Remember:** This is a governance-first system. FREQ LAW isn't optional—it's foundational. Every change must align with Fast, Robust, Evolutionary, and Quantified principles. When in doubt, consult the tests, read the source, and ask the operator.

Welcome to the Sophisticated Operational Lattice. Build with precision. Govern with authority. Evolve with purpose.
