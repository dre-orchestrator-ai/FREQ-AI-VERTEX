# FREQ AI SOL Architecture

## System Overview

The FREQ AI Sophisticated Operational Lattice (SOL) is a multi-agent AI orchestration system built on Google Cloud Vertex AI. It provides natural language orchestration capabilities for enterprise operations across regulated industries.

## Core Components

### 1. FSM State Controller (`core/fsm.py`)

The Finite State Machine controller manages the orchestration workflow through a rigid state progression:

```
IDLE → DIRECTIVE → VALIDATION → QUORUM → EXECUTION → AUDIT → COMPLETE
                                                               ↓
                                                            VETO
```

**Key Features:**
- State validation and transition tracking
- Timeout monitoring (default: 30s)
- State history and context management
- Elapsed time calculation

**States:**
- `IDLE`: System waiting for directive
- `DIRECTIVE`: Directive received and parsed
- `VALIDATION`: All 7 nodes analyze directive in parallel
- `QUORUM`: Achieve k=3 consensus from node votes
- `EXECUTION`: Execute approved directive
- `AUDIT`: Audit execution and log to BigQuery
- `COMPLETE`: Successful completion
- `VETO`: Consensus failed or explicit rejection

### 2. FREQ LAW Enforcer (`core/freq_law.py`)

Enforces three core compliance principles:

**Response Time < 2000ms:**
- Async timeout enforcement on all operations
- Automatic failure on timeout violations
- Per-operation timing metrics

**k=3 Consensus:**
- Minimum 3 positive votes required
- Configurable consensus threshold
- Node vote aggregation and validation

**BigQuery Audit Trail:**
- Event logging to BigQuery
- State transitions tracking
- Consensus decisions recording
- Execution audit trail

### 3. Seven Gemini Nodes (`nodes/`)

Each node is a specialized Gemini-powered AI agent with domain expertise:

#### Base Node (`base_node.py`)
- Abstract base class for all nodes
- Vertex AI integration
- System prompt management
- Vote extraction from responses
- Mock response generation for testing

#### Specialized Nodes (`gemini_nodes.py`)

1. **Strategic Operations**
   - High-level strategic planning
   - Business alignment analysis
   - Resource allocation recommendations
   - Risk assessment

2. **Supply Chain Intelligence (SPCI)**
   - Inventory optimization
   - Logistics and transportation
   - Supplier management
   - Demand forecasting

3. **Legacy Architect**
   - Legacy system modernization
   - Architecture patterns
   - Migration strategies
   - Technical debt assessment

4. **Governance Engine**
   - Regulatory compliance
   - Industry standards
   - Risk management
   - Audit requirements

5. **Executive Automation**
   - Workflow automation
   - Execution planning
   - Error handling
   - Monitoring setup

6. **Optimal Intelligence**
   - Data analytics
   - Performance optimization
   - Predictive modeling
   - Cost-benefit analysis

7. **Element Design**
   - System design
   - Component architecture
   - Interface design
   - Engineering specifications

### 4. SOL Orchestrator (`orchestration/orchestrator.py`)

Main orchestration engine that coordinates all components:

**Key Responsibilities:**
- Initialize and manage 7 Gemini nodes
- Control FSM state progression
- Enforce FREQ LAW compliance
- Process natural language directives
- Aggregate node responses
- Manage consensus voting
- Handle vertical domain context
- Audit and logging

**Orchestration Flow:**
```python
async def orchestrate(directive, vertical, context):
    1. Validate inputs and vertical domain
    2. Transition IDLE → DIRECTIVE
    3. Transition DIRECTIVE → VALIDATION
       - Process directive through all 7 nodes in parallel
       - Each node analyzes and votes (approve/reject)
    4. Transition VALIDATION → QUORUM
       - Aggregate votes
       - Check k=3 consensus
    5. If consensus PASSED:
       - Transition QUORUM → EXECUTION
       - Execute the directive
       - Transition EXECUTION → AUDIT
       - Audit the execution
       - Transition AUDIT → COMPLETE
    6. If consensus FAILED:
       - Transition to VETO
    7. Reset FSM for next orchestration
```

### 5. Vertical Domain Support (`verticals/`)

Five vertical domains with specialized context:

**Maritime:**
- Vessel operations, port logistics
- Regulations: IMO, SOLAS, MARPOL

**Agriculture:**
- Crop management, supply chain
- Regulations: FDA, USDA, GAP

