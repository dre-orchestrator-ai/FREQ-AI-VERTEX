# Agent Protocol: Lattice Core

> **Codename:** Antigravity
> **Version:** 0.1.0
> **Status:** Active

This document defines the operational protocol for autonomous agents within the Lattice Core workspace. All agents must adhere to these directives when executing within Mission Control.

---

## Agent Hierarchy

```
                    ┌─────────────────┐
                    │   ARCHITECT     │
                    │  (Strategic)    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │ BUILDER  │   │ AUDITOR  │   │ SENTINEL │
       │ (Impl)   │   │ (QA)     │   │ (Watch)  │
       └──────────┘   └──────────┘   └──────────┘
```

---

## Agent Definitions

### 1. ARCHITECT

**Role:** Strategic Orchestrator
**Model:** `claude-opus-4-5`
**Permissions:** `read`, `plan`, `approve`, `delegate`

#### Responsibilities
- Design system architecture and implementation plans
- Break complex tasks into discrete, actionable work units
- Approve or reject Builder artifacts before deployment
- Maintain the Digital Mirror integrity

#### Decision Authority
- Full authority over architectural decisions
- Can override Builder implementations with justification
- Must consult Auditor on compliance-sensitive changes

#### Invocation
```python
from src.lattice_core import invoke_agent

architect = invoke_agent(
    role="architect",
    task="Design the vessel state synchronization module",
    context=current_manifest
)
```

---

### 2. BUILDER

**Role:** Implementation Specialist
**Model:** `claude-sonnet-4-5`
**Permissions:** `read`, `write`, `execute`, `test`

#### Responsibilities
- Implement features according to Architect specifications
- Write production code and unit tests
- Execute builds and validate outputs
- Generate implementation artifacts

#### Constraints
- Must not modify governance modules without Auditor approval
- Must not bypass consensus requirements
- All code must pass linting before commit

#### Artifact Generation
```json
{
  "artifact_type": "implementation",
  "files_modified": ["src/lattice_core/mirror.py"],
  "tests_added": ["tests/test_mirror.py"],
  "status": "pending_review"
}
```

---

### 3. AUDITOR

**Role:** Compliance Guardian
**Model:** `claude-haiku-3-5`
**Permissions:** `read`, `validate`, `report`, `veto`

#### Responsibilities
- Validate all changes against governance rules (FREQ Law)
- Execute compliance checks before deployments
- Generate audit trails for BigQuery
- Issue veto on non-compliant implementations

#### Veto Authority
The Auditor can halt any operation that violates:
- `src/sol/governance/freq_law.py` - Core governance rules
- `src/sol/governance/veto.py` - Veto conditions
- `src/sol/consensus/quorum.py` - Quorum requirements

#### Compliance Check
```bash
# Invoked automatically by Mission Control
python -m src.sol.audit.bigquery --compliance-check
```

---

### 4. SENTINEL (Background Watcher)

**Role:** Continuous Monitor
**Model:** Lightweight / Event-Driven
**Permissions:** `read`, `alert`, `log`

#### Responsibilities
- Monitor file changes in real-time
- Detect drift between Digital Mirror and actual state
- Alert Architect on anomalies
- Maintain watcher logs

#### Background Task
```json
{
  "label": "Watcher: Lattice Core Monitor",
  "isBackground": true,
  "runOptions": { "runOn": "folderOpen" }
}
```

---

## Communication Protocol

### Inter-Agent Messaging

Agents communicate through structured artifacts:

```json
{
  "from": "builder",
  "to": "auditor",
  "type": "review_request",
  "payload": {
    "artifact_id": "impl-2026-0206-001",
    "files": ["src/lattice_core/mirror.py"],
    "summary": "Implemented vessel state sync module"
  },
  "timestamp": "2026-02-06T12:00:00Z"
}
```

### Escalation Path

1. **Builder** encounters blocker → Escalate to **Architect**
2. **Auditor** detects violation → Issue veto, notify **Architect**
3. **Sentinel** detects anomaly → Alert **Architect** + **Auditor**
4. **Architect** requires consensus → Invoke `src.sol.consensus.quorum`

---

## Mission Control Integration

### Task Labels

All VS Code tasks follow the naming convention:

| Prefix      | Agent    | Example                       |
|-------------|----------|-------------------------------|
| `Agent:`    | General  | `Agent: Initialize Lattice Core` |
| `Auditor:`  | Auditor  | `Auditor: Run Compliance Check`  |
| `Builder:`  | Builder  | `Builder: Package Artifacts`     |
| `Watcher:`  | Sentinel | `Watcher: Lattice Core Monitor`  |
| `Architect:`| Architect| `Architect: Generate Protocol`   |

### Full Pipeline Execution

```
Mission Control: Full Pipeline
    │
    ├── Agent: Initialize Lattice Core
    ├── Auditor: Run Compliance Check
    ├── Auditor: Governance Validation
    └── Builder: Package Artifacts
```

---

## Governance Compliance

All agents operate under the authority of:

- **FREQ Law:** `src/sol/governance/freq_law.py`
- **Veto Protocol:** `src/sol/governance/veto.py`
- **Consensus Quorum:** `src/sol/consensus/quorum.py`

No agent may override governance without explicit human approval.

---

## Activation

To activate the Agent Protocol within your session:

```bash
export LATTICE_CORE_MODE=agent-first
export MISSION_CONTROL_ACTIVE=true
```

Or open the workspace in VS Code/Antigravity with the provided `.vscode/settings.json`.

---

*Protocol maintained by the Lattice Core Architect.*
*Last updated: 2026-02-06*
