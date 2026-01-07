# CLAUDE.md - FREQ AI Vertex Orchestration Protocol

## Operator Identity & Interface

You are interfacing with the **Context Architect** of FREQ AI—a verbal orchestration operator who synthesizes intent through natural language directives. This operator does not write code; they articulate architectural intent.

### Operator Protocol

**Core Principle**: Translate verbal directives into executable lattice operations.

```
OPERATOR DIRECTIVE → INTENT CLASSIFICATION → LATTICE DECOMPOSITION → EXECUTION
```

**Directive Interpretation Rules**:
1. Parse natural language for strategic intent, not literal instructions
2. Decompose high-level goals into node-compatible operations
3. Never require the operator to specify implementation details
4. Always explain architectural decisions in business terms
5. Map directives to the appropriate lattice node(s) automatically

**Response Format**:
When receiving a directive, respond with:
- **Interpretation**: What you understood the directive to mean
- **Lattice Mapping**: Which node(s) will handle execution
- **FREQ LAW Alignment**: How this complies with governance constraints
- **Execution Plan**: Step-by-step breakdown of operations

---

## FREQ LAW Compliance Framework

### The Four Pillars

| Pillar | Constraint | Enforcement | Validation |
|--------|------------|-------------|------------|
| **F**ast | Response < 2000ms | GOV Engine timing gate | `validate_response_time()` |
| **R**obust | k=3 quorum consensus | Distributed voting | `check_quorum_requirement()` |
| **E**volutionary | Continuous improvement | SPCI metric cycles | Baseline → target tracking |
| **Q**uantified | Mandatory audit trail | BigQuery logging | `create_audit_entry()` |

### Compliance Validation Hooks

Before any operation executes, these validation hooks MUST pass:

```yaml
pre_execution_hooks:
  - name: timing_gate
    validator: GOVEngine.validate_operation()
    constraint: execution_time_ms < 2000
    on_failure: VETO with RESPONSE_TIME_VIOLATION

  - name: quorum_gate
    validator: QuorumConsensus.has_quorum()
    constraint: approval_count >= 3
    on_failure: VETO with QUORUM_NOT_MET

  - name: audit_gate
    validator: BigQueryAuditTrail.is_configured()
    constraint: audit_trail_enabled == true
    on_failure: VETO with AUDIT_TRAIL_MISSING

post_execution_hooks:
  - name: audit_log
    action: BigQueryAuditTrail.log_operation()
    required: always

  - name: metric_capture
    action: SPCI.record_metric()
    required: for_evolutionary_tracking
```

### VETO Authority

The GOV Engine holds **absolute VETO authority**. Any operation violating FREQ LAW constraints is blocked:

| Veto Reason | Trigger Condition | Resolution Path |
|-------------|-------------------|-----------------|
| `RESPONSE_TIME_VIOLATION` | execution_time > 2000ms | Optimize operation or decompose |
| `QUORUM_NOT_MET` | approvals < 3 | Re-initiate consensus round |
| `AUDIT_TRAIL_MISSING` | BigQuery not configured | Enable audit logging |
| `COMPLIANCE_VIOLATION` | Custom check failed | Address specific violation |
| `SECURITY_CONCERN` | Security policy breach | Security review required |
| `GOVERNANCE_OVERRIDE` | Manual executive veto | Escalation to operator |

---

## Lattice Node Architecture

### Node Role Boundaries

The Sophisticated Operational Lattice (SOL) comprises 7 specialized nodes. Each node has exclusive domain authority:

#### 1. Strategic OP (Priority: 1)
**Domain**: Mission-level coordination and cross-lattice orchestration

**Exclusive Operations**:
- `create_mission` - Define strategic missions with objectives
- `update_mission` - Modify mission parameters
- `get_mission_status` - Retrieve mission state
- `set_objective` - Establish strategic objectives
- `orchestrate` - Coordinate multi-node workflows

**Boundary**: Strategic OP defines WHAT to achieve; other nodes define HOW.

**State Ownership**: Active missions, strategic objectives, orchestration plans

---

#### 2. GOV Engine (Priority: 0 - HIGHEST)
**Domain**: Governance enforcement and absolute VETO authority

**Exclusive Operations**:
- `validate_operation` - FREQ LAW compliance check
- `request_quorum` - Initiate k=3 consensus round
- `submit_quorum_vote` - Record node approval/rejection
- `check_compliance` - Timing compliance validation
- `exercise_veto` - Manual governance override
- `get_veto_history` - Retrieve all VETO decisions
- `get_audit_log` - Access compliance audit log

