# CLAUDE.md - AI Assistant Guide for FREQ-AI-VERTEX

This document provides comprehensive guidance for AI assistants working with the FREQ-AI-VERTEX codebase.

## Project Overview

**FREQ-AI-VERTEX** is the **Sophisticated Operational Lattice (SOL)**, a distributed AI orchestration system designed for legacy modernization across regulated industries. It runs on Google Cloud Vertex AI Agent Builder using Gemini substrates.

### Core Identity

- **Package Name**: `freq-ai-sol`
- **Python Version**: 3.9+ (supports 3.9, 3.10, 3.11, 3.12)
- **License**: MIT
- **Deployment Target**: Google Cloud Vertex AI Agent Builder with Gemini 1.5 Pro

### Key Concepts

1. **FREQ LAW** - The governance protocol (Fast, Robust, Evolutionary, Quantified)
2. **Lattice Nodes** - Seven specialized AI nodes that form the orchestration system
3. **k=3 Quorum** - Consensus mechanism requiring 3 node approvals
4. **VETO Authority** - GOV Engine's absolute power to block non-compliant operations

## Directory Structure

```
FREQ-AI-VERTEX/
├── src/sol/                    # Main source code
│   ├── __init__.py             # Package entry point
│   ├── nodes/                  # Lattice node implementations
│   │   ├── base.py             # Base LatticeNode abstract class
│   │   ├── strategic_op.py     # Mission coordination
│   │   ├── spci.py             # Continuous improvement
│   │   ├── legacy_architect.py # Legacy system translation
│   │   ├── gov_engine.py       # Governance & VETO
│   │   ├── exec_automate.py    # Workflow execution
│   │   ├── optimal_intel.py    # Analytics & decisions
│   │   └── element_design.py   # Schema generation
│   ├── governance/             # Governance protocols
│   │   ├── freq_law.py         # FREQ LAW constraints
│   │   └── veto.py             # VETO authority
│   ├── consensus/              # Consensus mechanisms
│   │   └── quorum.py           # k=3 quorum consensus
│   ├── blueprint/              # Strategic blueprint
│   │   └── freq_blueprint.py   # FREQ Blueprint & SSC system prompt
│   ├── activation/             # Deployment phases
│   │   └── phase2_verification.py
│   └── audit/                  # Audit & logging
│       └── bigquery.py         # BigQuery audit trail
├── config/
│   ├── sol_config.yaml         # System configuration
│   └── vertex_ai_agent.yaml    # Vertex AI deployment config
├── tests/
│   └── test_sol.py             # Comprehensive test suite
├── .github/agents/
│   └── strategic-opus-code.md  # GitHub agent configuration
├── pyproject.toml              # Python package configuration
└── README.md                   # Project documentation
```

## Development Workflow

### Installation

```bash
# Base installation
pip install -e .

# With GCP dependencies (BigQuery, Vertex AI)
pip install -e ".[gcp]"

# With development tools (pytest, black, ruff, mypy)
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with verbose output
pytest tests/test_sol.py -v

# Run with coverage reporting
pytest tests/test_sol.py --cov

# Run specific test class
pytest tests/test_sol.py::TestFreqLaw -v

# Run specific test
pytest tests/test_sol.py::TestLatticeNodes::test_strategic_op_node -v
```

### Code Quality

```bash
# Format code with Black (line-length: 100)
black --line-length=100 src/

# Lint with Ruff
ruff check --select=E,F,W,I,UP src/

# Type checking with MyPy
mypy src/
```

## Architecture

### The Seven Lattice Nodes

| Node | Class | Purpose |
|------|-------|---------|
| Strategic OP | `StrategicOP` | Mission coordination, cross-node orchestration |
| SPCI | `SPCI` | Continuous improvement, metrics, experiments |
| Legacy Architect | `LegacyArchitect` | Protocol translation, data transformation |
| GOV Engine | `GOVEngine` | FREQ LAW compliance, VETO authority |
| Exec Automate | `ExecAutomate` | Workflow creation and execution |
| Optimal Intel | `OptimalIntel` | Analytics, recommendations, aggregation |
| Element Design | `ElementDesign` | Schema creation, artifact generation |

### FREQ LAW Governance

All operations must comply with FREQ LAW:

