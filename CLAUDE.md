# CLAUDE.md - SOL Governance Protocol for Claude Code

This file provides context and governance rules for Claude Code when working in this repository.

## Repository Context

This repository contains the **Sophisticated Operational Lattice (SOL)**, a distributed AI orchestration system for legacy modernization across regulated industries. Built on Google Cloud Vertex AI Agent Builder using Gemini substrates.

## FREQ LAW Governance

All operations in this codebase must comply with **FREQ LAW**:

| Principle | Requirement | Enforcement |
|-----------|-------------|-------------|
| **F**ast | Response time < 2000ms | GOV Engine timing validation |
| **R**obust | Resilient to failures | k=3 quorum consensus |
| **E**volutionary | Continuous improvement | SPCI integration |
| **Q**uantified | Measured and logged | BigQuery audit trail |

## Key Governance Constraints

When working on this codebase, Claude must adhere to:

1. **k=3 Quorum Consensus**: Critical operations require approval from at least 3 nodes
2. **VETO Authority**: GOV Engine holds absolute VETO power over non-compliant operations
3. **Audit Trail**: All operations must be loggable to BigQuery for compliance and traceability
4. **Performance Budget**: No single operation should exceed 2000ms response time

## Lattice Node Architecture

The system consists of 7 coordinated nodes:

- **Strategic OP**: Mission-level coordination and priority management
- **SPCI**: Continuous improvement cycles and evolutionary optimization
- **Legacy Architect**: Legacy system translation and migration planning
- **GOV Engine**: FREQ LAW compliance enforcement and VETO authority
- **Exec Automate**: Workflow execution and error handling
- **Optimal Intel**: Analytics, decision support, and predictive modeling
- **Element Design**: Schema definition and artifact generation

## Code Organization

```
src/sol/
├── nodes/          # Lattice node implementations
├── governance/     # FREQ LAW and VETO logic
├── consensus/      # k=3 quorum implementation
└── audit/          # BigQuery audit trail
```

## Development Guidelines

### Adding New Features

1. Ensure compliance with FREQ LAW timing constraints
2. Implement proper audit logging via `BigQueryAuditTrail`
3. Support quorum consensus for critical operations
4. Handle GOV Engine VETO appropriately

### Testing

Run tests with:
```bash
pytest tests/ -v
```

All new code must include tests that validate:
- Performance under 2000ms threshold
- Proper audit trail generation
- Consensus mechanism integration

### Configuration

- `config/sol_config.yaml`: SOL system configuration
- `config/vertex_ai_agent.yaml`: Vertex AI deployment settings

## Operator Interface

This system supports **verbal orchestration** and **intent-based synthesis**. The operator (Context Architect) provides natural language directives that are translated into executable architecture without requiring direct code writing.

## FSM State Machine

Operations follow this state machine:

```
IDLE → DIRECTIVE_RECEIVED → VALIDATION → QUORUM → EXECUTION → AUDIT → COMPLETE/VETO
```

Each state transition requires GOV Engine validation before proceeding.