**Boundary**: GOV Engine can VETO any operation from any node. No exceptions.

**State Ownership**: FREQ LAW constraints, VETO authority, pending quorum requests, compliance log

**Special Authority**: Absolute VETO power over all lattice operations

---

#### 3. SPCI (Priority: 2)
**Domain**: Systematic Process Continuous Improvement

**Exclusive Operations**:
- `record_metric` - Collect performance metrics
- `analyze_performance` - Statistical analysis (min/max/avg)
- `start_experiment` - Initiate A/B testing
- `end_experiment` - Conclude experiments
- `get_improvement_suggestions` - Generate optimization recommendations
- `create_improvement_cycle` - Track baseline → target improvements

**Boundary**: SPCI observes and optimizes; it does not execute business logic.

**State Ownership**: Metric history, experiments, improvement cycles, baselines

---

#### 4. Legacy Architect (Priority: 2)
**Domain**: Legacy system translation and protocol adaptation

**Exclusive Operations**:
- `register_adapter` - Configure protocol adapters
- `translate_protocol` - Protocol translation (REST, SOAP, GraphQL, gRPC)
- `transform_data` - Format transformation (XML ↔ JSON, CSV, etc.)
- `create_migration_plan` - Plan legacy system modernization
- `get_adapters` - List registered adapters

**Boundary**: Legacy Architect bridges external systems; internal node communication uses native protocols.

**State Ownership**: Adapters registry, transformations, migration plans

---

#### 5. Exec Automate (Priority: 3)
**Domain**: Multi-step workflow orchestration and execution

**Exclusive Operations**:
- `create_workflow` - Define workflow with steps
- `execute_workflow` - Run workflow sequentially/in parallel
- `pause_workflow` - Suspend execution
- `resume_workflow` - Restart paused workflow
- `cancel_workflow` - Abort workflow
- `get_workflow_status` - Retrieve execution state
- `list_workflows` - Enumerate all workflows

**Boundary**: Exec Automate orchestrates execution order; individual steps delegate to appropriate nodes.

**State Ownership**: Workflows, execution history, step status

**Workflow States**: `PENDING → RUNNING → (PAUSED) → COMPLETED|FAILED|CANCELLED`

---

#### 6. Optimal Intel (Priority: 3)
**Domain**: Analytics aggregation and decision support

**Exclusive Operations**:
- `register_data_source` - Connect analytics sources (BigQuery, APIs, nodes)
- `run_analysis` - Execute data analysis with results
- `get_recommendation` - Generate decision recommendations with confidence
- `aggregate_metrics` - Compute aggregations (sum, avg, min, max)
- `generate_report` - Create analytics dashboards

**Boundary**: Optimal Intel provides intelligence; it does not make decisions or take action.

**State Ownership**: Data sources, analyses, recommendations, reports

---

#### 7. Element Design (Priority: 3)
**Domain**: Schema definition and artifact generation

**Exclusive Operations**:
- `create_schema` - Define JSON Schema with validation rules
- `validate_schema` - Type-check data against schema
- `generate_artifact` - Create structured artifacts (configs, templates)
- `register_template` - Store template definitions
- `apply_template` - Substitute variables in templates
- `list_schemas` - Enumerate registered schemas

**Boundary**: Element Design defines structure; it does not populate content or execute logic.

**State Ownership**: Schemas, artifacts, templates, validation rules

---

## Inter-Node Communication Patterns

### Message Protocol

All node communication follows the `NodeMessage → NodeResponse` protocol:

```python
# Outbound Message Structure
NodeMessage:
  id: UUID                    # Unique message identifier
  source_node: str            # Originating node ID
  target_node: str            # Destination node ID
  operation: str              # Operation to execute
  payload: dict               # Operation parameters
  requires_quorum: bool       # Whether k=3 consensus needed
  timestamp: ISO8601          # Message creation time

# Response Structure
NodeResponse:
  message_id: UUID            # Corresponding message ID
  node_id: str                # Responding node ID
  success: bool               # Operation success flag
  result: dict                # Operation result data
  error: Optional[str]        # Error message if failed
  execution_time_ms: float    # Milliseconds elapsed
```

### Communication Patterns

#### Pattern 1: Direct Request-Response
```
Source Node → Target Node → Response
     ↓
Audit Trail
```
Use for: Simple operations not requiring consensus

#### Pattern 2: Quorum-Validated Request
```
Source Node → GOV Engine (validate) → Quorum Round
                                          ↓
                              Node1, Node2, Node3 vote
                                          ↓
                              Consensus achieved/rejected
                                          ↓
                              Target Node → Response
                                          ↓
                                    Audit Trail
```
Use for: Critical operations requiring distributed agreement

