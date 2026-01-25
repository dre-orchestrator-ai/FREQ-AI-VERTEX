# CLAUDE.md - AI Assistant Guide for FREQ-AI-VERTEX

## Project Overview

**FREQ-AI-VERTEX** is a Sophisticated Operational Lattice (SOL) system—a distributed AI orchestration framework with 7 specialized nodes governed by the FREQ LAW protocol. It is designed for deployment on Google Cloud Vertex AI with BigQuery audit integration.

**Core Identity:**
- System Name: SOL (Sophisticated Operational Lattice)
- Governance: FREQ LAW (Fast, Robust, Evolutionary, Quantified)
- Deployment Target: Google Cloud Vertex AI Agent Builder with Gemini substrates

## Quick Reference

```bash
# Install for development
pip install -e ".[dev]"

# Run all tests
pytest tests/test_sol.py -v

# Code formatting
black src/ tests/ --line-length 100

# Linting
ruff check src/ tests/

# Type checking
mypy src/
```

## Directory Structure

```
FREQ-AI-VERTEX/
├── .github/agents/           # Agent configuration docs
│   └── strategic-opus-code.md
├── config/
│   ├── sol_config.yaml       # SOL system configuration
│   └── vertex_ai_agent.yaml  # Vertex AI deployment config
├── src/sol/                  # Main source code
│   ├── nodes/                # 7 lattice node implementations
│   │   ├── base.py           # LatticeNode ABC + NodeMessage/NodeResponse
│   │   ├── strategic_op.py   # Mission coordination
│   │   ├── spci.py           # Continuous improvement
│   │   ├── legacy_architect.py
│   │   ├── gov_engine.py     # FREQ LAW enforcement
│   │   ├── exec_automate.py  # Workflow execution
│   │   ├── optimal_intel.py  # Analytics & decisions
│   │   └── element_design.py # Schema generation
│   ├── governance/           # FREQ LAW & VETO systems
│   │   ├── freq_law.py
│   │   └── veto.py
│   ├── consensus/            # k=3 quorum consensus
│   │   └── quorum.py
│   ├── audit/                # BigQuery audit trail
│   │   └── bigquery.py
│   ├── blueprint/            # FREQ Blueprint Phase 2
│   │   └── freq_blueprint.py
│   └── activation/           # Activation verification
│       └── phase2_verification.py
├── tests/
│   └── test_sol.py           # Comprehensive test suite
├── pyproject.toml            # Project configuration
└── README.md                 # User documentation
```

## Core Concepts

### 1. Lattice Nodes

Seven specialized nodes that communicate via message passing:

| Node | Type | Purpose |
|------|------|---------|
| **StrategicOP** | `strategic_op` | Mission-level coordination, workflow orchestration |
| **SPCI** | `spci` | Continuous improvement cycles, metrics collection |
| **LegacyArchitect** | `legacy_architect` | Legacy system translation, protocol adapters |
| **GOVEngine** | `gov_engine` | FREQ LAW enforcement, VETO authority |
| **ExecAutomate** | `exec_automate` | Workflow execution, multi-step automation |
| **OptimalIntel** | `optimal_intel` | Analytics, decision support, data aggregation |
| **ElementDesign** | `element_design` | Schema generation, artifact templates |

### 2. FREQ LAW Governance

Four-pillar governance protocol:
- **Fast**: Response time < 2000ms
- **Robust**: Error handling and graceful degradation
- **Evolutionary**: Continuous improvement metrics
- **Quantified**: Measurable outcomes with audit trails

### 3. Consensus System

- Quorum-based consensus with k=3 minimum votes
- Vote types: APPROVE, REJECT, ABSTAIN
- All decisions require consensus before execution

### 4. VETO Authority

GOVEngine has absolute veto power for:
- Security violations
- Policy violations
- Resource exhaustion
- Data integrity issues
- Compliance failures
- Unsafe operations

## Code Conventions

### Type Hints (Required)

All functions must have comprehensive type hints:

```python
def process_message(self, message: NodeMessage) -> NodeResponse:
    """Process incoming message and return response."""
    ...
```

### Dataclasses for Data Structures