**Manufacturing:**
- Production optimization, quality control
- Regulations: ISO 9001, OSHA

**Healthcare:**
- Patient data, clinical workflows
- Regulations: HIPAA, FDA, HITECH

**Construction:**
- Project management, safety
- Regulations: OSHA, building codes

Each vertical provides:
- Domain description
- Key operational concerns
- Applicable regulations
- Typical operations

### 6. Command-Line Interface (`cli.py`)

Natural language interface for orchestration:

```bash
python -m freq_ai.cli "Your directive" --vertical <domain> --verbose
```

**Features:**
- Interactive CLI with rich output
- Vertical domain selection
- Verbose mode for detailed node responses
- JSON output mode
- Help documentation

## Data Flow

```
User Input (Natural Language)
        ↓
CLI / Python API
        ↓
SOL Orchestrator
        ↓
    FSM Controller
        ↓
  [VALIDATION State]
        ↓
    ┌────────────────────────────────┐
    │  7 Gemini Nodes (Parallel)     │
    │  - Each analyzes directive     │
    │  - Each provides vote          │
    └────────────────────────────────┘
        ↓
    Aggregate Votes
        ↓
   FREQ LAW Enforcer
   (Check k=3 consensus)
        ↓
   [QUORUM Decision]
        ↓
    ┌─────────┬─────────┐
    │ PASSED  │ FAILED  │
    ↓         ↓
EXECUTION   VETO
    ↓
AUDIT
    ↓
COMPLETE
```

## Performance Characteristics

**Response Times:**
- Node processing: < 100ms (mock mode)
- Full orchestration: 100-150ms (mock mode)
- With Vertex AI: < 2000ms (enforced by FREQ LAW)

**Concurrency:**
- All 7 nodes process in parallel
- Async/await throughout
- Non-blocking I/O

**Scalability:**
- Stateless orchestrator (can be horizontally scaled)
- Session-based tracking
- Independent per-request execution

## Error Handling

**Timeout Errors:**
- FREQ LAW enforces 2000ms timeout
- Raises `FREQLawViolation` exception
- Logged and returned in result

**Node Failures:**
- Individual node failures don't halt orchestration
- Failed nodes automatically vote "reject"
- Logged for debugging

**Consensus Failures:**
- Transition to VETO state
- Audit trail captured
- Detailed voting results returned

## Security Considerations

**API Keys:**
- Google Cloud credentials required for Vertex AI
- Environment variable configuration
- No credentials in code

**Audit Trails:**
- All operations logged to BigQuery
- Session ID tracking
- Timestamp and context preservation

**Compliance:**
- Industry-specific regulations per vertical
- Governance Engine node validates compliance
- Audit state ensures traceability

## Extension Points

**Adding New Nodes:**
1. Inherit from `GeminiNode`
2. Implement `get_system_prompt()`
3. Add to orchestrator initialization
4. Update consensus requirements if needed

**Adding New Verticals:**
1. Add to `Vertical` enum
2. Define metadata in `VERTICAL_METADATA`
3. Document regulations and operations

**Custom FREQ LAW Rules:**
1. Modify `FREQLawEnforcer` initialization
2. Adjust timeouts and consensus requirements
3. Configure BigQuery dataset/table

## Testing

**Without GCP Credentials:**
- Nodes use mock responses
- All functionality testable locally
- No Vertex AI API calls

**With GCP Credentials:**
- Full Gemini model integration
- Real BigQuery audit logging
- Production-grade responses

## Monitoring and Observability

**Structured Logging:**
- JSON format logs
- Timestamp on all events
- Session ID correlation
- State transitions tracked

**Metrics:**
- Response times per operation
- Consensus success/failure rates
- Node voting patterns
- FSM state durations

**Audit Trail:**
- BigQuery dataset for compliance
- Queryable event history
- Retention policies configurable

## Deployment

**Requirements:**
- Python 3.9+
- Google Cloud project with Vertex AI
- Optional: BigQuery dataset

**Configuration:**
- `config.yaml` for system settings
- Environment variables for credentials
- Runtime parameter overrides

**Modes:**
- Development: Mock responses, no GCP required
- Production: Full Vertex AI integration, audit logging

## Future Enhancements

**Potential Additions:**
- Web UI for orchestration
- Real-time execution monitoring
- Custom node templates
- Multi-language support
- Advanced consensus algorithms
- Integration with other AI models
- Workflow templates per vertical
- Historical analytics dashboard