#### Pattern 3: Orchestrated Workflow
```
Strategic OP → Exec Automate (workflow definition)
                    ↓
              GOV Engine (compliance check)
                    ↓
              Step 1 → Node A → Audit
                    ↓
              Step 2 → Node B → Audit
                    ↓
              Step N → Node X → Audit
                    ↓
              Workflow Complete → SPCI (metrics)
```
Use for: Multi-step business processes

#### Pattern 4: Governance Intercept
```
Any Node → Operation Request
              ↓
         GOV Engine intercept
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
 APPROVED            VETOED
    ↓                   ↓
 Execute          Block + Log
    ↓                   ↓
 Audit Trail      Audit Trail
```
Use for: All operations (mandatory governance checkpoint)

### Routing Rules

| Source Node | Can Communicate With | Requires GOV Validation |
|-------------|---------------------|------------------------|
| Strategic OP | All nodes | Yes |
| GOV Engine | All nodes (broadcast authority) | No (self-validating) |
| SPCI | All nodes (observation only) | Yes |
| Legacy Architect | External systems + Element Design | Yes |
| Exec Automate | All nodes (workflow steps) | Yes |
| Optimal Intel | BigQuery + all nodes (read-only) | Yes |
| Element Design | Requesting node only | Yes |

---

## BigQuery Audit Trail Integration

### Schema Definition

All operations are logged to BigQuery with the following schema:

```sql
CREATE TABLE `{project_id}.sol_audit.operations` (
  id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  operation STRING NOT NULL,
  node_id STRING NOT NULL,
  node_type STRING NOT NULL,
  request_payload STRING,           -- JSON
  response_payload STRING,          -- JSON
  execution_time_ms FLOAT64 NOT NULL,
  success BOOL NOT NULL,
  error_message STRING,
  quorum_required BOOL NOT NULL,
  quorum_achieved BOOL NOT NULL,
  veto_applied BOOL NOT NULL,
  metadata STRING                   -- JSON
)
PARTITION BY DATE(timestamp)
CLUSTER BY node_type, operation;
```

### Integration Points

#### 1. Operation Logging
Every node operation triggers an audit entry:

```python
BigQueryAuditTrail.log_operation(
    operation="create_mission",
    node_id="strategic_op_001",
    node_type="STRATEGIC_OP",
    request_payload={"name": "Q1 Migration", "priority": "high"},
    response_payload={"mission_id": "m-123", "status": "created"},
    execution_time_ms=145.2,
    success=True,
    quorum_required=True,
    quorum_achieved=True,
    veto_applied=False
)
```

#### 2. VETO Logging
All VETO decisions are captured:

```python
BigQueryAuditTrail.log_operation(
    operation="execute_workflow",
    node_id="exec_automate_001",
    node_type="EXEC_AUTOMATE",
    request_payload={"workflow_id": "wf-456"},
    response_payload=None,
    execution_time_ms=2150.0,
    success=False,
    error_message="VETO: RESPONSE_TIME_VIOLATION",
    quorum_required=True,
    quorum_achieved=True,
    veto_applied=True
)
```

#### 3. Consensus Logging
Quorum rounds are fully audited:

```python
# Each vote in a consensus round
BigQueryAuditTrail.log_operation(
    operation="submit_quorum_vote",
    node_id="gov_engine_001",
    node_type="GOV_ENGINE",
    request_payload={
        "round_id": "r-789",
        "voter": "strategic_op_001",
        "vote": "APPROVE"
    },
    response_payload={"votes_received": 2, "quorum_met": False},
    execution_time_ms=12.5,
    success=True,
    quorum_required=False,
    quorum_achieved=False,
    veto_applied=False
)
```

### Query Patterns

```sql
-- Find all VETO'd operations in last 24 hours
SELECT * FROM `sol_audit.operations`
WHERE veto_applied = TRUE
  AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC;

-- Node performance analysis
SELECT
  node_type,
  operation,
  AVG(execution_time_ms) as avg_time,
  COUNT(*) as total_ops,
  COUNTIF(success = FALSE) as failures
FROM `sol_audit.operations`
WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY node_type, operation
ORDER BY avg_time DESC;

-- Quorum success rate
SELECT
  DATE(timestamp) as date,
  COUNTIF(quorum_achieved = TRUE) / COUNT(*) as quorum_success_rate
FROM `sol_audit.operations`
WHERE quorum_required = TRUE
GROUP BY date
ORDER BY date DESC;
```

### Buffer Configuration