```python
@dataclass
class NodeMessage:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_node: str = ""
    target_node: str = ""
    operation: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

### Node Implementation Pattern

All nodes inherit from `LatticeNode` ABC:

```python
class MyNode(LatticeNode):
    @property
    def node_type(self) -> NodeType:
        return NodeType.MY_NODE

    @property
    def description(self) -> str:
        return "Description of node purpose"

    def process_message(self, message: NodeMessage) -> NodeResponse:
        start_time = time.time()
        try:
            # Process logic here
            result = self._handle_operation(message)
            return NodeResponse(
                success=True,
                result=result,
                execution_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return NodeResponse(
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )
```

### Naming Conventions

- Classes: `PascalCase` (e.g., `StrategicOP`, `NodeMessage`)
- Functions/methods: `snake_case` (e.g., `process_message`, `create_workflow`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `FREQ_BLUEPRINT`, `SSC_SYSTEM_PROMPT`)
- Private methods: `_leading_underscore` (e.g., `_create_response`, `_validate_input`)
- Enums: `PascalCase` class, `UPPER_SNAKE_CASE` values

### Return Value Pattern

Operations return `Dict[str, Any]` with standard keys:

```python
# Success case
{"success": True, "workflow_id": "...", "status": "created"}

# Error case
{"error": "Description of what went wrong"}
```

## Testing Guidelines

### Test File Location

All tests in `tests/test_sol.py`

### Test Naming

```python
class TestNodeName:
    def test_operation_name(self):
        """Description of what is being tested."""
        ...
```

### Test Structure

```python
def test_workflow_creation(self):
    """Test that workflows are created correctly."""
    # Arrange
    node = StrategicOP()
    message = NodeMessage(
        source_node="operator",
        target_node="strategic_op",
        operation="create_workflow",
        payload={"name": "test_workflow", "steps": [...]}
    )

    # Act
    response = node.process_message(message)

    # Assert
    assert response.success is True
    assert "workflow_id" in response.result
```

### Running Tests

```bash
# All tests
pytest tests/test_sol.py -v

# Specific test class
pytest tests/test_sol.py::TestLatticeNodes -v

# Specific test
pytest tests/test_sol.py::TestLatticeNodes::test_strategic_op_workflow -v

# With coverage
pytest tests/test_sol.py -v --cov=src/sol
```

## Common Development Tasks

### Adding a New Node

1. Create node file in `src/sol/nodes/`:
```python
# src/sol/nodes/my_node.py
from .base import LatticeNode, NodeType, NodeMessage, NodeResponse

class MyNode(LatticeNode):
    # Implement required properties and methods
```

2. Add NodeType enum value in `src/sol/nodes/base.py`

3. Export in `src/sol/__init__.py`

4. Add tests in `tests/test_sol.py`

5. Update `config/sol_config.yaml` with node configuration

### Adding a New Operation to Existing Node

1. Add handler method in the node class:
```python
def _handle_new_operation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the new operation."""
    ...
```

2. Register in `process_message` dispatch logic

3. Add corresponding tests

### Modifying FREQ LAW Constraints

Edit `src/sol/governance/freq_law.py`:
- `FreqLawConfig` dataclass for constraint values
- `FreqLaw.validate()` for validation logic

Also update `config/sol_config.yaml` for deployment configuration.

## Important Files

| File | Purpose |
|------|---------|
| `src/sol/nodes/base.py` | Core abstractions (LatticeNode, NodeMessage, NodeResponse) |
| `src/sol/governance/freq_law.py` | FREQ LAW governance implementation |
| `src/sol/governance/veto.py` | VETO authority logic |
| `src/sol/consensus/quorum.py` | k=3 quorum consensus |
| `src/sol/blueprint/freq_blueprint.py` | System blueprint and SSC prompt |
| `config/sol_config.yaml` | Runtime configuration |
| `tests/test_sol.py` | Complete test suite |

## Configuration

### Key Configuration Parameters

From `config/sol_config.yaml`:

```yaml
freq_law:
  max_response_time_ms: 2000  # FREQ LAW: Fast
  quorum_k: 3                  # Consensus requirement
  audit_enabled: true          # BigQuery logging

consensus:
  min_votes: 3
  timeout_seconds: 30
```

### Environment Variables

For GCP deployment:
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `BIGQUERY_DATASET`: Audit log dataset
- `VERTEX_AI_LOCATION`: Deployment region (default: us-central1)

## Code Quality Tools

### Black (Formatting)

```bash
black src/ tests/ --line-length 100
```

Configuration in `pyproject.toml`:
```toml
[tool.black]
line-length = 100
```

### Ruff (Linting)

```bash
ruff check src/ tests/
ruff check src/ tests/ --fix  # Auto-fix
```

Configuration:
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "UP"]
```

### MyPy (Type Checking)

```bash
mypy src/
```

Configuration:
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
```

## Architecture Patterns

### Message Passing

Nodes communicate via `NodeMessage` → `NodeResponse`:

```python
message = NodeMessage(
    source_node="strategic_op",
    target_node="gov_engine",
    operation="validate_workflow",
    payload={"workflow_id": "...", "actions": [...]}
)
response = gov_engine.process_message(message)
```

### History Tracking

All nodes maintain message and response history:

```python
node._message_history  # List of received messages
node._response_history  # List of sent responses
```

### Audit Trail

All operations log to BigQuery via `AuditEntry`:

```python
entry = AuditEntry(
    timestamp=datetime.utcnow(),
    node_id=self.node_id,
    operation="create_workflow",
    payload={"workflow_id": "..."},
    result={"success": True}
)
audit_trail.log_entry(entry)
```

## Python Version

- Minimum: Python 3.9
- Tested: 3.9, 3.10, 3.11, 3.12

## Dependencies

Core:
- `pyyaml>=6.0`

GCP (optional):
- `google-cloud-bigquery>=3.0`
- `google-cloud-aiplatform>=1.40`

Development:
- `pytest>=7.0`
- `black>=23.0`
- `ruff>=0.1.0`
- `mypy>=1.0`

## Git Workflow

1. Create feature branch from main
2. Make changes following code conventions
3. Run tests: `pytest tests/test_sol.py -v`
4. Format code: `black src/ tests/`
5. Lint: `ruff check src/ tests/`
6. Type check: `mypy src/`
7. Commit with descriptive message
8. Push and create PR

## Troubleshooting

### Import Errors

Use relative imports within the sol package:
```python
from .base import LatticeNode  # Correct
from sol.base import LatticeNode  # Avoid
```

### Test Discovery Issues

Ensure `tests/__init__.py` exists (can be empty).

### Type Checking Failures

Install stubs for external packages:
```bash
pip install types-PyYAML
```

## License

MIT License - see README.md for details.
