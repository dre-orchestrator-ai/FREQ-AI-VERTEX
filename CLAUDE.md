# CLAUDE.md - AI Assistant Guide for FREQ-AI-VERTEX

This document provides context for AI assistants working with the FREQ-AI-VERTEX codebase.

## Project Overview

**FREQ-AI-VERTEX** contains the **Sophisticated Operational Lattice (SOL)** - a distributed AI orchestration system for legacy modernization across regulated industries. It is designed to be deployed on Google Cloud Vertex AI Agent Builder using Gemini substrates.

### Key Concepts

- **SOL (Sophisticated Operational Lattice)**: The core distributed AI orchestration architecture
- **FREQ LAW**: Governance protocol enforcing Fast, Robust, Evolutionary, Quantified operations
- **Lattice Nodes**: Specialized AI nodes that perform specific roles in the system
- **k=3 Quorum Consensus**: Critical operations require approval from at least 3 nodes
- **VETO Authority**: GOV Engine can absolutely veto non-compliant operations

## Codebase Structure

```
FREQ-AI-VERTEX/
├── src/
│   └── sol/                         # Main package
│       ├── activation/              # Deployment phases & verification
│       │   └── phase2_verification.py
│       ├── audit/                   # BigQuery audit trail
│       │   └── bigquery.py
│       ├── blueprint/               # FREQ Blueprint & SSC prompts
│       │   └── freq_blueprint.py
│       ├── consensus/               # Quorum voting system
│       │   └── quorum.py
│       ├── governance/              # FREQ LAW & VETO
│       │   ├── freq_law.py
│       │   └── veto.py
│       └── nodes/                   # Lattice node implementations
│           ├── base.py              # Base LatticeNode class
│           ├── strategic_op.py      # Mission coordination
│           ├── spci.py              # Continuous improvement
│           ├── legacy_architect.py  # Legacy translation
│           ├── gov_engine.py        # Governance & VETO
│           ├── exec_automate.py     # Workflow execution
│           ├── optimal_intel.py     # Analytics
│           └── element_design.py    # Schema generation
├── config/
│   ├── sol_config.yaml              # SOL configuration
│   └── vertex_ai_agent.yaml         # Vertex AI deployment config
├── tests/
│   └── test_sol.py                  # Test suite
├── .github/agents/
│   └── strategic-opus-code.md       # GitHub agent configuration
├── pyproject.toml                   # Python package configuration
└── README.md
```

## Development Commands

```bash
# Install base package
pip install -e .

# Install with GCP dependencies
pip install -e ".[gcp]"

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test class
pytest tests/test_sol.py::TestFreqLaw

# Format code with Black
black src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/
```

## Architecture & Key Patterns

### Lattice Nodes Hierarchy

| Node | Role | Priority |
|------|------|----------|
| **GOV Engine** | Governance & VETO authority | 0 (highest) |
| **Strategic OP** | Mission-level coordination | 1 |
| **SPCI** | Continuous improvement cycles | 2 |
| **Legacy Architect** | Legacy system translation | 2 |
| **Exec Automate** | Workflow execution | 3 |
| **Optimal Intel** | Analytics and decision support | 3 |
| **Element Design** | Schema and artifact generation | 3 |

### FREQ LAW Principles

All operations must comply with FREQ LAW:

| Principle | Requirement | Enforcement |
|-----------|-------------|-------------|
| **F**ast | Response time < 2000ms | GOV Engine timing validation |
| **R**obust | Resilient to failures | k=3 quorum consensus |
| **E**volutionary | Continuous improvement | SPCI integration |
| **Q**uantified | Measured and logged | BigQuery audit trail |

### Node Communication Pattern

All node exchanges follow the request-response-validate pattern:
1. Originating node issues intent packet (`NodeMessage`)
2. Receiving node acknowledges + processes
3. GOV Engine validates compliance
4. Audit trail logged before state transition

### Base Classes & Dataclasses

- `LatticeNode` (ABC): Base class for all nodes in `src/sol/nodes/base.py`
- `NodeMessage`: Message passed between lattice nodes
- `NodeResponse`: Response from a node operation
- `NodeType`: Enum of all node types

### Consensus System

The quorum system in `src/sol/consensus/quorum.py`:
- `QuorumConsensus`: Manager for consensus rounds
- `ConsensusRound`: Represents a voting round
- `Vote`: Individual vote with `VoteType` (APPROVE, REJECT, ABSTAIN)
- Default requirement: k=3 votes for approval

## Code Conventions

### Python Style
- Python 3.9+ required
- Line length: 100 characters (Black, Ruff)
- Use type hints for function signatures
- Docstrings for all public classes and methods

### Import Organization
- Standard library imports first
- Third-party imports second
- Local imports last (use relative imports within `sol` package)