| Principle | Requirement | Enforcement |
|-----------|-------------|-------------|
| **F**ast | Response < 2000ms | GOV Engine timing validation |
| **R**obust | Fault tolerant | k=3 quorum consensus |
| **E**volutionary | Continuous improvement | SPCI integration |
| **Q**uantified | Measured & logged | BigQuery audit trail |

### Message Pattern

All inter-node communication follows this pattern:

```python
from sol.nodes.base import NodeMessage, NodeResponse

# Create message
message = NodeMessage(
    source_node=source_id,
    target_node=target_id,
    operation="operation_name",
    payload={"key": "value"},
    requires_quorum=True  # Optional
)

# Process and get response
response = node.process_message(message)
# Returns NodeResponse with success, data, execution_time_ms
```

## Code Conventions

### Naming

- **Classes**: PascalCase (`LatticeNode`, `StrategicOP`, `GOVEngine`)
- **Functions/Methods**: snake_case (`process_message`, `create_mission`)
- **Constants**: UPPER_SNAKE_CASE (`FREQ_BLUEPRINT`, `SCHEMA`)
- **Modules**: lowercase with underscores (`freq_law.py`, `quorum.py`)

### Operation Naming Patterns

- `create_*` - Create new entities
- `update_*` - Modify existing entities
- `get_*` - Retrieve entities
- `validate_*` - Check compliance
- `execute_*` - Run workflows/commands

### Execution Time Tracking

All node operations must track execution time:

```python
import time

start_time = time.time()
# ... operation logic ...
execution_time_ms = (time.time() - start_time) * 1000
```

### UUIDs for Identifiers

Use `uuid.uuid4()` for all identifiers:

```python
import uuid
node_id = str(uuid.uuid4())
mission_id = str(uuid.uuid4())
```

### Error Handling

```python
def process_message(self, message: NodeMessage) -> NodeResponse:
    start_time = time.time()
    try:
        # ... operation logic ...
        return NodeResponse(
            success=True,
            data=result,
            execution_time_ms=(time.time() - start_time) * 1000
        )
    except Exception as e:
        return NodeResponse(
            success=False,
            data={"error": str(e)},
            execution_time_ms=(time.time() - start_time) * 1000
        )
```

### Audit Logging Pattern

```python
audit.log_operation(
    operation="operation_name",
    node_id=node.node_id,
    node_type=node.node_type.value,
    request_payload={...},
    response_payload={...},
    execution_time_ms=elapsed_ms,
    quorum_required=True,
    veto_applied=False
)
```

## Test Conventions

### Test Structure

Tests are organized by component in `tests/test_sol.py`:

- `TestFreqLaw` - FREQ LAW constraint validation
- `TestVetoAuthority` - VETO mechanism tests
- `TestQuorumConsensus` - Consensus mechanism tests
- `TestBigQueryAuditTrail` - Audit trail tests
- `TestLatticeNodes` - Individual node tests
- `TestIntegration` - Full workflow tests
- `TestBlueprintModule` - Blueprint validation tests
- `TestPhase2Verification` - Phase 2 verification tests

### Import Pattern for Tests

Tests use relative path imports:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sol.nodes import StrategicOP, GOVEngine
from sol.governance import FreqLaw
```

### Test Naming

- Test functions: `test_<what_is_being_tested>`
- Test classes: `Test<ComponentName>`

## Key Files Reference

### Configuration Files

- `config/sol_config.yaml` - System configuration (FREQ LAW thresholds, node settings, consensus config)
- `config/vertex_ai_agent.yaml` - Vertex AI Agent Builder deployment specification

### Governance

- `src/sol/governance/freq_law.py:FreqLaw` - FREQ LAW enforcement engine
- `src/sol/governance/veto.py:VetoAuthority` - VETO decision logic
- `src/sol/consensus/quorum.py:QuorumConsensus` - k=3 consensus mechanism

### Blueprint

- `src/sol/blueprint/freq_blueprint.py:FREQ_BLUEPRINT` - Complete system specification
- `src/sol/blueprint/freq_blueprint.py:SSC_SYSTEM_PROMPT` - Strategic Synthesis Core prompt

### Node Base

- `src/sol/nodes/base.py:LatticeNode` - Abstract base class all nodes inherit from
- `src/sol/nodes/base.py:NodeMessage` - Inter-node message dataclass
- `src/sol/nodes/base.py:NodeResponse` - Operation response dataclass

## Common Operations

### Creating a New Lattice Node

1. Inherit from `LatticeNode` in `src/sol/nodes/base.py`
2. Define `node_type` from `NodeType` enum
3. Implement `_handle_operation()` method
4. Add supported operations as private methods

```python
from sol.nodes.base import LatticeNode, NodeType, NodeMessage, NodeResponse

