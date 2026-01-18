# FREQ-AI-VERTEX

Sophisticated Operational Lattice (SOL) - Multi-node AI orchestration system for legacy modernization across regulated industries. Built on Gemini substrates with FREQ LAW governance, FSM state management, and sub-2000ms response protocols.

## System Identity

This repository contains the **Sophisticated Operational Lattice (SOL)**, a distributed AI orchestration system deployed on Google Cloud Vertex AI Agent Builder using Gemini substrates.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOL - Sophisticated Operational Lattice       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ Strategic OP │◄──►│     SPCI     │◄──►│   Legacy     │       │
│  │  (Mission)   │    │ (Continuous  │    │  Architect   │       │
│  └──────┬───────┘    │ Improvement) │    │(Translation) │       │
│         │            └──────┬───────┘    └──────┬───────┘       │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      GOV ENGINE                          │   │
│  │          FREQ LAW Compliance | VETO Authority            │   │
│  │              k=3 Quorum | BigQuery Audit                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │    Exec      │◄──►│   Optimal    │◄──►│   Element    │       │
│  │   Automate   │    │    Intel     │    │    Design    │       │
│  │  (Workflow)  │    │ (Analytics)  │    │  (Schema)    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Lattice Nodes

| Node | Role | Description |
|------|------|-------------|
| **Strategic OP** | Mission Coordination | High-level strategic planning, cross-node orchestration, priority management |
| **SPCI** | Continuous Improvement | Performance metrics, A/B testing, learning loops, evolutionary optimization |
| **Legacy Architect** | System Translation | Protocol translation, data transformation, legacy API adaptation, migration planning |
| **GOV Engine** | Governance & Compliance | FREQ LAW enforcement, k=3 quorum validation, absolute VETO authority |
| **Exec Automate** | Workflow Execution | Multi-step workflows, parallel/sequential execution, error handling |
| **Optimal Intel** | Decision Support | Data aggregation, predictive modeling, recommendations, dashboards |
| **Element Design** | Artifact Generation | Schema definition, artifact generation, template management |

## FREQ LAW Governance Protocol

All SOL operations are governed by **FREQ LAW**:

| Principle | Requirement | Enforcement |
|-----------|-------------|-------------|
| **F**ast | Response time < 2000ms | GOV Engine timing validation |
| **R**obust | Resilient to failures | k=3 quorum consensus |
| **E**volutionary | Continuous improvement | SPCI integration |
| **Q**uantified | Measured and logged | BigQuery audit trail |

### Key Governance Features

- **k=3 Quorum Consensus**: Critical operations require approval from at least 3 nodes
- **VETO Authority**: GOV Engine holds absolute VETO power over non-compliant operations
- **Audit Trail**: All operations logged to BigQuery for compliance and traceability

## Installation

### Quick Install (Recommended)

```bash
# One-line installation
curl -fsSL https://raw.githubusercontent.com/dre-orchestrator-ai/FREQ-AI-VERTEX/main/install.sh | bash

# With GCP support and virtual environment
curl -fsSL https://raw.githubusercontent.com/dre-orchestrator-ai/FREQ-AI-VERTEX/main/install.sh | bash -s -- --gcp --venv

# Development environment
curl -fsSL https://raw.githubusercontent.com/dre-orchestrator-ai/FREQ-AI-VERTEX/main/install.sh | bash -s -- --dev --venv
```

**Installation Options:**
- `--gcp` - Install with Google Cloud Platform dependencies
- `--dev` - Install development dependencies (pytest, black, ruff, mypy)
- `--venv` - Create and use a virtual environment
- `--skip-clone` - Skip repository cloning (use if already cloned)
- `--help` - Show all available options

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX.git
cd FREQ-AI-VERTEX

# Install base package
pip install -e .

# Install with GCP dependencies
pip install -e ".[gcp]"

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```python
from sol.nodes import StrategicOP, GOVEngine, SPCI
from sol.consensus import QuorumConsensus
from sol.governance import FreqLaw

# Initialize governance
freq_law = FreqLaw()
consensus = QuorumConsensus(required_votes=3)

# Create lattice nodes
strategic_op = StrategicOP()
gov_engine = GOVEngine()
spci = SPCI()

# Register nodes for consensus voting
consensus.register_voter(strategic_op.node_id)
consensus.register_voter(gov_engine.node_id)
consensus.register_voter(spci.node_id)

# Connect nodes
strategic_op.connect_node(gov_engine)
strategic_op.connect_node(spci)

# Execute operations with governance
print(f"Lattice nodes initialized: {strategic_op.node_type.value}")
```

## Project Structure

```
FREQ-AI-VERTEX/
├── src/
│   └── sol/
│       ├── __init__.py
│       ├── nodes/
│       │   ├── __init__.py
│       │   ├── base.py              # Base LatticeNode class
│       │   ├── strategic_op.py      # Mission coordination
│       │   ├── spci.py              # Continuous improvement
│       │   ├── legacy_architect.py  # Legacy translation
│       │   ├── gov_engine.py        # Governance & VETO
│       │   ├── exec_automate.py     # Workflow execution
│       │   ├── optimal_intel.py     # Analytics
│       │   └── element_design.py    # Schema generation
│       ├── governance/
│       │   ├── __init__.py
│       │   ├── freq_law.py          # FREQ LAW constraints
│       │   └── veto.py              # VETO authority
│       ├── consensus/
│       │   ├── __init__.py
│       │   └── quorum.py            # k=3 quorum consensus
│       └── audit/
│           ├── __init__.py
│           └── bigquery.py          # BigQuery audit trail
├── config/
│   ├── sol_config.yaml              # SOL configuration
│   └── vertex_ai_agent.yaml         # Vertex AI deployment
├── tests/
│   └── test_sol.py                  # Test suite
├── pyproject.toml                   # Python package config
└── README.md
```

## Configuration

### SOL Configuration (`config/sol_config.yaml`)

```yaml
freq_law:
  max_response_time_ms: 2000
  quorum_k: 3
  require_audit_trail: true
  enable_veto_authority: true

consensus:
  required_votes: 3
  timeout_seconds: 30
```

### Vertex AI Deployment

The `config/vertex_ai_agent.yaml` contains the Agent Builder configuration including:
- Playbooks for each lattice node
- Tools for FREQ LAW validation, quorum consensus, and audit logging
- Generative AI settings with Gemini 1.5 Pro

## Response Protocol

When receiving directives, SOL responds with architectural clarity:

1. **What**: Explains the operation being performed
2. **Why**: Justifies alignment with FREQ LAW
3. **How**: Describes integration with lattice topology

## Operator Interface

This system supports **verbal orchestration** and **intent-based synthesis**. Natural language directives are translated into executable architecture by the Context Architect role.

## License

MIT License - See LICENSE file for details.