```yaml
audit:
  enabled: true
  buffer_size: 100          # Entries before auto-flush
  flush_interval_seconds: 60
  bigquery:
    project_id: ${GCP_PROJECT_ID}
    dataset_id: sol_audit
    table_id: operations
    partition_by: timestamp
    cluster_by: [node_type, operation]
```

---

## FSM State Machine

The orchestration follows a deterministic finite state machine:

```
                    ┌──────────────────────────────────────┐
                    │                                      │
                    v                                      │
┌──────────┐   ┌─────────────────────┐   ┌────────────┐   │
│   IDLE   │──►│ DIRECTIVE_RECEIVED  │──►│ VALIDATION │   │
└──────────┘   └─────────────────────┘   └─────┬──────┘   │
     ▲              (Intent Parse)             │          │
     │                                         v          │
     │                                   ┌──────────┐     │
     │         ┌─────────────────────────│  QUORUM  │     │
     │         │                         └────┬─────┘     │
     │         │ (Consensus Rejected)         │           │
     │         │                              v           │
     │         │                        ┌───────────┐     │
     │         │                        │ EXECUTION │     │
     │         │                        └─────┬─────┘     │
     │         │                              │           │
     │         │                              v           │
     │         │                        ┌──────────┐      │
     │         │                        │  AUDIT   │      │
     │         │                        └────┬─────┘      │
     │         │                             │            │
     │         v                             v            │
     │    ┌────────┐                  ┌──────────┐        │
     └────│  VETO  │                  │ COMPLETE │────────┘
          └────────┘                  └──────────┘
```

| State | Description | Entry Condition | Exit Condition |
|-------|-------------|-----------------|----------------|
| `IDLE` | Awaiting operator directive | System ready | Directive received |
| `DIRECTIVE_RECEIVED` | Intent classification active | Operator input | Parse complete |
| `VALIDATION` | GOV Engine compliance check | Intent classified | Schema validated |
| `QUORUM` | k=3 node consensus polling | Validation passed | Consensus achieved |
| `EXECUTION` | Distributed task processing | Quorum approved | Workflow triggered |
| `AUDIT` | BigQuery trail logging | Execution complete | Audit committed |
| `COMPLETE` | Successful terminal state | Audit logged | Return to IDLE |
| `VETO` | Blocked terminal state | Governance failure | Return to IDLE |

---

## Development Guidelines

### Adding New Operations

1. Identify the appropriate node by domain (see Node Role Boundaries)
2. Implement operation in the node's `process_message()` handler
3. Add FREQ LAW compliance validation
4. Include audit logging in response path
5. Update tests in `tests/test_sol.py`

### FREQ LAW Checklist

Before merging any change:
- [ ] Response time < 2000ms verified
- [ ] Quorum logic included where required
- [ ] BigQuery audit entry generated
- [ ] VETO path handled gracefully
- [ ] SPCI metrics captured for improvement tracking

### Testing Requirements

```bash
# Run full test suite
pytest tests/test_sol.py -v

# Run with coverage
pytest tests/test_sol.py --cov=src/sol --cov-report=html

# Test specific node
pytest tests/test_sol.py::TestLatticeNodes::test_gov_engine_node -v
```

---

## Configuration Reference

### Environment Variables

```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export BIGQUERY_DATASET="sol_audit"
export FREQ_LAW_MAX_RESPONSE_MS="2000"
export FREQ_LAW_QUORUM_K="3"
```

### Configuration Files

| File | Purpose |
|------|---------|
| `config/sol_config.yaml` | Core SOL system configuration |
| `config/vertex_ai_agent.yaml` | Vertex AI Agent Builder deployment |
| `.github/agents/strategic-opus-code.md` | Claude Code agent configuration |

---

## Quick Reference

### Node Priority Hierarchy
```
GOV Engine (0) > Strategic OP (1) > SPCI, Legacy (2) > Exec, Intel, Design (3)
```

### FREQ LAW Mnemonic
```
Fast:         < 2000ms or VETO
Robust:       k=3 consensus or VETO
Evolutionary: SPCI tracks all metrics
Quantified:   BigQuery logs everything
```

### Common Operations

| Intent | Node | Operation |
|--------|------|-----------|
| "Start a new initiative" | Strategic OP | `create_mission` |
| "Check if this is allowed" | GOV Engine | `validate_operation` |
| "Track performance" | SPCI | `record_metric` |
| "Connect to legacy system" | Legacy Architect | `register_adapter` |
| "Run this process" | Exec Automate | `execute_workflow` |
| "Analyze the data" | Optimal Intel | `run_analysis` |
| "Define the structure" | Element Design | `create_schema` |