### Testing Conventions
- Tests in `tests/` directory
- Test files prefixed with `test_`
- Test classes prefixed with `Test`
- Test methods prefixed with `test_`
- Use pytest fixtures where appropriate

### Package Structure
- All source code under `src/sol/`
- Each submodule has an `__init__.py` with public exports
- Use relative imports for intra-package imports

## Key Files to Understand

1. **`src/sol/nodes/base.py`**: Core abstractions for the lattice node system
2. **`src/sol/governance/freq_law.py`**: FREQ LAW enforcement implementation
3. **`src/sol/consensus/quorum.py`**: k=3 quorum voting mechanism
4. **`src/sol/blueprint/freq_blueprint.py`**: System blueprint and SSC configuration
5. **`config/sol_config.yaml`**: Main configuration for SOL system

## Deployment Phases

The system follows a phased deployment approach:

1. **Phase 1**: Latticework Development - Building the core lattice infrastructure
2. **Phase 2**: Testing, Integration, Intelligence - Verification and activation
3. **Phase 3**: First Mission Simulation & Deployment - Production readiness

Run Phase 2 verification:
```python
from sol.activation import run_phase2_verification
report = run_phase2_verification()
```

## Common Patterns

### Creating a New Lattice Node

```python
from sol.nodes.base import LatticeNode, NodeType, NodeMessage, NodeResponse

class MyNode(LatticeNode):
    @property
    def node_type(self) -> NodeType:
        return NodeType.STRATEGIC_OP  # or appropriate type

    @property
    def description(self) -> str:
        return "Description of node's role"

    def process_message(self, message: NodeMessage) -> NodeResponse:
        # Handle the message and return response
        return NodeResponse(
            message_id=message.id,
            node_id=self.node_id,
            success=True,
            result={"status": "processed"}
        )
```

### Using Quorum Consensus

```python
from sol.consensus import QuorumConsensus, VoteType

consensus = QuorumConsensus(required_votes=3)
consensus.register_voter("node1")
consensus.register_voter("node2")
consensus.register_voter("node3")

round = consensus.initiate_consensus("my_operation", "initiator_node")
consensus.submit_vote(round.id, "node1", VoteType.APPROVE)
consensus.submit_vote(round.id, "node2", VoteType.APPROVE)
consensus.submit_vote(round.id, "node3", VoteType.APPROVE)

assert consensus.has_quorum(round.id)
```

### FREQ LAW Validation

```python
from sol.governance import FreqLaw
import time

freq_law = FreqLaw()
start_time = time.time()

# ... perform operation ...

result = freq_law.validate_response_time(start_time, "operation_name")
if not result["is_compliant"]:
    # Handle FREQ LAW violation
    pass
```

## Configuration

### SOL Config (`config/sol_config.yaml`)
- `freq_law`: FREQ LAW constraint settings
- `nodes`: Per-node configuration and priorities
- `consensus`: Quorum settings (k=3, timeout)
- `audit`: BigQuery audit configuration
- `vertex_ai`: Vertex AI deployment settings

### Key Configuration Values
- `max_response_time_ms`: 2000 (FREQ LAW Fast requirement)
- `quorum_k`: 3 (minimum votes for consensus)
- `require_audit_trail`: true (FREQ LAW Quantified requirement)
- `enable_veto_authority`: true (GOV Engine VETO power)

## Domain Context

This system is designed for **legacy modernization** in **regulated industries**. The "operator" (referred to as "Chief Dre" in the blueprint) works through **verbal orchestration** and **intent-based synthesis** - meaning natural language directives are translated into executable architecture.

### Mission Vectors
- **Vector Alpha**: Heritage Transmutation - COBOL/AS400 modernization to cloud-native
- **Vector Gamma**: Maritime Barge Drafting - Document processing with 99.8% accuracy target

## Testing

Run the full test suite:
```bash
pytest tests/test_sol.py -v
```

Test categories:
- `TestFreqLaw`: FREQ LAW governance tests
- `TestVetoAuthority`: VETO mechanism tests
- `TestQuorumConsensus`: k=3 quorum tests
- `TestBigQueryAuditTrail`: Audit logging tests
- `TestLatticeNodes`: Individual node tests
- `TestIntegration`: Full workflow integration tests
- `TestBlueprintModule`: Blueprint configuration tests
- `TestPhase2Verification`: Phase 2 activation tests

## Dependencies

### Core
- `pyyaml>=6.0`: YAML configuration parsing

### GCP (optional)
- `google-cloud-bigquery>=3.0.0`: Audit trail storage
- `google-cloud-aiplatform>=1.38.0`: Vertex AI integration

### Development
- `pytest>=7.0.0`: Testing framework
- `pytest-cov>=4.0.0`: Coverage reporting
- `black>=23.0.0`: Code formatting
- `ruff>=0.1.0`: Linting
- `mypy>=1.0.0`: Type checking