class NewNode(LatticeNode):
    def __init__(self):
        super().__init__(node_type=NodeType.NEW_TYPE)

    def _handle_operation(self, operation: str, payload: dict) -> dict:
        operations = {
            "operation_name": self._operation_handler,
        }
        handler = operations.get(operation)
        if handler:
            return handler(payload)
        return {"error": f"Unknown operation: {operation}"}
```

### Adding New Operations to Existing Node

1. Add handler method in the node class
2. Register in `_handle_operation()` operations dict
3. Add tests in `tests/test_sol.py`

### Validating FREQ LAW Compliance

```python
from sol.governance import FreqLaw

freq_law = FreqLaw()

# Check response time compliance
is_compliant = freq_law.validate_response_time(execution_time_ms)

# Check quorum requirement
quorum_met = freq_law.check_quorum_requirement(approved_count=3)

# Create audit entry
audit_entry = freq_law.create_audit_entry(
    operation="operation_name",
    node_id="node-id",
    execution_time_ms=150.5,
    success=True
)
```

### Using Consensus

```python
from sol.consensus import QuorumConsensus

consensus = QuorumConsensus(required_votes=3)
consensus.register_voter(node1_id)
consensus.register_voter(node2_id)
consensus.register_voter(node3_id)

# Start consensus round
round_id = consensus.initiate_round("proposal description")

# Submit votes
consensus.submit_vote(round_id, node1_id, VoteType.APPROVE)
consensus.submit_vote(round_id, node2_id, VoteType.APPROVE)
consensus.submit_vote(round_id, node3_id, VoteType.APPROVE)

# Check if quorum reached
reached, result = consensus.check_quorum(round_id)
```

## Deployment Phases

The system follows three deployment phases:

1. **Phase 1**: Latticework Development (core implementation)
2. **Phase 2**: Testing, Integration, Intelligence (current - verification)
3. **Phase 3**: First Mission Simulation & Deployment (production)

### Phase 2 Verification

```python
from sol.activation import Phase2Verifier

verifier = Phase2Verifier()
report = verifier.run_verification()
# Returns verification results for: blueprint, architecture, hierarchy,
# freq_law, ssc_prompt, mission_vectors
```

## Important Constraints

1. **Response Time**: All operations must complete within 2000ms
2. **Quorum**: Critical operations require k=3 node approvals
3. **Audit Trail**: All operations must be logged to BigQuery
4. **VETO**: GOV Engine can block any non-compliant operation

## Dependencies

### Required

- `pyyaml>=6.0` - Configuration parsing

### Optional (GCP)

- `google-cloud-bigquery>=3.0.0` - Audit logging
- `google-cloud-aiplatform>=1.38.0` - Vertex AI integration

### Development

- `pytest>=7.0.0` - Testing
- `pytest-cov>=4.0.0` - Coverage
- `black>=23.0.0` - Formatting
- `ruff>=0.1.0` - Linting
- `mypy>=1.0.0` - Type checking

## Mission Vectors

The system is designed for two primary mission vectors:

1. **Vector Alpha (Heritage Transmutation)**: COBOL/AS400 legacy modernization
2. **Vector Gamma (Maritime Barge Drafting)**: Target accuracy 0.998

## Hierarchy Levels

The system operates on a 6-level hierarchy:

| Level | Name | Description |
|-------|------|-------------|
| 0 | Sovereign Intent Originator | Chief Dre - ultimate authority |
| 1 | Strategic Synthesis Core | Central orchestrator |
| 2 | Domain Orchestrators | Domain-specific coordination |
| 3 | Specialist Executors | Task execution |
| 4 | Tool Adapters | External system integration |
| 5 | Runtime Realization | Execution environment |
